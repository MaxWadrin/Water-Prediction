import pickle
import networkx as nx
import csv
import json
import random
import math
import sys
import io
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
GRAPH_PATH = r"C:\Users\Administrator\Documents\Project\Water Prediction\build\v1\graph.pkl"
START_TIME = datetime(2026, 1, 1, 0, 0, 0)
DURATION_HOURS = 24
INTERVAL_MINUTES = 15

def load_graph():
    with open(GRAPH_PATH, 'rb') as f:
        return pickle.load(f)

def get_floor_level(node_name):
    # Extract floor number from "FloorX_Junction"
    if "Floor" in node_name and "Junction" in node_name:
        try:
            parts = node_name.split('_')[0] # FloorX
            level = int(parts.replace("Floor", ""))
            return level
        except:
            return 0
    return 0

def simulate_step(G, timestamp, anomaly_type=None, anomaly_node=None):
    # 1. Calculate Demands
    hour = timestamp.hour
    # Diurnal pattern: Peak at 8am and 8pm
    demand_factor = 1.0 + 0.6 * math.sin((hour - 6) * math.pi / 12) + 0.3 * math.sin((hour - 18) * math.pi / 12)
    
    current_demands = {}
    
    for n, data in G.nodes(data=True):
        base_demand = data.get('demand', 0.0)
        
        # Apply anomaly: Misuse
        if anomaly_type == "Misuse" and n == anomaly_node:
            base_demand += 500.0 # Huge increase
            
        current_demands[n] = base_demand * demand_factor * random.uniform(0.9, 1.1)

    # 2. Calculate Flows (Bottom-up aggregation)
    # Simplified: Flow in edge u->v is sum of demands in subtree rooted at v
    # Since it's a tree/DAG from Tank downwards
    
    # We need to find the Tank
    tank_node = "RoofTank"
    
    # Calculate flow for each edge
    edge_flows = {}
    node_inflows = {n: 0.0 for n in G.nodes()}
    
    # Topological sort to process from leaves up? Or just recursive demand sum
    # Since it's a gravity feed from Tank -> Floor1 -> Floor2... wait, usually Tank is at top.
    # Let's assume Tank -> Floor10 -> Floor9 ... -> Floor1
    # Based on graph details: RoofTank -> Floor1_Junction -> Floor2...
    # Wait, graph details said: RoofTank -> Floor1_Junction -> Floor2_Junction...
    # That implies Floor 1 is at top? Or just the order of connection.
    # Usually Roof Tank feeds top floor first.
    # Let's assume flow direction follows edges.
    
    # Recursive function to get total demand downstream
    memo_demand = {}
    
    def get_downstream_demand(u):
        if u in memo_demand:
            return memo_demand[u]
        
        total = current_demands.get(u, 0.0)
        
        # Leak adds to demand at the node
        if anomaly_type == "Leak" and u == anomaly_node:
             total += 300.0 # Leak flow
        
        for v in G.successors(u):
            flow_to_v = get_downstream_demand(v)
            edge_flows[(u, v)] = flow_to_v
            total += flow_to_v
            
        memo_demand[u] = total
        return total

    total_system_demand = get_downstream_demand(tank_node)
    
    # 3. Calculate Pressures
    # Tank Level
    tank_level = 5.0 # meters (constant for simplicity or varying?)
    # Let's vary it slightly
    tank_level += math.sin(hour * math.pi / 12) * 0.5
    
    node_pressures = {}
    node_pressures[tank_node] = tank_level * 9.81 # kPa approx (1m head ~ 9.81 kPa)
    
    # Propagate pressure downstream
    # Pressure = Upstream Pressure + Elevation Gain - Friction Loss
    # Elevation: Assume 3m drop per floor edge.
    # Friction: Proportional to Flow^2
    
    queue = [(tank_node, node_pressures[tank_node])]
    visited = set([tank_node])
    
    while queue:
        u, u_p = queue.pop(0)
        
        for v in G.successors(u):
            if v in visited:
                continue
                
            # Determine edge type/elevation change
            # Roof -> Floor1 (Top floor?)
            # If Floor 1 is top, then Floor 1 -> Floor 2 is going DOWN.
            # Elevation gain!
            
            # Simple model: Every pipe edge adds static head (going down) but loses dynamic head (friction)
            # TemplateConnection (to apartment) -> horizontal, no elevation change, just friction
            
            edge_data = G.edges[u, v]
            etype = edge_data.get('type', 'Pipe')
            
            flow = edge_flows.get((u, v), 0.0)
            
            friction_loss = 0.0001 * (flow ** 2) # Coefficient
            
            elevation_gain = 0.0
            if etype == 'Pipe':
                elevation_gain = 3.0 * 9.81 # 3 meters down
            elif etype == 'TemplateConnection':
                elevation_gain = 0.0
            
            # If Leak is downstream, friction increases due to high flow
            
            v_p = u_p + elevation_gain - friction_loss
            
            # Leak at node v causes local pressure drop
            if anomaly_type == "Leak" and v == anomaly_node:
                v_p -= 20.0 # Significant drop
                
            node_pressures[v] = v_p
            visited.add(v)
            queue.append((v, v_p))

    # Collect Data
    row = {"timestamp": timestamp.isoformat()}
    
    # We only record sensors? Or all nodes?
    # Plan said "Columns: Timestamp + Flow/Pressure/Level for all relevant nodes."
    # Let's record all junctions and apartments
    
    for n in G.nodes():
        # Pressure
        row[f"{n}_pressure"] = round(node_pressures.get(n, 0.0), 2)
        
        # Flow (Net flow through node? Or flow out of node?)
        # For apartments, flow is demand.
        # For junctions, flow is sum of outflows?
        # Let's use Demand for apartments, and Total Throughput for Junctions
        if "Apt" in n:
            row[f"{n}_flow"] = round(current_demands.get(n, 0.0), 2)
        else:
            # For junctions, maybe flow from upstream?
            # Let's sum inflows
            inflow = 0.0
            for pred in G.predecessors(n):
                inflow += edge_flows.get((pred, n), 0.0)
            row[f"{n}_flow"] = round(inflow, 2)
            
    return row

def generate_csv_string(data, fieldnames):
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)
    return output.getvalue()

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_data.py <output_dir>")
        return

    output_dir = Path(sys.argv[1])
    G = load_graph()
    
    # Identify nodes for anomalies
    # Leak: Floor5_Junction
    # Misuse: Floor1_Junction.Apt1
    
    leak_node = "Floor5_Junction"
    misuse_node = "Floor1_Junction.Apt1"
    
    # Generate Normal Data
    normal_data = []
    current_time = START_TIME
    num_steps = int(DURATION_HOURS * 60 / INTERVAL_MINUTES)
    
    for _ in range(num_steps):
        row = simulate_step(G, current_time)
        normal_data.append(row)
        current_time += timedelta(minutes=INTERVAL_MINUTES)
        
    fieldnames = list(normal_data[0].keys())
    
    # Generate Leak Data
    leak_data = []
    current_time = START_TIME
    leak_labels = []
    
    for i in range(num_steps):
        # Leak between 10am and 2pm
        is_leak = 10 <= current_time.hour < 14
        
        if is_leak:
            row = simulate_step(G, current_time, "Leak", leak_node)
            leak_labels.append({
                "timestamp": current_time.isoformat(),
                "node_id": leak_node,
                "anomaly_type": "Leak",
                "severity": "High"
            })
        else:
            row = simulate_step(G, current_time)
            
        leak_data.append(row)
        current_time += timedelta(minutes=INTERVAL_MINUTES)

    # Generate Misuse Data
    misuse_data = []
    current_time = START_TIME
    misuse_labels = []
    
    for i in range(num_steps):
        # Misuse between 6pm and 8pm
        is_misuse = 18 <= current_time.hour < 20
        
        if is_misuse:
            row = simulate_step(G, current_time, "Misuse", misuse_node)
            misuse_labels.append({
                "timestamp": current_time.isoformat(),
                "node_id": misuse_node,
                "anomaly_type": "Misuse",
                "severity": "Medium"
            })
        else:
            row = simulate_step(G, current_time)
            
        misuse_data.append(row)
        current_time += timedelta(minutes=INTERVAL_MINUTES)
        
    all_labels = leak_labels + misuse_labels
    
    # Helper to write
    def save(name, content):
        p = output_dir / name
        print(f"Writing to {p}")
        with open(p, 'w', newline='') as f:
            f.write(content)

    save("normal.csv", generate_csv_string(normal_data, fieldnames))
    save("leak_scenarios.csv", generate_csv_string(leak_data, fieldnames))
    save("misuse_scenarios.csv", generate_csv_string(misuse_data, fieldnames))
    save("labels.json", json.dumps(all_labels, indent=2))
    
    print("Done")

if __name__ == "__main__":
    main()
