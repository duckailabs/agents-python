import asyncio
import time
from typing import Dict, List, Optional

import aiohttp
import openai
from pydantic import BaseModel

from ...main import BaseAgent


class Message(BaseModel):
    from_agent_id: str
    content: str
    conversation_id: Optional[str] = None
    timestamp: float = time.time()

class ConversationMessage(BaseModel):
    role: str
    content: str

class MarketSentimentAgent(BaseAgent):
    def __init__(
        self,
        api_key: str,
        openai_api_key: str,
        api_url: str = "http://localhost:3000"
    ):
        self.api_url = api_url
        self.api_key = api_key
        self.openai_client = openai.Client(api_key=openai_api_key)
        self.conversation_history: Dict[str, List[ConversationMessage]] = {}
        self.last_message_timestamp: float = 0
        self._poll_task: Optional[asyncio.Task] = None
        self._session: Optional[aiohttp.ClientSession] = None

    async def start(self):
        """Start the agent and begin listening for messages"""
        try:
            self._session = aiohttp.ClientSession(
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": self.api_key
                }
            )
            self._poll_task = asyncio.create_task(self._start_polling())
            print("Market Sentiment Agent started successfully")
        except Exception as e:
            print(f"Failed to start agent: {e}")
            raise

    async def stop(self):
        """Stop the agent and cleanup"""
        if self._poll_task:
            self._poll_task.cancel()
            self._poll_task = None
        if self._session:
            await self._session.close()
            self._session = None
        print("Market Sentiment Agent stopped")

    async def _start_polling(self):
        """Start polling for new messages"""
        while True:
            try:
                async with self._session.get(
                    f"{self.api_url}/messages",
                    params={"since": self.last_message_timestamp}
                ) as response:
                    data = await response.json()
                    messages = data.get("messages", [])
                    
                    for message in messages:
                        msg = Message(**message)
                        await self.handle_message(msg)
                        self.last_message_timestamp = max(
                            self.last_message_timestamp,
                            msg.timestamp
                        )
            except Exception as e:
                print(f"Error polling messages: {e}")
            
            await asyncio.sleep(5)  # Poll every 5 seconds

    async def handle_message(self, message: Message):
        """Handle incoming messages"""
        try:
            print(f"Received message: {message}")
            
            # Process the message and generate response
            response = await self._process_message(message)
            
            # Send response back
            if response:
                async with self._session.post(
                    f"{self.api_url}/messages",
                    json={
                        "toAgentId": message.from_agent_id,
                        "content": response,
                        "conversationId": message.conversation_id
                    }
                ) as resp:
                    await resp.json()
        except Exception as e:
            print(f"Error handling message: {e}")

    async def _process_message(self, message: Message) -> Optional[str]:
        """Process incoming message and generate response using OpenAI"""
        try:
            # Get or initialize conversation history
            if message.from_agent_id not in self.conversation_history:
                self.conversation_history[message.from_agent_id] = []
            history = self.conversation_history[message.from_agent_id]

            # Build messages array with system prompt and history
            messages = [
                {
                    "role": "system",
                    "content": """You are a Market Sentiment Analysis agent in the OpenPond P2P network.
Your main capabilities:
- Analyze market sentiment and trends
- Provide insights on market movements
- Interpret financial news and data
Keep responses concise (2-3 sentences) but informative.
Your main traits:
- Professional and analytical
- Data-driven in your responses
- Focus on market sentiment and trends
- Expert in financial markets and crypto"""
                },
                *[{"role": m.role, "content": m.content} for m in history],
                {"role": "user", "content": message.content}
            ]

            # Add artificial delay to prevent rate limiting
            await asyncio.sleep(0.5)

            completion = await self.openai_client.chat.completions.create(
                messages=messages,
                model="gpt-3.5-turbo",
                temperature=0.7
            )

            response = completion.choices[0].message.content or "Sorry, I couldn't process that request."

            # Update conversation history
            history.extend([
                ConversationMessage(role="user", content=message.content),
                ConversationMessage(role="assistant", content=response)
            ])

            # Keep history limited to last 10 messages
            if len(history) > 10:
                history = history[2:]

            return response
        except Exception as e:
            print(f"Error processing message with OpenAI: {e}")
            return "Sorry, I encountered an error processing your message."

async def create_market_sentiment_agent(
    api_key: str,
    openai_api_key: str,
    api_url: Optional[str] = None
) -> MarketSentimentAgent:
    """Create and start a market sentiment agent"""
    agent = MarketSentimentAgent(api_key, openai_api_key, api_url)
    await agent.start()
    return agent 