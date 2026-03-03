#!/usr/bin/env python3
from typing import Any
import json

from qnet.config import c_env
from qnet.actant.future import load_corpus, Corpus


def corpus_to_cytoscape(c: Corpus) -> dict[str, list[dict[str, Any]]]:
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    # actant nodes
    for name, role in c.Actants.items():
        nodes.append({
            "data": {
                "id": f"a:{name}",
                "label": name,
                "partition": "actant",
                "role": role,
            },
            "classes": f"actant role-{role.lower()}",
        })

    # utterance nodes + edges
    for i, u in enumerate(c.Utterances, start=1):
        uid = f"u:{i}"
        nodes.append({
            "data": {
                "id": uid,
                "label": u.text,
                "partition": "utterance",
                "refs": [f"{s}.{v}" for (s, v) in u.refs],
            },
            "classes": "utterance",
        })
        for a in u.actants:
            if a in c.Actants:
                edges.append({
                    "data": {
                        "id": f"e:{uid}->{a}",
                        "source": uid,
                        "target": f"a:{a}",
                    }
                })

    return {"nodes": nodes, "edges": edges}

if __name__ == "__main__":
    c = load_corpus(c_env.ACTANT_FUTURE)
    elements = corpus_to_cytoscape(c)
    
    # Write to output file
    output_path = c_env.ACTANT_FUTURE_CYTO
    with open(output_path, 'w') as f:
        json.dump(elements, f, indent=2)
    print(f"Wrote Cytoscape elements to {output_path}")