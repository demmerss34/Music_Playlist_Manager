# Total Playlist Duration Microservice

Calculates the total duration of a user's liked songs.

## Port

Listens on `tcp://*:5558`

## Dependencies

- Uses `pandas`, `json`, and `zmq`
- Reads user song lists from `main_program/liked_songs/<username>.json`

## How It Works

- Loads a user's liked songs from a JSON file
- Computes and returns the total duration of all valid songs

## Running the Server

```
python zeroMQServer.py
```

## Making a Request (Client)

```
python zeroMQClient.py
```