import socket

from .data_db import Data_db

socket.socket(family=AF_INET, type=SOCK_STREAM, proto=0, fileno=None)

msg = [
        '2016-10-10 00:00',
        1,
        ]
data = [
        20,
        20,
        1000,
        600,
        ]

d1 = Data_db()
d2 = Data_db()

d1.write_in(msg, data)
d2.write_in(msg, data)

#这里要做一个指针
