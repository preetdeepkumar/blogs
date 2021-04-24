'''
Usage:
    send_to_kdf.py <log file name> <kinesis-firehose stream name>
'''

import sys
import boto3
import random
from time import sleep

firehose = boto3.client('firehose', region_name = 'ap-south-1')

def send_file_to_kdf(log_file):
    with open(log_file) as f:
        for line in f:
            sleep(random.randint(0, 3))
            try:
                response = firehose.put_record(
                    DeliveryStreamName=sys.argv[1],
                    Record={
                        'Data': line.strip().encode('utf-8')
                    }
                )
                print(response['ResponseMetadata']['HTTPStatusCode'])
            except Exception as e:
                print(str(e))

if __name__ == '__main__':
    send_file_to_kdf(sys.argv[2])
