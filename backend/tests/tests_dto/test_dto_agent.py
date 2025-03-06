from src.dto.dto_agent import agentDTO 
from dataclasses import FrozenInstanceError
import pytest


class MockRoleDTO:
    def __init__(self, name: str, description: str, prompt_system: str):
        self.name = name
        self.description = description
        self.prompt_system = prompt_system

@pytest.fixture
def example_roles():
    """Fixture fournissant deux rôles d'exemple."""
    return {
        "admin": MockRoleDTO(
            name="Admin", 
            description="Has full access to the system", 
            prompt_system="You are an administrator with full privileges."
        ),
        "user": MockRoleDTO(
            name="User", 
            description="Can access limited resources", 
            prompt_system="You are a standard user with limited privileges."
        )
    }

def test_agent_dto_immutability(example_roles):
    # Test d'initialisation valide
    agent = agentDTO(
        name="John Doe", 
        role=example_roles["admin"], 
        model_name="gpt-4", 
        temperature=0.7
    )

    # Vérification de l'immutabilité - tentative de modification qui doit échouer
    with pytest.raises(AttributeError):
        agent.name = "Jane Doe"
    
    with pytest.raises(AttributeError):
        agent.role = example_roles["user"]
    
    with pytest.raises(AttributeError):
        agent.model_name = "gpt-3.5-turbo"
    
    with pytest.raises(AttributeError):
        agent.temperature = 0.5

def test_agent_dto_invalid_initialization(example_roles):
    # Test avec un nom vide
    with pytest.raises(ValueError, match="Name cannot be empty or None type"):
        agentDTO(
            name="", 
            role=example_roles["admin"], 
            model_name="gpt-4", 
            temperature=0.7
        )

    # Test avec un nom None
    with pytest.raises(ValueError, match="Name cannot be empty or None type"):
        agentDTO(
            name=None, 
            role=example_roles["admin"], 
            model_name="gpt-4", 
            temperature=0.7
        )

    # Test avec un nom composé uniquement d'espaces
    with pytest.raises(ValueError, match="Name cannot be empty or None type"):
        agentDTO(
            name="   ", 
            role=example_roles["admin"], 
            model_name="gpt-4", 
            temperature=0.7
        )

    # Test avec un nom de modèle vide
    with pytest.raises(ValueError, match="Model name cannot be empty or None type"):
        agentDTO(
            name="John Doe", 
            role=example_roles["admin"], 
            model_name="", 
            temperature=0.7
        )

    # Test avec une température invalide (None)
    with pytest.raises(ValueError, match="Temprature cannot be empty or None type"):
        agentDTO(
            name="John Doe", 
            role=example_roles["admin"], 
            model_name="gpt-4", 
            temperature=None
        )

    # Test avec une température non float
    with pytest.raises(ValueError, match="Temprature has to be float type"):
        agentDTO(
            name="John Doe", 
            role=example_roles["admin"], 
            model_name="gpt-4", 
            temperature="0.7"
        )

def test_immutability(example_roles):
    """Vérifie qu'on ne peut pas modifier les attributs d'un agentDTO."""
    role = example_roles["admin"]
    agent = agentDTO(name="Alice", role=role, model_name="Llama3", temperature=0.7)

    # Vérification de l'impossibilité de modifier chaque attribut individuellement
    with pytest.raises(FrozenInstanceError):
        agent.name = "Bob"
    
    with pytest.raises(FrozenInstanceError):
        agent.role = example_roles["user"]
    
    with pytest.raises(FrozenInstanceError):
        agent.model_name = "GPT-4"
    
    with pytest.raises(FrozenInstanceError):
        agent.temperature = 1.2

    # Vérification supplémentaire que l'objet reste inchangé après les tentatives
    assert agent.name == "Alice"
    assert agent.role == role
    assert agent.model_name == "Llama3"
    assert agent.temperature == 0.7