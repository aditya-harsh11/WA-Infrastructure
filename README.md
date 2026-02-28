# WA UDP V2X Challenge

Challenge : https://github.com/exie21/wa-udp-v2x-challenge

## Overview
This project implements a simulated V2X (Vehicle-to-Everything) communication node using Python and UDP. The node listens for "beacon" messages from other vehicles, calculates their distance relative to the origin, and identifies the nearest neighbor.

## Features
-   **UDP Listener**: Listens on port 5005 for JSON-formatted beacon messages.
-   **Distance Calculation**: Computes Euclidean distance from the origin (0,0).
-   **Nearest Neighbor**: Identifies the closest vehicle from the received beacons.
-   **JSON Output**: Publishes a summary of the nearest neighbor in JSON format.
-   **Robustness**: Handles malformed messages, timeouts, and invalid data types gracefully.

## Requirements
-   Python 3.x
-   Standard libraries: `socket`, `json`, `time`, `math`, `sys`

## Usage

### Running the Node
To run the node primarily:
```bash
python3 candidate/neighbor_node.py
```
The node will listen for 1 second after the first message is received and then print the summary to stdout.

### Running with Test Harness
To simulate traffic and test the node:
```bash
# Terminal 1: Start the publisher (sends fake beacon messages)
./harness/launch.sh

# Terminal 2: Run the node
python3 candidate/neighbor_node.py
```

### Running Automated Tests
To run the full test suite (provided by the challenge grader):
```bash
./grader/run_all.sh
```

## Project Structure
-   `candidate/`: Contains the source code (`neighbor_node.py`).
-   `harness/`: Contains scripts to simulate beacon publishers.
-   `grader/`: Contains test scripts to verify correctness.
