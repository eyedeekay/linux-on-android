import struct
import socket
import threading
import os
import Queue

SOCKET_TIMEOUT = 1.
QUEUE_TIMEOUT = 1.
QUEUE_LENGTH = 1024
BUFFER_LENGTH = 1024
SOCKET_PATH = '/dev/socket/rild'

os.setgid(1001)
os.setuid(1001)

class RILDConnection:
    def __init__(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(SOCKET_PATH)
        self.sock.settimeout(SOCKET_TIMEOUT)

        self.input_queue = Queue.Queue(QUEUE_LENGTH)
        self.output_queue = Queue.Queue(QUEUE_LENGTH)

        self.stop = False

        self.receiver = threading.Thread(None, self.receive)
        self.receiver.start()
        self.sender = threading.Thread(None, self.send)
        self.sender.start()

    def receive(self):
        buffer = ''
        while not self.stop:
            while len(buffer)<4:
                try:
                    buffer += self.sock.recv(BUFFER_LENGTH)
                except socket.timeout:
                    if self.stop: 
                        return
            size, = struct.unpack('!i', buffer[:4])
            while len(buffer) < 4 + size:
                try:
                    buffer += self.sock.recv(1024)
                except socket.timeout:
                    if self.stop: 
                        return
            message = buffer[4:(4+size)]
            buffer = buffer[(4+size):]
            self.input_queue.put(message)


    def send(self):
        while not self.stop:
            try:
                message = self.output_queue.get(True, QUEUE_TIMEOUT)
            except Queue.Empty:
                continue
            buffer = struct.pack('!i', len(message))
            buffer += message
            pos = 0
            while pos<len(buffer):
                try:
                    pos += self.sock.send(buffer[pos:])
                except socket.timeout:
                    if self.stop: 
                        return
                        
    def close(self):
        self.stop = True
        self.sender.join()
        self.receiver.join()
        self.sock.close()


def example():        
    rild = RILDConnection()

    try:
        message = rild.input_queue.get()
        serial_no, message_type = struct.unpack('ii', message[:8])
        print 'Message #%d, type %d:' % (serial_no, message_type)
        message = message[8:]
        print 'Data:', message.__repr__()

        parcel = struct.pack('iiii', 23, 1, 1, 1)
        rild.output_queue.put(parcel)

        message = rild.input_queue.get()
        serial_no, message_type = struct.unpack('ii', message[:8])
        print 'Message #%d, type %d:' % (serial_no, message_type)
        message = message[8:]
        print 'Data:', message.__repr__()

        message = rild.input_queue.get(True, 1)
        serial_no, message_type = struct.unpack('ii', message[:8])
        print 'Message #%d, type %d:' % (serial_no, message_type)
        message = message[8:]
        print 'Data:', message.__repr__()

    finally:
        rild.close()

if __name__=='__main__':
    example()
