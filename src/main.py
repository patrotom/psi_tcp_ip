#!/usr/bin/python3
'''Sample TCP/IP server'''
import socket
BUFFER_SIZE = 32

class Handler:
    def __init__(self, connection, client_address):
        '''Constructor'''
        self.connection = connection
        self.client_address = client_address
        self.raw_data = ''
        self.buffer = ''

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
        return False

    def EvaluateMessage(self, message):
        '''Method that is evaluating messages'''
        print(message)
        if message == 'close':
            return False
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
