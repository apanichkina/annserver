#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import os
from HttpConnection import *
import errno
import argparse

DEF_HOST = '127.0.0.1'
DEF_PORT = 8081
DEF_WORKERS_COUNT = 8
DEF_NCPU = 2
DEF_ROOT_DIR = os.path.dirname(__file__) + 'document_root'


def main():
    print 'ok'
    parser = argparse.ArgumentParser()
    parser.add_argument('-host', type=str, help="Host")
    parser.add_argument('-p', type=int, help="Port")
    parser.add_argument('-c', type=int, help="CPUs count")
    parser.add_argument('-r', type=str, help="Root directory")
    args = vars(parser.parse_args())

    host = args['host'] or DEF_HOST
    port = args['p'] or DEF_PORT
    cpu_count = args['c'] or DEF_NCPU
    document_root = args['r'] or DEF_ROOT_DIR

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(1024)

    forks = []
    for x in range(0, DEF_WORKERS_COUNT * cpu_count):
        pid = os.fork()
        forks.append(pid)
        if pid == 0:
            print 'Running worker with PID:', os.getpid()
            while True:
                try:
                    client_connection, client_address = sock.accept()
                except IOError as e:
                    code, msg = e.args
                    if code == errno.EINTR:
                        continue
                    else:
                        raise
                http_connection = HttpConnection(client_connection, document_root)
                http_connection.do_response()
                client_connection.close()

    sock.close()

    for pid in forks:
        os.waitpid(pid, 0)

if __name__ == '__main__':
    main()