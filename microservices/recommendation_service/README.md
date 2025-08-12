# Music Recommendation Microservice

Listens on `tcp://*:5555` and serves music recommendations based on:
- Artist (`recommend_by_artist`)
- Genre (`recommend_by_genre`)
- Popularity (`recommend_popular`)

## Dependencies

- Uses `pandas`, `sqlite3`, and `zmq`
- Optionally supports `scikit-learn` and `joblib` (if ML models are used)
- Requires a local SQLite database: `songsData.db`

## How It Works

- Artist and popular recommendations come from a cleaned Pandas dataframe
- Genre-based recommendations come from a SQLite database (`songsData.db`),
  which is optionally restored from `songsData_dump.sql`

## Running the Server

```
python zeroMQServer.py
```

## Making a Request (Client)

```
python zeroMQClient.py
```





