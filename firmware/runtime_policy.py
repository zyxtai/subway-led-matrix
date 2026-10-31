import time
"""Hardware-independent New York schedule and per-feed freshness policy."""

def sunday_day(year, month):
    # Gregorian weekday, Sunday=0 (Sakamoto).
    offsets = (0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4)
    y = year - (1 if month < 3 else 0)
    weekday = (y + y // 4 - y // 100 + y // 400 + offsets[month-1] + 1) % 7
    return 1 + (-weekday) % 7


def utc_offset(utc):
    year, month, day, hour = utc[:4]
    if 3 < month < 11:
        return -4
    if month < 3 or month > 11:
        return -5
    boundary = sunday_day(year, month) + (7 if month == 3 else 0)
    after = (day, hour) >= (boundary, 7 if month == 3 else 6)
    return (-4 if after else -5) if month == 3 else (-5 if after else -4)


def rush(local):
    minutes = local[3] * 60 + local[4]
    return 300 <= minutes < 510


def reboot_minute(local):
    return local[3] == 4 and local[4] == 59


def daily_remaining(local):
    seconds = local[3]*3600 + local[4]*60 + local[5]
    return 4*3600 + 59*60 - seconds


def scaled_colors(colors, normal):
    if normal:
        return colors
    dimmed = [sum((max(4, (color >> shift & 255) // 8) if (color >> shift & 255) else 0) << shift for shift in (16,8,0)) for color in colors]
    if len(colors) > 3 and colors[3] == 0x202000:
        dimmed[3] = 0x080800  # Keep the R yellow legible in off-hours mode.
    if len(colors) > 6:
        dimmed[6] = 0x000008  # Slightly brighter off-hours E blue.
    # Raise white text above the lowest PWM level to reduce the greenish appearance.
    for index in (1,5):
        if len(colors) > index and colors[index] == 0x101010:
            dimmed[index] = 0x101010
    return tuple(dimmed)


class FeedCache:
    def __init__(self, names, stops):
        self.stops = tuple(stops)
        self.entries = {name: {'rows': {}, 'timestamp': None, 'failed': False} for name in names}

    def success(self, name, rows, timestamp):
        self.entries[name] = {'rows': rows, 'timestamp': timestamp, 'failed': False}

    def failure(self, name):
        self.entries[name]['failed'] = True

    def snapshot(self, now):
        merged = {stop: [] for stop in self.stops}
        ages = []
        warning = False
        for item in self.entries.values():
            stamp = item['timestamp']
            age = None if stamp is None else now - stamp
            warning = warning or item['failed'] or age is None or age > 90
            if age is None or age > 180 or age < -60:
                continue
            ages.append(max(0,age))
            for stop in self.stops:
                merged[stop].extend(row for row in item['rows'].get(stop,()) if row[0] >= now)
        merged = {stop: sorted(set(rows))[:24] for stop, rows in merged.items()}
        # Each feed was already filtered for expiry; one old feed cannot hide the rest.
        return merged, (min(ages) if ages else None), warning


def nyan_active(local):
    return not rush(local) and local[4] == 0


def overnight(local):
    minutes = local[3]*60 + local[4]
    return minutes >= 8*60+30 or minutes < 4*60+59


def wake_delay(native_now):
    """Seconds to next 04:59 New York; handles overnight DST changes."""
    utc=time.localtime(native_now)
    local=time.localtime(native_now+utc_offset(utc)*3600)
    naive=time.mktime((local[0],local[1],local[2],4,59,0,0,-1,-1))
    if local[3]*60+local[4] >= 8*60+30:
        naive+=86400
    guess=naive+5*3600
    target=naive-utc_offset(time.localtime(guess))*3600
    return max(1,target-native_now)


def standby_interval(native_now):
    # Frequent checks; target the final 04:59 boundary rather than oversleep it.
    return min(60, wake_delay(native_now))
