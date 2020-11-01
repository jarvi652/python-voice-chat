import socket
import pyaudio
import wave
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad,unpad
from base64 import b64encode,b64decode
from json import dumps,loads


def clientServer(protocol):
    if(protocol == 2):
        ip = input('enter server IP:')
        port = int(input('enter target port of server:'))
        print("Server ip:" + ip + "\nPort:" + str(port))
        MACaddress = input('enter  server MACaddress:')
        def get_key(MACaddress):
            salt = b"this is a salt"
            kdf = PBKDF2(MACaddress, salt, 16, 1000)
            key = kdf[:16]
            return key
        tcpkey = get_key(MACaddress)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        s.connect((ip, port))
        while True:
            try:
                print('connected to server')
                chunk_size = 1024
                audio_format = pyaudio.paInt16
                channels = 1
                rate = 20000  # frame rate
                seconds = 3
                filename = 'myfile.wav'

                # initialising py audio
                p = pyaudio.PyAudio()
                record_stream = p.open(format=audio_format, channels=channels, rate=rate, input=True,
                                       frames_per_buffer=chunk_size)
                print('recording....')
                # starts recording
                frames = []  # frame list
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
                s.send(result.encode())
                print("audio sent")
                s.close()
                main()
                json_input = s.recv(1024)
                b64 = loads(json_input)
                iv = b64decode(b64['iv'])
                ct = b64decode(b64['ciphertext'])
                cipher = AES.new(tcpkey, AES.MODE_CBC, iv=iv)
                pt = unpad(cipher.decrypt(ct), AES.block_size)
                play_stream = p.open(format=audio_format, channels=channels, rate=rate, output=True,
                                     frames_per_buffer=chunk_size)
                play_stream.write(pt)
                s.close()
                main()
                break
            except:
                print('connection was interrupted')
                main()
    else:
        print('UDP is NOT AVAILABLE')
        main()

def main():
    protocol = int(input("Select (1)UDP o (2)TCP: "))
    clientServer(protocol)

if __name__ == "__main__":
    main()

