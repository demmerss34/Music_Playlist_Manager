"""
ZeroMQ Server
"""
import zmq
import songRecommenderKNN
import genreQuery


def main():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")

    print("ZeroMQ Server started on port 5555... Press Ctrl+C to stop.")

    try:
        while True:
            try:
                received_data = socket.recv_json()
                print(f"\n Received request: {received_data}")

                request_type = received_data.get("type")

                if request_type == "recommend_by_artist":
                    artist = received_data.get("artist", "")
                    print(f"Artist of interest: {artist}")
                    recommendations = (
                        songRecommenderKNN.get_more_songs_by_artist(artist)
                    )


                elif request_type == "recommend_popular":
                    print("Recommending top popular songs...")
                    recommendations = (
                        songRecommenderKNN.get_top_popular_songs()
                    )

                elif request_type == "recommend_by_genre":
                    genre = received_data.get("genre", "")
                    print(f"Genre of interest: {genre}")
                    connection = genreQuery.createConnection()
                    rows = genreQuery.returnByGenre(connection, genre)
                    recommendations = genreQuery.formartDict(connection, rows)
                    genreQuery.closeConnection(connection)

                else:
                    print(f"Unknown request type: {request_type}")
                    recommendations = {"error": "Invalid request type"}

                print(f"Sending recommendations: {recommendations}")
                socket.send_json(recommendations)

            except Exception as e:
                print(f"Error processing request: {e}")
                socket.send_json({"error": str(e)})

    except KeyboardInterrupt:
        print("\n Server manually stopped.")

    finally:
        print("Closing socket and terminating context...")
        socket.close()
        context.term()
        print("Server shutdown complete.")


if __name__ == "__main__":
    main()
