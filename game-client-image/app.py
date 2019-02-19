#!/usr/bin/python
import time
import os
import numpy as np
import socket
import urllib
import requests
import datetime
import sys
import json

if __name__ == '__main__':
    loadsize=10
    server=os.environ['SERVER_ENDPOINT']
    sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    ipport=server.split(":")
    while True:
        sample= np.random.random_sample((loadsize,))
        sorted_sample=sorted(sample,key=float)
        sock.sendto(str(sorted_sample)+server,(ipport[0],int(ipport[1])))
        print "Sent "+str(sorted_sample)+ " to " +server
        time.sleep(5)
