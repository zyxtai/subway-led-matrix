"""Transparent pixel-art cat/rainbow overlay; never changes the arrival bitmap."""
COLORS = (0x000000, 0x101010, 0x202020, 0x301020, 0x301800,
          0x300000, 0x302000, 0x202000, 0x002000, 0x001020, 0x100020)


def paint(bitmap, step, active, seconds=0):
    bitmap.fill(0)
    if not active:
        return
    # 2x sprite (40x24 px); pass begins every 10 seconds during minute 00.
    seconds = max(0, min(60, seconds))
    pass_number = int(seconds // 10)
    progress = seconds - pass_number * 10
    left = 126 - int(progress * 18)
    top = 3
    # Rainbow accumulates after pass one. Last pass wipes it right-to-left
    # behind the cat, reaching the left edge before the minute ends.
    if pass_number == 0:
        trail_left, trail_right = left + 34, 125
    elif pass_number < 5:
        trail_left, trail_right = 2, 125
    else:
        trail_left, trail_right = 2, min(125,left+34)
    for stripe in range(6):
        for y in range(9+stripe*2,11+stripe*2):
            for x in range(max(2,trail_left),trail_right+1):
                bitmap[x,y] = stripe+5

    def pixel(x, y, color):
        for dx in range(2):
            for dy in range(2):
                px,py = left+x*2+dx,top+y*2+dy
                if 2<=px<=125 and 2<=py<=29:
                    bitmap[px,py] = color

    # Pastry body: toasted edge, pink center and tiny sprinkles.
    for y in range(2, 10):
        for x in range(6, 17):
            pixel(x,y,4 if x in (6,16) or y in (2,9) else 3)
    for x,y in ((8,4),(12,3),(14,6),(10,7),(13,8)):
        pixel(x,y,1)
    # Gray head, pointed ears, dark eyes, and pink cheek.
    for y in range(4, 10):
        for x in range(1, 7):
            pixel(x,y,2)
    for x,y in ((1,2),(1,3),(2,3),(5,2),(5,3),(6,3)):
        pixel(x,y,2)
    for x,y in ((1,6),(4,6),(2,8),(3,8)):
        pixel(x,y,1)  # Dark face features use dim neutral gray.
    pixel(1,7,3)
    # Animated feet and raised tail.
    foot = (int(step)//2)%2
    for x in (4,8,13):
        pixel(x+foot,10,2)
        pixel(x+foot,11,2)
    for x,y in ((17,7),(18,7),(19,6),(19,5)):
        pixel(x,y,2)
