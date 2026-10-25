"""Active service-alert selectors, without copying large descriptive text."""
from mta_minimal import fields, scalar, text


def decode(data, now):
    timestamp = None
    for n, w, a, b in fields(data, 0, len(data)):
        if n == 1 and w == 2:
            timestamp = scalar(data, a, b, 3)
            if scalar(data, a, b, 2, 0) != 0:
                raise ValueError('Differential alerts unsupported')
    if timestamp is None or now - timestamp > 900 or timestamp - now > 60:
        raise ValueError('Alert feed stale or clock incorrect')
    selectors = []
    for n, w, a, b in fields(data, 0, len(data)):
        if n != 2 or w != 2 or scalar(data, a, b, 2, 0):
            continue
        for en, ew, x, y in fields(data, a, b):
            if en != 5 or ew != 2:
                continue
            periods = []
            spans = []
            for an, aw, c, d in fields(data, x, y):
                if an == 1 and aw == 2:
                    periods.append((scalar(data, c, d, 1), scalar(data, c, d, 2)))
                elif an == 5 and aw == 2:
                    spans.append((c, d))
            for c, d in spans:
                route = stop = trip = direction = agency = route_type = None
                for sn, sw, v, z in fields(data, c, d):
                    if sn == 1 and sw == 2:
                        agency = text(data, v, z)
                    elif sn == 2 and sw == 2:
                        route = text(data, v, z)
                    elif sn == 3 and sw == 0:
                        route_type = v
                    elif sn == 4 and sw == 2:
                        for tn, tw, u, end in fields(data, v, z):
                            if tn == 1 and tw == 2:
                                trip = text(data, u, end)
                            elif tn == 5 and tw == 2 and route is None:
                                route = text(data, u, end)
                            elif tn == 6 and tw == 0:
                                direction = u
                    elif sn == 5 and sw == 2:
                        stop = text(data, v, z)
                    elif sn == 6 and sw == 0:
                        direction = v
                if route is not None and route not in ('E', 'F', 'M', 'R'):
                    continue
                if stop is not None and stop not in ('G10', 'G10N', 'G10S'):
                    continue
                # NYCT subway agency; ignore selectors from other transit agencies.
                if agency not in (None, 'MTA NYCT', 'NYCT', 'MTASBWY') or route_type not in (None, 1):
                    continue
                if route is None and stop is None and trip is None:
                    continue
                selectors.append((route, stop, trip, direction, tuple(periods)))
                if len(selectors) > 1024:
                    raise ValueError('Too many alert selectors')
    return timestamp, selectors
