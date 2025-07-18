import yaml

from models import Graph
from config import c_env

def get_source() -> Graph:
    with open(c_env.SOURCE_FILE, "r") as f:
        yaml_dict = yaml.safe_load(f)
        return Graph.model_validate(yaml_dict)