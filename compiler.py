import networkx as nx
import pickle
import json
import os
import sys

def load_graph_data(version):
    """Parses WaterSystem.txt to build the base graph."""
    filepath = f"data/{version}/WaterSystem.txt"
    G = nx.DiGraph()
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found.")
        return G
    
    with open(filepath, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if not parts: continue
            
            if parts[0] == "Source":
                G.add_node(parts[1], type="Source")
            elif parts[0] == "Tank":
                G.add_node(parts[1], type="Tank")
            elif parts[0] == "Pipe":
                G.add_edge(parts[1], parts[2], type="Pipe")
    return G

def load_templates(version):
    """Parses Floor_Templates.txt to load subgraph templates."""
    filepath = f"data/{version}/Floor_Templates.txt"
    templates = {}
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found.")
        return templates

    current_template = None
    current_graph = None
    
    with open(filepath, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if not parts: continue
            
            print(f"DEBUG: Parsing line: {parts}", file=sys.stderr)
            if parts[0] == "Template":
                current_template = parts[1]
                current_graph = nx.DiGraph()
                print(f"DEBUG: Started template {current_template}", file=sys.stderr)
            elif parts[0] == "EndTemplate":
                if current_template and current_graph is not None:
                    templates[current_template] = current_graph
                current_template = None
                current_graph = None
            elif parts[0] == "Node":
                if current_graph is not None:
                    current_graph.add_node(parts[1])
            elif parts[0] == "Edge":
                if current_graph is not None:
                    current_graph.add_edge(parts[1], parts[2])
    return templates

def apply_templates(G, version, templates):
    """Parses Template_Application.txt and expands templates into the main graph."""
    filepath = f"data/{version}/Template_Application.txt"
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found.")
        return G

    with open(filepath, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if not parts: continue
            
            if parts[0] == "Apply":
                template_name = parts[1]
                attach_node = parts[2]
                
                if template_name in templates:
                    template_graph = templates[template_name]
                    # Relabel nodes to be unique: attach_node.template_node
                    mapping = {n: f"{attach_node}.{n}" for n in template_graph.nodes()}
                    subgraph = nx.relabel_nodes(template_graph, mapping)
                    
                    G.add_nodes_from(subgraph.nodes(data=True))
                    G.add_edges_from(subgraph.edges(data=True))
                    
                    # Connect attachment point
                    # Updated to support 'FloorInlet' based on new DSL
                    root_node = mapping.get("FloorInlet")
                    if not root_node:
                        root_node = mapping.get("Riser")
                    
                    if root_node:
                         G.add_edge(attach_node, root_node, type="TemplateConnection")
                    else:
                        # Fallback
                        pass

    return G

def attach_demands(G, version):
    """Parses Demand_Profiles.txt and attaches demand attributes."""
    filepath = f"data/{version}/Demand_Profiles.txt"
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found.")
        return G

    with open(filepath, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if not parts: continue
            
            if parts[0] == "Demand":
                node = parts[1]
                value = float(parts[2])
                if node in G.nodes:
                    G.nodes[node]['demand'] = value
                else:
                    print(f"Warning: Demand node {node} not found in graph.")
    return G

def attach_sensors(G, version):
    """Parses Sensors.txt and attaches sensor attributes."""
    filepath = f"data/{version}/Sensors.txt"
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found.")
        return G

    with open(filepath, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if not parts: continue
            
            if parts[0] == "Sensor":
                node = parts[1]
                sensor_type = parts[2]
                if node in G.nodes:
                    G.nodes[node]['sensor'] = sensor_type
                else:
                    print(f"Warning: Sensor node {node} not found in graph.")
    return G

import argparse
import base64

def save_artifacts(G, version, mode):
    """Prints artifacts to stdout based on mode."""
    
    if mode == 'json':
        summary = {
            "nodes": G.number_of_nodes(),
            "edges": G.number_of_edges(),
            "zones": [], 
            "sources": len([n for n, d in G.nodes(data=True) if d.get('type') == 'Source']),
            "tanks": len([n for n, d in G.nodes(data=True) if d.get('type') == 'Tank']),
            "sensors": len([n for n, d in G.nodes(data=True) if 'sensor' in d])
        }
        print(json.dumps(summary, indent=2), flush=True)
        
    elif mode == 'pickle':
        # Serialize to bytes, then base64 encode, then print as string
        pickled = pickle.dumps(G)
        b64_pickled = base64.b64encode(pickled).decode('utf-8')
        print(b64_pickled, flush=True)

def main():
    # print("DEBUG: Starting main", file=sys.stderr)
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', default='v1')
    parser.add_argument('--mode', choices=['json', 'pickle'], required=True)
    args = parser.parse_args()
    
    version = args.version
    # print(f"DEBUG: Version {version}", file=sys.stderr)
    
    G = load_graph_data(version)
    # print(f"DEBUG: Loaded graph with {G.number_of_nodes()} nodes", file=sys.stderr)
    
    templates = load_templates(version)
    # print(f"DEBUG: Loaded {len(templates)} templates", file=sys.stderr)
    
    G = apply_templates(G, version, templates)
    # print(f"DEBUG: Applied templates, nodes: {G.number_of_nodes()}", file=sys.stderr)
    
    G = attach_demands(G, version)
    G = attach_sensors(G, version)
    
    save_artifacts(G, version, args.mode)

if __name__ == "__main__":
    main()
