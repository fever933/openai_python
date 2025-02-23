from flask import Flask, render_template, request, jsonify,Response,stream_with_context
from datetime import datetime, date
import json
import os
import openai
import time
import requests
from openai import OpenAI
from uuid import uuid4


app = Flask(__name__)

# 在文件顶部添加你的 OpenAI API 密钥
from config import API_KEY  # 导入 API 密钥

class FoodItem:
    def __init__(self, name, expiry_date, quantity, category, unit, create_date=None, id=None):
        self.id = id or str(uuid4())
        self.name = name
        self.expiry_date = expiry_date  # 保存为字符串格式
        self.quantity = quantity
        self.category = category
        self.unit = unit
        self.create_date = create_date if create_date else date.today().strftime('%Y-%m-%d')  # 保存为字符串格式
    
    def to_dict(self):
        expiry_date = self.expiry_date
        create_date = self.create_date

            # 确保 expiry_date 和 create_date 是 datetime.date 类型
        if isinstance(expiry_date, str):
            expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').date()
        if isinstance(create_date, str):
            create_date = datetime.strptime(create_date, '%Y-%m-%d').date()
        return {
            'id': self.id,
            'name': self.name,
            'expiry_date': self.expiry_date,
            'quantity': self.quantity,
            'category': self.category,
            'unit': self.unit,
            'create_date': self.create_date
        }

class FridgeManager:
    def __init__(self):
        self.items = []
        self.data_file = 'fridge_data.json'
        self.load_data()
    
    def save_data(self):
        try:
            data = [item.to_dict() for item in self.items]
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving data: {str(e)}")
    
    def load_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.items = [FoodItem(**item) for item in data]
        except Exception as e:
            print(f"加载数据时出错: {str(e)}")

fridge = FridgeManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/foods', methods=['GET'])
def get_foods():
    today = date.today()
    foods = []
    fridge = FridgeManager()


    for item in fridge.items:
        # 将字符串转换为 datetime.date 对象
        expiry_date = datetime.strptime(item.expiry_date, '%Y-%m-%d').date()
        status = "已过期" if expiry_date < today else \
                "即将过期" if (expiry_date - today).days <= 3 else "正常"
        foods.append({
            **item.to_dict(),
            'status': status
        })
    return jsonify(foods)
        

@app.route('/api/foods', methods=['POST'])
def add_food():
    try:
        data = request.json
        food = FoodItem(
            name=data['name'],
            expiry_date=data['expiry_date'],
            quantity=int(data['quantity']),
            category=data['category'],
            unit=data['unit'],
            create_date=data['create_date'],
        )
        fridge.items.append(food)
        fridge.save_data()
        return jsonify({'message': '添加成功'}), 200
    except Exception as e:
        print(f"添加食物时出错: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/foods/<id>', methods=['DELETE'])
def remove_food(id):
    try:
        quantity = int(request.args.get('quantity', 1))
        for item in fridge.items:
            if item.id == id:
                if item.quantity <= quantity:
                    fridge.items.remove(item)
                else:
                    item.quantity -= quantity
                fridge.save_data()
                return jsonify({'message': '删除成功'}), 200
        return jsonify({'error': '未找到食物'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/foods/all/<id>', methods=['DELETE'])
def remove_all_food(id):
    try:
        fridge.items = [item for item in fridge.items if item.id != id]
        fridge.save_data()
        return jsonify({'message': '所有指定食物已删除'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
@app.route('/api/suggestions', methods=['POST'])
def get_suggestions():
    try:
        # Read ingredients from fridge data
        ingredients = []
        data = request.get_json()
        need_buy_more_value = data.get('needBuyMore', 'false')
        need_buy_more = '必要情况可以去买一些常见蔬菜作为配菜' if need_buy_more_value.lower() == 'true' else '尽量不要买其他配菜'
        try:
            with open('fridge_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                ingredients = [f"{item['name']} ({item['quantity']} {item['unit']})" for item in data]
        except FileNotFoundError:
            return jsonify({'error': '找不到食材数据文件'}), 404
        except json.JSONDecodeError:
            return jsonify({'error': '食材数据格式错误'}), 400
        except Exception as e:
            return jsonify({'error': f'读取食材数据失败: {str(e)}'}), 500

        if not ingredients:
            return jsonify({'error': '冰箱中没有食材'}), 404

        # Create prompt with ingredients
        ingredients_str = ', '.join(ingredients)
        prompt = f"你是一个小红书的美食博主，请根据家里冰箱已有的食材： '{ingredients_str}'，请给出可以制作的家常菜建议，'{need_buy_more}',做出两到三个菜，供两个人吃，要求菜品要精致营养，荤素搭配，不要搞奇怪的搭配尽可能的常见的，淮扬菜、川湘菜、东北菜都可以，葱姜蒜等家里常备不需考虑。"
        print(prompt)
        # Call API
        try:
            client = OpenAI(
                api_key=API_KEY,  # 使用从 config.py 中读取的 API 密钥
                base_url="https://api.deepseek.com"
            )

            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                timeout=30  # 增加超时时间
            )

            def generate():
                try:
                    for chunk in response:
                        if chunk.choices[0].delta.content:
                            yield f"{chunk.choices[0].delta.content}"
                except Exception as e:
                    yield f"生成建议时出错: {str(e)}"

            return Response(
                stream_with_context(generate()), 
                mimetype='text/event-stream'
            )

        except Exception as e:
            return jsonify({'error': f'API调用失败: {str(e)}'}), 503

    except Exception as e:
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500 
    
    

if __name__ == '__main__':
    app.run(debug=True) 