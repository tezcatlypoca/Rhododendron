from dataclasses import dataclass, field
from src.agents.Agent import Agent
from dto_message import Message
from datetime import Date

@dataclass(repr=True, eq=True, frozen=True)
class Conversation:
    _id: str
    messages: list[Message] = field(default=[])
    participants: list[Agent] = field(default=[])
    timestamp: Date
    context: str
    projectId: int
    status:str = field(default='initial') # 'draft' | 'active' | 'archived'

    def __post_init__(self):
        if not self.is_valid_timestamp(self.timestamp):
            raise ValueError("Timestamp cannot be empty")
        
        if not self.is_valid_date_type(self.timestamp):
            raise ValueError("Timestamp has to be Date type")

        if not self.is_valid_context(self.context):
            raise ValueError("Context cannot be empty")
        
        if not self.is_valid_project_id(self.projectId):
            raise ValueError("Project id cannot be empty")
    # END FUNCTION
        
    @staticmethod
    def is_valid_timestamp(timestamp: Date) -> bool:
        return timestamp is not None
    
    @staticmethod
    def is_valid_date_type(timestamp: Date) -> bool:
        return isinstance(timestamp, Date)
        
    @staticmethod
    def is_valid_context(context: str) -> bool:
        return bool(context.strip())
    
    @staticmethod
    def is_valid_project_id(projectId: str):
        return bool(projectId.strip())
# END FUNCTION