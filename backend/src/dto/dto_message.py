from dataclasses import dataclass, field
from datetime import date

@dataclass(repr=True, eq=True, frozen=True)
class MessageDTO:
    id: str
    conversationId: str
    senderId: str
    content: str
    timestamp: date
    status: str = field(default="initial") # 'send' | 'delivered' | 'read'

    def __post_init__(self):
        if not self.is_valid_sender_id(self.senderId):
            raise ValueError("Sender id cannot be empty or None type")
        
        if not self.is_valid_timestamp(self.timestamp):
            raise ValueError("Timestamp cannot be empty or None type")
        
        if not self.is_valid_date_type(self.timestamp):
            raise ValueError("Timestamp has to be Date type")
        
        if not self.is_valid_content(self.content):
            raise ValueError("Content cannot be empty or None type")
    # END FUNCTION
        
    @staticmethod
    def is_valid_sender_id(senderId: str) -> bool:
        return senderId is not None and bool(senderId.strip())

    @staticmethod
    def is_valid_content(content: str) -> bool:
        return content is not None and  bool(content.strip())
    
    @staticmethod
    def is_valid_timestamp(timestamp: date) -> bool:
        return timestamp is not None
    
    @staticmethod
    def is_valid_date_type(timestamp: date) -> bool:
        return isinstance(timestamp, date)
# END CLASS