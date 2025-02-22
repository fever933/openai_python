from flask import Flask, render_template, request, jsonify,Response,stream_with_context
from openai import OpenAI

app = Flask(__name__)

# Set your OpenAI API key here
# openai.api_key = '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'
# DeepSeek API URL
# openai.api_key = 'sk-cf183fa0e2314e63b0f616f471a32b26'
# openai.base_url= 'https://api.deepseek.com'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    try:
        user_input = request.form['user_input']
        client = OpenAI(api_key="sk-cf183fa0e2314e63b0f616f471a32b26", base_url="https://api.deepseek.com")

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": user_input}],
            stream=True
        )

        def generate():
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield f"{chunk.choices[0].delta.content}"

        return Response(stream_with_context(generate()), mimetype='text/event-stream')
    except KeyError:
        return "Bad Request: Missing 'user_input' field", 400

if __name__ == '__main__':
    app.run(debug=True)