import zmq

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

def send_request(payload, timeout=5000):  # timeout in milliseconds
    socket.setsockopt(zmq.RCVTIMEO, timeout)
    socket.setsockopt(zmq.SNDTIMEO, timeout)

    socket.send_json(payload)
    try:
        response = socket.recv_json()
        return response
    except zmq.error.Again:
        raise TimeoutError(f"No response from microservice within {timeout} ms")




