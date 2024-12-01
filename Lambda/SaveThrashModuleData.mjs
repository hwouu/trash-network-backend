import { DynamoDBClient, PutItemCommand } from "@aws-sdk/client-dynamodb";
const dynamoDBClient = new DynamoDBClient({ region: "ap-northeast-2" });

function calculateCapacity(mainSensor, subSensor) {
    if (mainSensor <= 0 || subSensor <= 0) {
        return 0;
    }

    let sensorToUse = mainSensor; // 기본적으로 메인 센서를 사용

    // 조건에 맞는 센서 선택
    if (mainSensor <= 30 && subSensor > 17) {
        sensorToUse = mainSensor; // 메인 센서가 30 이하이고 서브 센서가 17 초과면 메인 센서 기준
    } else if (mainSensor <= 30 && subSensor <= 17) {
        sensorToUse = subSensor; // 메인 센서가 30 이하이고 서브 센서가 17 이하이면 서브 센서 기준
    }

    // 선택된 센서를 기준으로 용량 계산
    const capacity = Math.max(0, Math.min(100, (1 - sensorToUse / 60) * 100));
    return Math.round(capacity * 10) / 10; // 소수점 첫째 자리까지 반올림
}

export const handler = async (event) => {
    console.log("Received event:", JSON.stringify(event, null, 2));

    // Event 데이터에서 필요한 정보를 추출
    const deviceId = event.deviceId || "정보 없음";
    const mainUltrasonicSensor = parseFloat(event.mainUltrasonicSensor) || 0;
    const subUltrasonicSensor = parseFloat(event.subUltrasonicSensor) || 0;
    const flameDetected = event.flameDetected || 0;
    // 배터리 음수면 0 반환
    const batteryLevel = Math.max(0, parseFloat(event.batteryLevel) || 0);
    const isFull = event.state?.desired?.isFull === "true";
    const capacity = calculateCapacity(mainUltrasonicSensor, subUltrasonicSensor);

    const timestamp = new Date().toISOString();
    const ttl = Math.floor(new Date().getTime() / 1000) + 24 * 60 * 60;

    const temperature = 15;
    const lastUpdated = new Date().toISOString();

    const locationMap = {
        ThrashModule1: "과학관 2층 중앙계단",
        ThrashModule2: "강의동 2층 휴게실",
        ThrashModule3: "학생회관 GS 편의점 옆", 
    };

    const location = locationMap[deviceId] || "정보 없음";

    const params = {
        TableName: 'TrashBinStatus',
        Item: {
            deviceId: { S: deviceId },
            timestamp: { S: timestamp },
            batteryLevel: { N: batteryLevel.toString() },
            capacity: { N: capacity.toString() },
            flameDetected: { N: flameDetected.toString() },
            isFull: { BOOL: isFull },
            lastUpdated: { S: lastUpdated },
            location: { S: location },
            temperature: { N: temperature.toString() },
            ttl: { N: ttl.toString() }
        }
    };

    try {
        const command = new PutItemCommand(params);
        const response = await dynamoDBClient.send(command);
        console.log("Data saved to DynamoDB:", response);
    } catch (error) {
        console.error("Error saving data to DynamoDB:", error);
    }

    return { statusCode: 200, body: 'Data processed successfully.' };
};