from dataclasses import dataclass, field
from src.agents.Agent import Agent
from dto_message import MessageDTO
from datetime import date

@dataclass(repr=True, eq=True, frozen=True)
class ConversationDTO:
    _id: str
    timestamp: date
    context: str
    projectId: int
    messages: list[MessageDTO] = field(default=[])
    participants: list[Agent] = field(default=[])
    status:str = field(default='initial') # 'draft' | 'active' | 'archived'

    def __post_init__(self):
        if not self.is_valid_timestamp(self.timestamp):
            raise ValueError("Timestamp cannot be empty or None type")
        
        if not self.is_valid_date_type(self.timestamp):
            raise ValueError("Timestamp has to be Date type")

        if not self.is_valid_context(self.context):
            raise ValueError("Context cannot be empty or None type")
        
        if not self.is_valid_project_id(self.projectId):
            raise ValueError("Project id cannot be empty or None type")
    # END FUNCTION

    @staticmethod
    def is_valid_timestamp(timestamp: date) -> bool:
        return timestamp is not None
    
    @staticmethod
    def is_valid_date_type(timestamp: date) -> bool:
        return isinstance(timestamp, date)
        
    @staticmethod
    def is_valid_context(context: str) -> bool:
        return context is not None and bool(context.strip())
    
    @staticmethod
    def is_valid_project_id(projectId: str):
        return projectId is not None and bool(projectId.strip())
# END FUNCTION