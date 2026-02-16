#Author: 
#Date:
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
- Ignore malformed messages; don’t crash.
- Do NOT listen to ticks (5006).
"""

import socket, json, time, math, sys
from typing import Dict, Any, Optional, Tuple

HOST = "127.0.0.1"
PORT_BEACON = 5005
COLLECT_WINDOW_MS = 1000  # ~1 second

def now_ms() -> int:
    return int(time.time() * 1000)

def euclidean_dist_to_origin(pos) -> float:
    # TODO: validate pos is [x,y] of numbers; compute distance
    if not isinstance(pos, (list, tuple)) or len(pos) != 2:
        raise ValueError("Position must be a list or tuple of length 2")
    if not all(isinstance(x, (int, float)) for x in pos):
        raise ValueError("Position coordinates must be numbers")
    return math.sqrt(pos[0]**2 + pos[1]**2)

def nearest_neighbor(neighbors: Dict[str, Dict[str, Any]]) -> Optional[Tuple[str, float]]:
    # neighbors[id] -> {"pos":[x,y], "speed": float, "last_ts": int}
    # TODO: iterate neighbors, compute min distance, return (id, dist) or None
    if not neighbors:
        return None
    
    nearest_id = None
    min_dist = float('inf')
    
    for neighbor_id, data in neighbors.items():
        try:
            dist = euclidean_dist_to_origin(data["pos"])
            if dist < min_dist:
                min_dist = dist
                nearest_id = neighbor_id
        except (ValueError, KeyError, TypeError):
            continue
            
    if nearest_id is None:
        return None
        
    return (nearest_id, min_dist)

def main() -> int:
    neighbors: Dict[str, Dict[str, Any]] = {}
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT_BEACON))
    sock.settimeout(1.5) 

    first_ts: Optional[int] = None
    try:
        while True:
            try:
                data, _ = sock.recvfrom(4096)
            except socket.timeout:
                break  

            try:
                msg = json.loads(data.decode("utf-8"))
            except json.JSONDecodeError:
                continue  
            
            # Expect: {"id": "...", "pos":[x,y], "speed": float, "ts": int}
            # TODO: validate required keys/types defensively
            # If valid:
            #   neighbors[msg["id"]] = {"pos": msg["pos"], "speed": msg["speed"], "last_ts": msg["ts"]}
            #hint: beacon handling, check each message and store in neighbors, try to cover edge cases
            # try to avoid changing anything in the main function outside this TODO block
            
            # Validation
            if not isinstance(msg, dict):
                continue
            
            required_keys = {"id", "pos", "speed", "ts"}
            if not required_keys.issubset(msg.keys()):
                continue
            
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
            
            # Store valid message
            neighbors[msg["id"]] = {
                "pos": msg["pos"],
                "speed": msg["speed"], 
                "last_ts": msg["ts"]
            }

            #END of TODO block
            now = now_ms()
            if first_ts is None:
                first_ts = now
            # stop after ~1 second from first message
            if first_ts is not None and (now - first_ts) >= COLLECT_WINDOW_MS:
                break

    finally:
        sock.close()

    # Build summary
    nn = nearest_neighbor(neighbors)
    summary = {
        "topic": "/v2x/neighbor_summary",
        "count": len(neighbors),
        "nearest": None if nn is None else {"id": nn[0], "dist": nn[1]},
        "ts": now_ms(),
    }
    print(json.dumps(summary), flush=True)
    return 0

if __name__ == "__main__":
    sys.exit(main())
