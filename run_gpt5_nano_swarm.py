#!/usr/bin/env python3
"""
Background Runner for GPT-5 Nano ARC3 Agent.
Runs the GPT-5 Nano agent on all available games in the background.
"""

import threading
import logging
import requests
import json
import os
import signal
import sys
from functools import partial
from agents import Swarm, AVAILABLE_AGENTS

# Configuration
AGENT_NAME = "gpt5nano"
ROOT_URL = "https://three.arcprize.org"
TAGS = ["gpt-5-nano", "automated-run", "background"]

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("gpt5_nano_run.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("GPT5NanoRunner")

def get_all_games():
    """Fetch all available games from the ARC3 API."""
    try:
        response = requests.get(f"{ROOT_URL}/api/games")
        response.raise_for_status()
        games = [g["game_id"] for g in response.json()]
        logger.info(f"Fetched {len(games)} games from API.")
        return games
    except Exception as e:
        logger.error(f"Failed to fetch games: {e}")
        return []

def run_agent(swarm):
    """Run the swarm of agents."""
    try:
        swarm.run()
        logger.info("Swarm completed successfully.")
    except Exception as e:
        logger.error(f"Swarm encountered an error: {e}")

def cleanup(swarm, signum, frame):
    """Graceful shutdown handling."""
    logger.info("Shutdown signal received. Cleaning up...")
    # Add any specific cleanup logic if Swarm supports it
    sys.exit(0)

def main():
    if AGENT_NAME not in AVAILABLE_AGENTS:
        logger.error(f"Agent '{AGENT_NAME}' not found in AVAILABLE_AGENTS.")
        return

    games = get_all_games()
    if not games:
        logger.error("No games to play.")
        return

    logger.info(f"Starting swarm with agent '{AGENT_NAME}' on {len(games)} games...")
    
    swarm = Swarm(
        AGENT_NAME,
        ROOT_URL,
        games,
        tags=TAGS,
    )

    # Note: main.py uses a thread for run_agent, but for a background script 
    # we can just run it in the main thread or as a daemon.
    # To run in "background", the user should call it with 'nohup' or similar,
    # but we can also handle it here.
    
    signal.signal(signal.SIGINT, partial(cleanup, swarm))
    signal.signal(signal.SIGTERM, partial(cleanup, swarm))

    try:
        swarm.run()
    except KeyboardInterrupt:
        logger.info("Interrupted by user.")
    except Exception as e:
        logger.error(f"Main loop error: {e}")

if __name__ == "__main__":
    main()
