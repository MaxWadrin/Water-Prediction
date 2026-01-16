import networkx as nx
import pickle
import os

def generate_mock_graph():
    G = nx.DiGraph()

    # Define Nodes
    # Zone A: Source and some junctions
    G.add_node("Source_1", type="SOURCE", elevation=100.0, zone="ZONE_A")
    G.add_node("Junction_A1", type="JUNCTION", elevation=90.0, zone="ZONE_A")
    G.add_node("Junction_A2", type="JUNCTION", elevation=85.0, zone="ZONE_A")

    # Zone B: Supplied by Zone A
    G.add_node("Tank_B", type="TANK", elevation=120.0, zone="ZONE_B")
    G.add_node("Junction_B1", type="JUNCTION", elevation=110.0, zone="ZONE_B")

    # Zone C: Isolated, but we'll add a bad connection
    G.add_node("Junction_C1", type="JUNCTION", elevation=50.0, zone="ZONE_C")

    # Define Edges
    # Normal flow in Zone A (Gravity)
    G.add_edge("Source_1", "Junction_A1", type="PIPE", length=100)
    G.add_edge("Junction_A1", "Junction_A2", type="PIPE", length=50)

    # Pump from Zone A to Zone B (Lifting water)
    # Elevation 85 -> 120. Needs pump.
    G.add_edge("Junction_A2", "Tank_B", type="PUMP", pump_curve="Curve_1")

    # Flow in Zone B
    G.add_edge("Tank_B", "Junction_B1", type="PIPE", length=200)

    # ERROR 1: Cross-zone feed (Zone A to Zone C directly, maybe forbidden or just tracked)
    # The prompt example says "CROSS_ZONE_FEED" "ZONE_A->ZONE_C" is a soft warning.
    G.add_edge("Junction_A1", "Junction_C1", type="PIPE", length=500)

    # ERROR 2: Elevation/Pump Consistency
    # Let's add a pump pumping DOWNHILL significantly, which might be flagged.
    # Or a pipe going UPHILL significantly without a pump.
    # Let's do Pipe Uphill: Junction_C1 (50) -> Junction_C_High (150) without pump.
    G.add_node("Junction_C_High", type="JUNCTION", elevation=150.0, zone="ZONE_C")
    G.add_edge("Junction_C1", "Junction_C_High", type="PIPE", length=100)

    # Save graph
    artifact_dir = r"c:/Users/Administrator/.gemini/antigravity/brain/34d2cc9b-7e64-4143-81f7-37a588066865"
    output_path = os.path.join(artifact_dir, "graph.pkl")
    
    print(f"Writing to: {output_path}")
    with open(output_path, "wb") as f:
        pickle.dump(G, f)
    
    print(f"Mock graph generated at {os.path.abspath(output_path)}")
    print(f"Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")

if __name__ == "__main__":
    generate_mock_graph()
