#!/usr/bin/python3
'''Sample TCP/IP server'''
import socket
import _thread
import time

BUFFER_SIZE = 1024
SERVER_KEY = 54621
CLIENT_KEY = 45328

SERVER_SYNTAX_ERROR = '301 SYNTAX_ERROR\a\b'.encode()
SERVER_LOGIN_FAILED = '300 LOGIN FAILED\a\b'.encode()
SERVER_OK = '200 OK\a\b'.encode()
SERVER_MOVE = '102 MOVE\a\b'.encode()
SERVER_TURN_LEFT = '103 TURN LEFT\a\b'.encode()
SERVER_TURN_RIGHT = '104 TURN RIGHT\a\b'.encode()
SERVER_PICK_UP = '105 GET MESSAGE\a\b'.encode()
SERVER_LOGOUT = '106 LOGOUT\a\b'.encode()
SERVER_SYNTAX_ERROR = '301 SYNTAX ERROR\a\b'
SERVER_LOGIC_ERROR = '302 LOGIC ERROR\a\b'
CLIENT_RECHARGING = 'RECHARGING\a\b'
CLIENT_FULL_POWER = 'FULL POWER\a\b'

class Listener:
    '''Class which handles receiving the messages from a robot'''
    def __init__(self, connection):
        ''''Constructor'''
        self.connection = connection
        self.raw_data = ''
        self.buffer = ''
    
    def Listen(self):
        '''Method that reads data from the buffer'''
        while True:
            self.connection.settimeout(1)
            data = self.connection.recv(BUFFER_SIZE)
            if data:
                raw_data = data.decode('ascii')
                print('Received:', raw_data)
                self.buffer += raw_data
                return True
    
    def getMessage(self):
        '''Method that is parsing messages from the input buffer'''
        # Error handling: everywhere I am getting a message
        while True:
            message = self.buffer.partition('\a\b')
            if message[1]:
                self.buffer = message[2]
                print(message[0])
                if message[0] == CLIENT_RECHARGING:
                    self.rechargeRobot()
                else:
                    return message[0]
            if not self.Listen():
                return False
    
    def rechargeRobot(self):
        '''Method which will recharge our robot'''
        while True:
            self.connection.settimeout(1)
            data = self.connection.recv(BUFFER_SIZE)
            if data:
                raw_data = data.decode('ascii')
                self.buffer += raw_data
                message = self.buffer.partition('\a\b')
                if message[1]:
                    self.buffer = message[2]
                    if message[0] != CLIENT_FULL_POWER:
                        self.connection.sendall(SERVER_LOGIC_ERROR)
                        return False
                elif len(raw_data) >= 14:
                    self.connection.sendall(SERVER_SYNTAX_ERROR)
                    return False
            
class Authenticator:
    '''Class which handles authetication of a robot'''
    def __init__(self, name, connection):
        '''Constructor'''
        self.name = name
        self.connection = connection
        self.ascii_count = 0
        self.server_hash = None

    def validateName(self):
        '''Method which validates a name of a robot'''
        return len(self.name) <= 10

    def computeHash(self):
        '''Method which computes a hash from a name of a robot'''
        for i in range(0, len(self.name), 1):
            self.ascii_count += ord(self.name[i])
        self.server_hash = ((self.ascii_count * 1000) + SERVER_KEY) % 65536
        return self.server_hash
    
    def compareHash(self, client_hash):
        '''Method which compares hash on the server-side with hash on the client-side'''
        return (self.ascii_count * 1000 + CLIENT_KEY) % 65536 == int(client_hash)

class Mover:
    '''Class which handles moving of a robot'''
    def __init__(self, connection):
        '''Constructor'''
        self.connection = connection
        self.prev_coordinates = [999, 999]
        self.act_coordinates = [999, 1000]
        self.act_direction = 4
        self.desired_square = [2, 2]
        self.move_coeficient = 0

    def setCoordinates(self, message):
        '''Method which parses coordinates from the message'''
        tmp = message[3:].split(' ')
        self.prev_coordinates[0] = self.act_coordinates[0]
        self.prev_coordinates[1] = self.act_coordinates[1]
        self.act_coordinates[0] = int(tmp[0])
        self.act_coordinates[1] = int(tmp[1])

    def checkMoveSuccess(self):
        '''Method which checks whether a robot moved forward'''
        return self.act_coordinates != self.prev_coordinates

    def figureOutDirection(self):
        '''Method which determines a direction which is robot standing'''
        if self.act_coordinates[0] > self.prev_coordinates[0]:
            self.act_direction = 1
        elif self.act_coordinates[0] < self.prev_coordinates[0]:
            self.act_direction = 3
        elif self.act_coordinates[1] > self.prev_coordinates[1]:
            self.act_direction = 0
        elif self.act_coordinates[1] < self.prev_coordinates[1]:
            self.act_direction = 2

    def changeDirection(self):
        '''Method which change direction of a robot to one to the right'''
        if self.act_direction == 3:
            self.act_direction = 0
        else:
            self.act_direction += 1

    def selectMove(self):
        '''Method which returns desired move of our robot'''
        print('Coordinates:', self.act_coordinates[0], self.act_coordinates[1])
        print('Desired square:', self.desired_square[0], self.desired_square[1])
        if self.act_coordinates[1] > self.desired_square[1]:
            if self.act_direction != 2:
                self.changeDirection()
                return SERVER_TURN_RIGHT
            return SERVER_MOVE
        elif self.act_coordinates[1] < self.desired_square[1]:
            if self.act_direction != 0:
                self.changeDirection()
                return SERVER_TURN_RIGHT
            return SERVER_MOVE
        
        if self.act_coordinates[0] > self.desired_square[0]:
            if self.act_direction != 3:
                self.changeDirection()
                return SERVER_TURN_RIGHT
            return SERVER_MOVE
        elif self.act_coordinates[0] < self.desired_square[0]:
            if self.act_direction != 1:
                self.changeDirection()
                return SERVER_TURN_RIGHT
            return SERVER_MOVE

class Handler:
    '''Class which handles communication with a robot'''
    def __init__(self, connection, client_address):
        '''Constructor'''
        self.connection = connection
        self.client_address = client_address
        self.listener = Listener(self.connection)
        self.mover = Mover (self.connection)

    def Handle(self):
        '''Method which handles whole process of finding a secret message'''
        if not self.Authenticate():
            return
        self.initialMove()
        self.moveRobotToInnerSquare()
        if self.searchInnerSquare():
            self.connection.sendall(SERVER_LOGOUT)
            return
        
    def Authenticate(self):
        '''Method which handles authentication of a robot'''
        name = self.listener.getMessage()
        authenticator = Authenticator(name, self.connection)
        
        if not authenticator.validateName():
            self.connection.sendall(SERVER_SYNTAX_ERROR)
            return False

        self.connection.sendall((str(authenticator.computeHash()) + '\a\b').encode())

        client_hash = self.listener.getMessage()
        if client_hash > 5:
            self.connection.sendall(SERVER_SYNTAX_ERROR)
            return False
        if not authenticator.compareHash(client_hash):
            self.connection.sendall(SERVER_LOGIN_FAILED)
            return False
        
        self.connection.sendall(SERVER_OK)
        return True

    def initialMove(self):
        '''Method which performs initial move of a robot to compute initial coordinates'''
        init_cnt = 0
        while init_cnt < 2:
            self.connection.sendall(SERVER_MOVE)
            coordinates = self.listener.getMessage()
            if coordinates > 10:
                self.connection.sendall(SERVER_SYNTAX_ERROR)
                return False
            self.mover.setCoordinates(coordinates)
            if self.mover.checkMoveSuccess():
                init_cnt +=1
    
    def moveRobotToInnerSquare(self):
        '''Method will directs our robot to the desired coordinates in the inner square'''
        self.mover.figureOutDirection()
        while True:
            if self.mover.act_coordinates[0] == 2 and self.mover.act_coordinates[1] == 2:
                break
            self.connection.sendall(self.mover.selectMove())
            self.mover.setCoordinates(self.listener.getMessage())
    
    def turnRobot(self, direction):
        '''Method which will change direction of a robot to the left to prepare him for searching'''
        while True:
            if self.mover.act_direction != direction:
                self.mover.changeDirection()
                self.connection.sendall(SERVER_TURN_RIGHT)
                self.mover.setCoordinates(self.listener.getMessage())
            else:
                break

    def moveRobotForward(self):
        '''Method which will move a robot one field straight and checks whether a robot moved'''
        while True:
            self.connection.sendall(SERVER_MOVE)
            self.mover.setCoordinates(self.listener.getMessage())
            if self.mover.checkMoveSuccess():
                break

    def pickUpMessage(self, message):
        '''Method which will let a robot to try to pick up a message and will return True if the message is found'''
        if message != '':
            return True
        return False

    def searchInnerSquare(self):
        '''Method which will let a robot search the inner square'''
        # Need to figure out whether it is mandatory to keep asking if the robot is not moving
        self.connection.sendall(SERVER_PICK_UP)
        if self.pickUpMessage(self.listener.getMessage()):
            return True

        for i in range(0, 5, 1):
            if i != 0:
                self.turnRobot(2)
                self.moveRobotForward()
                self.connection.sendall(SERVER_PICK_UP)
                if self.pickUpMessage(self.listener.getMessage()):
                    return True
            if i == 0 or i == 2 or i == 4:
                self.turnRobot(3)
            elif i == 1 or i == 3:
                self.turnRobot(1)
            for _ in range(0, 4, 1):
                self.moveRobotForward()
                self.connection.sendall(SERVER_PICK_UP)
                if self.pickUpMessage(self.listener.getMessage()):
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
        c.Handle()
        connection.close()
main()
