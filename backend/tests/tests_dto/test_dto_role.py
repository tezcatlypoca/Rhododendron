import pytest
import dataclasses
from src.dto.dto_role import RoleDTO, ClassicRoleDTO, ManagerRoleDTO

@pytest.fixture
def valid_role_data():
    """Fixture fournissant des données valides pour un RoleDTO."""
    return {
        "name": "TestRole",
        "description": "Un rôle de test complet",
        "prompt_system": "Tu es un agent de test conçu pour vérifier les fonctionnalités."
    }

def test_role_dto_valid_initialization(valid_role_data):
    """Test d'initialisation avec des données valides."""
    role = RoleDTO(**valid_role_data)
    
    assert role.name == valid_role_data["name"]
    assert role.description == valid_role_data["description"]
    assert role.prompt_system == valid_role_data["prompt_system"]

def test_role_dto_immutability(valid_role_data):
    """Vérifie l'immutabilité du RoleDTO."""
    role = RoleDTO(**valid_role_data)
    
    # Tentatives de modification qui doivent échouer
    with pytest.raises(dataclasses.FrozenInstanceError):
        role.name = "NewName"
    
    with pytest.raises(dataclasses.FrozenInstanceError):
        role.description = "New Description"
    
    with pytest.raises(dataclasses.FrozenInstanceError):
        role.prompt_system = "New Prompt"

def test_role_dto_invalid_initialization():
    """Test des cas d'initialisation invalides."""
    # Test avec un nom vide
    with pytest.raises(ValueError, match="Name cannot be empty or None type"):
        RoleDTO(name="", description="Test", prompt_system="Prompt")
    
    # Test avec un nom composé uniquement d'espaces
    with pytest.raises(ValueError, match="Name cannot be empty or None type"):
        RoleDTO(name="   ", description="Test", prompt_system="Prompt")
    
    # Test avec une description vide
    with pytest.raises(ValueError, match="Description cannot be empty or None type"):
        RoleDTO(name="TestRole", description="", prompt_system="Prompt")
    
    # Test avec un prompt système vide
    with pytest.raises(ValueError, match="Prompt system cannot be empty or None type"):
        RoleDTO(name="TestRole", description="Test", prompt_system="")

def test_default_role_dtos():
    """Test des DTO de rôles par défaut."""
    # Test ClassicRoleDTO
    classic_role = ClassicRoleDTO(prompt_system="Custom Prompt")
    assert classic_role.name == "IA Assistant"
    assert classic_role.description == "IA Assistant"
    assert classic_role.prompt_system == "Custom Prompt"

    # Test ManagerRoleDTO avec valeurs par défaut
    manager_role = ManagerRoleDTO()
    assert manager_role.name == "Manager"
    assert manager_role.description == "Responsable de la planification et de la coordination du projet"
    assert manager_role.prompt_system.startswith("Tu es un Manager de projet")

def test_role_dto_string_representation(valid_role_data):
    """Vérifie la représentation textuelle du RoleDTO."""
    role = RoleDTO(**valid_role_data)
    expected_str = f"Role(nom={valid_role_data['name']}, description={valid_role_data['description']})"
    assert str(role) == expected_str

def test_role_dto_comparison(valid_role_data):
    """Vérifie l'égalité entre RoleDTO."""
    role1 = RoleDTO(**valid_role_data)
    role2 = RoleDTO(**valid_role_data)
    role3 = RoleDTO(
        name="DifferentRole", 
        description="Different Description", 
        prompt_system="Different Prompt"
    )
    
    assert role1 == role2  # Doivent être égaux
    assert role1 != role3  # Doivent être différents