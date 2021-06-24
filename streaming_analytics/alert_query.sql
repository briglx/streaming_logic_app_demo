SELECT
    E.deviceId,
    E.ipAddress,
    E.operatorId,
    E.deviceSerialNbr,
    Collect(E.eventId) as eventId,
    Collect(E.event) as event,
    L.Description as eventDescription,
    Collect(E.eventName) as eventName,
    Collect(E.setOrClear) as setOrClear,
    Collect(E.stopPointId) as stopPointId,
	E.eventReasonCodeId,
    Collect(E.eventDtm) as EventDate,
    Count(E.eventId) as EventCount,
	COUNT(E.eventReasonCodeId) AS [ReasonCount]
Into
    FilteredEventHub
FROM
	RawEventHub E
JOIN
    EventNameLookup L
ON E.eventId = L.Code  
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