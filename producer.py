import redis
import json
from datetime import datetime

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, db=0)

# Create test message
message = {
  "message_id": "123abc",
  "type": "order_created",
  "sender": "order_service",
  "payload": {
    "order_id": 987,
    "user_id": 42,
    "total": 199.90
  },
  "timestamp": "2025-05-22T15:00:00Z"
}

# Send message to queue
r.lpush('alarm_queue', json.dumps(message))
print(f"Sent message with ID: {message['message_id']}")
