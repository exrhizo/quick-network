import cytoscape, { type ElementDefinition } from "cytoscape";
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
  try {
    console.log("Fetching elements...");
    const elements = await fetchElements();
    console.log("Elements loaded:", elements.nodes.length, "nodes,", elements.edges.length, "edges");
    
    const cy = cytoscape({
      container: document.getElementById("cy")!,
      elements: [...elements.nodes, ...elements.edges],
      style,
      // Remove wheelSensitivity to avoid warning
    });
    console.log("Cytoscape initialized");

    const idsByPartition = (p: Partition): string[] =>
      cy.nodes().filter(n => n.data("partition") === p).map(n => n.id());

    const layoutSplit = () => {
      console.log("Running split layout...");
      const left = idsByPartition("actant");
      const right = idsByPartition("utterance");
      console.log("Split layout - actants:", left.length, "utterances:", right.length);

      // Pin x; let force handle y
      const fixedNodeConstraint = [
        ...left.map(id => ({ nodeId: id, position: { x: -250 } })),
        ...right.map(id => ({ nodeId: id, position: { x: 250 } })),
      ];

      const layout = cy.layout({ ...fcoseBase, fixedNodeConstraint });
      layout.run();
      
      layout.on('layoutstop', () => {
        console.log("Split layout complete, fitting...");
        cy.fit(cy.elements(), 50);
        cy.center();
      });
    };

    const layoutRings = () => {
      console.log("Running rings layout...");
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

      const layout = cy.layout({ ...fcoseBase, randomize: false });
      layout.run();
      
      layout.on('layoutstop', () => {
        console.log("Rings layout complete, fitting...");
        cy.fit(cy.elements(), 50);
        cy.center();
      });
    };

    const layoutFree = () => {
      console.log("Running free layout...");
      const layout = cy.layout({ ...fcoseBase });
      layout.run();
      
      layout.on('layoutstop', () => {
        console.log("Free layout complete, fitting...");
        cy.fit(cy.elements(), 50);
        cy.center();
      });
    };

    // Wait a moment for container to be ready, then run initial layout
    setTimeout(() => {
      layoutSplit();
    }, 100);

    (document.getElementById("layout-split") as HTMLButtonElement).onclick = layoutSplit;
    (document.getElementById("layout-rings") as HTMLButtonElement).onclick = layoutRings;
    (document.getElementById("layout-free") as HTMLButtonElement).onclick = layoutFree;
  } catch (error) {
    console.error("Error initializing cytoscape:", error);
  }
};

init();