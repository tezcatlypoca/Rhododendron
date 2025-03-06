import pytest
import dataclasses
from datetime import date

# Mock de Message
@dataclasses.dataclass(frozen=True)
class Message:
    id: str
    conversationId: str
    senderId: str
    content: str
    timestamp: date
    status: str = "initial"
    
    def __post_init__(self):
        if not self.senderId:
            raise ValueError("Sender id cannot be empty or None type")
        
        if not self.timestamp:
            raise ValueError("Timestamp cannot be empty or None type")
            
        if not isinstance(self.timestamp, date):
            raise ValueError("Timestamp has to be Date type")
            
        if not self.content:
            raise ValueError("Content cannot be empty or None type")

@pytest.fixture
def valid_message_data():
    """Fixture fournissant des données valides pour un Message DTO."""
    return {
        "id": "msg_123",
        "conversationId": "conv_456",
        "senderId": "user_789",
        "content": "Bonjour, ceci est un message de test",
        "timestamp": date.today(),
        "status": "initial"
    }

def test_message_dto_valid_initialization(valid_message_data):
    """Test d'initialisation avec des données valides."""
    message = Message(**valid_message_data)
    
    assert message.id == valid_message_data["id"]
    assert message.conversationId == valid_message_data["conversationId"]
    assert message.senderId == valid_message_data["senderId"]
    assert message.content == valid_message_data["content"]
    assert message.timestamp == valid_message_data["timestamp"]
    assert message.status == "initial"

def test_message_dto_immutability(valid_message_data):
    """Vérifie l'immutabilité du Message DTO."""
    message = Message(**valid_message_data)
    
    # Tentatives de modification qui doivent échouer
    with pytest.raises(dataclasses.FrozenInstanceError):
        message.id = "new_id"
    
    with pytest.raises(dataclasses.FrozenInstanceError):
        message.senderId = "new_sender"
    
    with pytest.raises(dataclasses.FrozenInstanceError):
        message.content = "Nouveau contenu"
    
    with pytest.raises(dataclasses.FrozenInstanceError):
        message.status = "read"

def test_message_dto_invalid_initialization():
    """Test des cas d'initialisation invalides."""
    # Test avec un senderId vide
    with pytest.raises(ValueError, match="Sender id cannot be empty or None type"):
        Message(
            id="msg_123", 
            conversationId="conv_456", 
            senderId="", 
            content="Test", 
            timestamp=date.today()
        )
    
    # Test avec un timestamp None
    with pytest.raises(ValueError, match="Timestamp cannot be empty or None type"):
        Message(
            id="msg_123", 
            conversationId="conv_456", 
            senderId="user_789", 
            content="Test", 
            timestamp=None
        )
    
    # Test avec un timestamp invalide
    with pytest.raises(ValueError, match="Timestamp has to be Date type"):
        Message(
            id="msg_123", 
            conversationId="conv_456", 
            senderId="user_789", 
            content="Test", 
            timestamp="2024-01-01"
        )
    
    # Test avec un contenu vide
    with pytest.raises(ValueError, match="Content cannot be empty or None type"):
        Message(
            id="msg_123", 
            conversationId="conv_456", 
            senderId="user_789", 
            content="", 
            timestamp=date.today()
        )