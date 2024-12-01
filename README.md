# 💡 Trash Network Backend

🏢 **실시간 쓰레기통 모니터링 시스템**

이 저장소는 실시간 쓰레기통 모니터링 시스템을 위한 백엔드 및 클라우드 인프라를 제공합니다. AWS IoT Core, Lambda, DynamoDB를 활용하여 IoT 디바이스 데이터를 수집, 처리, 저장하며 실시간 모니터링 및 알림 기능을 지원합니다.

---

## 🖌️ 시스템 아키텍처

```
[IoT Device] --> [AWS IoT Core] --> [IoT Rules] --> [Lambda Functions] --> [DynamoDB]
                                                 --> [SNS (Email Alerts)]
```

- **AWS IoT Core**: IoT 디바이스 상태 관리 및 데이터 수신
- **IoT Rules**: SQL 규칙을 사용해 디바이스 상태 기반 작업 트리거
- **Lambda Functions**: 데이터 처리, 저장 및 알림 전송
- **DynamoDB**: 디바이스 상태 및 이력 데이터 저장
- **SNS**: 관리자 이메일 알림 발송

---

## 🎯 주요 기능

### 1. 데이터 수집 및 처리
- IoT 디바이스로부터 실시간 센서 데이터 수신
- 쓰레기통 용량 계산 및 상태 업데이트
- 화재 감지 및 경고 시스템

### 2. 데이터 저장 및 조회
- 디바이스별 상태 및 이력 데이터 저장
- 실시간 상태 조회 API 제공
- 통계 데이터 분석 및 제공

### 3. 알림 시스템
- 화재 감지 시 즉시 관리자 이메일 알림 전송
- 쓰레기통 포화 상태 알림

---

## 🔄 디렉토리 구조

```
.
├── Lambda/
│   ├── GetTrashBinStatistics.py   # 통계 데이터 조회
│   ├── GetTrashBinStatus.py       # 실시간 상태 조회
│   ├── SaveThrashModuleData.mjs   # 센서 데이터 저장
│   └── SendEmailToAdmin.mjs       # 관리자 알림 전송
└── Rule_SQL/
    ├── ThrashModuleN_DetectFlame.sql          # 화재 감지 (포화 상태)
    ├── ThrashModuleN_DetectFlame_NotFull.sql  # 화재 감지 (비포화 상태)
    ├── ThrashModuleN_IsFull.sql               # 포화 상태 감지
    └── ThrashModuleN_NotFull.sql              # 정상 상태 감지
```

---

## 🔐 API 문서

### 1. 쓰레기통 상태 조회 API
```
GET /status
GET /status/{deviceId}
```
- 전체 또는 특정 디바이스의 현재 상태 조회

### 2. 통계 데이터 조회 API
```
GET /statistics?type=hourly&deviceId={deviceId}
GET /statistics?type=location&deviceId={deviceId}
GET /statistics?type=events&deviceId={deviceId}
GET /statistics?type=summary&deviceId={deviceId}
```
- **hourly**: 시간대별 통계
- **location**: 위치별 통계
- **events**: 이벤트 이력
- **summary**: 디바이스 요약 정보

---

## 🌐 AWS 리소스 설정

### DynamoDB 테이블 구조
```json
{
  "TableName": "TrashBinStatus",
  "KeySchema": [
    { "AttributeName": "deviceId", "KeyType": "HASH" },
    { "AttributeName": "timestamp", "KeyType": "RANGE" }
  ]
}
```

### IoT Rules 설정
- SQL 규칙을 통해 디바이스 상태 업데이트 시 Lambda 함수 트리거
- 화재 감지 시 추가 알림 기능 활성화

---

## ⚙️ 개발 환경 설정

1. AWS CLI 설치 및 설정:
```bash
aws configure
```

2. 필요한 AWS 서비스 권한:
- AWS IoT Core
- AWS Lambda
- Amazon DynamoDB
- Amazon SNS

3. 환경 변수 설정:
```bash
# .env 파일 생성
AWS_REGION=ap-northeast-2
SNS_TOPIC_ARN=arn:aws:sns:ap-northeast-2:XXXXXXXXXXXX:emailToK
```

---

## 🎨 로컬 테스트

Lambda 함수 로컬 테스트를 위한 예시 이벤트:
```json
{
  "deviceId": "ThrashModule1",
  "mainUltrasonicSensor": 25,
  "subUltrasonicSensor": 15,
  "flameDetected": 0,
  "batteryLevel": 85
}
```

---

## ✍️ 라이선스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

