# Quick Network Scientist


## System Setup


#### Installations
 - [vscode](https://code.visualstudio.com/docs/setup/mac)

 - [Install brew if you don't have it](https://brew.sh/) - package manager for mac
 - `brew install gh` or [Github CLI](https://cli.github.com/) - github command line
 - [Install uv](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer) python package manager
 
 #### Setup Project Directory (this repository)
 - `gh repo clone exrhizo/quick-network` - creates a folder called quick-network
 - Rename it if you want `mv quick-network docu-knowledge`
 - `code quick-network`
    - `cd quick-network`
    - `ls .` 
 - `./uv sync` - install the python packages in this directory (configured by pyproject.toml)
 - `which python` - goal to have this pointing to `./.venv` setup by uv ^
 - `node --version` - claude requires  Node.js 18+
   - if not having latest, probably use `brew` to upgrade [instructions](https://nodesource.com/blog/update-Node.js-versions-on-MacOS)
 - `npm install -g @anthropic-ai/claude-code` see [Claude Code](https://www.anthropic.com/claude-code)
 - With claude installed, `claude` and ask it to follow `ai_notes/initial_plan.md` will it work?

## We will ask Claude to wire up, started with o3, and saved to [[ai_notes/initial_plan.md]]


I have this graph in python, how would I load it into
 - https://www.sigmajs.org/
 - ipycytoscape
 - [cosmograph](https://cosmograph.app/docs/cosmograph/Cosmograph%20Python/get-started-widget/)

```python
class Node(BaseModel):
    id: str
    label: str
    type: NodeType
    description: str


class Edge(BaseModel):
    source: str
    target: str
    relationship_type: RelationshipType
    description: str


class Graph(BaseModel):
    nodes: list[Node]
    edges: list[Edge]
```

#### Easy network visualization tools good for small graphs:

 - https://www.sigmajs.org/
 - ipycytoscape
 - [cosmograph](https://cosmograph.app/docs/cosmograph/Cosmograph%20Python/get-started-widget/)