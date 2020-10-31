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
                self.address = input('enter  Computer-name:')
            except:
                print("Cannot connect to Server")
                pass
            # start thread
            threading.Thread(target=self.recieve_server).start()
            self.encrypt_stream()
    def audio_recording(self):
        chunk_size = 1024
        audio_format = pyaudio.paInt16
        channels = 1
        rate = 20000
        seconds = 5
        filename = "myfile.wav"
        # initialising microphone recording
        print("recording has begun")
        p = pyaudio.PyAudio()
        play_stream = p.open(format=audio_format, channels=channels, rate=rate, output=True,
                                       frames_per_buffer=chunk_size)
        record_stream = p.open(format=audio_format, channels=channels, rate=rate, input=True,
                                         frames_per_buffer=chunk_size)
        frames = []
        for i in range(0, int(rate/chunk_size * seconds)):
            data = record_stream.write(1024)
            frames.append(data)
        print("okay, wait abit")
        record_stream.stop_stream()
        record_stream.close()
        p.terminate()
        wf= wave.open(filename, "wb")
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(audio_format))
        wf.setframerate(rate)
        wf.writeframes(b'' .join(frames))
        with open(filename, 'rb') as outFile:
            chunk = outFile.read(chunk_size)
        print("Recording completed please wait")
        return chunk


    def get_key(self):
        name=self.address
        salt = b"this is a salt"
        kdf = PBKDF2(name, salt, 16, 1000)
        key = kdf[:16]
        return key
    def recieve_server(self):
        while 1:
            try:
                tcpkey = self.get_key()
                json_input = self.s.recv(1024)
                b64 = loads(json_input)
                iv = b64decode(b64['iv'])
                ct = b64decode(b64['ciphertext'])
                cipher = AES.new(tcpkey, AES.MODE_CBC, iv=iv)
                pt = unpad(cipher.decrypt(ct), AES.block_size)

            except:
                pass

    def encrypt_stream(self):
        while 1:
            try:
                tcpkey=self.get_key()
                data=self.audio_recording()
                cipher = AES.new(tcpkey, AES.MODE_CBC)
                ct_bytes = cipher.encrypt(pad(data, AES.block_size))
                iv = b64encode(cipher.iv).decode('utf-8')
                ct = b64encode(ct_bytes).decode('utf-8')
                result = dumps({'iv': iv, 'ciphertext': ct})
                self.s.send(result.encode())
            except:
                pass




client=Client()
