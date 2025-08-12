# Random Song Microservice

Returns a random song from the dataset.

## Port

Listens on `tcp://*:5556`

## Dependencies

- Requires a local copy of `spotify_data.csv` in this directory
- Uses `pandas` and `zmq`

## How It Works

- Loads the dataset from `spotify_data.csv`
- Returns a randomly selected song record

## Running the Server

```
python zeroMQServer.py
```

## Making a Request (Client)

```
python zeroMQClient.py
```