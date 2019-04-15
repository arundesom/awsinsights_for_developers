import json
import boto3

def lambda_handler(event, context):
    # TODO implement
    
    operation = event['http_method']

    if operation == 'GET':
        lst = []
        log = boto3.client('logs', event['region'])
        response = log.get_query_results(
            queryId=event['queryid']
        )
        return response
        
    elif operation == 'POST':
        log = boto3.client('logs', event['body']['region'])
        response = log.start_query(
			logGroupName=event['body']['logGroupName'],
			startTime=int(event['body']['startTime']),
			endTime=int(event['body']['endTime']),
			queryString=event['body']['queryString']
		)
		
        return response
