import socket
import pyaudio
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad,unpad
from base64 import b64encode,b64decode
from pickle import dumps,loads
from json import dumps,loads
import wave

#clientserver function
def clientServer(protocol):
    if(protocol == 2):
        ip = socket.gethostbyname(socket.gethostname())
        port = int(input('Enter port number to run on --> '))
        print("Server ip:" + ip)
        MACaddress = input('enter MACaddress:')
        def get_key(MACaddress):
            salt = b"this is a salt"
            kdf = PBKDF2(MACaddress, salt, 16, 1000)
            key = kdf[:16]
            return key
        #Initialising TCP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        s.bind((ip, port))
        s.listen(2)
        print('waiting for connections...')
        conn, addr = s.accept()
        print("Client: " + str(addr[0]) + " connected")
        while True:
            try:
                json_input = conn.recv(4096)
                b64 = loads(json_input)
                iv = b64decode(b64['iv'])
                ct = b64decode(b64['ciphertext'])
                tcpkey = get_key(MACaddress)
                cipher = AES.new(tcpkey, AES.MODE_CBC, iv=iv)
                pt = unpad(cipher.decrypt(ct), AES.block_size)#decoded client message
                p = pyaudio.PyAudio()
                chunk_size = 1024  # 512
                audio_format = pyaudio.paInt16
                channels = 1
                rate = 20000

                play_stream = p.open(format=audio_format, channels=channels, rate=rate, output=True,
                                         frames_per_buffer=chunk_size)
                for frame in pt:
                    play_stream.write(frame)
                play_stream.stop_stream()
                play_stream.close()
                p.terminate()
                break
            except:
                s.close()
                print('connection terminated')
                main()

    else:
        print('UDP is NOT AVAILABLE')
        main()
#main behaves as a module i.e once its called the clientserver function will repeat
def main():
    protocol = int(input("Select (1)UDP o (2)TCP: "))
    #calls the clientServer function
    clientServer(protocol)

if __name__ == "__main__":
    main()