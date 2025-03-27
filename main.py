import asyncio

from ib_async import *


async def main():

    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=1)
    print(await ib.reqCurrentTime())

if __name__ == "__main__":
    asyncio.run(main())

