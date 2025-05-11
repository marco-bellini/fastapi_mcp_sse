import asyncio
import logging
import mcp

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print(mcp.__file__)

from mcp_agent.core.fastagent import FastAgent

# Create the application
fast = FastAgent("fast-agent example")


# Define the agent
@fast.agent(name="WeatherForecaster", instruction="You are a helpful AI Agent", servers=["weather"])
async def main():
    # use the --model command line switch or agent arguments to change model
    logger.debug("Starting WeatherForecaster agent")
    async with fast.run() as agent:
        logger.debug("Agent running in interactive mode")
        await agent.interactive()


if __name__ == "__main__":
    logger.debug("Starting main application")
    asyncio.run(main())
