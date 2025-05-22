import redis
import json
from datetime import datetime

r = redis.Redis(host='localhost', port=6379, db=0)

while True:
    # Blocking pop to wait for new messages
    metadata = r.brpop('alarm_queue')
    message = json.loads(metadata[1].decode('utf-8'))

    print(f"Received message:")
    print(f"Message ID: {message.get('message_id')}")
    print(f"Type: {message.get('type')}")
    print(f"Sender: {message.get('sender')}")
    print(f"Timestamp: {message.get('timestamp')}")
    print(f"Payload: {message.get('payload')}")
