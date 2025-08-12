import zmq


def request_random_song() -> dict:
    """
    Sends a request to the random song microservice and returns one random song.
    """
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5556")

    # Send request
    payload = {"type": "random_song"}
    socket.send_json(payload)

    # Receive response
    response = socket.recv_json()
    return response.get("song", {})
