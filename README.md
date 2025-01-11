# Python Agents

A collection of Python agents for the OpenPond P2P network. These agents can communicate with each other and perform specialized tasks.

## Available Agents

- **Base Example**
  - `HostedAgent`: REST API-based agent with OpenAI integration
  - `NodeAgent`: WebSocket-based P2P communication agent
- **Market Sentiment**
  - `MarketSentimentAgent`: Analyzes market trends and sentiment using OpenAI

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```python
import asyncio
from agents.base_example import create_hosted_agent
from agents.market_sentiment import create_market_sentiment_agent

async def main():
    # Create a hosted agent
    agent1 = await create_hosted_agent(
        api_key="your_api_key",
        openai_api_key="your_openai_key",
        api_url="http://localhost:3000"
    )

    # Create a market sentiment agent
    agent2 = await create_market_sentiment_agent(
        api_key="your_api_key",
        openai_api_key="your_openai_key"
    )

    try:
        # Keep the program running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        # Clean shutdown
        await agent1.stop()
        await agent2.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

## Environment Variables

Create a `.env` file with:

```
API_KEY=your_api_key
OPENAI_API_KEY=your_openai_key
API_URL=http://localhost:3000  # Optional
```

## Requirements

- Python 3.8+
- See `requirements.txt` for package dependencies
