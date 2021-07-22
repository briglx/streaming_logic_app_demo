Select 
    deviceId,
    ipAddress,
    operatorId,
    deviceSerialNbr,
    COUNT(*) AS HeartbeatCount,
    'HeartbeatQuery' as Source
from RawEventHub TIMESTAMP BY eventDtm
Group By
    deviceId,
	TumblingWindow(minute, 3)
Having 
    HeartbeatCount < 4