from pydantic import BaseModel, Field
from typing import Dict

class AppConfig(BaseModel):
    currencies: Dict[str, float] = Field(default_factory=dict)
    period: int
    debug: bool = False
    api: bool = False


def parse_debug(value: str) -> bool:
    if value is None:
        return False
    true_values = {"1", "true", "True", "y", "Y", "yes", "Yes"}
    false_values = {"0", "false", "False", "n", "N", "no", "No"}

    val = str(value).strip()
    if val in true_values:
        return True
    elif val in false_values:
        return False
    else:
        return False
