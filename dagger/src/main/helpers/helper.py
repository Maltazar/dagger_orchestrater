
from typing import List


def prepare_key_value_args(vars: dict) -> List[str]:
    var_args = []
    for var in vars:
        for key, value in var.items():
            var_args.append(f"-var={key}={value}")
    return var_args