"""128x32 pixel renderer: two-pixel outer border, two visible E/F/M/R trains with alternating pages per row."""
from station_config import MANHATTAN_STOP, QUEENS_STOP

# Compact glyphs drawn at 2x for bold 10-pixel-high direction labels.
FONT = {
 'A':('010','101','111','101','101'),
 'E':('111','100','110','100','111'),
 'O':('111','101','101','101','111'),
 'I':('111','010','010','010','111'),
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
    'E': ('11111', '10000', '10000', '11110', '10000', '10000', '11111'),
    'F': ('11111', '10000', '10000', '11110', '10000', '10000', '10000'),
    'R': ('11110', '10001', '10001', '11110', '10100', '10010', '10001'),
}
# Palette: black, time white, M orange, R yellow, stale red, dim direction white.
COLORS = (0x000000, 0x101010, 0x602000, 0x202000, 0x600000, 0x101010, 0x000030, 0x602000)


def draw_text(bitmap, text, x, y, scale=1, color=1, clip=None):
    for char in text:
        glyph = FONT.get(char, FONT['-'])
        for row, bits in enumerate(glyph):
            for column, bit in enumerate(bits):
                if bit == '1':
                    for dy in range(scale):
                        for dx in range(scale):
                            px = x + column * scale + dx
                            if clip is None or clip[0] <= px <= clip[1]:
                                bitmap[px, y + row * scale + dy] = color
        x += len(glyph[0]) * scale + 1


def nearest(arrivals, now, page=0):
    upcoming = sorted((row for row in arrivals if row[0] >= now), key=lambda row: row[0])[:4]
    start = 2*page if len(upcoming)>2 else 0
    return upcoming[start:start+2]


def paint(bitmap, arrivals, now, age, failed=False, scroll_step=None, flip_step=None):
    page, squeeze = flip_state(flip_step or 0)
    bitmap.fill(0)
    stale = failed or age is None or age > 90
    hidden = age is None or age > 180
    for stop, title, y in ((MANHATTAN_STOP, 'MANHATTAN', 3), (QUEENS_STOP, 'FOREST HILLS', 18)):
        # Identical x coordinate and wrap period keep both leading letters aligned.
        label_x = 2 if scroll_step is None else scroll_x(scroll_step)
        draw_text(bitmap, title, label_x, y, scale=2, color=5, clip=(2, 56))
        if scroll_step is not None:
            draw_text(bitmap, title, label_x + scroll_period(), y, scale=2, color=5, clip=(2, 56))
        # Wide label viewport restored; train slots at x=60 and x=94.
        trains = [] if hidden else nearest(arrivals.get(stop, []), now, page)
        for slot, left in enumerate((60, 94)):
            if slot >= len(trains):
                draw_text(bitmap, '--', left + 4, y + 2)
                continue
            timestamp, trip, route = trains[slot][:3]
            cx, cy = left + 6, y + 5
            for dy in range(-6, 7):
                for dx in range(-6, 7):
                    if dx * dx + dy * dy <= 36:
                        bitmap[cx + dx, cy + dy] = {'E': 6, 'F': 7, 'M': 2, 'R': 3}[route]
            # Larger 5x7 black letter cut out of the colored badge.
            glyph = BADGE_FONT[route]
            for gy, bits in enumerate(glyph):
                for gx, bit in enumerate(bits):
                    if bit == '1':
                        bitmap[cx - 2 + gx, cy - 3 + gy] = 0
            minutes = display_minutes(timestamp, now, stop)
            value = str(minutes) if minutes <= 99 else '99+'
            # Restore large time digits.
            draw_text(bitmap, value, left + 15, y, scale=2 if len(value)<=2 else 1)
        if stale:
            # Stale status below label; x=57..59 stays a three-pixel badge gap.
            bitmap[2, y + 11] = 4
            bitmap[3, y + 11] = 4
            bitmap[4, y + 11] = 4
    if squeeze:
        squeeze_trains(bitmap,squeeze)
    return 'STALE' if stale else 'LIVE'


def visual_key(arrivals, now, age, failed=False):
    """Only repaint when pixels would change, rather than on every clock tick."""
    stale = failed or age is None or age > 90
    hidden = age is None or age > 180
    key = [stale]
    for stop in (MANHATTAN_STOP, QUEENS_STOP):
        trains = [] if hidden else nearest(arrivals.get(stop, []), now)
        key.append(tuple((row[2], min(100, display_minutes(row[0], now, stop))) for row in trains))
    return tuple(key)


def display_minutes(timestamp, now, stop):
    minutes = (timestamp - now + 59) // 60
    return max(0, minutes - 1)


def text_width(text, scale=2):
    return sum(len(FONT[c][0]) * scale + 1 for c in text) - 1


def scroll_period():
    # Eight black columns after the longer name; shared spacing keeps initials aligned.
    return max(text_width('MANHATTAN'), text_width('FOREST HILLS')) + 8


def scroll_x(step):
    return 2 - (int(step) % scroll_period())


def flip_state(step):
    step=int(step)
    page=(step//60)%2
    phase=step%60
    # Six-second page interval; a 1.2-second collapse/expand transition.
    if phase<48:return page,0
    levels=(1,2,3,4,5,6,6,5,4,3,2,1)
    return (page if phase<54 else 1-page),levels[phase-48]


def squeeze_trains(bitmap,amount):
    for top in (2,17):
        original=bytearray(bitmap[x,y] for y in range(top,top+13) for x in range(60,126))
        for y in range(top,top+13):
            for x in range(60,126):bitmap[x,y]=0
        if amount>=6:continue
        for row in range(13):
            target=top+6+round((row-6)*(6-amount)/6)
            for column in range(66):
                color=original[row*66+column]
                if color:bitmap[60+column,target]=color
