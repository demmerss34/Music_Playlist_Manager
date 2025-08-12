# Song-by-Year Microservice

Returns a random song from a given year.

## Port

Listens on `tcp://*:5557`

## Dependencies

- Requires a local copy of `spotify_data.csv` in this directory
- Uses `pandas` and `zmq`

## How It Works

- Loads the dataset from `spotify_data.csv`
- Filters songs based on the provided year
- Returns a random song from that year

## Running the Server

```
python zeroMQServer.py
```

## Making a Request (Client)

```
python zeroMQClient.py
```