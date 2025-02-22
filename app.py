from flask import Flask, render_template, request, jsonify,Response,stream_with_context
from datetime import datetime, date
import json
import os
import openai
import time
import requests
from openai import OpenAI

app = Flask(__name__)

# 在文件顶部添加你的 OpenAI API 密钥
# openai.api_key = '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'  # 替换为你的 API 密钥

class FoodItem:
    def __init__(self, name, expiry_date, quantity, category):
        self.name = name
        self.expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').date()
        self.quantity = quantity
        self.category = category
    
    def to_dict(self):
        return {
            'name': self.name,
            'expiry_date': self.expiry_date.strftime('%Y-%m-%d'),
            'quantity': self.quantity,
            'category': self.category
        }

class FridgeManager:
    def __init__(self):
        self.items = []
        self.data_file = 'fridge_data.json'
        self.load_data()
    
    def save_data(self):
        data = [item.to_dict() for item in self.items]
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
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
    for item in fridge.items:
        status = "已过期" if item.expiry_date < today else \
                "即将过期" if (item.expiry_date - today).days <= 3 else "正常"
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
            category=data['category']
        )
        fridge.items.append(food)
        fridge.save_data()
        return jsonify({'message': '添加成功'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/foods/<name>', methods=['DELETE'])
def remove_food(name):
    try:
        quantity = int(request.args.get('quantity', 1))
        for item in fridge.items:
            if item.name == name:
                if item.quantity <= quantity:
                    fridge.items.remove(item)
                else:
                    item.quantity -= quantity
                fridge.save_data()
                return jsonify({'message': '删除成功'}), 200
        return jsonify({'error': '未找到食物'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/suggestions', methods=['POST'])
def get_suggestions():
    try:
        # Read ingredients from fridge data
        ingredients = []
        try:
            with open('fridge_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                ingredients = [f"{item['name']} ({item['quantity']}份)" for item in data]
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
        prompt = f"作为一个专业厨师，基于以下食材及其数量 '{ingredients_str}'，请给出可以制作的家常菜建议，要求尽可能只用提供的食材，不需要全用完，用网红厨师王刚的风格回答。"

        # Call API
        try:
            client = OpenAI(
                api_key="sk-cf183fa0e2314e63b0f616f471a32b26", 
                base_url="https://api.deepseek.com"
            )

            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                stream=True
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