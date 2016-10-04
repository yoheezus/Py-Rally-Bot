import asyncio
import logging
import sys
import time
import functools

SERVER_ADDRESS = ('208.85.93.164', 443)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s: %(message)s',
    stream=sys.stderr
)
log = logging.getLogger('main')
event_loop = asyncio.get_event_loop()
gaia_ssid = 'rbbecmqxho7da7a0643b42cb10s82ykdy2m4meocwzfxf1g8'


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
        self.flashpack = ['S55', 'FLASH', 1, 0, 2, 48]
        self.timestamp = [29, 1, self.gaia_id, 3, str(time.time())[0:-8]]
        self.method45 = [45, 2, 1, 1, 1, '', self.gaia_id, 0, 0, 1, 'btn0', self.avatar_url, self.username, self.gaia_id, 0, 8, 0,
                   self.gaia55_sid, 0, 0]

    def connection_made(self, transport):
        self.transport = transport
        self.transport.write(self.p_encode(['S55', 'FLASH', 1, 0, 2, 48]))
        self.log.debug('Sent: flash packet')
        asyncio.ensure_future(self.pingu())

    def data_received(self, data):
        ssid = ''
        self.data = self.p_decode(data.decode())
        if self.data[0][0] == '1':
            ssid += self.data[0][1]
        elif self.data[0][0] == '10':
            self.log.debug('Chat: {!r}'.format(self.data[0][4]))
        else:
            self.log.debug('received: {!r}'.format(self.data))
        if ssid:
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
        data += '\x02'.join(packet) + '\x03'
        data += '\x00'
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
        await asyncio.sleep(40)
        log = logging.getLogger('Ping!')
        self.transport.write(self.p_encode([62, '']))
        log.debug('Pong!')
        asyncio.ensure_future(self.pingu())

client_completed = asyncio.Future()
client_factory = functools.partial(RallyClient, gaia_ssid, '36931745', 'Yoheezus',
              'ava/a1/88/32c19cd223388a1_M_6.00_11_1465590975', '15731')
factory_coro = event_loop.create_connection(client_factory, *SERVER_ADDRESS)
try:
    event_loop.run_until_complete(factory_coro)
    event_loop.run_forever()
except KeyboardInterrupt:
    pass

finally:
    factory_coro.close()
    event_loop.close()

