import socket

HOST = '114.215.82.136'
PORT = 7790
BUFSIZ = 1024
ADDR = (HOST, PORT)

def control(ask_sent, password):
    sock = socket.socket()
    sock.connect(ADDR)
    sock.send(password.encode())
    perm = sock.recv(BUFSIZ)
    if perm.decode() == '允许控制':
        sock.send(ask_sent.encode())
        stat = sock.recv(BUFSIZ)
        if stat.decode() == '成功':
            sock.send('exit'.encode())
            sure = sock.recv(BUFSIZ)
            if sure.decode() == '退出':
                sock.close()
                return 0
            else:
                sock.close()
                return 1
        else:
            sock.close()
            return 2
    else:
        sock.close()
        return 3
