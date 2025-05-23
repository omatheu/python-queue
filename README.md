# Redis Notification System

A simple notification system using Redis, WebSockets, and Python.

## Components

- **Producer**: Sends messages to a Redis queue
- **Consumer**: Reads messages from the Redis queue and forwards them to connected clients via WebSocket
- **Frontend**: A simple web page that connects to the WebSocket server and displays notifications

## Setup

1. Install Redis on your system
2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the System

1. Start Redis server if not already running:
   ```
   redis-server
   ```

2. Start the consumer (WebSocket server):
   ```
   python consumer.py
   ```

3. Open the frontend in a browser:
   ```
   # You can use any simple HTTP server, for example:
   python -m http.server 8000 --directory frontend
   ```
   Then open http://localhost:8000 in your browser

4. Send test messages using the producer:
   ```
   python producer.py
   ```

## How It Works

1. The producer sends messages to a Redis queue (`alarm_queue`)
2. The consumer reads messages from the queue and forwards them to connected WebSocket clients
3. The frontend connects to the WebSocket server and displays notifications as they arrive
