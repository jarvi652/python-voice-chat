import socket,OpenSSL
import pyaudio
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad,unpad
from base64 import b64encode,b64decode
from pickle import dumps,loads
from json import dumps,loads
import wave
import threading

def clientServer(protocol):
    ip = socket.gethostbyname(socket.gethostname())
    port = int(input('Enter port number to run on --> '))
    print("Server ip:" + ip)
    if(protocol == 2):
        MACaddress = input('enter MACaddress:')
        def get_key(MACaddress):
            salt = b"this is a salt"
            kdf = PBKDF2(MACaddress, salt, 16, 1000)
            key = kdf[:16]
            return key
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        s.bind((ip, port))
        s.listen(2)
        print('waiting for connections...')
        conn, addr = s.accept()
        print("Client: " + str(addr[0]) + " connected")
        while True:
            try:
                p = pyaudio.PyAudio()
                chunk_size = 1024  # 512
                audio_format = pyaudio.paInt16
                channels = 1
                rate = 20000
                seconds = 3
                filename = 'mserverfile.wav'
                json_input = conn.recv(4096)
                b64 = loads(json_input)
                iv = b64decode(b64['iv'])
                ct = b64decode(b64['ciphertext'])
                tcpkey = get_key(MACaddress)
                cipher = AES.new(tcpkey, AES.MODE_CBC, iv=iv)
                pt = unpad(cipher.decrypt(ct), AES.block_size)
                play_stream = p.open(format=audio_format, channels=channels, rate=rate, output=True,
                                         frames_per_buffer=chunk_size)
                play_stream.write(pt)
                print("audio recieved")

                tcpkey = get_key(MACaddress)
                record_stream = p.open(format=audio_format, channels=channels, rate=rate, input=True,
                                       frames_per_buffer=chunk_size)
                print('recording....')
                frames = []
                for i in range(0, int(rate / chunk_size * seconds)):
                    data = record_stream.read(chunk_size)
                    frames.append(data)
                print('wait....')
                record_stream.stop_stream()
                record_stream.close()
                wf = wave.open(filename, 'wb')
                wf.setnchannels(channels)
                wf.setsampwidth(p.get_sample_size(audio_format))
                wf.setframerate(rate)
                wf.writeframes(b"".join(frames))
                wf.close()
                with open(filename, "rb") as client_message:
                    chunk = client_message.read(chunk_size)
                cipher = AES.new(tcpkey, AES.MODE_CBC)
                ct_bytes = cipher.encrypt(pad(chunk, AES.block_size))
                iv = b64encode(cipher.iv).decode('utf-8')
                ct = b64encode(ct_bytes).decode('utf-8')
                result = dumps({'iv': iv, 'ciphertext': ct})
                conn.send(result.encode())
                print("audio sent")

                break
            except:
                s.close()
                print('connection terminated')
                main()

    else:
        print('UDP is NOT AVAILABLE')
        main()

def main():
    protocol = int(input("Select (1)UDP o (2)TCP: "))
    clientServer(protocol)

if __name__ == "__main__":
    main()