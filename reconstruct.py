import socket
import threading
import time

"""
1. Functions to break down and re-assemble packets that need to be sent, into a more readable and editable format.
2. Creation of a socket to the right ip and port. Sending the right information at initialisation.
    - PORT: 443
    - IP: Changes between 3: (1) 208.85.93.114 (2) ? (3) ?
    - Gaia info needed: gaia55_sid, gaia_id, username, avatar_url, roomid, xy coords (Needed for positioning in rally).
            * Room id and IP can be found by 'toggle ip' and xy coord can be found in 'debug' commands in rally
3. Packets must be sent in a certain order to connect: FLASH VERSION. TIMESTAMP CONNECTION AND GAIA ID (Method 29)
    and METHOD 45: gid, btno, ava, username, gid.
5. The responses from the 3 packets will allow us to determine other information, such as rally server session id.
6. Packet method 20 (joining the room) will allow to connect after receiving all the information.
"""


class Rally():
    def __init__(self, ip, gaia55_sid, gaia_id, username, avatar_url, roomid, xy=('390', '615')):
        self.roomid = roomid
        self.xy = ':'.join(xy) # Joins coords into 1 string
        # ^-- coord useable --^

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, 443))
        # ^-- Creates and also connects to the socket on given IP address --^

        # v-- Beginning first establishing connection to server by sending 3 packets. --v
        self.send(['S55', 'FLASH', 1, 0, 2, 48])
        self.send([29, 1, gaia_id, 3, str(time.time())[0:-8]])
        self.send([45, 2, 1, 1, 1, '', gaia_id, 0, 0, 1, 'btn0', avatar_url, username, gaia_id, 0, 8, 0,
                                 gaia55_sid, 0, 0]) # Joins the server but not room

        self.ssid = self.p_decode(self.read())[0][1]
        # self.ssid = self.read().split('\x02')[1] # Reads the socket after sending packet 45, splits and reads list
        # to get the server session id

        self.send([20, 3, self.ssid, roomid, '', self.xy, 'left:front:0:0:3', 1, 'btn0', avatar_url, username, gaia_id,
                   '', 8, 0, 0, 0])  # ^-- This joins me to a rom within the server.--^

        self.send([53, 'updatePos:' + self.xy + ':dirRight:faceFront:0:0:0:normal:3', self.ssid, 1, roomid])

        threading.Timer(10.0, self.pingu).start()

        while True:
            data = self.read()
            data = (self.p_decode(data))
            print(data)


            '''
            if data[0][0] == '10':
                if data[0][4] == 'follow':
                    print(data)
                    self.follow(data)
                elif data[0][4] == 'stop':
                    self.send([53, 'updatePos:' + '400:600' + ':dirRight:faceFront:0:0:0:normal:3', self.ssid, 1, roomid])'''



    def p_encode(self, packets):
        '''
        Encodes a list made up of the packet requirements into a real 'packet', to be sent,
         that will be accepted by server. By joining each element in list with appropriate control character usng .join.
        '''
        data = ''
        packet = [str(x) for x in packets] # turns all non str into str
        for ky, vl in enumerate(packet):
            if isinstance(vl, list): # if value is a list
                packet[ky] = '\x01'.join(vl)
        data += '\x02'.join(packet) + '\x03'
        data += '\x00'
        return data


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

    def send(self, data):
        self.sock.send(self.p_encode(data).encode('utf-8'))

    def read(self):
        packet = ''
        #while True:
        data = self.sock.recv(4096).decode()
        packet += data
        return packet

    def pingu(self):
        self.send([62, ''])  # Send ping packet

    def follow(self, data):
        who_to_follow = '3211'
        if data[0][0] == '53':
            if data[0][2] == who_to_follow:
                # if data[0][3] == '8160':
                print(data)
                return self.send([data[0][0], data[0][1], self.ssid, '1', self.roomid])

    def chat(self):
        pass
        #self.send([10, self.ssid, 1, msg])

if __name__ == '__main__':

    test2 = 'S55\x02FLASH\x021\x020\x032\x0248\x03\x00'
    test3 = 'S55\x02FLASH\x021\x020\x022\x0248\x03\x00'

    ip = '208.85.93.114'
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, 443))







