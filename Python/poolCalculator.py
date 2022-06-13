#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket
import multiprocessing
from multiprocessing import shared_memory
import numpy as np
import statistics
import os, sys

def server():
    outData = input('please input numbers: ')
    sendClient1(outData)
    sendClient2(outData)
    shmName, size =  sendClient3(outData)
    shm = shared_memory.SharedMemory(name=shmName, create=False)

    processClient3(shmName, size)

def client1():
    HOST = '0.0.0.0'
    PORT = 7000

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(5)

    # print('client1 ready at: %s:%s' % (HOST, PORT))

    while True:
        conn, addr = s.accept()
        # print('connected by ' + str(addr))

        while True:
            inData = conn.recv(1024)
            if len(inData) == 0: 
                conn.close()
                # print('server closed connection.')
                break
            stringArray =  inData.decode().split()
            mapObject = map(int, stringArray)
            numbers = list(mapObject)
            mean = np.mean(numbers)
            outData = 'mean ' + str(mean)
            conn.send(outData.encode())
        break

def sendClient1(outData):
    HOST = '0.0.0.0'
    PORT = 7000

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    s.send(outData.encode())
    inData = s.recv(1024)
    if len(inData) == 0: 
        s.close()
        print('server closed connection.')
    print('client 1: ' + inData.decode())

def sendClient2(data):
    r, w = os.pipe() 
    pid = os.fork()     

    if pid > 0:
        os.close(w)
        r = os.fdopen(r)
        result = r.read()
        print('client 2: ' + result)
        sys.exit(0)
    else:
        print('client 2 is ready')
        os.close(r)
        w = os.fdopen(w, 'w')
        stringArray =  data.split()
        mapObject = map(int, stringArray)
        numbers = list(mapObject)
        median = np.median(numbers)
        outData = 'median ' + str(median)
        w.write(outData)
        w.close()

def sendClient3(data):
    stringArray =  data.split()
    mapObject = map(int, stringArray)
    numbers = list(mapObject)
    a=np.array(numbers)
    shm=shared_memory.SharedMemory(create=True, size=a.nbytes)

    b=np.ndarray(a.shape, dtype=a.dtype, buffer=shm.buf)
    b[:]=a[:]
    return shm.name, a.shape;

def processClient3(shmName, size):
    existingShm=shared_memory.SharedMemory(name=shmName)
    print('client 3 is ready')

    c=np.ndarray(size, dtype=np.int64, buffer=existingShm.buf)
    mode = statistics.mode(c)
    outData = 'mode ' + str(mode)
    print('client 3: ' + outData)
    existingShm.close()
    existingShm.unlink()

if __name__ == '__main__': 
    r, w = os.pipe() 
    pid = os.fork()
    if pid > 0:
        os.close(w)
        r = os.fdopen(r)
        result = r.read()
        print(result)
        server()
    else:
        os.close(r)
        w = os.fdopen(w, 'w')
        result = 'client 1 ready'
        w.write(result)
        w.close()
        client1()
