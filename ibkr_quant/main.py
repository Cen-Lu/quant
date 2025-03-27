import os
import time
from dotenv import load_dotenv
from ib_insync import *
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('IBKR Quant')

class IBKRQuant:
    def __init__(self):
        self.ib = IB()
        self.connected = False
        load_dotenv()
        self.account = os.getenv('IB_ACCOUNT')
        
    def connect(self, retries: int = 3) -> bool:
        """Connect to IBKR TWS/Gateway with auto-reconnect"""
        for attempt in range(retries):
            try:
                host = os.getenv('IB_HOST', '127.0.0.1')
                port = int(os.getenv('IB_PORT', 7497))
                client_id = int(os.getenv('IB_CLIENT_ID', 1))
                
                self.ib.connect(host, port, clientId=client_id)
                self.connected = True
                logger.info(f"Successfully connected to IBKR (Account: {self.account})")
                return True
            except Exception as e:
                wait_time = 2 ** attempt
                logger.error(f"Connection failed (attempt {attempt+1}): {str(e)}. Retrying in {wait_time}s")
                time.sleep(wait_time)
        return False

    def get_account_summary(self):
        """Get account summary information"""
        if not self.connected:
            self.connect()
        return self.ib.accountSummary()

    def disconnect(self):
        """Gracefully disconnect from IBKR"""
        if self.connected:
            self.ib.disconnect()
            self.connected = False
            logger.info("Disconnected from IBKR")

if __name__ == "__main__":
    bot = IBKRQuant()
    if bot.connect():
        print("Connection successful!")
        print("Account Summary:", bot.get_account_summary())
    else:
        print("Connection failed")
