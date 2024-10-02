import os
import json
import asyncio
import websockets
from flask import Flask, request, send_from_directory
from google.cloud import speech
from google.oauth2 import service_account

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Google Speech-to-Text client
credentials = service_account.Credentials.from_service_account_file("path/to/your-service-account-file.json")
client = speech.SpeechClient(credentials=credentials)

# Flask application
app = Flask(__name__)

# Transcription Request Configuration
request_config = {
    "config": {
        "encoding": speech.RecognitionConfig.AudioEncoding.MULAW,
        "sample_rate_hertz": 8000,
        "language_code": "en-GB",
    },
    "interim_results": True,
}

# WebSocket server handling
connected_clients = set()

async def handle_connection(websocket, path):
    print("New Connection Initiated")
    recognize_stream = None
    
    try:
        async for message in websocket:
            msg = json.loads(message)
            
            if msg['event'] == "connected":
                print(f"A new call has connected.")
                
            elif msg['event'] == "start":
                print(f"Starting Media Stream {msg['streamSid']}")
                recognize_stream = client.streaming_recognize(request=request_config)
                
                for response in recognize_stream:
                    transcript = response.results[0].alternatives[0].transcript
                    print(transcript)
                    
                    # Broadcast the transcription to all connected clients
                    for client_ws in connected_clients:
                        if client_ws.open:
                            await client_ws.send(json.dumps({
                                'event': 'interim-transcription',
                                'text': transcript
                            }))
            
            elif msg['event'] == "media":
                # Send media packets to recognize_stream
                if recognize_stream:
                    recognize_stream.write(msg['media']['payload'])
                    
            elif msg['event'] == "stop":
                print("Call Has Ended")
                if recognize_stream:
                    recognize_stream.close()
                
    except websockets.ConnectionClosed:
        print("Connection Closed")
        
    finally:
        connected_clients.remove(websocket)

# Setup WebSocket route
async def websocket_handler(websocket, path):
    connected_clients.add(websocket)
    await handle_connection(websocket, path)

# Serve static files for frontend
@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

@app.route('/', methods=['POST'])
def handle_post():
    response = f"""
    <Response>
      <Start>
        <Stream url="wss://{request.host}/"/>
      </Start>
      <Say>I will stream the next 60 seconds of audio through your websocket</Say>
      <Pause length="60" />
    </Response>
    """
    return response, 200, {'Content-Type': 'text/xml'}

# Start the Flask server
if __name__ == '__main__':
    import threading
    import websockets
    
    def start_websocket_server():
        asyncio.get_event_loop().run_until_complete(
            websockets.serve(websocket_handler, "localhost", 8080)
        )
        asyncio.get_event_loop().run_forever()
    
    # Run WebSocket server in a separate thread
    ws_thread = threading.Thread(target=start_websocket_server)
    ws_thread.start()
    
    # Run Flask server
    app.run(port=8080)