#!/bin/sh

# Start the Letta server in the background
poetry run letta server &

# Start the Yanara service
poetry run python -m yanara.main
