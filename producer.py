import redis
import json
import uuid
from datetime import datetime
import time
import random
import argparse

r = redis.Redis(host='localhost', port=6379, db=0)

NOTIFICATION_TYPES = {
    "order_created": "New order #{order_id} created with total ${total}",
    "payment_received": "Payment of ${amount} received for order #{order_id}",
    "order_shipped": "Order #{order_id} has been shipped",
    "new_message": "New message from {sender}: '{content}'",
    "system_alert": "System alert: {message}"
}

def generate_test_message(notification_type=None, user_id=None):
    if not notification_type or notification_type not in NOTIFICATION_TYPES:
        notification_type = random.choice(list(NOTIFICATION_TYPES.keys()))
    if not user_id:
        user_id = random.randint(1, 100)
    payload = {
        "user_id": user_id
    }
    if notification_type == "order_created":
        payload.update({
            "order_id": random.randint(1000, 9999),
            "total": round(random.uniform(10, 1000), 2)
        })
    elif notification_type == "payment_received":
        payload.update({
            "order_id": random.randint(1000, 9999),
            "amount": round(random.uniform(10, 1000), 2)
        })
    elif notification_type == "order_shipped":
        payload.update({
            "order_id": random.randint(1000, 9999),
            "tracking_number": f"TRK{random.randint(10000, 99999)}"
        })
    elif notification_type == "new_message":
        payload.update({
            "sender": f"User{random.randint(1, 100)}",
            "content": random.choice([
                "Hello there!",
                "How are you?",
                "Can we talk?",
                "Check this out!",
                "Important message"
            ])
        })
    elif notification_type == "system_alert":
        payload.update({
            "message": random.choice([
                "Server maintenance scheduled",
                "New features available",
                "Please update your profile",
                "Security alert detected",
                "System update completed"
            ])
        })
    message = {
        "message_id": str(uuid.uuid4()),
        "type": notification_type,
        "sender": "notification_service",
        "payload": payload,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    return message

def send_message(message):
    r.lpush('alarm_queue', json.dumps(message))
    print(f"Sent message with ID: {message['message_id']}")
    print(f"Type: {message['type']}")
    print(f"For user: {message['payload'].get('user_id')}")
    print(f"Timestamp: {message['timestamp']}")
    print("---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send test notifications to Redis queue')
    parser.add_argument('--count', type=int, default=1, help='Number of notifications to send')
    parser.add_argument('--interval', type=float, default=1.0, help='Interval between sends (seconds)')
    parser.add_argument('--type', type=str, help='Notification type (leave empty for random)')
    parser.add_argument('--user', type=int, help='User ID (leave empty for random)')
    args = parser.parse_args()
    print(f"Sending {args.count} notification(s) with {args.interval}s interval...")
    for i in range(args.count):
        message = generate_test_message(args.type, args.user)
        send_message(message)
        if i < args.count - 1:
            time.sleep(args.interval)
    print("Done!")