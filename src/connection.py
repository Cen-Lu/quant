import os
import time
import dotenv
from ib_async.ib import IB
from typing import Dict

dotenv.load_dotenv()

class IBKRConnection:
    """Synchronous IBKR connection manager with auto-reconnect"""

    def __init__(self):
        self.ib = IB()
        # Set connection details AFTER creating IB()
        self.ib.host = os.getenv("IB_HOST", "127.0.0.1")
        self.ib.port = int(os.getenv("IB_PORT", "7497"))
        self.ib.client_id = int(os.getenv("IB_CLIENT_ID", "1"))

        self.account = os.getenv("IB_ACCOUNT")
        self.connected = False

    def connect(self, retries: int = 3) -> bool:
        """Establish a synchronous connection with exponential backoff."""
        for attempt in range(retries):
            try:
                # .connect() in ib_async blocks until it finishes or raises an error
                self.ib.connect()
                self.connected = True
                print(f"✅ Connected to account: {self.account}")
                return True
            except ConnectionError as e:
                wait_time = 2 ** attempt
                print(f"⚠️ Connection failed (attempt {attempt+1}): Retrying in {wait_time}s")
                time.sleep(wait_time)
        return False

    def get_account_summary(self) -> Dict:
        """Fetch paper/live account summary (synchronous)."""
        if not self.connected:
            self.connect()
        return self.ib.get_account_summary()

    def safe_disconnect(self):
        """Graceful shutdown."""
        if self.connected:
            self.ib.disconnect()
            self.connected = False
            print("🔌 Disconnected from IBKR")
