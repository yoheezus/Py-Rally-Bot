import asyncio
import functools

from asyncio_rally import RallyClient
from login import GaiaAuth

USERNAME = 'Yoheezus'
PASSWORD = 'FuceCombHibl0['
auth = GaiaAuth(USERNAME, PASSWORD)

SERVER_ADDRESS = ('208.85.93.114', 443)
ROOM_ID = '45002'

GAIA_SSID = auth.sid
GAIA_ID, GAIA_AVATAR_URL = auth.method107()
event_loop = asyncio.get_event_loop()

if __name__ == '__main__':

    client_factory = functools.partial(RallyClient, GAIA_SSID, GAIA_ID, USERNAME,
                                       GAIA_AVATAR_URL, ROOM_ID)
    # client_factory instantiates the RallyClient class. Due to use of Protocol style asyncio,
    # functools.partial must be used to pass arguments

    factory_coro = event_loop.create_connection(client_factory, *SERVER_ADDRESS)
    # Connects the instance to Event loop and the server socket. (Like sock.connect())
    try:
        event_loop.run_until_complete(factory_coro)
        # Loops until factory is done. Would shut down if client recieves no data
        # But run_forever() stops that
        event_loop.run_forever()
    except KeyboardInterrupt:
        pass

    finally:
        # cleanly stops the event loop and coroutine.
        factory_coro.close()
        event_loop.close()


