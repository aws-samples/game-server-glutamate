from chalice import Chalice
import boto3
import json
import ast
from boto3.dynamodb.conditions import Key, Attr

app = Chalice(app_name='game-server-inventory-api-lambda')
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
endpoint_table = dynamodb.Table('game-server-status-by-endpoint')

#TODO read the groups dynamically 
grp1='mockup-server-grp1'
grp2='mockup-server-grp2'

@app.route('/set-gs-busy/{endpoint}')
def set_gs_busy(endpoint):
    response_read = endpoint_table.query(
        KeyConditionExpression=Key('endpoint').eq(endpoint)
    )
    status='busy'
    print(str(response_read))
    data={
      'public_hostname':response_read['Items'][0]['info']['public_hostname'],
      'public_port':str(response_read['Items'][0]['info']['public_port']),
      'region':response_read['Items'][0]['info']['region'],
      'type':response_read['Items'][0]['info']['type']
    }
    group=response_read['Items'][0]['group']

    response_write=endpoint_table.put_item(
        Item={
          'endpoint': endpoint,
          'info': data,
          'status':status,
          'group':group
        } 
    )
    print("PutItem succeeded for endpoint_table")
    return {endpoint:status}

def get_avail_gs_per_group(group):
    response_read = endpoint_table.query(
        IndexName='status-group-index',
        KeyConditionExpression=Key('status').eq('init') & Key('group').eq(group)
    )
    count=response_read['Count']
    print 'count of '+group+'='+str(count)
    if (count==0):
       print 'no gs are availiable for '+group
       return

    if (group>=1):
       print 'we have one or more than one gs that is availible in '+group+' we take the first one'
       print json.dumps(response_read['Items'][0])
       endpoint=response_read['Items'][0]['endpoint'] 
       print 'group '+group+' endpoint '+endpoint

    return endpoint
    
@app.route('/get-availiable-gs')
def get_avail_gs():
    endpoints=[]
    grp1_endpoint=get_avail_gs_per_group(grp1)
    endpoints.append(grp1_endpoint)
    grp2_endpoint=get_avail_gs_per_group(grp2)
    endpoints.append(grp2_endpoint)

    return endpoints

@app.route('/')
def index():
    return {"supported calls": "/get-availiable-gs,/set-gs-busy/{endpoint}"}
# The view function above will return {"hello": "world"}
# whenever you make an HTTP GET request to '/'.
#
# Here are a few more examples:
#
# @app.route('/hello/{name}')
# def hello_name(name):
#    # '/hello/james' -> {"hello": "james"}
#    return {'hello': name}
#
# @app.route('/users', methods=['POST'])
# def create_user():
#     # This is the JSON body the user sent in their POST request.
#     user_as_json = app.current_request.json_body
#     # We'll echo the json body back to the user in a 'user' key.
#     return {'user': user_as_json}
#
# See the README documentation for more examples.
#
