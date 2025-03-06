import pytest
import dataclasses

# Mock de Artefact
@dataclasses.dataclass(frozen=True)
class Artefact:
    id: str
    type: str
    content: str
    creator: str
    version: str = "1.0.0"
    
    def __post_init__(self):
        valid_types = ["code", "doc", "test"]
        
        if self.type not in valid_types:
            raise ValueError("Type should be a code like: 'code' | 'doc' | 'test'")
        
        if not self.content:
            raise ValueError("Content cannot be empty or None type")
            
        if not self.creator:
            raise ValueError("Creator cannot be empty or None type")

@pytest.fixture
def valid_artefact_data():
    """Fixture fournissant des données valides pour un Artefact DTO."""
    return {
        "id": "art_123",
        "type": "code",
        "content": "def hello_world():\n    print('Hello, World!')",
        "creator": "test_user",
        "version": "1.0.0"
    }

def test_artefact_dto_valid_initialization(valid_artefact_data):
    """Test d'initialisation avec des données valides."""
    artefact = Artefact(**valid_artefact_data)
    
    assert artefact.id == valid_artefact_data["id"]
    assert artefact.type == "code"
    assert artefact.content == valid_artefact_data["content"]
    assert artefact.creator == valid_artefact_data["creator"]
    assert artefact.version == valid_artefact_data["version"]

def test_artefact_dto_immutability(valid_artefact_data):
    """Vérifie l'immutabilité du Artefact DTO."""
    artefact = Artefact(**valid_artefact_data)
    
    # Tentatives de modification qui doivent échouer
    with pytest.raises(dataclasses.FrozenInstanceError):
        artefact.id = "new_id"
    
    with pytest.raises(dataclasses.FrozenInstanceError):
        artefact.type = "doc"
    
    with pytest.raises(dataclasses.FrozenInstanceError):
        artefact.content = "Nouveau contenu"
    
    with pytest.raises(dataclasses.FrozenInstanceError):
        artefact.creator = "new_user"

def test_artefact_dto_invalid_initialization():
    """Test des cas d'initialisation invalides."""
    # Test avec un type invalide
    with pytest.raises(ValueError, match="Type should be a code like: 'code' | 'doc' | 'test'"):
        Artefact(
            id="art_123", 
            type="invalid", 
            content="Test content", 
            creator="test_user", 
            version="1.0.0"
        )
    
    # Test avec un contenu vide
    with pytest.raises(ValueError, match="Content cannot be empty or None type"):
        Artefact(
            id="art_123", 
            type="code", 
            content="", 
            creator="test_user", 
            version="1.0.0"
        )
    
    # Test avec un créateur vide
    with pytest.raises(ValueError, match="Creator cannot be empty or None type"):
        Artefact(
            id="art_123", 
            type="code", 
            content="Test content", 
            creator="", 
            version="1.0.0"
        )

def test_artefact_dto_valid_types():
    """Test tous les types valides d'artefact."""
    valid_types = ["code", "doc", "test"]
    
    for art_type in valid_types:
        artefact = Artefact(
            id="art_123", 
            type=art_type, 
            content="Test content", 
            creator="test_user", 
            version="1.0.0"
        )
        assert artefact.type == art_type