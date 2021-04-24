import base64
import re
import json
from datetime import datetime

# regex to match sample Spark log records
p = re.compile(r'(\d+/\d+/\d+\s\d+:\d+:\d+) (\w+) (\w+.+): (.*)')

def lambda_handler(event, context):
    output = []

    for record in event['records']:
        # fetch log record in text format
        text = str(base64.b64decode(record['data']), 'utf-8')
        
        # Extract the log record
        m = p.match(text)
        if m:
            groups = m.groups()
            payload = { 
                'timestamp': datetime.strptime(groups[0], "%d/%m/%y %H:%M:%S").isoformat(),
                'severity' : groups[1],
                'module' : groups[2],
                'message' : groups[3]
            }
            output_record = {
            'recordId': record['recordId'],
            'result': 'Ok',
            'data': base64.b64encode(json.dumps(payload).encode('utf-8')).decode('utf-8')
            }
            output.append(output_record)
        else:
            print('No matching log record {}'.format(text))

    print('Processed {} records'.format(len(output)))

    return {'records': output}