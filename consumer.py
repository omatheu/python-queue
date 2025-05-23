import redis
import json
import asyncio
import websockets
import signal
from datetime import datetime

connected_clients = {}

r = redis.Redis(host='localhost', port=6379, db=0)

NOTIFICATION_TEMPLATES = {
    "order_created": "New order #{order_id} created with total ${total}",
    "payment_received": "Payment of ${amount} received for order #{order_id}",
    "order_shipped": "Order #{order_id} has been shipped via {tracking_number}",
    "new_message": "New message from {sender}: '{content}'",
    "system_alert": "System alert: {message}"
}

DEFAULT_TEMPLATE = "New notification from {sender}"

def format_notification_message(msg_type, payload, sender):
    template = NOTIFICATION_TEMPLATES.get(msg_type, DEFAULT_TEMPLATE)
    
    try:
        formatted_message = template.format(**payload, sender=sender)
    except KeyError:
        formatted_message = f"New {msg_type} notification"
    
    return formatted_message

async def handle_connection(websocket):
    request_headers = getattr(websocket, 'request_headers', {})
    user_id = "unknown"
    user_id = "12345"
    connected_clients[user_id] = websocket
    print(f"Client connected: {user_id}")
    
    try:
        async for message in websocket:
            print(f"Received message from client {user_id}: {message}")
    except Exception as e:
        print(f"Error in websocket communication: {e}")
    finally:
        if user_id in connected_clients:
            del connected_clients[user_id]
            print(f"Client disconnected: {user_id}")

async def process_redis_messages():
    redis_async = redis.Redis(host='localhost', port=6379, db=0)
    
    while True:
        try:
            message_data = redis_async.brpop('alarm_queue', timeout=1)
            
            if message_data:
                message = json.loads(message_data[1].decode('utf-8'))
                
                print(f"Received message:")
                print(f"Message ID: {message.get('message_id')}")
                print(f"Type: {message.get('type')}")
                print(f"Sender: {message.get('sender')}")
                print(f"Timestamp: {message.get('timestamp')}")
                print(f"Payload: {message.get('payload')}")
                
                msg_type = message.get('type')
                payload = message.get('payload', {})
                sender = message.get('sender')
                user_id = str(payload.get('user_id', ''))
                
                notification_message = format_notification_message(msg_type, payload, sender)
                
                notification = {
                    'type': msg_type,
                    'message': notification_message,
                    'timestamp': message.get('timestamp')
                }
                
                if user_id and user_id in connected_clients:
                    try:
                        await connected_clients[user_id].send(json.dumps(notification))
                        print(f"Notification sent to user {user_id}: {notification_message}")
                    except Exception as e:
                        print(f"Error sending to user {user_id}: {e}")
                else:
                    disconnected = []
                    for client_id, client_ws in connected_clients.items():
                        try:
                            await client_ws.send(json.dumps(notification))
                            print(f"Notification broadcast to user {client_id}: {notification_message}")
                        except Exception as e:
                            print(f"Error sending to {client_id}: {e}")
                            disconnected.append(client_id)
                    
                    for client_id in disconnected:
                        del connected_clients[client_id]
        except Exception as e:
            print(f"Error processing message: {e}")
        
        await asyncio.sleep(0.1)

async def main():
    stop = asyncio.Future()
    server = await websockets.serve(handle_connection, "localhost", 8080)
    
    redis_task = asyncio.create_task(process_redis_messages())
    
    def handle_signal(signum, frame):
        stop.set_result(None)
    
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    
    print("🚀 Notification server running at ws://localhost:8080")
    print("Waiting for Redis messages and WebSocket connections...")
    
    await stop
    
    server.close()
    await server.wait_closed()
    redis_task.cancel()
    
    print("Server shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())