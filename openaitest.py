import os
from typing import Optional
import requests
import json

class DeepSeekAPI:
  def __init__(self, api_key: Optional[str] = None):
    self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
    if not self.api_key:
      raise ValueError("DeepSeek API key is required")
    self.base_url = "https://api.deepseek.com/v1"
  
  def ask_cooking_tips_stream(self, question: str):
    endpoint = f"{self.base_url}/chat/completions"
    
    headers = {
      "Authorization": f"Bearer {self.api_key}",
      "Content-Type": "application/json"
    }
    
    data = {
      "messages": [
        {"role": "system", "content": "You are a professional chef who can provide detailed cooking advice."},
        {"role": "user", "content": question}
      ],
      "model": "deepseek-chat",
      "temperature": 0.7,
      "stream": True  # 启用流式输出
    }
    
    try:
      response = requests.post(endpoint, headers=headers, json=data, stream=True)
      response.raise_for_status()
      
      for line in response.iter_lines():
        if line:
          # 移除 "data: " 前缀并解析 JSON
          json_str = line.decode('utf-8').replace('data: ', '')
          if json_str != '[DONE]':
            try:
              json_data = json.loads(json_str)
              if 'choices' in json_data and len(json_data['choices']) > 0:
                content = json_data['choices'][0]['delta'].get('content', '')
                if content:
                  print(content, end='', flush=True)
            except json.JSONDecodeError:
              continue
      print()  # 最后打印换行
    except requests.exceptions.RequestException as e:
      print(f"Error making request: {str(e)}")

def main():
  # Replace with your actual API key or set it as an environment variable
  api_key = "sk-545e0b28cc5f4292bb69ebac2d256a19"
  
  deepseek = DeepSeekAPI(api_key)
  
  while True:
    question = input("\n请输入您的烹饪问题 (输入 'quit' 退出): ")
    if question.lower() == 'quit':
      break
      
    print("\n回答：")
    deepseek.ask_cooking_tips_stream(question)
    print("\n" + "="*50)

if __name__ == "__main__":
  main()