import json
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime
from decimal import Decimal

# DynamoDB 리소스 초기화
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('TrashBinStatus')

# Decimal JSON 인코더
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))  # 디버깅용 로그
        
        # API Gateway에서 받은 HTTP 메서드 확인
        http_method = event['httpMethod']
        
        # GET 요청 처리
        if http_method == 'GET':
            # 특정 deviceId가 지정된 경우
            path_parameters = event.get('pathParameters', {})
            if path_parameters and 'deviceId' in path_parameters:
                return get_single_bin_status(path_parameters['deviceId'])
            # 모든 디바이스 상태 조회
            else:
                return get_all_bins_status()
        
        # OPTIONS 요청 처리 (CORS 지원)
        elif http_method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': get_cors_headers(),
                'body': json.dumps('OK')
            }
        
        return {
            'statusCode': 400,
            'headers': get_cors_headers(),
            'body': json.dumps('Invalid request method')
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")  # 디버깅용 로그
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': str(e)})
        }

def get_single_bin_status(device_id):
    """특정 쓰레기통의 최신 상태 조회"""
    try:
        response = table.query(
            KeyConditionExpression=Key('deviceId').eq(device_id),
            ScanIndexForward=False,  # 최신 데이터부터 조회
            Limit=1
        )
        
        if not response['Items']:
            return {
                'statusCode': 404,
                'headers': get_cors_headers(),
                'body': json.dumps({
                    'message': f'No data found for device: {device_id}'
                })
            }
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps(response['Items'][0], cls=DecimalEncoder)
        }
    except Exception as e:
        print(f"Error in get_single_bin_status: {str(e)}")
        raise e

def get_all_bins_status():
    """모든 쓰레기통의 최신 상태 조회"""
    try:
        response = table.scan()
        items = response['Items']
        
        # 디바이스별로 가장 최신 데이터만 필터링
        latest_status = {}
        for item in items:
            device_id = item['deviceId']
            if device_id not in latest_status or item['timestamp'] > latest_status[device_id]['timestamp']:
                latest_status[device_id] = item
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'items': list(latest_status.values()),
                'count': len(latest_status)
            }, cls=DecimalEncoder)
        }
    except Exception as e:
        print(f"Error in get_all_bins_status: {str(e)}")
        raise e

def get_cors_headers():
    """CORS 헤더 반환"""
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'OPTIONS,GET',
        'Content-Type': 'application/json'
    }