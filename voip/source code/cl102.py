import socket
import pyaudio
import threading
import wave
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad,unpad
from base64 import b64encode,b64decode
from json import dumps,loads

class Client:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        while 1:
            try:
                self.ip =input('enter server IP:')
                self.port=int(input('enter target port of server:'))
                print("Server ip:" + self.ip + "\nPort:" + str(self.port))
                self.s.connect((self.ip, self.port))
                break
            except:
                print("Cannot connect to Server")
            chunk_size = 1024
            audio_format = pyaudio.paInt16
            channels = 1
            rate = 20000
            seconds = 5
            print("Start talking")
            #initialising microphone recording
            self.p = pyaudio.PyAudio()
            self.play_stream=self.p.open(format=audio_format, channels=channels, rate=rate, output=True,
                                     frames_per_buffer=chunk_size)
            self.record_stream = self.p.open(format=audio_format, channels=channels, rate=rate, input=True,
                                       frames_per_buffer=chunk_size)
            print("Connected to server")
            # start thread
            threading.Thread(target=self.recieve_server).start()
            self.encrypt_stream()
    def recieve_server(self):
        while True:
            try:
                data = self.s.recv(1024)
                self.play_stream.write(data)
            except:
                pass


    def encrypt_stream(self):
        address = input('enter  name:')
        while 1:
            try:
                def get_key(address):
                    salt = b"this is a salt"
                    kdf = PBKDF2(address, salt, 16, 1000)
                    key = kdf[:16]
                    return key
                tcpkey=get_key(address)
                data = self.record_stream.read(1024)
                cipher = AES.new(tcpkey, AES.MODE_CBC)
                ct_bytes = cipher.encrypt(pad(data, AES.block_size))
                iv = b64encode(cipher.iv).decode('utf-8')
                ct = b64encode(ct_bytes).decode('utf-8')
                result = dumps({'iv': iv, 'ciphertext': ct})
                self.s.sendall(result.encode())
            except:
                print("audio sent")
                pass



class main():
    Client()
if __name__ == "__main__":
    main()