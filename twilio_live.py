import threading
import os
import json
import asyncio
import websockets
from flask import Flask, request, send_from_directory
from pydub import AudioSegment
from LLMOps.OpenAI import OpenAILLMHandler, OpenAISpeechHandler
from DBOps.firebase import FirebaseOps
from prompt import system_prompt
import io
import configparser
import logging
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set Log Level
logger = logging.getLogger()
logger.setLevel(logging.WARNING)

# Define Config Object
config = configparser.ConfigParser()
config.read('config.ini')

# Read OpenAI API key from config
openai_api_key = config['OpenAI']['api_key']

llm_model = config['Models']['llm']
stt_model = config['Models']['stt']

# Create OpenAI Handlers
llm_handler = OpenAILLMHandler(openai_api_key)

# Create Speech to text handler Handler
speech_to_text_handler = OpenAISpeechHandler(openai_api_key)

# Create Firebase Handler
firebase_handler = FirebaseOps(config['Firebase']['credentials_path'], config['Firebase']['database_url'])

# create messages and insert system prompt
messages = [
    {
        "role": "system",
        "content": [
            {
                "type": "text", 
                "text": system_prompt
            }
        ]
    }
]

# Twilio credentials
account_sid = config['Twilio']['account_sid']
auth_token = config['Twilio']['auth_token']
twilio_client = Client(account_sid, auth_token)

# Flask application
app = Flask(__name__)

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

# Function to process audio stream
def process_audio_stream(audio_stream):
    audio = AudioSegment.from_file(io.BytesIO(audio_stream), format="wav")
    chunk_length_ms = 10 * 1000  # 10 seconds in milliseconds
    for i, chunk_start in enumerate(range(0, len(audio), chunk_length_ms)):
        chunk = audio[chunk_start:chunk_start + chunk_length_ms]
        
        buffer = io.BytesIO()
        buffer.name = f"chunk_{i+1}.wav"
        chunk.export(buffer, format="wav")
        buffer.seek(0)
        
        transcription, cost, language = speech_to_text_handler.transcribe_buffer(buffer)
        if len(transcription.split()) < 10:
            continue
        
        messages.append({"role": "user", "content": f"Chunk {i+1}: {transcription}"})
        response_message, cost, role, model, completion_tokens, prompt_tokens = llm_handler.send_text(
            messages,
            model=llm_model
        )
        
        firebase_handler.update_value(key='Response', value=response_message)
        messages.append({"role": role, "content": response_message})
        
        print(f"Chunk {i+1} processed:")
        print(f"Transcription: {transcription}")
        print(f"LLM Response: {response_message}")
        print("----------------------------------")
        print()

# Start the Flask server
if __name__ == '__main__':
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
