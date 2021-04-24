import base64
import re
import json
from datetime import datetime

# regex to match sample Spark log records
p = re.compile(r'(\d+/\d+/\d+\s\d+:\d+:\d+) (\w+) (\w+.+): (.*)')

def lambda_handler(event, context):
    output = []
    custom_metric_count = 0
    
    for record in event['records']:
        # fetch log record in text format
        text = str(base64.b64decode(record['data']), 'utf-8')
        
        if re.search("Partition.*not found.*", text):
            custom_metric_count += 1
        
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

    # append custom metric
    now = datetime.utcnow().strftime("%d/%m/%y %H:%M:%S")
    custom_payload = { 
                'timestamp': datetime.strptime(now, "%d/%m/%y %H:%M:%S").isoformat(),
                'severity' : 'INFO',
                'module' : 'custom.metric',
                'message' : 'Partition.*not found.*',
                'value' : custom_metric_count
    }
    custom_record = {
            'recordId': record['recordId'],
            'result': 'Ok',
            'data': base64.b64encode(json.dumps(custom_payload).encode('utf-8')).decode('utf-8')
    }
    output.append(custom_record)

    return {'records': output}