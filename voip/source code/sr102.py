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
                self.s.listen(2)
                print('waiting for connections...')
                conn, addr = self.s.accept()
                print("Client: " + str(addr[0]) + " connected")
                threading.Thread(target=self.handle_client,args=(conn,addr,)).start()
                break
            except:
                print("Couldn't bind client")
                main()
    def handle_client(self,conn,addr):
        while 1:
            try:
                data=conn.recv(1024)
            except socket.error:
                conn.close()
                main()


class main:
    Server()
if __name__ == "__main__":
    main()
