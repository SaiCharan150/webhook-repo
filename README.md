# GitHub Webhook Receiver

A Flask application that receives GitHub webhook events, stores them in MongoDB, and displays them in a web interface.

## Features

- Receives GitHub webhook events (push, pull request, merge)
- Stores events in MongoDB
- Web interface that auto-refreshes every 15 seconds
- Supports webhook secret verification

## Setup

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your configuration: