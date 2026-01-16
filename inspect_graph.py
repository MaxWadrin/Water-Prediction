import pickle
import networkx as nx
import sys

def inspect_graph(pkl_path, output_path):
    try:
        with open(pkl_path, 'rb') as f:
            G = pickle.load(f)
        
        with open(output_path, "w") as out:
            out.write(f"Graph Type: {type(G)}\n")
            out.write(f"Nodes: {len(G.nodes)}\n")
            out.write(f"Edges: {len(G.edges)}\n")
            
            out.write("\nNodes:\n")
            for n, data in G.nodes(data=True):
                out.write(f"  {n}: {data}\n")
                
            out.write("\nEdges:\n")
            for u, v, data in G.edges(data=True):
                out.write(f"  {u} -> {v}: {data}\n")
        print(f"Graph details written to {output_path}")
            
    except Exception as e:
        print(f"Error reading graph: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        output_path = "graph_details.txt"
    else:
        output_path = sys.argv[1]
    inspect_graph(r"C:\Users\Administrator\Documents\Project\Water Prediction\build\v1\graph.pkl", output_path)
