#!/usr/bin/python
import sys
import os
import socket
import random
import subprocess
import boto3
import json
import fileinput
import signal
import requests
from ec2_metadata import ec2_metadata

# global variables 
region='us-west'
public_hostname=''
public_port=''
private_ipv4=''
endpoints=''


# Get the service resource
sqs_cli=boto3.resource('sqs',region_name='us-west-2')

# Get the api endpoint for availiable game servers for this instance target group
apiendpoint=os.environ['APIENDPOINT']
get_avail_gs_call='https://'+apiendpoint+'/api/get-availiable-gs'
set_busy_gs_call='https://'+apiendpoint+'/api/set-gs-busy'

# Get the queue
queuename=os.environ['QUEUENAME']
queue = sqs_cli.get_queue_by_name(QueueName=queuename)

def sigterm_handler(_signo, _stack_frame):
    print 'in sigterm_handler'
    publish_game_server_status('terminating','lb')
      

def publish_game_server_status(status,server_type):
    print 'in publish_game_server_status with hostname='+public_hostname+' port='+str(public_port)+' region='+region+' status='+status+' type='+server_type+' private_ipv4='+private_ipv4
    data={
      'public_hostname':public_hostname,
      'public_port':str(public_port),
      'region':region,
      'status':status,
      'type':server_type,
      'private_ipv4':private_ipv4,
      'endpoints':endpoints
    }
    print str(data)
    try: 
       # Send the message to the queue 
       response = queue.send_message(
           MessageBody=str(data)
       )
    
       # The response is NOT a resource, but gives you a message ID and MD5
       print('response message id is '+response.get('MessageId'))
    except Exception as e:
        print 'error publishing server status via SQS'
        print str(e)


def get_rand_port():
    print 'in get random port'
    # Attempting to get random port
    try:
      s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      print 'socket created'
      s.bind(('',0))
    except socket.error as msg:
      print 'bind failed. Error is '+str(msg[0])+' Msg '+msg[1]
    print 'socket bind complete '
    # Capture the port and release the socket
    port=s.getsockname()[1]
    s.close()
    print 'dynamic port to start the game server is '+str(port)
    return port

def set_busy_gs(gs_endpoint):
    print 'in set_busy_gs('+gs_endpoint+')'
    try:
       r=requests.get(set_busy_gs_call+'/'+gs_endpoint)
       return r.json()
    except Exception as e:
        print str(e)

def get_avail_gs():
    print 'in get_avail_gs'
    try:
       r=requests.get(get_avail_gs_call)
       print 'first endpoint='+str(r.json()[0])
       print 'second endpoint='+str(r.json()[1])
       return r.json()
    except Exception as e:
        print str(e)

if __name__ == '__main__':
  # Catch SIGTERM to report game-server status
  signal.signal(signal.SIGTERM, sigterm_handler)

  # Getting ports and hostname from the platform
  public_port=get_rand_port()
  print 'got server port '+str(public_port)
  public_hostname=ec2_metadata.public_hostname
  print 'about to launch the load balancer server '+public_hostname 

  # Getting target game servers
  print 'Getting target game servers'
  endpoints=get_avail_gs()
  os.environ['ENDPOINT1']=endpoints[0]
  os.environ['ENDPOINT2']=endpoints[1]
 
  # Mark the gs as busy 
  set_busy_gs(endpoints[0])
  set_busy_gs(endpoints[1])

  print 'Populating LB_IP='+public_hostname+' and LB_PORT='+str(public_port) 
  os.environ['LB_IP']=public_hostname
  os.environ['LB_PORT']=str(public_port)
  

  print 'lb_ip='+public_hostname
  print 'lb_port='+str(public_port)
  try:
    # Publishing game-server init status
    publish_game_server_status('init','lb')

    # Configuring the LB with the target game servers
    subprocess.call(['/setconfig'])
  except Exception as e:
    print 'error in subprocess or sqs pub'
    print str(e)
