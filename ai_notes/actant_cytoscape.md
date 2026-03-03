# Plan

* Convert your `Corpus` → Cytoscape elements (two node types + edges).
* Vite + Cytoscape.js + `cytoscape-fcose` for force-directed with **constraints**:

  * **Split**: pin x-coordinates of partitions (actants left, utterances right) and let force solve y.
  * **Rings**: seed concentric radii, then run fcose for a gentle jiggle.

No fluff—drop-in code.

---

### Python: corpus → Cytoscape elements

```python
# ./bin/actant/future_to_cytoscape.py
from typing import Any

from qnet.config import c_env
from qnet.actant.future import load_corpus


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
    # TODO: write to c_env.ACTANT_FUTURE_CYTO
```


---

### Vite + Cytoscape.js (+ fcose)

```
cd frontends
npm create vite@latest actant_cytoscape -- --template vanilla-ts
cd actant_cytoscape
npm i cytoscape cytoscape-fcose
```

`index.html`

```html
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>Bipartite Cytoscape</title>
    <style>
      html, body, #cy { height: 100%; margin: 0; }
      .toolbar { position: fixed; top: 8px; left: 8px; z-index: 10; background: #fff; padding: 6px 8px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,.1); font-family: ui-sans-serif, system-ui; }
      button { margin-right: 6px; }
    </style>
  </head>
  <body>
    <div class="toolbar">
      <button id="layout-split">Split</button>
      <button id="layout-rings">Rings</button>
      <button id="layout-free">Free</button>
    </div>
    <div id="cy"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
```

`src/main.ts`

```ts
import cytoscape, { ElementDefinition } from "cytoscape";
import fcose from "cytoscape-fcose";
cytoscape.use(fcose);

type Partition = "actant" | "utterance";

const fetchElements = async (): Promise<{ nodes: ElementDefinition[]; edges: ElementDefinition[] }> => {
  // Serve your JSON (e.g., `uv run qnet/actant/dump_cyto.py > public/elements.json`)
  const res = await fetch("/elements.json");
  return res.json();
};

const style = [
  { selector: "node", style: { "font-size": 10, "text-valign": "center", "text-halign": "center", "label": "data(label)", "background-color": "#999", "color": "#222" } },
  { selector: "node.actant", style: { "shape": "round-rectangle", "background-color": "#6baed6" } },
  { selector: "node.utterance", style: { "shape": "ellipse", "background-color": "#74c476" } },
  { selector: "edge", style: { "width": 1.5, "curve-style": "haystack", "opacity": 0.7 } },
];

const fcoseBase = {
  name: "fcose",
  quality: "default" as const,
  animate: false,
  randomize: true,
  nodeRepulsion: 6000,
  idealEdgeLength: 90,
  nodeSeparation: 45,
  // keep it tidy
  samplingType: true,
};

const init = async () => {
  const elements = await fetchElements();
  const cy = cytoscape({
    container: document.getElementById("cy")!,
    elements: [...elements.nodes, ...elements.edges],
    style,
    wheelSensitivity: 0.2,
  });

  const idsByPartition = (p: Partition): string[] =>
    cy.nodes().filter(n => n.data("partition") === p).map(n => n.id());

  const layoutSplit = () => {
    const left = idsByPartition("actant");
    const right = idsByPartition("utterance");

    // Pin x; let force handle y
    const fixedNodeConstraint = [
      ...left.map(id => ({ nodeId: id, position: { x: -250 } })),
      ...right.map(id => ({ nodeId: id, position: { x: 250 } })),
    ];

    cy.layout({ ...fcoseBase, fixedNodeConstraint }).run();
  };

  const layoutRings = () => {
    // Seed concentric radii, then relax with fcose (no constraints)
    const center = { x: cy.width() / 2, y: cy.height() / 2 };
    const a = idsByPartition("actant");
    const u = idsByPartition("utterance");

    const placeRing = (ids: string[], r: number) => {
      const n = ids.length || 1;
      ids.forEach((id, i) => {
        const t = (2 * Math.PI * i) / n;
        cy.getElementById(id).position({ x: center.x + r * Math.cos(t), y: center.y + r * Math.sin(t) });
      });
    };

    placeRing(a, 180);
    placeRing(u, 320);

    cy.layout({ ...fcoseBase, randomize: false }).run();
  };

  const layoutFree = () => cy.layout({ ...fcoseBase }).run();

  // initial
  layoutSplit();

  (document.getElementById("layout-split") as HTMLButtonElement).onclick = layoutSplit;
  (document.getElementById("layout-rings") as HTMLButtonElement).onclick = layoutRings;
  (document.getElementById("layout-free") as HTMLButtonElement).onclick = layoutFree;

  // Small UX: fit after layout
  cy.once("layoutstop", () => cy.fit(undefined, 40));
};

init();
```

---

### Wire-up

* Dump elements:
  `uv run bin/actant/future_to_cytoscape.py`

Check types and ruff
