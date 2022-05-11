import asyncio
import logging
import ssl
import sys
import certifi
import websockets
from transaction import Transaction

STREAM_ENDPOINT = "wss://mainnet.clana.io/transactions"
logging.basicConfig(level=logging.INFO)


class Watcher:
    def __init__(self, account: str = "") -> None:
        self._account = account
        self._ledger_state_version = self._load_last_state_version()

    def _load_last_state_version(self) -> int:
        # Can be used to load the last stored ledger state version of the last
        # received message from disk or database in case of a restart.
        # Default is 0 and is therefore syncing from the beginning.
        # Warning: different accounts need to have their own stored state version!
        return 0

    @property
    def _endpoint(self):
        uri = STREAM_ENDPOINT
        if self._account:
            uri += f"/{self._account}"
        return f"{uri}?state_version={self._ledger_state_version}"

    def _update_state_version(self, tx: Transaction):
        # Keep track of synced state version and check it’s incrementing (state version is global)
        if tx.transaction_status.ledger_state_version <= self._ledger_state_version:
            raise RuntimeError(
                f"ledger_state_version has decreased from {self._ledger_state_version} to {tx.transaction_status.ledger_state_version}"
            )
        logging.getLogger("Watcher").debug(
            f"Incrementing ledger state version to {tx.transaction_status.ledger_state_version}"
        )
        self._ledger_state_version = tx.transaction_status.ledger_state_version

    async def watch(self):
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.load_verify_locations(certifi.where())
        connect = websockets.connect(self._endpoint, ssl=ssl_context)
        logging.info(f"Connecting to {self._endpoint}")
        async for websocket in connect:
            try:
                await self.message_handler(websocket)
            except websockets.ConnectionClosed:
                logging.error(
                    f"Websocket disconnected, reconnecting to {self._endpoint}..."
                )
                connect.handle_redirect(self._endpoint)
                continue

    async def message_handler(self, websocket):
        while True:
            message = await websocket.recv()
            tx = Transaction.from_json(message)
            self._update_state_version(tx)
            await self.transaction_handler(tx)

    async def transaction_handler(self, transaction: Transaction):
        logging.info(transaction)


def main(account: str):
    watcher = Watcher(account=account)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    task = loop.create_task(watcher.watch())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        task.cancel()


if __name__ == "__main__":
    argv = sys.argv[1:]
    account = argv[0] if argv else ""
    main(account)
