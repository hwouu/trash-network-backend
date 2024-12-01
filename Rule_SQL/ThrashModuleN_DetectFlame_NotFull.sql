/*
주제: $aws/things/ThrashModuleN/shadow/update/accepted
*/

SELECT 
  state.reported.name AS deviceId, 
  state.reported.mainUltrasonicSensor AS mainUltrasonicSensor, 
  state.reported.subUltrasonicSensor AS subUltrasonicSensor, 
  state.reported.detectFlame AS flameDetected, 
  state.reported.battery AS batteryLevel, 
  {'desired':{'isFull': 'false','redLED': 'ON'}} as state
FROM 
  '$aws/things/ThrashModuleN/shadow/update/accepted' 
WHERE 
  state.reported.name = "ThrashModuleN" 
  AND state.reported.detectFlame > 0 
  AND (state.reported.mainUltrasonicSensor > 30 
    OR state.reported.subUltrasonicSensor > 17)

/* 
작업
1. Republish to AWS IoT Topic
  - 주제: $$aws/things/ThrashModuleN/shadow/update
  - 서비스 품질: 0

2. Lambda
  - 함수: SaveThrashModuleData
  - 함수: SendEmailToAdmin
*/