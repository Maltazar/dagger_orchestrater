import yaml
from models.model import Orchestrate

def load_yaml(file_path: str) -> Orchestrate:
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
    return Orchestrate(root=data)