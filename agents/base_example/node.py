import asyncio
import json
from typing import Dict, List, Optional

import websockets
from pydantic import BaseModel

from ...main import BaseAgent


class Message(BaseModel):
    from_agent_id: str
    content: str
    conversation_id: Optional[str] = None

class NodeAgent(BaseAgent):
    def __init__(
        self,
        node_url: str = "ws://localhost:8080",
        agent_id: Optional[str] = None
    ):
        self.node_url = node_url
        self.agent_id = agent_id
        self._websocket: Optional[websockets.WebSocketClientProtocol] = None
        self._message_handlers: List[callable] = []
        self._running = False

    async def start(self):
        """Start the agent and connect to the node"""
        try:
            self._running = True
            await self._connect()
            print("Node Agent started successfully")
        except Exception as e:
            print(f"Failed to start agent: {e}")
            raise

    async def stop(self):
        """Stop the agent and cleanup"""
        self._running = False
        if self._websocket:
            await self._websocket.close()
            self._websocket = None
        print("Node Agent stopped")

    async def _connect(self):
        """Connect to the node websocket"""
        try:
            self._websocket = await websockets.connect(self.node_url)
            
            # Register the agent if we have an ID
            if self.agent_id:
                await self._websocket.send(json.dumps({
                    "type": "register",
                    "agentId": self.agent_id
                }))
            
            # Start message handling loop
            asyncio.create_task(self._handle_messages())
        except Exception as e:
            print(f"Error connecting to node: {e}")
            raise

    async def _handle_messages(self):
        """Handle incoming websocket messages"""
        while self._running and self._websocket:
            try:
                message = await self._websocket.recv()
                data = json.loads(message)
                
                # Convert to Message object
                if "type" in data and data["type"] == "message":
                    msg = Message(**data["payload"])
                    await self.handle_message(msg)
            except websockets.exceptions.ConnectionClosed:
                print("Connection closed, attempting to reconnect...")
                await asyncio.sleep(5)
                await self._connect()
            except Exception as e:
                print(f"Error handling websocket message: {e}")
                await asyncio.sleep(1)

    async def handle_message(self, message: Message):
        """Handle incoming messages"""
        try:
            print(f"Received message: {message}")
            
            # Call all registered message handlers
            for handler in self._message_handlers:
                await handler(message)
                
        except Exception as e:
            print(f"Error handling message: {e}")

    async def send_message(self, to_agent_id: str, content: str, conversation_id: Optional[str] = None):
        """Send a message to another agent"""
        if not self._websocket:
            raise RuntimeError("Not connected to node")
            
        try:
            await self._websocket.send(json.dumps({
                "type": "message",
                "payload": {
                    "toAgentId": to_agent_id,
                    "content": content,
                    "conversationId": conversation_id
                }
            }))
        except Exception as e:
            print(f"Error sending message: {e}")
            raise

    def on_message(self, handler: callable):
        """Register a message handler"""
        self._message_handlers.append(handler)
        return lambda: self._message_handlers.remove(handler)

async def create_node_agent(
    node_url: Optional[str] = None,
    agent_id: Optional[str] = None
) -> NodeAgent:
    """Create and start a node agent"""
    agent = NodeAgent(node_url, agent_id)
    await agent.start()
    return agent 