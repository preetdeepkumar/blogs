import json
import boto3
import os
import json 
from urllib.parse import unquote_plus
from botocore.config import Config

config = Config( retries = { 'max_attempts': 2, 'mode': 'standard' } )
athena = boto3.client('athena', config=config)

sqs = boto3.resource('sqs')
queue_in = sqs.get_queue_by_name(QueueName=os.environ['QUEUE_IN'])
queue_out = sqs.get_queue_by_name(QueueName=os.environ['QUEUE_OUT'])

def lambda_handler(event, context):
    # get messages from queue
    for message in queue_in.receive_messages(MessageAttributeNames=['All'], MaxNumberOfMessages=10, VisibilityTimeout=300, WaitTimeSeconds=20):
        body = json.loads(message.body)
        # check the athena query status executed in first lambda_sqs_athena function
        response = athena.get_query_execution(QueryExecutionId=body['qid'])
        state = response['QueryExecution']['Status']['State']
        reason = response['QueryExecution']['Status']['StateChangeReason']    
        if state != 'QUEUED':
            if (state in 'FAILED') and ('AlreadyExistsException' not in reason):
                # enqueue for reprocessing
                queue_out.send_message(MessageBody=body['msg'])
            message.delete()
