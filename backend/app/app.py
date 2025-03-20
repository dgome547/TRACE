# backend/app/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from webcrawler import crawl

app = Flask(__name__)
CORS(app)

@app.route('/app/webcrawler', methods=['POST'])
def start_crawler():
    data = request.json
    url = data.get('url')
    depth_limit = int(data.get('depthLimit', 1))
    timeout = int(data.get('timeout', 5000))
    
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    try:
        results = crawl(url, depth_limit, timeout)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/example', methods=['GET'])
def example_route():
    return jsonify({"message": "Hello from Flask!"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)