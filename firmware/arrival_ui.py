"""128x32 pixel renderer: two-pixel outer border, two M/R trains per row."""
# Compact glyphs drawn at 2x for bold 10-pixel-high direction labels.
FONT = {
 ' ':('000','000','000','000','000'),
 'M':('10001','11011','10101','10001','10001'), 'N':('1001','1101','1101','1011','1001'),
 'T':('111','010','010','010','010'), 'F':('111','100','110','100','100'),
 'R':('110','101','110','101','101'), 'S':('111','100','111','001','111'),
 'H':('101','101','111','101','101'), 'L':('100','100','100','100','111'),
 '0':('111','101','101','101','111'), '1':('010','110','010','010','111'),
 '2':('110','001','010','100','111'), '3':('110','001','010','001','110'),
 '4':('101','101','111','001','001'), '5':('111','100','110','001','110'),
 '6':('011','100','111','101','111'), '7':('111','001','010','010','010'),
 '8':('111','101','111','101','111'), '9':('111','101','111','001','110'),
 '-':('000','000','111','000','000'), '+':('000','010','111','010','000'),
}
BADGE_FONT = {
    'M': ('10001', '11011', '10101', '10101', '10001', '10001', '10001'),
    'R': ('11110', '10001', '10001', '11110', '10100', '10010', '10001'),
}
# Palette: black, time white, M orange, R yellow, stale red, dim direction white.
COLORS = (0x000000, 0x101010, 0x201000, 0x202000, 0x600000, 0x101010)


def draw_text(bitmap, text, x, y, scale=1, color=1):
    for char in text:
        glyph = FONT.get(char, FONT['-'])
        for row, bits in enumerate(glyph):
            for column, bit in enumerate(bits):
                if bit == '1':
                    for dy in range(scale):
                        for dx in range(scale):
                            bitmap[x + column * scale + dx, y + row * scale + dy] = color
        x += len(glyph[0]) * scale + 1


def nearest(arrivals, now):
    return sorted((row for row in arrivals if row[0] >= now), key=lambda row: row[0])[:2]


def paint(bitmap, arrivals, now, age, failed=False):
    bitmap.fill(0)
    stale = failed or age is None or age > 90
    hidden = age is None or age > 180
    for stop, title, y in (('G10S', 'MNTN', 3), ('G10N', 'FRST HLS', 18)):
        draw_text(bitmap, title, 2, y, scale=2, color=5)
        # At most 55 px for title; slots occupy x=60..89 and x=94..123.
        trains = [] if hidden else nearest(arrivals.get(stop, []), now)
        for slot, left in enumerate((60, 94)):
            if slot >= len(trains):
                draw_text(bitmap, '--', left + 4, y + 2)
                continue
            timestamp, trip, route = trains[slot]
            cx, cy = left + 6, y + 5
            for dy in range(-6, 7):
                for dx in range(-6, 7):
                    if dx * dx + dy * dy <= 36:
                        bitmap[cx + dx, cy + dy] = 2 if route == 'M' else 3
            # Larger 5x7 black letter cut out of the colored badge.
            glyph = BADGE_FONT[route]
            for gy, bits in enumerate(glyph):
                for gx, bit in enumerate(bits):
                    if bit == '1':
                        bitmap[cx - 2 + gx, cy - 3 + gy] = 0
            minutes = display_minutes(timestamp, now, stop)
            value = str(minutes) if minutes <= 99 else '99+'
            # 2x digits; 99+ uses 1x so every value stays inside the border.
            draw_text(bitmap, value, left + 15, y, scale=2 if len(value) <= 2 else 1)
        if stale:
            # Visible stale indicator between the labels and badges; border stays black.
            bitmap[58, y + 3] = 4
            bitmap[58, y + 4] = 4
            bitmap[58, y + 6] = 4
    return 'STALE' if stale else 'LIVE'


def visual_key(arrivals, now, age, failed=False):
    """Only repaint when pixels would change, rather than on every clock tick."""
    stale = failed or age is None or age > 90
    hidden = age is None or age > 180
    key = [stale]
    for stop in ('G10S', 'G10N'):
        trains = [] if hidden else nearest(arrivals.get(stop, []), now)
        key.append(tuple((row[2], min(100, display_minutes(row[0], now, stop))) for row in trains))
    return tuple(key)


def display_minutes(timestamp, now, stop):
    minutes = (timestamp - now + 59) // 60
    return max(0, minutes - (1 if stop == 'G10S' else 0))
