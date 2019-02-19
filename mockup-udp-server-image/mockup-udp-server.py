#!/usr/bin/python
import time
import threading
import sys
import os
import numpy as np
import socket
import urllib
import requests
import datetime
import numbers
import json
import signal 
import random

starttime = time.time()

if __name__ == '__main__':
    port=int(os.environ['SERVER_PORT'])
    UDPSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    listen_addr = ('',port)
    UDPSock.bind(listen_addr)
    print "UDPSock Listen on "+str(port)
    duration=int(random.randint(40,45)*35)
    while True:
        '''
        if time.time() - starttime > duration:
          print >>sys.stdout, 'time to go'
          print "time.time()"
          print time.time()
          print "starttime"
          print starttime
          sys.exit()
        '''
        print "STILL ALIVE"
        data,addr = UDPSock.recvfrom(4096)
        print >>sys.stdout, 'received %s bytes from %s' % (len(data), addr)
        print >>sys.stdout, data
        print data.strip(),addr
        if data:
          sent = UDPSock.sendto(data, addr)
          print >>sys.stdout, 'sent %s bytes back to %s' % (sent, addr)
          sample=np.random.random_sample((10,))
#          print >>sys.stdout, 'sample %s' % (str(data))
          data_ret=sorted(sample,key=float)
          print >>sys.stdout, 'sample returned %s' % (str(data_ret))
