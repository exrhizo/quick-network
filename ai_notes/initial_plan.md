Below is one minimal path for each target viewer. All snippets assume you already have `graph: Graph` (the Pydantic object) in memory.

---

## 0  Shared helper (Python)

```python
from pathlib import Path
import json, pandas as pd, networkx as nx
from ipycytoscape import CytoscapeWidget
from cosmograph import cosmo   # pip install cosmograph_widget
from typing import Iterable

def _node_rows(nodes: Iterable[Node]):
    return [dict(id=n.id, label=n.label, type=n.type, description=n.description) for n in nodes]

def _edge_rows(edges: Iterable[Edge]):
    return [dict(source=e.source, target=e.target,
                 relationship_type=e.relationship_type,
                 description=e.description) for e in edges]

def to_dfs(g: Graph):
    return (pd.DataFrame(_node_rows(g.nodes)),
            pd.DataFrame(_edge_rows(g.edges)))

def to_networkx(g: Graph) -> nx.DiGraph:
    G = nx.DiGraph()
    for n in g.nodes:
        G.add_node(n.id, **n.model_dump(exclude={'id'}))
    for e in g.edges:
        G.add_edge(e.source, e.target, **e.model_dump(exclude={'source', 'target'}))
    return G

def to_sigma_json(g: Graph, path: Path = Path("graph.json")):
    data = {
        "nodes": _node_rows(g.nodes),
        "edges": [
            dict(id=f"e{i}", **er) for i, er in enumerate(_edge_rows(g.edges))
        ],
    }
    path.write_text(json.dumps(data))
```

---

## 1  Sigma.js (via Graphology in the browser)

```html
<!-- graph.json comes from to_sigma_json(graph) -->
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <script type="module">
      import Graph from "https://unpkg.com/graphology@0.25.1/dist/graphology.esm.js";
      import Sigma from "https://unpkg.com/sigma@2.3.0/dist/sigma.esm.js";

      fetch("graph.json")
        .then((r) => r.json())
        .then(({ nodes, edges }) => {
          const g = new Graph();
          nodes.forEach((n) =>
            g.addNode(n.id, { label: n.label, size: 5, color: "#4e79a7" })
          );
          edges.forEach((e) => g.addEdge(e.source, e.target));
          new Sigma(g, document.getElementById("sigma"));
        });
    </script>
  </head>
  <body>
    <div id="sigma" style="width:100%;height:600px"></div>
  </body>
</html>
```

Sigma.js expects a **Graphology** graph; the fetch‑convert‑render loop above is the minimal bridge from your JSON export ([sigmajs.org][1]).

---

## 2  ipycytoscape (Jupyter)

```python
G_nx = to_networkx(graph)      # helper above
cyto = CytoscapeWidget()
cyto.graph.add_graph_from_networkx(G_nx)
cyto                              # renders in‑notebook
```

`ipycytoscape` natively consumes a NetworkX graph; styling can be tweaked later with `cyto.set_style(...)` ([ipycytoscape.readthedocs.io][2]).

---

## 3  Cosmograph Python widget

```python
nodes_df, edges_df = to_dfs(graph)

cosmo(
    points=nodes_df,
    links=edges_df,
    point_id_by="id",
    link_source_by="source",
    link_target_by="target",
    point_label_by="label",
    point_include_columns=["type", "description"],
    link_include_columns=["relationship_type", "description"],
)
```

`cosmo` auto‑renders an interactive force‑directed view inside the notebook (or Colab). Extra node/link columns immediately become filterable attributes ([next.cosmograph.app][3]).

---

### TL;DR

* **Sigma.js** → dump JSON → fetch in browser → feed Graphology → Sigma renderer.
* **ipycytoscape** → convert to NetworkX → `CytoscapeWidget`.
* **Cosmograph** → convert to pandas DataFrames → call `cosmo(...)`.

These conversions stay loss‑less, so you can layer richer styling or metadata later without revisiting the core transforms.

[1]: https://www.sigmajs.org/docs/ "Introduction | sigma.js"
[2]: https://ipycytoscape.readthedocs.io/en/latest/examples/networkx.html?utm_source=chatgpt.com "NetworkX — ipycytoscape 1.0.3 documentation - Read the Docs"
[3]: https://next.cosmograph.app/docs/widget/get-started-widget/ "Get started | Cosmograph"
