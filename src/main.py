#!/usr/bin/python3
'''Sample TCP/IP server'''
import socket
BUFFER_SIZE = 32
SERVER_KEY = 54621
CLIENT_KEY = 45328

class Authenticator:
    '''Class which handles authetication of a robot'''
    def __init__(self, name, connection):
        '''Constructor'''
        self.name = name
        self.connection = connection
    
    def Handle(self):
        if not self.ValidateName():
            return False
        my_hash = self.ComputeHash()
        

    def ValidateName(self):
        '''Method which validates a name of a robot'''
        if len(self.name) > 10:
            return False
        return True

    def ComputeHash(self):
        '''Method which computes a hash from a name of a robot'''
        ascii_count = 0
        for i in range(0, len(self.name), 1):
            ascii_count += ord(name[i])
        tmp = (ascii_count * 1000) % 65536
        return (tmp + SERVER_KEY) % 65536
# Bude potrebne oddelit logiku prijmania sprav ako od handlera, tak od autentifikatora kvoli prijmaniu sprav z viacerych miest v kode!
class Handler:
    '''Class which handles communication with a robot'''
    def __init__(self, connection, client_address):
        '''Constructor'''
        self.connection = connection
        self.client_address = client_address
        self.raw_data = ''
        self.buffer = ''
        self.msg_count = 0

    def Listen(self):
        '''Method that reads data from the buffer'''
        while True:
            data = self.connection.recv(BUFFER_SIZE)
            
            if data:
                raw_data = data.decode('ascii')
                print('Received:', raw_data)
                self.buffer += raw_data
            if not self.Parse():
                break
    
    def Parse(self):
        '''Method that is parsing messages from the input buffer'''
        message = self.buffer.partition('\\a\\b')
        if message[1]:
            self.buffer = message[2]
            return self.EvaluateMessage(message[0])
        elif message[0] == 'close':
            print('closing...')
            return False
        else:
            return True

    def EvaluateMessage(self, message):
        '''Method that is evaluating messages'''
        print(message)
        if self.msg_count == 0:


        return True

def main():
    '''Sample TCP/IP connection from server side'''
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = ('localhost', 10000)
    print('Starting up on {}, port: {}'.format(*server_address))
    sock.bind(server_address)

    sock.listen(1)

    while True:
        print('Waiting for a connection...')
        connection, client_address = sock.accept()
        c = Handler(connection, client_address)
        c.Listen()
        connection.close()
main()
