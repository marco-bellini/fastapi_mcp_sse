import uvicorn
import os
from weather_app import app
import logging  # Import logging
import argparse  # Import argparse for command-line arguments

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
    logger.debug("Starting argument parser for SSL options.")
    parser = argparse.ArgumentParser(
        description="Run the FastAPI server with optional SSL configuration."
    )
    parser.add_argument("--ssl-keyfile", type=str, help="Path to the SSL key file.")
    parser.add_argument(
        "--ssl-certfile", type=str, help="Path to the SSL certificate file."
    )
    args = parser.parse_args()

    logger.info(f"Launching FastAPI server on {HOST}:{PORT} (SSL: key={args.ssl_keyfile}, cert={args.ssl_certfile})")
    try:
        uvicorn.run(
            app,
            host=HOST,
            port=PORT,
            log_level="info",
            ssl_keyfile=args.ssl_keyfile,
            ssl_certfile=args.ssl_certfile,
        )
        logger.info("Uvicorn server started successfully.")
    except Exception as e:
        logger.exception(f"Failed to start Uvicorn server: {e}")


if __name__ == "__main__":
    logger.debug("__main__ entrypoint reached. Calling run().")
    run()
