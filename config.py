# config.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# IB API connection parameters
IB_CONFIG = {
    "host": os.getenv("IB_HOST", "127.0.0.1"),
    "port": int(os.getenv("IB_PORT", 4002)),
    "client_id": int(os.getenv("IB_CLIENT_ID", 1))
}

# Other configuration settings can be added here.