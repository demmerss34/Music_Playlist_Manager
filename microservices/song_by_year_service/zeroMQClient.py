import zmq

ADDRESS = "tcp://127.0.0.1:5557"

def send_year_request(year: int, timeout_ms: int = 5000) -> dict:
    """
    Ask the song-by-year microservice for a random song from the given
    year. Raises TimeoutError if the service doesn't respond in time.
    """
    if not isinstance(year, int):
        raise ValueError("year must be an integer")

    context = zmq.Context.instance()
    socket = context.socket(zmq.REQ)
    socket.connect(ADDRESS)

    try:
        payload = {"type": "get_song_by_year", "year": year}
        socket.send_json(payload)

        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN)
        socks = dict(poller.poll(timeout_ms))

        if socks.get(socket) == zmq.POLLIN:
            return socket.recv_json()
        else:
            raise TimeoutError(f"No response from song-by-year "
                               f"service within {timeout_ms} ms")
    finally:
        socket.close()
