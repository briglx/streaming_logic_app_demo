SELECT
    deviceId,
    ipAddress,
    operatorId,
    deviceSerialNbr,
    Collect(eventId) as eventId,
    Collect(event) as event,
    Collect(eventName) as eventName,
    Collect(setOrClear) as setOrClear,
    Collect(stopPointId) as stopPointId,
	eventReasonCodeId,
    Collect(eventDtm) as EventDate,
    Count(eventId) as EventCount,
	COUNT(eventReasonCodeId) AS [ReasonCount]
Into
    FilteredEventHub
FROM
	RawEventHub
Where
     eventReasonCodeId like 'ffff'
GROUP BY
    deviceId,
    ipAddress,
    deviceSerialNbr,
    operatorId,
	eventReasonCodeId,
	TumblingWindow(minute, 2)
Having
    ReasonCount > 1