import json
import boto3
import os
import json 
from urllib.parse import unquote_plus
from botocore.config import Config

db_name = os.environ['DB_NAME']
table_name = os.environ['TABLE_NAME']
query_output = os.environ['QUERY_OUTPUT']

config = Config( retries = { 'max_attempts': 2, 'mode': 'standard' } )
athena = boto3.client('athena', config=config)

sqs = boto3.resource('sqs')
queue_in = sqs.get_queue_by_name(QueueName=os.environ['QUEUE_IN'])
queue_out = sqs.get_queue_by_name(QueueName=os.environ['QUEUE_OUT'])

def submit_to_athena(partition_name):
    query = 'ALTER TABLE {table} ADD PARTITION ({partition})'.format(table=table_name, partition=partition_name)
    response = athena.start_query_execution(
                    QueryString=query,
                    QueryExecutionContext={
                        'Database': db_name
                    },
                    ResultConfiguration={
                        'OutputLocation': query_output
                    })
    return response['QueryExecutionId']
    
def lambda_handler(event, context):
    # get messages from queue
    for message in queue_in.receive_messages(MessageAttributeNames=['All'], MaxNumberOfMessages=10, VisibilityTimeout=300, WaitTimeSeconds=20):
        body = json.loads(message.body)
        if 'Records' in body:
            # each body will have only one partition value or object key
            record = body['Records'][0]
            key = unquote_plus(record['s3']['object']['key'])
            partition = key.replace('rawdata/retail/', '').split('/')[0].replace('dt=','')
            # submit to Athena and collect query execution id
            qid = submit_to_athena('dt=\''+ partition +'\'')
            # send both to another queue
            queue_out.send_message(MessageBody=json.dumps({ 'qid' : qid, 'msg' : message.body }))            
        message.delete()
            
            
