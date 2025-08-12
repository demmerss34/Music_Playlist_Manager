import zmq

ADDRESS = "tcp://127.0.0.1:5558"


# client for Total Duration service
def send_duration_request(username: str) -> dict:
    """
    Requests the total duration of a user's liked songs.
    """
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://127.0.0.1:5558")

    payload = {
        "type": "get_total_duration",
        "username": username
    }

    socket.send_json(payload)

    # Poll for a response within timeout (e.g., 5 seconds)
    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)
    socks = dict(poller.poll(timeout=5000))  # 5-second timeout

    if socks.get(socket) == zmq.POLLIN:
        response = socket.recv_json()
        return response
    else:
        raise TimeoutError("No response from total duration service")
