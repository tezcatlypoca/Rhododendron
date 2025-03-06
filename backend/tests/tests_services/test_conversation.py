import pytest
from datetime import date, timedelta
from unittest.mock import Mock, patch
from src.services.Agent import Agent
from src.dto.dto_message import MessageDTO
from src.dto.dto_conversation import ConversationDTO
from src.services.Conversation import Conversation

class TestConversation:
    """
    Tests unitaires pour la classe métier Conversation
    """
    
    @pytest.fixture
    def mock_agent(self):
        """Fixture pour créer un agent mock"""
        agent = Mock(spec=Agent)
        agent.id = "agent_1"
        agent.name = "Test Agent"
        return agent
    
    @pytest.fixture
    def mock_message(self):
        """Fixture pour créer un message mock"""
        message = Mock(spec=MessageDTO)
        message.id = "msg_1"
        message.sender_id = "agent_1"
        message.content = "Test message"
        message.timestamp = date.today()
        return message
    
    @pytest.fixture
    def sample_conversation(self, mock_agent):
        """Fixture pour créer une instance de conversation de test"""
        return Conversation.with_params(
            conversation_id="conv_1",
            timestamp=date.today(),
            context="Test context",
            project_id="proj_1",
            messages=[],
            participants=[mock_agent],
            status="initial"
        )
    
    def test_empty_init(self):
        """Teste l'initialisation d'une conversation vide"""
        conversation = Conversation()
        assert conversation.id is None
        assert conversation.timestamp is None
        assert conversation.context is None
        assert conversation.project_id is None
        assert isinstance(conversation.messages, list)
        assert len(conversation.messages) == 0
        assert isinstance(conversation.participants, list)
        assert len(conversation.participants) == 0
        assert conversation.status == "initial"
    
    def test_with_params(self, mock_agent):
        """Teste l'initialisation via la méthode with_params"""
        conversation = Conversation.with_params(
            conversation_id="conv_2",
            timestamp=date.today(),
            context="Another context",
            project_id="proj_2",
            messages=[],
            participants=[mock_agent],
            status="draft"
        )
        assert conversation.id == "conv_2"
        assert conversation.timestamp == date.today()
        assert conversation.context == "Another context"
        assert conversation.project_id == "proj_2"
        assert len(conversation.messages) == 0
        assert conversation.participants == [mock_agent]
        assert conversation.status == "draft"
    
    def test_init(self, sample_conversation, mock_agent):
        """Teste l'initialisation correcte d'une conversation"""
        assert sample_conversation.id == "conv_1"
        assert sample_conversation.timestamp == date.today()
        assert sample_conversation.context == "Test context"
        assert sample_conversation.project_id == "proj_1"
        assert len(sample_conversation.messages) == 0
        assert sample_conversation.participants == [mock_agent]
        assert sample_conversation.status == "initial"
    
    def test_set_id(self, sample_conversation):
        """Teste la méthode set_id"""
        sample_conversation.set_id("new_id")
        assert sample_conversation.id == "new_id"
    
    def test_set_timestamp(self, sample_conversation):
        """Teste la méthode set_timestamp"""
        new_date = date.today() - timedelta(days=5)
        sample_conversation.set_timestamp(new_date)
        assert sample_conversation.timestamp == new_date
    
    def test_set_context(self, sample_conversation):
        """Teste la méthode set_context"""
        sample_conversation.set_context("Updated context")
        assert sample_conversation.context == "Updated context"
    
    def test_set_project_id(self, sample_conversation):
        """Teste la méthode set_project_id"""
        sample_conversation.set_project_id("new_project")
        assert sample_conversation.project_id == "new_project"
    
    def test_is_configured(self, sample_conversation):
        """Teste la méthode is_configured avec une conversation complètement configurée"""
        assert sample_conversation.is_configured() is True
    
    def test_is_configured_incomplete(self):
        """Teste la méthode is_configured avec une conversation incomplète"""
        conversation = Conversation()
        assert conversation.is_configured() is False
        
        # Configuration partielle
        conversation.set_id("test_id")
        conversation.set_context("Test Context")
        assert conversation.is_configured() is False
        
        # Configuration complète
        conversation.set_timestamp(date.today())
        conversation.set_project_id("proj_test")
        assert conversation.is_configured() is True
    
    def test_add_message(self, sample_conversation, mock_message):
        """Teste l'ajout d'un message à la conversation"""
        sample_conversation.add_message(mock_message)
        assert mock_message in sample_conversation.messages
        assert len(sample_conversation.messages) == 1
    
    def test_add_duplicate_message(self, sample_conversation, mock_message):
        """Teste qu'on ne peut pas ajouter deux fois le même message"""
        sample_conversation.add_message(mock_message)
        sample_conversation.add_message(mock_message)
        assert len(sample_conversation.messages) == 1
    
    def test_add_participant(self, sample_conversation):
        """Teste l'ajout d'un participant à la conversation"""
        new_agent = Mock(spec=Agent)
        new_agent.id = "agent_2"
        new_agent.name = "Another Agent"
        
        sample_conversation.add_participant(new_agent)
        assert new_agent in sample_conversation.participants
        assert len(sample_conversation.participants) == 2
    
    def test_add_duplicate_participant(self, sample_conversation, mock_agent):
        """Teste qu'on ne peut pas ajouter deux fois le même participant"""
        sample_conversation.add_participant(mock_agent)
        assert len(sample_conversation.participants) == 1
    
    def test_remove_participant(self, sample_conversation, mock_agent):
        """Teste le retrait d'un participant de la conversation"""
        result = sample_conversation.remove_participant(mock_agent.id)
        assert result is True
        assert mock_agent not in sample_conversation.participants
        assert len(sample_conversation.participants) == 0
    
    def test_remove_nonexistent_participant(self, sample_conversation):
        """Teste le retrait d'un participant qui n'existe pas"""
        result = sample_conversation.remove_participant("nonexistent_id")
        assert result is False
        assert len(sample_conversation.participants) == 1
    
    def test_change_status_valid(self, sample_conversation):
        """Teste le changement de statut vers une valeur valide"""
        result = sample_conversation.change_status("active")
        assert result is True
        assert sample_conversation.status == "active"
    
    def test_change_status_invalid(self, sample_conversation):
        """Teste le changement de statut vers une valeur invalide"""
        result = sample_conversation.change_status("invalid_status")
        assert result is False
        assert sample_conversation.status == "initial"  # Status inchangé
    
    def test_get_messages_by_participant(self, sample_conversation, mock_message):
        """Teste la récupération des messages d'un participant spécifique"""
        # Ajout d'un message du premier participant
        sample_conversation.add_message(mock_message)
        
        # Ajout d'un message d'un autre participant
        other_message = Mock(spec=MessageDTO)
        other_message.id = "msg_2"
        other_message.sender_id = "agent_2"
        other_message.content = "Another message"
        other_message.timestamp = date.today()
        sample_conversation.add_message(other_message)
        
        # Vérification que seul le message du participant demandé est retourné
        messages = sample_conversation.get_messages_by_participant("agent_1")
        assert len(messages) == 1
        assert messages[0] == mock_message
    
    def test_get_messages_by_date_range(self, sample_conversation):
        """Teste la récupération des messages dans une plage de dates"""
        # Message d'aujourd'hui
        msg_today = Mock(spec=MessageDTO)
        msg_today.id = "msg_today"
        msg_today.timestamp = date.today()
        
        # Message d'hier
        msg_yesterday = Mock(spec=MessageDTO)
        msg_yesterday.id = "msg_yesterday"
        msg_yesterday.timestamp = date.today() - timedelta(days=1)
        
        # Message d'avant-hier
        msg_before_yesterday = Mock(spec=MessageDTO)
        msg_before_yesterday.id = "msg_before_yesterday"
        msg_before_yesterday.timestamp = date.today() - timedelta(days=2)
        
        # Ajout des messages à la conversation
        sample_conversation.add_message(msg_today)
        sample_conversation.add_message(msg_yesterday)
        sample_conversation.add_message(msg_before_yesterday)
        
        # Test de récupération sur une plage qui inclut seulement hier et aujourd'hui
        start_date = date.today() - timedelta(days=1)
        end_date = date.today()
        
        messages = sample_conversation.get_messages_by_date_range(start_date, end_date)
        assert len(messages) == 2
        assert msg_today in messages
        assert msg_yesterday in messages
        assert msg_before_yesterday not in messages
    
    def test_to_dto(self, sample_conversation, mock_agent, mock_message):
        """Teste la conversion de l'objet métier en DTO"""
        sample_conversation.add_message(mock_message)
        
        dto = sample_conversation.to_dto()
        
        assert isinstance(dto, ConversationDTO)
        assert dto._id == sample_conversation.id
        assert dto.timestamp == sample_conversation.timestamp
        assert dto.context == sample_conversation.context
        assert dto.projectId == sample_conversation.project_id
        assert dto.status == sample_conversation.status
        assert len(dto.messages) == 1
        assert len(dto.participants) == 1
    
    def test_from_dto(self):
        """Teste la création d'un objet métier à partir d'un DTO"""
        # Création d'un DTO mock
        mock_dto = Mock(spec=ConversationDTO)
        mock_dto._id = "conv_from_dto"
        mock_dto.timestamp = date.today()
        mock_dto.context = "Context from DTO"
        mock_dto.projectId = "proj_dto"
        mock_dto.messages = []
        mock_dto.participants = []
        mock_dto.status = "active"
        
        conversation = Conversation.from_dto(mock_dto)
        
        assert conversation.id == "conv_from_dto"
        assert conversation.timestamp == date.today()
        assert conversation.context == "Context from DTO"
        assert conversation.project_id == "proj_dto"
        assert conversation.status == "active"
        assert len(conversation.messages) == 0
        assert len(conversation.participants) == 0
    
    def test_archive(self, sample_conversation):
        """Teste l'archivage d'une conversation"""
        result = sample_conversation.archive()
        assert result is True
        assert sample_conversation.status == "archived"
    
    def test_archive_already_archived(self, sample_conversation):
        """Teste l'archivage d'une conversation déjà archivée"""
        sample_conversation.status = "archived"
        result = sample_conversation.archive()
        assert result is False
    
    def test_is_active(self, sample_conversation):
        """Teste la méthode is_active"""
        # Par défaut, une conversation initiale n'est pas active
        assert sample_conversation.is_active() is False
        
        # Changement vers le statut actif
        sample_conversation.status = "active"
        assert sample_conversation.is_active() is True
        
        # Une conversation archivée n'est pas active
        sample_conversation.status = "archived"
        assert sample_conversation.is_active() is False
    
    def test_get_participant_count(self, sample_conversation):
        """Teste le comptage des participants"""
        assert sample_conversation.get_participant_count() == 1
        
        new_agent = Mock(spec=Agent)
        new_agent.id = "agent_2"
        sample_conversation.add_participant(new_agent)
        
        assert sample_conversation.get_participant_count() == 2
    
    def test_get_message_count(self, sample_conversation, mock_message):
        """Teste le comptage des messages"""
        assert sample_conversation.get_message_count() == 0
        
        sample_conversation.add_message(mock_message)
        assert sample_conversation.get_message_count() == 1
        
        # Ajout d'un deuxième message
        message2 = Mock(spec=MessageDTO)
        message2.id = "msg_2"
        sample_conversation.add_message(message2)
        
        assert sample_conversation.get_message_count() == 2