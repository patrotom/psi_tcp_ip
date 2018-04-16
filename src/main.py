#!/usr/bin/python3
'''Sample TCP/IP server'''
import socket
BUFFER_SIZE = 32
SERVER_KEY = 54621
CLIENT_KEY = 45328

SERVER_SYNTAX_ERROR = "301 SYNTAX_ERROR\\a\\b".encode()
SERVER_LOGIN_FAILED = "300 LOGIN FAILED\\a\\b".encode()
SERVER_OK = "200 OK\\a\\b".encode()

class Authenticator:
    '''Class which handles authetication of a robot'''
    def __init__(self, name, connection):
        '''Constructor'''
        self.name = name
        self.connection = connection
        self.message_count = 0
        self.my_hash = None
        self.ascii_count = 0
    
    def Handle(self, client_hash = None):
        '''Method which directly handles authentication of a robot using other member methods'''
        if client_hash is None:
            if not self.ValidateName():
                self.connection.sendall(SERVER_SYNTAX_ERROR)
                return False
            self.my_hash = self.ComputeHash()
            self.connection.sendall(str(self.my_hash).encode())
            return True
        else:
            tmp = (self.ascii_count * 1000 + CLIENT_KEY) % 65536
            if tmp != int(client_hash):
                self.connection.sendall(SERVER_LOGIN_FAILED)
                return False
            else:
                self.connection.sendall(SERVER_OK)
                return True

    def ValidateName(self):
        '''Method which validates a name of a robot'''
        if len(self.name) > 10:
            return False
        return True

    def ComputeHash(self):
        '''Method which computes a hash from a name of a robot'''
        for i in range(0, len(self.name), 1):
            self.ascii_count += ord(self.name[i])
        tmp = (self.ascii_count * 1000) % 65536
        return (tmp + SERVER_KEY) % 65536

class Handler:
    '''Class which handles communication with a robot'''
    def __init__(self, connection, client_address):
        '''Constructor'''
        self.connection = connection
        self.client_address = client_address
        self.raw_data = ''
        self.buffer = ''
        self.init_count = 0
        self.move_count = 0
        self.auth = Authenticator(None, None)

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
        if self.init_count < 2:
            if self.init_count == 0:
                self.auth.name = message
                self.auth.connection = self.connection
                self.init_count += 1
                return self.auth.Handle()
            self.init_count += 1
            return self.auth.Handle(message)
        elif message == "close":
            return False
        return True

def main():
    '''Main of the program'''
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
