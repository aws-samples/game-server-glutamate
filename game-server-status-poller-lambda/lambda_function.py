import json
import boto3
import ast
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
timestamp_table = dynamodb.Table('game-server-status-by-time')
endpoint_table = dynamodb.Table('game-server-status-by-endpoint')
lb_endpoint_table = dynamodb.Table('lb-status-by-endpoint')

def lambda_handler(event, context):
#    print(json.dumps(event))
    for record in event['Records']:
        # Deserialize data
        body=record["body"]
        print(body)
        dict_body=ast.literal_eval(body)
        timestamp=record['attributes']['SentTimestamp']
        status=dict_body['status']
        region=dict_body['region']
        public_port=str(dict_body['public_port'])
        private_ipv4=dict_body['private_ipv4']
        public_hostname=dict_body['public_hostname']
        _type=dict_body['type']
        endpoint=private_ipv4+':'+str(public_port)
        public_endpoint=public_hostname+':'+str(public_port)
        group=dict_body['group']

        # Serialize data
        if (_type=='gs'):
          data={
           'public_hostname':public_hostname,
           'public_port':public_port,
           'region':region,
           'status':status,
           'type':_type, 
           'timestamp':timestamp
          }

        if (_type=='lb'):
          target_gs=dict_body['endpoints']
          data={
           'region':region,
           'type':_type,
           'target_gs':target_gs,
           'timestamp':timestamp
          } 

        if(status=='terminating' and _type=='lb'):
            response_read = lb_endpoint_table.query(
                KeyConditionExpression=Key('endpoint').eq(public_endpoint)
            )
            print("Read by endpoint "+str(response_read))
            for i in response_read['Items']:
                print("Going to delete "+str(i))
                try:
                    response_delete = lb_endpoint_table.delete_item(
                        Key={
                            'endpoint': public_endpoint
                        }
                    )
                except ClientError as e:
                    print(e)
                print("DeleteItem from lb_endpoint_table succeeded:")

        if(status=='terminating' and _type=='gs'):
            response_read = endpoint_table.query(
                KeyConditionExpression=Key('endpoint').eq(endpoint)
            )
            print("Read by endpoint "+str(response_read))
            for i in response_read['Items']:
                print("Going to delete "+str(i))
                try:
                    response_delete = endpoint_table.delete_item(
                        Key={
                            'endpoint': endpoint
                        }
                    )
                except ClientError as e:
                    print(e)
                print("DeleteItem from endpoint_table succeeded:")
                
        if(status=='init' and _type=='lb'):
            response_endpoint_table = lb_endpoint_table.put_item(
                Item={
                    'endpoint': public_endpoint,
                    'status': status,
                    'group': group,
                    'info': data
                }
            )
            print("PutItem succeeded for endpoint_table")

        if(status=='init' and _type=='gs'):
            response_endpoint_table = endpoint_table.put_item(
                Item={
                    'endpoint': endpoint,
                    'status': status,
                    'group': group,
                    'info': data
                }
            )
            print("PutItem succeeded for endpoint_table")
            
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from game-server-status-poller')
    }

