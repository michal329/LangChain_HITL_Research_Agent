import subprocess
import sys
from utils.logger import get_logger

logger = get_logger(__name__)

def main():
    """
    Main entrypoint to run the Sage B/C Research Assistant application.
    """
    logger.info("Initializing and launching Sage B/C Research Assistant...")
    try:
        # Launch Streamlit app.py programmatically
        subprocess.run(["streamlit", "run", "app.py"], check=True)
    except KeyboardInterrupt:
        logger.info("Application stopped by user.")
    except Exception as e:
        logger.error(f"Failed to launch application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
