#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
from HttpConnection import HttpConnection


def main():
    print 'ok'
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('127.0.0.1', 8081))
    sock.listen(5)
    conn, addr = sock.accept()
    http_connection = HttpConnection(conn)
    # client_query = conn.recv(1024)
    query = http_connection.parser()
    headers, body = http_connection.create_answer()
    print headers
    conn.send(headers)
    if body is not None:
        body.seek(0)
        block = body.read(4096)
        while (block):
            conn.send(block)
            block = body.read(4096)
        body.close()
    conn.close()

if __name__ == '__main__':
    main()