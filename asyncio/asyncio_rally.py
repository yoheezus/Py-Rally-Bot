import asyncio
import logging
import sys
import time
import functools
"""
1. Functions to break down and re-assemble packets that need to be sent, into a more readable and editable format.
2. Creation of a socket to the right ip and port. Sending the right information at initialisation.
    - PORT: 443
    - IP: Changes between 3: (1) 208.85.93.114 (2) 208.85.93.164 (3) ?
    - Gaia info needed: gaia55_sid, gaia_id, username, avatar_url, roomid, xy coords (Needed for positioning in rally).
            * Room id and IP can be found by 'toggle ip' and xy coord can be found in 'debug' commands in rally
3. Packets must be sent in a certain order to connect: FLASH VERSION. TIMESTAMP CONNECTION AND GAIA ID (Method 29)
    and METHOD 45: gid, btno, ava, username, gid.
5. The responses from the 3 packets will allow us to determine other information, such as rally server session id.
6. Packet method 20 (joining the room) will allow to connect after receiving all the information.
GAIA ID CAN BE FOUND IN PROFILE LINK
ALL INFO CAN BE GOTTEN FROM http://gaiaonline.com/chat/gsi/index.php?v=json&m=[[102,[GAIA ID GOES HERE]]]
"""


logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s: %(message)s',
    stream=sys.stderr
)
log = logging.getLogger('main')
event_loop = asyncio.get_event_loop()

SERVER_ADDRESS = ('IP_ADDR', 443)
GAIA_SSID = 'GAIA SSID'
GAIA_ID = 'GAIA USER ID'
GAIA_USERNAME = 'USERNAME'
GAIA_AVATAR_URL = 'AVATAR URL'
ROOM_ID = 'ROOM ID' # Get this by typing 'toggle ip' in Rally

clients = [] # This is for the input. 

# If you want a different starting position, change COORDS. use 'debug' in rally to see Coords.
class RallyClient(asyncio.Protocol):
    def __init__(self, gaia55_sid, gaia_id, username, avatar_url, roomid, xy=('360', '610')):
        self.gaia55_sid = gaia55_sid
        self.gaia_id = gaia_id
        self.username = username
        self.avatar_url = avatar_url
        self.roomid = roomid
        self.xy1 = xy
        self.xy2 = ':'.join(xy)
        self.log = logging.getLogger('RallyClient')
        self.flashpack = ['S55', 'FLASH', 1, 0, 2, 48] # Sends flash version info (NOT EVEN USED)
        self.timestamp = [29, 1, self.gaia_id, 3, str(time.time())[0:-8]] # Sends a timestamp to server
        self.method45 = [45, 2, 1, 1, 1, '', self.gaia_id, 0, 0, 1, 'btn0', self.avatar_url, self.username, self.gaia_id, 0, 8, 0,
                   self.gaia55_sid, 0, 0] # joins the rally server, but not a room.

    def connection_made(self, transport):
        # Connection made triggers once, when connection is established after event_loop.create_connection
        self.transport = transport
        self.transport.write(self.p_encode(['S55', 'FLASH', 1, 0, 2, 48])) # Encodes flash packet.
        self.log.debug('Sent: flash packet')
        asyncio.ensure_future(self.pingu()) # Starts the ping sending loop. (Not quite sure how this works)
        
        clients.append(self) # Appends instance to clients. Used for input

    def data_received(self, data):
        # Everytime data is received this is called.
        ssid = '' # SSID named here for the check
        self.data = self.p_decode(data.decode()) # Decode the data from bytes into a list. easier to read / format
        if self.data[0][0] == '1': # First packet will be holding the ssid, it's method 1, so this checks for 1 as the first item.
            ssid += self.data[0][1] # Sets your gaia rally session id, different to your GAIA_SSID
        elif self.data[0][0] == '10': # If packet method is 10, indicates a chat message
            self.log.debug('Chat: {!r}'.format(self.data[0][4]))
        else:
            None
            # self.log.debug('received: {!r}'.format(self.data)) # Prints to cmdline the data, is annoying at the moment. Feel free to remove.
        # Below this line the rest of the packets for the initial connection handshake are sent. Some require the rally ssid
        # Which is why we check it has its value. All Debug messages are just for user clarification.
        if ssid:
            self.ssid = ssid
            self.log.debug('SSID is: {!r}'.format(ssid))
            self.transport.write(self.p_encode(self.timestamp))
            self.log.debug('Sent time stamp.')
            self.transport.write(self.p_encode(self.method45))
            self.log.debug('Sent method 45')
            self.transport.write(self.p_encode([20, 3, ssid, self.roomid, '', self.xy1, 'left:front:0:0:3', 1, 'btn0', self.avatar_url, self.username, self.gaia_id,
             '', 8, 0, 0, 0])) # Connects to the room within rally server.
            self.log.debug('Sent method 20.')
            self.transport.write(self.p_encode([53, 'updatePos:' + self.xy2 + ':dirRight:faceFront:0:0:0:normal:3', ssid, 1, self.roomid]))
            self.log.debug('Sent user content.') # This packet makes your avatar appear in rally.
    
    def send_chat(self, text):
        chat_pack = self.p_encode([10, self.ssid, 1, self.roomid, text])
        self.transport.write(chat_pack)
        log.debug('{!r} Sent: {!r}'.format(self.ssid, text))
        
    def connection_lost(self, exc):
        print('server lost connection')
        print('stop the loop')

    def p_encode(self, packets):
        '''
            Encodes a list made up of the packet requirements into a real 'packet', to be sent,
             that will be accepted by server. By joining each element in list with appropriate control character usng .join.
             EG. ['S55', 'FLASH', 1, 0, 2, 48] into b'S55\x02FLASH\x021\x020\x022\x0248\x03\x00'
            '''
        data = ''
        packet = [str(x) for x in packets]  # turns all non str into str
        for ky, vl in enumerate(packet):
            if isinstance(vl, list):  # if value is a list
                packet[ky] = '\x01'.join(vl)
        data += '\x02'.join(packet) + '\x03'
        data += '\x00'
        return data.encode()

    def p_decode(self, packets):
        '''
        Decodes a packet into a list, making it easy to edit. Does this by splitting
        by control characters.
        EG. b'S55\x02FLASH\x021\x020\x022\x0248\x03\x00' into ['S55', 'FLASH', 1, 0, 2, 48]
        '''
        data = []
        transmission = packets.split('\x00')
        for packet in transmission:
            packets = packet.split('\x03')
            for part in packets:
                if part:
                    thing = part.split('\x02')
                    for ky, vl in enumerate(thing):
                        if '\x01' in vl:
                            thing[ky] = vl.split('\x01')

                    data.append(thing)
        return data

    async def pingu(self): # Sends a ping packet to keep connection to rally alive.
        await asyncio.sleep(40)
        log = logging.getLogger('Ping!')
        self.transport.write(self.p_encode([62, '']))
        log.debug('Pong!')
        asyncio.ensure_future(self.pingu())
        
async def send_from_stdin(loop):
    while True:
        send_msg = await loop.run_in_executor(None, input, "Chat >")
        for client in clients:
            client.send_chat(send_msg)

if __name__ == '__main__':
    
    client_factory = functools.partial(RallyClient, GAIA_SSID, GAIA_ID, GAIA_USERNAME,
                      GAIA_AVATAR_URL, ROOM_ID)
    # client_factory instantiates the RallyClient class. Due to use of Protocol style asyncio,
    # functools.partial must be used to pass arguments
    # Connects the instance to Event loop and the server socket. (Like sock.connect())
        factory_coro = event_loop.create_connection(client_factory, *SERVER_ADDRESS)
    # Connects the instance to Event loop and the server socket. (Like sock.connect())

    try:
        event_loop.run_until_complete(factory_coro)
        # Loops until factory is done. Would shut down if client recieves no data
        # But run_forever() stops that
        asyncio.ensure_future(send_from_stdin(event_loop))
        event_loop.run_forever()
    except KeyboardInterrupt:
        pass

    finally:
        # cleanly stops the event loop and coroutine.
        factory_coro.close()
        event_loop.close()

