import { SNSClient, PublishCommand } from "@aws-sdk/client-sns"; // AWS SDK v3

const snsClient = new SNSClient();

export const handler = async (event) => {
    console.log("Event received:", JSON.stringify(event, null, 2));

    // Event 데이터에서 필요한 정보를 추출
    const deviceName = event.deviceId || "정보 없음";
    const detectFlame = event.flameDetected || "정보 없음";
    const timestamp = new Date().toISOString();

    const locationMap = {
      ThrashModule1: "과학관 2층 중앙계단", 
      ThrashModule2: "강의동 2층 휴게실", 
      ThrashModule3: "학생회관 GS 편의점 옆", 
    };

    const location = locationMap[deviceId] || "정보 없음";

    // SNS 메시지 내용 생성 (커스터마이징)
    const message = `
    🚨 [긴급 알림] 화재 감지 발생 🚨
    ----------------------------------------
    📟 장치명: ${deviceName}
    📍 위치: ${location}
    🔥 화염 감지 여부: ${detectFlame > 0 ? "화재 발생" : "화재 없음"}
    🕒 감지 시간: ${timestamp}
    ----------------------------------------
    조치를 즉시 취해 주세요!
    `;

    const params = {
        Message: message,
        Subject: `🔥 [화재 경고] ${deviceName} 장치에서 이상 감지됨!`,
        TopicArn: "arn:aws:sns:ap-northeast-2:637423387234:emailToK",
    };

    try {
        const result = await snsClient.send(new PublishCommand(params));
        console.log("SNS Message Sent:", result);
        return { status: "SNS Sent Successfully", result };
    } catch (error) {
        console.error("Error sending SNS:", error);
        return { status: "Error", error };
    }
};