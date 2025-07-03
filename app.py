from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# MongoDB configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client.github_events
events_collection = db.events

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('X-GitHub-Event'):
        data = request.json
        event_type = request.headers['X-GitHub-Event']
        
        # Verify the webhook secret if configured
        secret = os.getenv('WEBHOOK_SECRET')
        if secret:
            signature = request.headers.get('X-Hub-Signature-256', '').split('=')[1]
            if not verify_signature(secret, request.data, signature):
                return jsonify({'status': 'unauthorized'}), 401
        
        # Process different event types
        if event_type == 'push':
            process_push_event(data)
        elif event_type == 'pull_request':
            process_pull_request_event(data)
        
        return jsonify({'status': 'success'}), 200
    return jsonify({'status': 'bad request'}), 400

def verify_signature(secret, payload, signature):
    import hmac
    import hashlib
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_signature, signature)

def process_push_event(data):
    event = {
        'request_id': data['after'],
        'author': data['pusher']['name'],
        'action': 'PUSH',
        'from_branch': None,  # Not applicable for push
        'to_branch': data['ref'].split('/')[-1],
        'timestamp': datetime.utcnow().isoformat()
    }
    events_collection.insert_one(event)

def process_pull_request_event(data):
    pr_data = data['pull_request']
    action = data['action']
    
    if action == 'closed' and pr_data['merged']:
        event_type = 'MERGE'
    else:
        event_type = 'PULL_REQUEST'
    
    event = {
        'request_id': str(pr_data['number']),
        'author': pr_data['user']['login'],
        'action': event_type,
        'from_branch': pr_data['head']['ref'],
        'to_branch': pr_data['base']['ref'],
        'timestamp': datetime.utcnow().isoformat()
    }
    events_collection.insert_one(event)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/events')
def get_events():
    events = list(events_collection.find({}, {'_id': 0}).sort('timestamp', -1).limit(10))
    return jsonify(events)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)