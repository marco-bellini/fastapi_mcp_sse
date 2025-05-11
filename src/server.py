import uvicorn
import os
from app import app
import logging # Import logging

# Configure basic logging for the server
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



# Environment variable configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# # Ensure SECRET_KEY is set for JWT authentication
# SECRET_KEY = os.getenv("SECRET_KEY")
# if not SECRET_KEY:
#     logger.warning("SECRET_KEY environment variable not set. Using a default key (NOT secure for production!).")
#     # The default is set in auth.py, but emphasizing the warning here is good.


def run():
    """Start the FastAPI server with uvicorn"""
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")


if __name__ == "__main__":
    run()
