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

# Mock de Agent
@dataclasses.dataclass
class Agent:
    name: str
    role: str = None
    model_name: str = "default_model"
    temperature: float = 0.5

# Mock de Conversation
@dataclasses.dataclass(frozen=True)
class Conversation:
    _id: str
    timestamp: date
    context: str
    projectId: int
    messages: list = dataclasses.field(default_factory=list)
    participants: list = dataclasses.field(default_factory=list)
    status: str = "initial"
    
    def __post_init__(self):
        if not self.timestamp:
            raise ValueError("Timestamp cannot be empty or None type")
            
        if not isinstance(self.timestamp, date):
            raise ValueError("Timestamp has to be Date type")
            
        if not self.context:
            raise ValueError("Context cannot be empty or None type")
            
        if self.projectId is None:
            raise ValueError("Project id cannot be empty or None type")

@pytest.fixture
def valid_conversation_data():
    """Fixture fournissant des données valides pour un Conversation DTO."""
    return {
        "_id": "conv_123",
        "timestamp": date.today(),
        "context": "Projet de développement logiciel",
        "projectId": 42,
        "messages": [],
        "participants": [],
        "status": "initial"
    }

def test_conversation_dto_valid_initialization(valid_conversation_data):
    """Test d'initialisation avec des données valides."""
    conversation = Conversation(**valid_conversation_data)
    
    assert conversation._id == valid_conversation_data["_id"]
    assert conversation.timestamp == valid_conversation_data["timestamp"]
    assert conversation.context == valid_conversation_data["context"]
    assert conversation.projectId == valid_conversation_data["projectId"]
    assert conversation.messages == []
    assert conversation.participants == []
    assert conversation.status == "initial"

def test_conversation_dto_immutability(valid_conversation_data):
    """Vérifie l'immutabilité du Conversation DTO."""
    conversation = Conversation(**valid_conversation_data)
    
    # Tentatives de modification qui doivent échouer
    with pytest.raises(dataclasses.FrozenInstanceError):
        conversation._id = "new_id"
    
    with pytest.raises(dataclasses.FrozenInstanceError):
        conversation.timestamp = date(2024, 1, 1)
    
    with pytest.raises(dataclasses.FrozenInstanceError):
        conversation.context = "Nouveau contexte"
    
    with pytest.raises(dataclasses.FrozenInstanceError):
        conversation.status = "archived"

def test_conversation_dto_invalid_initialization():
    """Test des cas d'initialisation invalides."""
    # Test avec un timestamp None
    with pytest.raises(ValueError, match="Timestamp cannot be empty or None type"):
        Conversation(
            _id="conv_123", 
            timestamp=None, 
            context="Test", 
            projectId=42
        )
    
    # Test avec un timestamp invalide
    with pytest.raises(ValueError, match="Timestamp has to be Date type"):
        Conversation(
            _id="conv_123", 
            timestamp="2024-01-01", 
            context="Test", 
            projectId=42
        )
    
    # Test avec un contexte vide
    with pytest.raises(ValueError, match="Context cannot be empty or None type"):
        Conversation(
            _id="conv_123", 
            timestamp=date.today(), 
            context="", 
            projectId=42
        )
    
    # Test avec un project ID None
    with pytest.raises(ValueError, match="Project id cannot be empty or None type"):
        Conversation(
            _id="conv_123", 
            timestamp=date.today(), 
            context="Test", 
            projectId=None
        )

def test_conversation_dto_with_optional_fields(valid_conversation_data):
    """Test l'initialisation avec des champs optionnels."""
    # Ajout de messages et participants
    mock_message = Message(
        id="msg_1", 
        conversationId="conv_123", 
        senderId="user_1", 
        content="Test message", 
        timestamp=date.today()
    )
    mock_agent = Agent(name="Test Agent", role=None, model_name="test_model", temperature=0.7)
    
    conversation_data = valid_conversation_data.copy()
    conversation_data["messages"] = [mock_message]
    conversation_data["participants"] = [mock_agent]
    
    conversation = Conversation(**conversation_data)
    
    assert len(conversation.messages) == 1
    assert conversation.messages[0] == mock_message
    assert len(conversation.participants) == 1
    assert conversation.participants[0] == mock_agent