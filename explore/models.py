from typing import Literal
from pydantic import BaseModel

# ------------------------- categorical literals -------------------------

NodeType = Literal[
    "Person", "Organization", "Technology/Craft", "Technology", "Component",
    "Material", "Element/Material", "Concept", "Concept/Energy Source",
    "Concept/Application", "Concept/Phenomenon", "Phenomenon",
    "Phenomenon/Energy", "Natural Phenomenon", "Structure/Technology",
    "Structure/Observation", "Field of Study/Technology", "Effect", "Event",
]

RelationshipType = Literal[
    "ENABLES", "USES_MATERIAL", "HAS_COMPONENT", "TAPS_INTO", "EXHIBITS",
    "DESCRIBED_BY", "UTILIZES", "CREATES_BUBBLE_IN", "EMITS", "DEMONSTRATES",
    "BASED_ON", "USES_AS_INPUT", "PRODUCES", "INCORPORATES",
    "CONSTRUCTED_PRIMARILY_OF", "PERFORMS", "IS_A_FORM_OF",
    "EMITS_LIGHT_LIKE", "PROVIDES", "RELEVANT_TO", "UNDERLIES", "POWERS",
    "EXHIBITS_PRINCIPLE_OF", "FORMS_CLUSTER_OF", "DISCOVERED_AND_STUDIED_BY",
    "CAUSES", "PRODUCED_CLEANEST_FROM", "PRODUCED_BY", "WORK_ON_BY",
    "LEADS_TO", "CREATES_TURBULENCE_IN", "INTERACTS_WITH", "STUDIED_BY",
    "DEVELOPED_BY", "SIMULATES", "LINKED_TO", "OBSERVED_IN",
    "PROPOSED_TECHNOLOGY_FOR", "BELIEVED_IN", "USED", "FATHER_WORKED_AT",
    "RESEARCHED", "SUSPICIOUSLY_LINKED_TO", "INVOLVED_IN", "THEORIZED",
    "EXPLAINED", "PRODUCED_SIMILAR_EFFECTS", "IS_CORE_OF", "EXHIBITED",
    "CAUSED_DAMAGE_TO",
]

# ------------------------------ models ----------------------------------

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
