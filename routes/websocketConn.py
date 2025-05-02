from fastapi import WebSocket
import redis
import json
from typing import Dict
import os
# from routes.chat import redis_client


HOST_REDIS = os.getenv('HOST_REDIS')

redis_client = redis.Redis(host=HOST_REDIS, port=6379, db=0,  decode_responses=True)

class connectionManager:
    
    def __init__(self):
        self.activeconnections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, clientId:str):
        await websocket.accept()
        self.activeconnections[clientId] = websocket
        
    
    def disconnect(self, client_id: str):
        del self.activeconnections[client_id]
   
    async def send_personal_message(self, message: dict, client_id: str):
        websocket = self.activeconnections.get(client_id)
        if websocket:
            await websocket.send_text(json.dumps(message))
        else:
            redis_client.rpush(f"messages:{client_id}", json.dumps({
                'sender_id': client_id,
                'message': message
            }))
            # print("ne",message)
    
    async def broadcast(self, message: dict, senderId: str, recieverId: str):
        receiver_ws = self.activeconnections.get(recieverId)
        if receiver_ws:
            await receiver_ws.send_text(json.dumps(message))
        else:
            # If the receiver is not connected, push the message to Redis
            redis_client.rpush(f"messages:{recieverId}", json.dumps({
                'sender_id': senderId,
                'message': message
            }))
        # print("nos",message)