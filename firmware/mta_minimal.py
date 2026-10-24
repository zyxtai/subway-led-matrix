"""Small read-only GTFS-RT subset decoder for the CircuitPython experiment.

Unknown fields are skipped; this is not a general protobuf implementation.
Returns at most four upcoming M/R predictions per configured platform.
"""
STOPS = {'G10S': 'Manhattan-bound', 'G10N': 'Forest Hills-bound'}


def varint(data, pos, end):
    value = 0
    for shift in range(0, 70, 7):
        if pos >= end:
            raise ValueError('Truncated protobuf varint')
        byte = data[pos]
        pos += 1
        value |= (byte & 127) << shift
        if not byte & 128:
            return value, pos
    raise ValueError('Oversized protobuf varint')


def fields(data, start, end):
    pos = start
    while pos < end:
        tag, pos = varint(data, pos, end)
        number, wire = tag >> 3, tag & 7
        if number == 0:
            raise ValueError('Invalid protobuf field')
        if wire == 0:
            value, pos = varint(data, pos, end)
            yield number, wire, value, 0
        else:
            if wire == 2:
                size, pos = varint(data, pos, end)
            elif wire == 1:
                size = 8
            elif wire == 5:
                size = 4
            else:
                raise ValueError('Unsupported protobuf wire type')
            stop = pos + size
            if stop > end:
                raise ValueError('Truncated protobuf field')
            yield number, wire, pos, stop
            pos = stop


def text(data, start, end):
    return bytes(data[start:end]).decode('utf-8')


def scalar(data, start, end, field, default=None):
    result = default
    for number, wire, a, b in fields(data, start, end):
        if number == field and wire == 0:
            result = a
    return result


def parse_update(data, start, end, now, arrivals):
    route = None
    trip_id = None
    relationship = 0
    for number, wire, a, b in fields(data, start, end):
        if number == 1 and wire == 2:
            for n, w, x, y in fields(data, a, b):
                if n == 1 and w == 2:
                    trip_id = text(data, x, y)
                elif n == 5 and w == 2:
                    route = text(data, x, y)
                elif n == 4 and w == 0:
                    relationship = x
    if route not in ('R', 'M') or not trip_id or relationship in (3, 7):
        return
    for number, wire, a, b in fields(data, start, end):
        if number != 2 or wire != 2:
            continue
        stop_id = None
        timestamp = None
        stop_relationship = 0
        for n, w, x, y in fields(data, a, b):
            if n == 4 and w == 2:
                stop_id = text(data, x, y)
            elif n == 2 and w == 2:
                timestamp = scalar(data, x, y, 2)
            elif n == 5 and w == 0:
                stop_relationship = x
        if stop_id not in STOPS or stop_relationship in (1, 2):
            continue
        if timestamp is None or timestamp < now or timestamp > now + 86400:
            continue
        rows = arrivals[stop_id]
        row = (timestamp, trip_id, route)
        if row not in rows:
            rows.append(row)
            rows.sort()
            del rows[4:]


def decode(data, now):
    timestamp = None
    incrementality = 0
    version = None
    # Validate freshness before reading predictions.
    for number, wire, a, b in fields(data, 0, len(data)):
        if number == 1 and wire == 2:
            timestamp = scalar(data, a, b, 3)
            incrementality = scalar(data, a, b, 2, 0)
            for n, w, x, y in fields(data, a, b):
                if n == 1 and w == 2:
                    version = text(data, x, y)
    if version not in ('1.0', '2.0') or incrementality != 0:
        raise ValueError('Unsupported feed header')
    if timestamp is None or now - timestamp > 180 or timestamp - now > 60:
        raise ValueError('Feed is stale or board clock is incorrect')
    arrivals = {stop: [] for stop in STOPS}
    for number, wire, a, b in fields(data, 0, len(data)):
        if number != 2 or wire != 2:
            continue
        if scalar(data, a, b, 2, 0):
            continue
        for n, w, x, y in fields(data, a, b):
            if n == 3 and w == 2:
                parse_update(data, x, y, now, arrivals)
    return timestamp, arrivals
