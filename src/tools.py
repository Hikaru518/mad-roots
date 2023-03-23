import json
from typing import Dict


def read_json(file_path: str) -> Dict:
    with open(file_path, "r") as f:
        data = json.load(f)

    return data

