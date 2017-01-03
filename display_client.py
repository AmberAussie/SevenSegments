import socket
from settings import Settings


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP
    while True:
        msg = input('>')
        if msg == 'exit':  # as X is forbidden
            break
        sock.sendto(msg.encode(), (Settings.Server.ip, Settings.Server.port))
    print('closing...')
