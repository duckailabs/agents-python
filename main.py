from abc import ABC, abstractmethod
from typing import Dict, Type


class BaseAgent(ABC):
    """Base class for all agents"""
    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def handle_message(self, message: dict):
        pass

from agents.market_sentiment.agent import MarketSentimentAgent
from agents.with_distributed.agent import DistributedAgent
from agents.with_turnkey.agent import TurnkeyAgent

# Import all agent implementations
from agents.base_example.hosted import HostedAgent
from agents.base_example.node import NodeAgent

# Export all agents
__all__ = [
    'BaseAgent',
    'HostedAgent',
    'NodeAgent',
    'MarketSentimentAgent',
    'DistributedAgent',
    'TurnkeyAgent'
]
