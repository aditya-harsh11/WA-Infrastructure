#Author: Aditya Harshavardhan
#Date: 2/26/2026
#This should be the only file you edit. You are free to look at other files for reference, but do not change them.
#Below are are two methods which you must implement: euclidean_dist_to_origin and nearest_neighbor as well as the main function beacon handling. 
#Helper Functions are allowed, but not required. You must not change the imports, the main function signature, or the return value of the main function.


"""
Neighbor Table

Listen on UDP 127.0.0.1:5005 for beacon messages:
  {"id":"veh_XXX","pos":[x,y],"speed":mps,"ts":epoch_ms}

Collect beacons for ~1 second starting from the *first* message.
Then print exactly ONE JSON line and exit:

{
  "topic": "/v2x/neighbor_summary",
  "count": <int>,
  "nearest": {"id": "...", "dist": <float>} OR null,
  "ts": <now_ms>
}

Constraints:
- Python 3 stdlib only.
- Ignore malformed messages; don't crash.
- Do NOT listen to ticks (5006).
"""

import socket, json, time, math, sys
from typing import Dict, Any, Optional, Tuple

HOST = "127.0.0.1"
PORT_BEACON = 5005
COLLECT_WINDOW_MS = 1000  # ~1 second

# Helper: Gets the current time in milliseconds (1 second = 1000 milliseconds)
def now_ms() -> int:
    return int(time.time() * 1000)

# Function: Calculates how far a point (x, y) is from the center (0, 0)
def euclidean_dist_to_origin(pos) -> float:
    # 1. Validation: Ensure we actually received a list/tuple with exactly two coordinates
    if not isinstance(pos, (list, tuple)) or len(pos) != 2:
        raise ValueError("Position must be a list or tuple of length 2")
    
    # 2. Validation: Ensure those coordinates are actual numbers (not text or booleans)
    if not all(isinstance(x, (int, float)) for x in pos):
        raise ValueError("Position coordinates must be numbers")
    
    # 3. Math: Use the Pythagorean theorem (sqrt(x^2 + y^2)) to find the straight-line distance
    return math.sqrt(pos[0]**2 + pos[1]**2)

# Function: Looks through all known vehicles and finds the one closest to the origin
def nearest_neighbor(neighbors: Dict[str, Dict[str, Any]]) -> Optional[Tuple[str, float]]:
    # If we haven't received any messages yet, return nothing (None)
    if not neighbors:
        return None
    
    nearest_id = None
    min_dist = float('inf') # Start with "infinity" so the first car we check is always closer
    
    # Loop through every car we've stored in our 'neighbors' dictionary
    for neighbor_id, data in neighbors.items():
        try:
            # Calculate distance for this specific car
            dist = euclidean_dist_to_origin(data["pos"])
            # If this car is closer than our current "best" (min_dist), update it
            if dist < min_dist:
                min_dist = dist
                nearest_id = neighbor_id
        except (ValueError, KeyError, TypeError):
            # If a specific car has bad data, just skip it and move to the next one
            continue
            
    if nearest_id is None:
        return None
        
    return (nearest_id, min_dist)

def main() -> int:
    # 'neighbors' is a dictionary: key is Vehicle ID, value is its latest data
    # This prevents duplicates: if "veh_1" sends 5 messages, we just keep the latest.
    neighbors: Dict[str, Dict[str, Any]] = {}
    
    # Create a UDP "Socket" (think of this as a network ear/listener)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Bind it to the address 127.0.0.1 (your own computer) and Port 5005
    sock.bind((HOST, PORT_BEACON))
    # If no data comes for 1.5 seconds, we stop waiting (timeout)
    sock.settimeout(1.5) 

    first_ts: Optional[int] = None # Records when the VERY first message arrives
    try:
        while True:
            try:
                # Recvfrom: Wait for a message to arrive on the network
                data, _ = sock.recvfrom(4096)
            except socket.timeout:
                # If the network goes quiet for too long, exit the loop
                break  

            try:
                # The data comes in as raw bytes, so we 'decode' it to text
                # and 'loads' it into a Python dictionary (JSON)
                msg = json.loads(data.decode("utf-8"))
            except json.JSONDecodeError:
                # If the message is scrambled/broken, ignore it
                continue  
            
            # --- DEFENSIVE VALIDATION BLOCK ---
            # We must ensure the message has exactly what we expect (ID, Position, Speed, Time)
            if not isinstance(msg, dict):
                continue
            
            required_keys = {"id", "pos", "speed", "ts"}
            if not required_keys.issubset(msg.keys()): # Check if all keys exist
                continue
            
            # Ensure types are correct to prevent math errors later
            if not isinstance(msg["id"], str):
                continue
                
            if not isinstance(msg["pos"], (list, tuple)) or len(msg["pos"]) != 2:
                continue
            if not all(isinstance(x, (int, float)) for x in msg["pos"]):
                continue

            if not isinstance(msg["speed"], (int, float)):
                continue

            if not isinstance(msg["ts"], int):
                continue
            
            # --- STORAGE ---
            # Save the valid message! We store it in our dictionary indexed by its ID.
            neighbors[msg["id"]] = {
                "pos": msg["pos"],
                "speed": msg["speed"], 
                "last_ts": msg["ts"]
            }

            # --- TIMER LOGIC ---
            now = now_ms()
            if first_ts is None:
                first_ts = now # Mark the start time when the first message arrives
            
            # The challenge asks to run for exactly 1 second (1000ms) after the first message
            if first_ts is not None and (now - first_ts) >= COLLECT_WINDOW_MS:
                break

    finally:
        # Always close the 'ear' (socket) when finished to free up the network port
        sock.close()

    # Once the loop is finished, find the winner!
    nn = nearest_neighbor(neighbors)
    
    # Build the final report in the exact format the challenge requires
    summary = {
        "topic": "/v2x/neighbor_summary",
        "count": len(neighbors), # How many unique vehicles did we see?
        "nearest": None if nn is None else {"id": nn[0], "dist": nn[1]},
        "ts": now_ms(),
    }
    # Print the report to the screen as a single line of JSON
    print(json.dumps(summary), flush=True)
    return 0

if __name__ == "__main__":
    sys.exit(main())
