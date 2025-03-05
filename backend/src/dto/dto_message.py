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
        if not self.is_valid_sender_id(self.senderId):
            raise ValueError("Sender id cannot be empty")
        
        if not self.is_valid_timestamp(self.timestamp):
            raise ValueError("Timestamp cannot be empty")
        
        if not self.is_valid_date_type(self.timestamp):
            raise ValueError("Timestamp has to be Date type")
        
        if not self.is_valid_content(self.content):
            raise ValueError("Content cannot be empty")
    # END FUNCTION
        
    @staticmethod
    def is_valid_sender_id(senderId: str) -> bool:
        return bool(senderId.strip())

    @staticmethod
    def is_valid_content(content: str) -> bool:
        return bool(content.strip())
    
    @staticmethod
    def is_valid_timestamp(timestamp: Date) -> bool:
        return timestamp is not None
    
    @staticmethod
    def is_valid_date_type(timestamp: Date) -> bool:
        return isinstance(timestamp, Date)
# END CLASS