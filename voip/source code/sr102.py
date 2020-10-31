import socket
import threading
import pyaudio
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import unpad
from base64 import b64decode
from json import loads

class Server:
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


    def handle_client(self,conn,addr):
        address=input("Enter computer name: ")
        while 1:
            try:
                def get_key(address):
                    salt = b"this is a salt"
                    kdf = PBKDF2(address, salt, 16, 1000)
                    key = kdf[:16]
                    return key
                tcpkey = get_key(address)
                json_input = self.s.recv(1024)
                b64 = loads(json_input)
                iv = b64decode(b64['iv'])
                ct = b64decode(b64['ciphertext'])
                cipher = AES.new(tcpkey, AES.MODE_CBC, iv=iv)
                pt = unpad(cipher.decrypt(ct), AES.block_size)
            except socket.error:
                conn.close()



server=Server()

