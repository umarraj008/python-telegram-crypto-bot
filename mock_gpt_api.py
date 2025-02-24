from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/v1/chat/completions', methods=['POST'])
def mock_gpt():
    """
    Simulates OpenAI's GPT-3.5 Turbo API response.
    """

    data = request.json
    messages = data.get("messages", [])
    
    # Extracting the message content
    user_message = messages[-1]['content'] if messages else ""

    # Simulated logic: If the message contains "coin", return a fake CA
    if "coin" in user_message.lower():
        response_text = "Buy,4nZgJwz2qY9s5XVrW1K8LR6PpD5R7JmV4Bg1y6f3qJAz"
    elif "scam" in user_message.lower():
        response_text = "Rug Pull,4nZgJwz2qY9s5XVrW1K8LR6PpD5R7JmV4Bg1y6f3qJAz"
    else:
        response_text = "No CA,"

    # Fake GPT response format
    return jsonify({
        "id": "test-gpt-response",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "gpt-3.5-turbo",
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": response_text
                }
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 5,
            "total_tokens": 15
        }
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)