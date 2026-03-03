from typing import Any
from pathlib import Path
import json

from neo4j import GraphDatabase, Driver


JSONDict = dict[str, Any]


def load_snapshot(path: Path) -> JSONDict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def import_snapshot(driver: Driver, snapshot: JSONDict) -> None:
    actants: list[JSONDict] = snapshot["actants"]
    xnets: list[JSONDict] = snapshot["xnets"]
    events: list[JSONDict] = snapshot.get("events", [])

    with driver.session() as session:
        # Drop everything for a clean import
        session.run("MATCH (n) DETACH DELETE n")

        # --- Actants ---
        for actant in actants:
            session.run(
                """
                CREATE (a:Actant {
                    id: $id,
                    label: $label,
                    type: $type,
                    salience: $salience,
                    tags: $tags,
                    description: $description
                })
                """,
                id=actant["id"],
                label=actant["label"],
                type=actant["type"],
                salience=actant.get("salience"),
                tags=actant.get("tags", []),
                description=actant.get("description"),
            )

        # --- X-nets: nodes ---
        for xnet in xnets:
            state: JSONDict = xnet["current_state"]
            session.run(
                """
                CREATE (x:Xnet {
                    id: $id,
                    label: $label,
                    category: $category,
                    description: $description,
                    priority: $priority,
                    phase: $phase,
                    aspect: $aspect,
                    aksionsart: $aksionsart,
                    progress: $progress,
                    felt_intensity: $felt_intensity,
                    mood: $mood
                })
                """,
                id=xnet["id"],
                label=xnet["label"],
                category=xnet["category"],
                description=xnet.get("description"),
                priority=xnet.get("priority"),
                phase=state["phase"],
                aspect=state["aspect"],
                aksionsart=state["aksionsart"],
                progress=state.get("progress"),
                felt_intensity=state.get("felt_intensity"),
                mood=state.get("mood"),
            )

        # --- X-nets: actant roles ---
        for xnet in xnets:
            xnet_id = xnet["id"]
            for role in xnet.get("actants", []):
                session.run(
                    """
                    MATCH (a:Actant {id: $actant_id}), (x:Xnet {id: $xnet_id})
                    CREATE (a)-[:ROLE_IN_XNET {role: $role, note: $note}]->(x)
                    """,
                    actant_id=role["actant_id"],
                    xnet_id=xnet_id,
                    role=role["role"],
                    note=role.get("note"),
                )

        # --- X-nets: dependencies ---
        for xnet in xnets:
            xnet_id = xnet["id"]
            deps: JSONDict = xnet.get("dependencies", {})

            for dep in deps.get("enabled_by", []):
                session.run(
                    """
                    MATCH (x:Xnet {id: $xnet_id}), (d:Xnet {id: $dep_id})
                    CREATE (x)-[:ENABLED_BY {note: $note}]->(d)
                    """,
                    xnet_id=xnet_id,
                    dep_id=dep["xnet_id"],
                    note=dep.get("note"),
                )

            for dep in deps.get("supports", []):
                session.run(
                    """
                    MATCH (x:Xnet {id: $xnet_id}), (d:Xnet {id: $dep_id})
                    CREATE (x)-[:SUPPORTS {note: $note}]->(d)
                    """,
                    xnet_id=xnet_id,
                    dep_id=dep["xnet_id"],
                    note=dep.get("note"),
                )

            for dep in deps.get("blocked_by", []):
                session.run(
                    """
                    MATCH (x:Xnet {id: $xnet_id}), (d:Xnet {id: $dep_id})
                    CREATE (x)-[:BLOCKED_BY {note: $note}]->(d)
                    """,
                    xnet_id=xnet_id,
                    dep_id=dep["xnet_id"],
                    note=dep.get("note"),
                )

        # --- Events: nodes ---
        for event in events:
            session.run(
                """
                CREATE (e:Event {
                    id: $id,
                    label: $label,
                    timestamp: $timestamp,
                    description: $description
                })
                """,
                id=event["id"],
                label=event["label"],
                timestamp=event["timestamp"],
                description=event.get("description"),
            )

        # --- Events: actant roles ---
        for event in events:
            event_id = event["id"]
            for role in event.get("actant_roles", []):
                session.run(
                    """
                    MATCH (a:Actant {id: $actant_id}), (e:Event {id: $event_id})
                    CREATE (a)-[:ROLE_IN_EVENT {role: $role, note: $note}]->(e)
                    """,
                    actant_id=role["actant_id"],
                    event_id=event_id,
                    role=role["role"],
                    note=role.get("note"),
                )

        # --- Events: impacts on X-nets ---
        for event in events:
            event_id = event["id"]
            for impact in event.get("xnet_impacts", []):
                session.run(
                    """
                    MATCH (e:Event {id: $event_id}), (x:Xnet {id: $xnet_id})
                    CREATE (e)-[:IMPACT_ON {effect: $effect, note: $note}]->(x)
                    """,
                    event_id=event_id,
                    xnet_id=impact["xnet_id"],
                    effect=impact["effect"],
                    note=impact.get("note"),
                )


def main() -> None:
    snapshot_path = Path("data/self_world/2025-Nov-29.json")

    snapshot = load_snapshot(snapshot_path)

    uri = "neo4j://127.0.0.1:7687"
    user = "neo4j"
    password = "password"

    driver: Driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        import_snapshot(driver, snapshot)
    finally:
        driver.close()


if __name__ == "__main__":
    main()
