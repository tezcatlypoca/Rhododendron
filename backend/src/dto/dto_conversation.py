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
        if not self.is_valid_context(self.context):
            raise ValueError("Context cannot be empty")
        
    @staticmethod
    def is_valid_context(context: str) -> bool:
        return bool(context.strip())
# END FUNCTION