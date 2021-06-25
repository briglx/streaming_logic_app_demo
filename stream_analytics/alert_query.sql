SELECT
    E.deviceId,
    E.ipAddress,
    E.operatorId,
    E.deviceSerialNbr,
    CAST( E.eventId AS bigint) as eventId,
    L.Code,
    L.Description as eventDescription,
    'AlertQuery' as Source
Into
    FilteredEventHub
FROM
	RawEventHub E
JOIN
    EventNameLookup L
ON 
    E.eventId = CAST( L.Code AS bigint) 
Where
    E.eventId <> 100
