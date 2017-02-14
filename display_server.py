#!/usr/bin/env python3
import socket
from simple7seg import Simple7Seg, TextAnim


class Server(Simple7Seg):
    TIMEOUT = 0.5

    def __init__(self, settings):
        self.sock = socket.socket(socket.AF_INET,  # Internet
                                  socket.SOCK_DGRAM)  # UDP
        self.sock.bind((settings.Server.ip, settings.Server.port))
        self.sock.settimeout(Server.TIMEOUT)
        super(Server, self).__init__(settings.Driver)
        self.print_anim([TextAnim('LISTEN on '+str(settings.Server.port))])

    def process(self):
        try:
            data, addr = self.sock.recvfrom(1024)  # buffer size is 1024 bytes
            msg = data.decode()
            print("\n<", addr, ":", msg)
            self.print_anim([TextAnim(msg)])
        except socket.timeout:
            pass
        super(Server, self).process()

if __name__ == '__main__':
    from settings import Settings

    srv = Server(Settings)
    while True:
        srv.process()
