import json
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime, timedelta
from decimal import Decimal
import collections

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('TrashBinStatus')

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    try:
        http_method = event['httpMethod']
        if http_method == 'GET':
            query_params = event.get('queryStringParameters', {}) or {}
            stats_type = query_params.get('type', 'hourly')
            device_id = query_params.get('deviceId')  # deviceId 파라미터 추가
            
            # deviceId가 지정된 경우 해당 디바이스의 통계만 조회
            if stats_type == 'hourly':
                return get_hourly_statistics(device_id)
            elif stats_type == 'location':
                return get_location_statistics(device_id)
            elif stats_type == 'events':
                return get_event_statistics(device_id)
            elif stats_type == 'summary':
                return get_device_summary(device_id)
            
        return {
            'statusCode': 400,
            'headers': get_cors_headers(),
            'body': json.dumps('Invalid request')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': str(e)})
        }

def query_device_data(device_id=None):
    """디바이스별 데이터 조회"""
    if device_id:
        response = table.query(
            KeyConditionExpression=Key('deviceId').eq(device_id)
        )
        return response['Items']
    else:
        response = table.scan()
        return response['Items']

def get_hourly_statistics(device_id=None):
    """시간대별 통계 데이터"""
    try:
        items = query_device_data(device_id)
        
        # deviceId별로 구분하여 데이터 수집
        device_stats = collections.defaultdict(
            lambda: collections.defaultdict(
                lambda: {'count': 0, 'total_capacity': 0, 'alert_count': 0}
            )
        )
        
        for item in items:
            curr_device_id = item['deviceId']
            timestamp = datetime.fromisoformat(item['timestamp'].replace('Z', '+00:00'))
            hour = timestamp.hour
            
            device_stats[curr_device_id][hour]['count'] += 1
            device_stats[curr_device_id][hour]['total_capacity'] += float(item['capacity'])
            if item.get('flameDetected') or item.get('isFull'):
                device_stats[curr_device_id][hour]['alert_count'] += 1
        
        # 결과 포맷팅
        formatted_data = {}
        for curr_device_id, hours in device_stats.items():
            formatted_data[curr_device_id] = []
            for hour in range(24):
                if hours[hour]['count'] > 0:
                    avg_capacity = hours[hour]['total_capacity'] / hours[hour]['count']
                    formatted_data[curr_device_id].append({
                        'hour': hour,
                        'average_capacity': round(avg_capacity, 2),
                        'alert_count': hours[hour]['alert_count']
                    })
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'hourly_stats': formatted_data if not device_id else formatted_data.get(device_id, [])
            }, cls=DecimalEncoder)
        }
    except Exception as e:
        raise e

def get_location_statistics(device_id=None):
    """위치별 통계 데이터"""
    try:
        items = query_device_data(device_id)
        
        # deviceId별로 구분하여 데이터 수집
        device_location_stats = collections.defaultdict(
            lambda: collections.defaultdict(
                lambda: {
                    'count': 0,
                    'total_capacity': 0,
                    'alert_count': 0,
                    'flame_detections': 0
                }
            )
        )
        
        for item in items:
            curr_device_id = item['deviceId']
            location = item['location']
            
            device_location_stats[curr_device_id][location]['count'] += 1
            device_location_stats[curr_device_id][location]['total_capacity'] += float(item['capacity'])
            if item.get('isFull'):
                device_location_stats[curr_device_id][location]['alert_count'] += 1
            if item.get('flameDetected'):
                device_location_stats[curr_device_id][location]['flame_detections'] += 1
        
        # 결과 포맷팅
        formatted_data = {}
        for curr_device_id, locations in device_location_stats.items():
            formatted_data[curr_device_id] = []
            for location, data in locations.items():
                if data['count'] > 0:
                    formatted_data[curr_device_id].append({
                        'location': location,
                        'average_capacity': round(data['total_capacity'] / data['count'], 2),
                        'alert_count': data['alert_count'],
                        'flame_detections': data['flame_detections']
                    })
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'location_stats': formatted_data if not device_id else formatted_data.get(device_id, [])
            }, cls=DecimalEncoder)
        }
    except Exception as e:
        raise e

def get_event_statistics(device_id=None):
    """이벤트 통계 데이터"""
    try:
        items = query_device_data(device_id)
        
        # deviceId별로 이벤트 수집
        device_events = collections.defaultdict(list)
        
        for item in items:
            curr_device_id = item['deviceId']
            timestamp = item['timestamp']
            
            if item.get('flameDetected'):
                device_events[curr_device_id].append({
                    'type': 'flame',
                    'timestamp': timestamp,
                    'location': item['location'],
                    'deviceId': curr_device_id
                })
            if item.get('isFull'):
                device_events[curr_device_id].append({
                    'type': 'full',
                    'timestamp': timestamp,
                    'location': item['location'],
                    'deviceId': curr_device_id
                })
        
        # 각 디바이스별로 이벤트 시간순 정렬
        for curr_device_id in device_events:
            device_events[curr_device_id].sort(key=lambda x: x['timestamp'], reverse=True)
            device_events[curr_device_id] = device_events[curr_device_id][:50]  # 최근 50개만
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'events': device_events if not device_id else device_events.get(device_id, [])
            })
        }
    except Exception as e:
        raise e

def get_device_summary(device_id=None):
    """디바이스별 요약 통계"""
    try:
        items = query_device_data(device_id)
        
        # deviceId별 요약 데이터 수집
        device_summary = collections.defaultdict(lambda: {
            'total_records': 0,
            'avg_capacity': 0,
            'max_capacity': 0,
            'total_alerts': 0,
            'total_flame_detections': 0,
            'last_location': 'unknown'
        })
        
        for item in items:
            curr_device_id = item['deviceId']
            capacity = float(item['capacity'])
            
            summary = device_summary[curr_device_id]
            summary['total_records'] += 1
            summary['avg_capacity'] += capacity
            summary['max_capacity'] = max(summary['max_capacity'], capacity)
            if item.get('isFull'):
                summary['total_alerts'] += 1
            if item.get('flameDetected'):
                summary['total_flame_detections'] += 1
            summary['last_location'] = item['location']
        
        # 평균 계산
        for summary in device_summary.values():
            if summary['total_records'] > 0:
                summary['avg_capacity'] = round(summary['avg_capacity'] / summary['total_records'], 2)
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'summary': device_summary if not device_id else device_summary.get(device_id, {})
            }, cls=DecimalEncoder)
        }
    except Exception as e:
        raise e

def get_cors_headers():
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'OPTIONS,GET',
        'Content-Type': 'application/json'
    }