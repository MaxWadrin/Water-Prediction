import networkx as nx
import pickle
import json
import argparse
import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any

# --- Data Structures ---

class ValidationResult:
    def __init__(self, rule_name: str, location: str, message: str, is_hard_failure: bool):
        self.rule_name = rule_name
        self.location = location
        self.message = message
        self.is_hard_failure = is_hard_failure

    def to_dict(self):
        return {
            "rule": self.rule_name,
            "location": self.location,
            "message": self.message
        }

class ValidationReport:
    def __init__(self):
        self.hard_failures: List[ValidationResult] = []
        self.soft_warnings: List[ValidationResult] = []

    def add_result(self, result: ValidationResult):
        if result.is_hard_failure:
            self.hard_failures.append(result)
        else:
            self.soft_warnings.append(result)

    def get_status(self):
        if self.hard_failures:
            return "FAIL"
        if self.soft_warnings:
            return "WARN"
        return "PASS"

    def to_json(self):
        return {
            "status": self.get_status(),
            "hard_failures": [r.to_dict() for r in self.hard_failures],
            "soft_warnings": [r.to_dict() for r in self.soft_warnings]
        }

# --- Rules Engine ---

class ValidationRule(ABC):
    @abstractmethod
    def check(self, graph: nx.DiGraph) -> List[ValidationResult]:
        pass

class CrossZoneFeedRule(ValidationRule):
    def check(self, graph: nx.DiGraph) -> List[ValidationResult]:
        results = []
        for u, v, data in graph.edges(data=True):
            zone_u = graph.nodes[u].get("zone")
            zone_v = graph.nodes[v].get("zone")
            
            if zone_u and zone_v and zone_u != zone_v:
                # Found a cross-zone connection
                results.append(ValidationResult(
                    rule_name="CROSS_ZONE_FEED",
                    location=f"{zone_u}→{zone_v} ({u}→{v})",
                    message=f"Connection detected between different zones: {zone_u} and {zone_v}",
                    is_hard_failure=False # Soft warning as per prompt example
                ))
        return results

class ElevationConsistencyRule(ValidationRule):
    def check(self, graph: nx.DiGraph) -> List[ValidationResult]:
        results = []
        for u, v, data in graph.edges(data=True):
            elev_u = graph.nodes[u].get("elevation")
            elev_v = graph.nodes[v].get("elevation")
            edge_type = data.get("type", "PIPE")

            if elev_u is None or elev_v is None:
                continue

            # Check: Flowing uphill without a pump?
            # Allow small tolerance or maybe it's a pressurized pipe? 
            # For this rule, let's assume if it goes up more than 5m without a pump, it's suspicious.
            # Real systems have pressure, but this is a "Consistency" check.
            
            elevation_diff = elev_v - elev_u
            
            if edge_type != "PUMP":
                if elevation_diff > 5.0:
                     results.append(ValidationResult(
                        rule_name="ELEVATION_CONSISTENCY",
                        location=f"{u}→{v}",
                        message=f"Flow uphill ({elevation_diff}m) without pump.",
                        is_hard_failure=True # Let's call this a hard failure for demonstration
                    ))
            
            # Check: Pump pumping downhill?
            if edge_type == "PUMP":
                if elevation_diff < -10.0: # Pumping downhill significantly
                     results.append(ValidationResult(
                        rule_name="PUMP_FEASIBILITY",
                        location=f"{u}→{v}",
                        message=f"Pump pushing water downhill ({elevation_diff}m). Potential energy waste or configuration error.",
                        is_hard_failure=False 
                    ))

        return results

# --- Main Agent ---

def run_validation(input_path: str, output_path: str):
    print(f"Loading graph from {input_path}...")
    try:
        with open(input_path, "rb") as f:
            graph = pickle.load(f)
    except (FileNotFoundError, EOFError, pickle.UnpicklingError) as e:
        print(f"Error loading graph: {e}")
        # Create a failure report
        report = ValidationReport()
        report.add_result(ValidationResult(
            rule_name="INPUT_VALIDATION",
            location="File Load",
            message=f"Failed to load graph from {input_path}: {str(e)}",
            is_hard_failure=True
        ))
        
        # Ensure output directory exists
        # os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "w") as f:
            json.dump(report.to_json(), f, indent=2)
        
        print(json.dumps(report.to_json(), indent=2))
        return

    print(f"Graph loaded. Nodes: {graph.number_of_nodes()}, Edges: {graph.number_of_edges()}")

    report = ValidationReport()
    rules = [
        CrossZoneFeedRule(),
        ElevationConsistencyRule()
    ]

    print("Running validation rules...")
    for rule in rules:
        results = rule.check(graph)
        for res in results:
            report.add_result(res)

    # Ensure output directory exists
    # os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print(f"Writing report to {output_path}...")
    try:
        with open(output_path, "w") as f:
            json.dump(report.to_json(), f, indent=2)
    except Exception as e:
        print(f"Failed to write report to file: {e}")
    
    print("Validation complete.")
    print(json.dumps(report.to_json(), indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validation Agent")
    parser.add_argument("--input", default="graph.pkl", help="Path to input graph.pkl")
    parser.add_argument("--output", default="reports/v1/validation_report.json", help="Path to output JSON report")
    args = parser.parse_args()

    run_validation(args.input, args.output)
