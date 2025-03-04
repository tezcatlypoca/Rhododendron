from dataclasses import dataclass, field
from datetime import Date

@dataclass(repr=True, eq=True, frozen=True)
class Message:
    id: str
    conversationId: str
    senderId: str
    content: str
    timestamp: Date
    status: str = field(default="initial") # 'send' | 'delivered' | 'read'

    def __post_init__(self):
        if not self.is_valid_content(self.content):
            raise ValueError("Content cannot be empty")

    @staticmethod
    def is_valid_content(content: str) -> bool:
        return bool(content.strip())
# END CLASS