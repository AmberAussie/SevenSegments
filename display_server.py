import socket
from simple7seg import Simple7SegAsnyc, driver, TextAnim

UDP_IP = "127.0.0.1"
UDP_PORT = 45454


class Server(Simple7SegAsnyc):
    TIMEOUT = 0.5

    def __init__(self, drv: driver.Driver_7Seg, ip, port):
        self.sock = socket.socket(socket.AF_INET,  # Internet
                                  socket.SOCK_DGRAM)  # UDP
        self.sock.bind((ip, port))
        self.sock.settimeout(Server.TIMEOUT)
        self.txt = ''
        super(Server, self).__init__(drv)

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
    drv = driver.SerialDriver_7Seg(('COM4', 9600))
    srv = Server(drv, UDP_IP, UDP_PORT)

    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP
    try:
        while True:
            msg = input('>')
            sock.sendto(msg.encode(), (UDP_IP, UDP_PORT))
    except KeyboardInterrupt:
        pass
    srv.join(2)
