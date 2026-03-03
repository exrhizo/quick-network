import yaml
from pathlib import Path
from pydantic import BaseModel
from typing import Literal, Any

from qnet.config import c_env

type Role = Literal["Actor", "Constructor", "Constraint"]
type Story = Literal["social", "career", "creative", "present"]
type Variant = Literal["heaven", "hell", "null"]

class Utterance(BaseModel):
    text: str
    story: Story
    variant: Variant
    actants: list[str]
    affect: int  # pa - na in [−4..+4]
    pa: int
    na: int

class Corpus(BaseModel):
    Utterances: list[Utterance]
    Actants: dict[str, Role]

def _coerce_story_variant(u: dict[str, Any]) -> tuple[Story, Variant]:
    ref = (u.get("refs") or ["present.null"])[0]
    s, v = ref.split(".", 1)
    return s, v  # type: ignore[return-value]

def _coerce_affect(u: dict[str, Any]) -> int:
    if "affect" in u:
        return int(u["affect"])
    pa = int(u.get("pa", 3))
    na = int(u.get("na", 3))
    return pa - na  # [-4..+4]

def load_corpus(path: str | Path) -> Corpus:
    raw = yaml.safe_load(Path(path).read_text())
    out: list[dict[str, Any]] = []
    for u in raw.get("Utterances", []):
        story, variant = _coerce_story_variant(u)
        out.append({
            "text": u["text"],
            "story": story,
            "variant": variant,
            "actants": u.get("actants", []),
            "affect": _coerce_affect(u),
            "pa": u.get("pa", 3),
            "na": u.get("na", 3),
        })
    return Corpus(Utterances=[Utterance(**u) for u in out], Actants=raw.get("Actants", {}))

if __name__ == "__main__":
    corpus = load_corpus(c_env.ACTANT_FUTURE)
    print(corpus.Utterances[0].model_dump_json(indent=2))
