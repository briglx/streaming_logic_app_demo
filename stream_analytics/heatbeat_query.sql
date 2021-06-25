Select 
    deviceId,
    COUNT(*) AS HeartbeatCount
from RawEventHub TIMESTAMP BY eventDtm
Group By
    deviceId,
	TumblingWindow(second, 30)
Having 
    HeartbeatCount < 5