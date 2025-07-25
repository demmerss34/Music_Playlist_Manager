import zmq
import json
import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()
AUTH_KEY = os.getenv("AUTH_KEY")

def send_request(payload: dict) -> dict:
    """
    Sends a payload to the recommendation microservice via ZeroMQ.
    The payload must include a 'type' key such as 'recommend_by_genre'.
    The function attaches the auth key and returns the JSON-decoded response.
    """
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")

    payload["auth_key"] = AUTH_KEY
    socket.send_string(json.dumps(payload))

    response = socket.recv()
    return json.loads(response.decode('utf-8'))


