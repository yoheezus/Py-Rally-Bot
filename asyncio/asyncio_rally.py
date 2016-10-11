import asyncio
import logging
import sys
import time
import functools
"""
1. Functions to break down and re-assemble packets that need to be sent, into a more readable and editable format.
2. Creation of a socket to the right ip and port. Sending the right information at initialisation.
    - PORT: 443
    - IP: Changes between 3: (1) 208.85.93.114 (2) 208.85.93.164 (3) 208.85.93.149
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

# Block below is only necessary if running this file directly, else look in asyncio_main.py
SERVER_ADDRESS = ('208.85.93.114', 443)
GAIA_SSID = 'GAIA_SSID'
GAIA_ID = 'GAIA_ID'
GAIA_USERNAME = 'GAIA_USERNAME'
GAIA_AVATAR_URL = 'AVATAR_URL'
ROOM_ID = 'ROOM ID'

# Change xy coords to appear in a different place. Type debug in chat to find coords.
class RallyClient(asyncio.Protocol):
    def __init__(self, gaia55_sid, gaia_id, username, avatar_url, roomid, xy=('393', '932')):
        self.gaia55_sid = gaia55_sid
        self.gaia_id = gaia_id
        self.username = username
        self.avatar_url = avatar_url
        self.roomid = roomid
        self.xy1 = xy
        self.xy2 = ':'.join(xy)
        self.log = logging.getLogger('RallyClient')
        self.flashpack = ['S55', 'FLASH', 1, 0, 2, 48]
        self.timestamp = [29, 1, self.gaia_id, 3, '-' + str(time.time())[0:-8]]
        self.method45 = [45, 2, 1, 1, 1, '', self.gaia_id, 0, 0, 1, 'btn0', self.avatar_url, self.username, self.gaia_id, 0, 8, 0,
                   self.gaia55_sid, 0, 0]
        self.connected_users = {}

    def connection_made(self, transport):
        self.transport = transport
        self.transport.write(self.p_encode(['S55', 'FLASH', 1, 0, 2, 48]))
        self.log.debug('Sent: flash packet')
        asyncio.ensure_future(self.pingu())

    def data_received(self, data):
        ssid = ''
        self.data = self.p_decode(data.decode())
        for packet in self.data: # This foor loop allows us to go through each packet seperately. 

            if packet[0] == '1': # Packet 1 includes ssid, this retreives it.
                ssid += packet[1]
            elif packet[0] == '10':
                cmsg = packet[4]
                self.log.debug('(Chat) {!r}: {!r}'.format(self.connected_users[packet[1]], cmsg))
                #chat commands here
                #if cmsg == 'print':
                    #do something
            elif packet[0] == '7':
                self.log.debug('received: {!r}'.format(packet))
            elif packet[0] == '6': # Checks users already in room when joining
                self.add_to_userlist(packet)
                self.log.debug('Added User!')
            elif packet[0] == '21': # Checks User joining server/room packet
                    self.add_to_userlist(packet)
            elif packet[0] == '11': # Checks users leaving room/server
                self.add_to_userlist(packet)  # This function has a delete option too.
            else:
                None
                # self.log.debug('received: {!r}'.format(packet))
        if ssid:
            self.ssid = ssid 
            self.log.debug('SSID is: {!r}'.format(ssid))
            self.transport.write(self.p_encode(self.timestamp))
            self.log.debug('Sent time stamp.')
            self.transport.write(self.p_encode(self.method45))
            self.log.debug('Sent method 45')
            self.transport.write(self.p_encode([20, 3, ssid, self.roomid, '', self.xy1, 'left:front:0:0:3', 1, 'btn0', self.avatar_url, self.username, self.gaia_id,
                 '', 8, 0, 0, 0]))
            self.log.debug('Sent method 20.')
            self.transport.write(self.p_encode([53, 'updatePos:' + self.xy2 + ':dirRight:faceFront:0:0:0:normal:3', ssid, 1, self.roomid]))
            self.log.debug('Sent user content.')
            self.connected_users[ssid] = self.username  # Adds The bot user account to connected users list.

    def connection_lost(self, exc):
        print('server lost connection')
        print('stop the loop')

    def p_encode(self, packets):
        '''
            Encodes a list made up of the packet requirements into a real 'packet', to be sent,
             that will be accepted by server. By joining each element in list with appropriate control character usng .join.
            '''
        data = ''
        packet = [str(x) for x in packets]  # turns all non str into str
        for ky, vl in enumerate(packet):
            if isinstance(vl, list):  # if value is a list
                packet[ky] = '\x01'.join(vl)
        data += '\x02'.join(packet) + '\x03\x00'
        return data.encode()

    def p_decode(self, packets):
        '''
        Decodes a packet into a list, making it easy to edit. Does this by splitting
        by control characters.
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

    async def pingu(self):
        """
        Sends a ping packet to severs every 40 seconds. Stops disconnection.
        """
        await asyncio.sleep(40)
        log = logging.getLogger('Ping!')
        self.transport.write(self.p_encode([62, '']))
        log.debug('Pong!')
        asyncio.ensure_future(self.pingu())

    def add_to_userlist(self, me6): # This function deals with users joining / leaving room.
        if me6[0] == '6': #Adds user to dict when joining rally room.
            for x in me6:
                try:
                    self.connected_users[me6[1]] = me6[7]
                except IndexError:
                    print('ERROR: ', me6)
                    continue
        if me6[0] == '21' and me6[2] == self.roomid: # And statement checks if it's same room.
            try:
                self.connected_users[me6[1]] = me6[9]
                self.transport.write(self.p_encode(
                    [53, 'updatePos:' + self.xy2 + ':dirRight:faceFront:0:0:0:normal:3', self.ssid, 1, self.roomid])) # So Avatar
                # appears to new users who join the room
                self.log.debug('User {!r} joined room.'.format(self.connected_users[me6[1]])) 
            except IndexError:
                print('ERROR: ', me6)
        elif me6[0] == '21' and me6[3] == self.roomid:
            try:
                self.log.debug('User {!r} went to a different room.'.format(self.connected_users[me6[1]]))
                del self.connected_users[me6[1]]
            except KeyError:
                print('Something went wrong.')        

        if me6[0] == '11' and me6[3] == self.roomid: # And statement checks if its same room.
            try:
                self.log.debug('User {!r} left the room.'.format(self.connected_users[me6[1]]))
                del self.connected_users[me6[1]]
            except KeyError:
                print('Something went wrong')



if __name__ == '__main__':

    client_factory = functools.partial(RallyClient, GAIA_SSID, GAIA_ID, GAIA_USERNAME,
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

