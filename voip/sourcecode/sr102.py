import socket
import threading
import pyaudio
import wave
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import unpad
from base64 import b64decode
from json import loads


class Server:
    def handle_client(self, conn, addr):
        while 1:
            try:
                data = conn.recv(1024)
                chunk_size = 1024
                audio_format = pyaudio.paInt16
                channels = 1
                rate = 20000
                frames = []
                p = pyaudio.PyAudio()
                play_stream = p.open(format=audio_format, channels=channels, rate=rate, output=True,
                                     frames_per_buffer=chunk_size)
                i = 1
                while data != '':
                    data = conn.recv(1024)
                    play_stream.write(data)
                    i = i + 1
                    frames.append(data)
                    print(i)
                play_stream.stop_stream()
                play_stream.close()
                p.terminate()
                self.broadcast(conn, data)
            except socket.error:
                conn.close()
                print("Server session interrupted")
                self.__class__()
    def __init__(self):
        self.ip = socket.gethostbyname(socket.gethostname())
        self.port = int(input('Enter port number to run on --> '))
        print("Server ip:" + self.ip)
        while 1:
            try:
                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
                self.s.bind((self.ip, self.port))

                break
            except:
                print("Couldn't bind client")
                Server()
        self.connections = []
        self.accept_connections()

    def accept_connections(self):
        self.s.listen(2)
        print('waiting for connections...')
        while True:
            conn, addr = self.s.accept()
            print("Client: " + str(addr[0]) + " connected")
            self.connections.append(conn)
            threading.Thread(target=self.handle_client, args=(conn, addr)).start()

    def broadcast(self, sock, data):
        for client in self.connections:
            if client != self.s and client != sock:
                try:
                    client.send(data)
                except:
                    self.__class__()

if __name__ == '__main__':
    server = Server()
