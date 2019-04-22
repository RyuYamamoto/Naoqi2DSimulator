#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import numpy as np

class SocketServer:
    def __init__(self, ip, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((ip, port))
        self.socket.listen(1)

        self.target = np.array([0, 0, 0])
        self.flag = False

        print("start socket server...")

    def update(self):
        while True:
            conn, addr = self.socket.accept()
            if conn:
                data = conn.recv(1024).decode()
                if not data:
                    break
                result = str(data)
                result = result.split(',')
                if len(result) != 3:
                    break
                else:
                    try:
                        self.target = np.array([float(result[0]), float(result[1]), float(result[2])])
                        self.flag = True
                    except Exception as message:
                        print("Invalid Parameter => " + str(message))

    def get_target_value(self):
        if self.flag is True:
            self.flag = False
            return self.target
