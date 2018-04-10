#!/usr/bin/python3
"""Sample TCP/IP server"""
import socket
BUFFER_SIZE = 32
# Spravy mozu byt odosielane naraz, nemusi prist cela sprava naraz, takze sa musim vzdy pozerat na validnu spravu pomocou delimiterov. Rozdelit si logiku na viac vrstiev a oddelit si prijmanie rechargingu a dalsich 3 typov sprav od klienta.
def login(connection, client_address):
    """Function which authenticates a new robot"""
    msg_count = 0
    while True:
        data = connection.recv(16)
        raw_data = data.decode('ascii')
        
        print('Received:', raw_data)

        if data:
            print('Sending data back to the client...')
            connection.sendall(data)
        else:
            print('No data from:', client_address)
            break
        

def main():
    """Sample TCP/IP connection from server side"""

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the port
    server_address = ('localhost', 10000)
    print('Starting up on {}, port: {}'.format(*server_address))
    sock.bind(server_address)

    # Listen for incoming connections
    sock.listen(1)

    while True:
        # Wait for a connection
        print('Waiting for a connection...')
        connection, client_address = sock.accept()
        login(connection, client_address)
        # Clean up the connection
        connection.close()
main()
