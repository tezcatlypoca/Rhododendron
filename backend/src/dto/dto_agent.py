from dataclasses import dataclass
from dto_role import Role

@dataclass(repr=True, eq=True, frozen=True)
class agentDTO:
    name: str
    role: Role
    model_name: str
    temperature: float

    def __post_init__(self):
        pass

    @staticmethod
    def is_valid_model_name(model_name: str) -> bool:
        return bool(model_name.strip())
    
    @staticmethod
    def is_valid_name(name: str) -> bool:
        return bool(name.strip())
    
    @staticmethod
    def is_valid_temperature(temperature: str) -> bool:
        return bool((temperature != None) && (isinstance(temperature, float)))