from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from ...services.websocket_manager import manager
from ...services.conversation_service import ConversationService
from ...database import get_db
from sqlalchemy.orm import Session
import json

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket, 
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Endpoint WebSocket pour la communication en temps réel
    
    Args:
        websocket: La connexion WebSocket
        token: Token JWT d'authentification
        db: Session de base de données
    """
    # Ajouter des logs détaillés
    print(f"Tentative de connexion WebSocket avec token: {token[:10]}...")
    
    try:
        # Établir la connexion
        await manager.connect(websocket, token)
        print(f"Connexion WebSocket établie avec succès")
        
        conversation_service = ConversationService()
        
        # Boucle de réception des messages
        while True:
            # Attendre un message du client
            data = await websocket.receive_text()
            print(f"Message WebSocket reçu: {data[:50]}...")
            
            try:
                # Convertir le message en JSON
                message_data = json.loads(data)
                message_type = message_data.get("type")
                payload = message_data.get("payload", {})
                
                print(f"Message traité: type={message_type}")
                
                # Traitement selon le type de message
                if message_type == "subscribe":
                    # Abonnement à une conversation
                    conversation_id = payload.get("conversation_id")
                    if conversation_id:
                        print(f"Abonnement à la conversation: {conversation_id}")
                        await manager.subscribe_to_conversation(websocket, conversation_id)
                
                elif message_type == "message":
                    # Message envoyé par l'utilisateur
                    conversation_id = payload.get("conversation_id")
                    content = payload.get("content")
                    
                    if conversation_id and content:
                        print(f"Nouveau message dans conversation {conversation_id}: {content[:50]}...")
                        # Créer le message dans la base de données
                        message_data = {
                            "role": "user",
                            "content": content,
                            "metadata": {}
                        }
                        
                        # Ajouter le message à la conversation
                        message = conversation_service.add_message(
                            conversation_id=conversation_id,
                            message_data=message_data,
                            db=db
                        )
                        
                        # Diffuser le message à tous les abonnés de la conversation
                        await manager.broadcast_to_conversation(
                            {
                                "type": "new_message",
                                "payload": {
                                    "id": str(message.id),
                                    "conversation_id": str(message.conversation_id),
                                    "role": message.role,
                                    "content": message.content,
                                    "timestamp": message.timestamp.isoformat(),
                                    "metadata": message.metadata
                                }
                            },
                            conversation_id
                        )
            
            except json.JSONDecodeError as e:
                # Ignorer les messages non-JSON
                print(f"Erreur JSON dans le message: {e}")
                pass
            except Exception as e:
                # Envoyer l'erreur au client
                print(f"Erreur lors du traitement du message: {e}")
                await manager.send_personal_message(
                    {
                        "type": "error",
                        "payload": {
                            "message": str(e)
                        }
                    },
                    websocket
                )
    
    except WebSocketDisconnect:
        # Gérer la déconnexion du client
        print("Client WebSocket déconnecté")
        await manager.disconnect(websocket)
    except Exception as e:
        print(f"Erreur lors de la gestion WebSocket: {str(e)}")
        if not websocket.client_state == 4:  # Si la connexion n'est pas déjà fermée
            await websocket.close(code=1011, reason=f"Erreur: {str(e)}")