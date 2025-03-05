from dataclasses import dataclass
from dto_role import RoleDTO

@dataclass(repr=True, eq=True, frozen=True)
class agentDTO:
    name: str
    role: RoleDTO
    model_name: str
    temperature: float

    def __post_init__(self):
        if not self.is_valid_name(self.name):
            raise ValueError("Name cannot be empty")
        
        if not self.is_valid_model_name(self.model_name):
            raise ValueError("Model name cannot be empty")
        
        if not self.is_valid_temperature(self.temperature):
            raise ValueError("Temprature cannot be empty")
        
        if not self.is_float(self.temperature):
            raise ValueError("Temprature has to be float type")
    # END FUNCTION

    @staticmethod
    def is_valid_model_name(model_name: str) -> bool:
        return bool(model_name.strip())
    
    @staticmethod
    def is_valid_name(name: str) -> bool:
        return bool(name.strip())
    
    @staticmethod
    def is_valid_temperature(temperature: float) -> bool:
        return (temperature is not None) 
    
    def is_float(temperature: float) -> float:
        return isinstance(temperature, float)
# END FUNCTION