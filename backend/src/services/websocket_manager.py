from typing import Dict, Set, Awaitable, Optional, List
from fastapi import WebSocket, WebSocketDisconnect, Depends, HTTPException
import json
import asyncio
from datetime import datetime

class ConnectionManager:
    """
    Gestionnaire de connexions WebSocket
    Gère les connexions actives et la distribution des messages
    """
    def __init__(self):
        # Connexions actives par utilisateur
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Abonnements par conversation
        self.conversation_subscriptions: Dict[str, Set[WebSocket]] = {}
        # Token JWT associé à chaque connexion
        self.connection_tokens: Dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket, token: str):
        """
        Établit une connexion WebSocket
        
        Args:
            websocket: La connexion WebSocket
            token: Le token JWT d'authentification
        """
        # D'abord accepter la connexion
        await websocket.accept()
        
        # Stocker le token pour cette connexion
        self.connection_tokens[websocket] = token
        
        try:
            # Dans un environnement réel, on validerait le token ici
            # Pour l'instant, accepter n'importe quel token pour éviter le 403
            # NOTE: Implémentation simplifiée pour le développement
            
            # Utiliser un identifiant temporaire pour le développement
            user_id = "temp_user_id"
            
            # Ajouter la connexion au dictionnaire
            if user_id not in self.active_connections:
                self.active_connections[user_id] = set()
            self.active_connections[user_id].add(websocket)
            
            # Envoyer un message de bienvenue
            await self.send_personal_message(
                {
                    "type": "connection_established",
                    "payload": {
                        "message": "Connexion établie",
                        "user_id": user_id,
                        "timestamp": datetime.now().isoformat()
                    }
                },
                websocket
            )
        except Exception as e:
            print(f"Erreur lors de la connexion WebSocket: {str(e)}")
            # Ne pas fermer la connexion pour l'instant

    async def disconnect(self, websocket: WebSocket):
        """
        Gère la déconnexion d'un client WebSocket
        
        Args:
            websocket: La connexion WebSocket à fermer
        """
        # Identifier l'utilisateur
        user_id = None
        for uid, connections in self.active_connections.items():
            if websocket in connections:
                user_id = uid
                connections.remove(websocket)
                if not connections:
                    del self.active_connections[uid]
                break
        
        # Supprimer des abonnements aux conversations
        for conv_id, subscribers in list(self.conversation_subscriptions.items()):
            if websocket in subscribers:
                subscribers.remove(websocket)
                if not subscribers:
                    del self.conversation_subscriptions[conv_id]
        
        # Supprimer le token associé
        if websocket in self.connection_tokens:
            del self.connection_tokens[websocket]

    async def subscribe_to_conversation(self, websocket: WebSocket, conversation_id: str):
        """
        Abonne un client WebSocket à une conversation spécifique
        
        Args:
            websocket: La connexion WebSocket
            conversation_id: L'ID de la conversation à suivre
        """
        if conversation_id not in self.conversation_subscriptions:
            self.conversation_subscriptions[conversation_id] = set()
        self.conversation_subscriptions[conversation_id].add(websocket)
        
        # Envoyer une confirmation d'abonnement
        await self.send_personal_message(
            {
                "type": "subscription_confirmed",
                "payload": {
                    "conversation_id": conversation_id,
                    "timestamp": datetime.now().isoformat()
                }
            },
            websocket
        )

    async def broadcast_to_conversation(self, message: dict, conversation_id: str):
        """
        Diffuse un message à tous les clients abonnés à une conversation
        
        Args:
            message: Le message à diffuser
            conversation_id: L'ID de la conversation concernée
        """
        if conversation_id in self.conversation_subscriptions:
            await self.broadcast(message, list(self.conversation_subscriptions[conversation_id]))

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """
        Envoie un message à un client spécifique
        
        Args:
            message: Le message à envoyer
            websocket: La connexion WebSocket destinataire
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Erreur lors de l'envoi du message: {str(e)}")
            await self.disconnect(websocket)

    async def broadcast(self, message: dict, websockets: List[WebSocket]):
        """
        Diffuse un message à plusieurs clients
        
        Args:
            message: Le message à diffuser
            websockets: Liste des connexions WebSocket destinataires
        """
        for websocket in websockets.copy():
            try:
                await websocket.send_json(message)
            except Exception as e:
                print(f"Erreur lors de la diffusion du message: {str(e)}")
                await self.disconnect(websocket)

# Créer une instance singleton du gestionnaire
manager = ConnectionManager()