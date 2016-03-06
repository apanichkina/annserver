#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from time import gmtime, strftime
import urllib

CONTENT_TYPE = {
    'html': 'text/html',
    'css': 'text/css',
    'js': 'application/javascript',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'swf': 'application/x-shockwave-flash',
    'txt': 'text/plain'
}
DEFAULT_CONTENT_TYPE = 'application/octet-stream'
STATUS_REASON_PHRASE = {
    200: 'OK',
    400: 'Bad request',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method not allowed',
    500: 'Internal Server Error',
    502: 'Bad Gateway',
    504: 'Gateway Time-out'
}
SERVER_NAME = 'Annginx'
SEPARATOR = '\r\n'
INDEX = 'index.html'
SUPPORT_METHODS = ['GET', 'HEAD']
PORTION_TO_SEND = 4096


class HttpConnection:
    def __init__(self, connection, root_dir):
        self.connection = connection
        self.document_root = root_dir
        self.method = ''
        self.url = ''
        self.path = ''
        self.full_path = ''
        self.parameters = ''
        self.protocol = 'HTTP/1.1'
        self.headers = {}
        self.status = 200
        self.file_size = ''
        self.content_type = 'txt'
        self.body = None

    def do_response(self):
        client_body = self.parser()
        headers, body = self.create_answer()
        self.connection.send(headers)

        if body is not None:
            body.seek(0)
            block = body.read(PORTION_TO_SEND)
            while (block):
                self.connection.send(block)
                block = body.read(PORTION_TO_SEND)
            body.close()

    def parser(self):
        client_query = self.connection.recv(1024)
        data = client_query.split('\r\n')
        start_string = data[0]
        self.method, self.url, self.protocol = start_string.split(' ', 2)
        #Игнорировать параметры или отдавать 405?
        path = self.url.split('?')[0]
        print self.path
        self.path = urllib.unquote(path).decode('utf8')
        for i, line in enumerate(data[1:], 1):
            if line.strip():
                key, value = line.split(': ', 1)
                self.headers[key.lower()] = value
            else:
                break
        body = data[i + 1]
        return body

    def find_content(self):
        if '..' in self.path:
            self.status = 400
            return
        else:
            self.full_path = self.document_root + self.path
            if os.path.isfile(self.full_path):
                content = self.path.split('/')[-1]
                self.content_type = content.split('.')[-1]
                self.file_size = os.stat(self.full_path).st_size
                ##body
            else:
                if '.' in self.path:
                    self.status = 404
                else:#путь заканчивается не файлом
                    self.full_path = self.document_root + self.path + INDEX
                    if os.path.isfile(self.full_path):
                        self.content_type = INDEX.split('.')[-1]
                        self.file_size = os.stat(self.full_path).st_size
                        ##body
                    else:#в директории нет index файла
                        self.status = 403

    def create_answer(self):
        if self.method in SUPPORT_METHODS:
            self.find_content()
        else:
            self.status = 405

        response = '{protocol} {status} {reason_phrase}'.format(protocol=self.protocol, status=self.status,
                                                          reason_phrase=STATUS_REASON_PHRASE[self.status]) + SEPARATOR
        response += 'Date: {date}'.format(date=strftime("%a, %d %b %Y %X GMT", gmtime())) + SEPARATOR
        response += 'Server: {server_name}'.format(server_name=SERVER_NAME) + SEPARATOR
        response += 'Connection: keep-alive' + SEPARATOR
        if self.status == 200:
            response += 'Content-Length: {length}'.format(length=self.file_size) + SEPARATOR
            response += 'Content-Type: {content_type}'.format(content_type=CONTENT_TYPE.setdefault(self.content_type, DEFAULT_CONTENT_TYPE)) + SEPARATOR
            response += SEPARATOR
            if self.method == 'GET':
                self.body = open(self.full_path, 'rb')
        return response, self.body

