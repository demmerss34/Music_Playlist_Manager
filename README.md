# CS361 Music Playlist Manager 

This project is a Python-based CLI application that allows users to manage a 
personal music playlist, inspired by services like Spotify.

It supports adding, deleting, and viewing songs in your playlist, and 
communicates with a recommendation microservice to fetch personalized song 
recommendations based on:
- The same artist
- The same genre
- Overall popularity (excluding songs already on your playlist)

## Features

- Add songs by title and artist from a dataset
- Remove songs from your playlist
- View your current playlist 
- Communicate with an external recommendation microservice (via ZeroMQ)
- Secured with environment-based API authentication (`.env` file)







