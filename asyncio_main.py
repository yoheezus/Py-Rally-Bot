import asyncio
import functools

from asyncio_rally import RallyClient
from login import GaiaAuth

USERNAME = 'Yoheezus'
PASSWORD = 'MyPass'
SERVER_ADDRESS = ('208.85.93.114', 443)
GAIA_ID = '36931745'
GAIA_AVATAR_URL = 'ava/a1/88/32c19cd223388a1_M_6.00_11_1465590975'
ROOM_ID = '45002'

auth = GaiaAuth(USERNAME, PASSWORD)

GAIA_SSID = auth.sid
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


