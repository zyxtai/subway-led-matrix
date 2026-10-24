import time
import displayio
import terminalio
from adafruit_matrixportal.matrix import Matrix
from adafruit_display_text import label

# Two 64x32 panels chained horizontally form one 128x32 display.
matrix = Matrix(width=128, height=32, bit_depth=2)
display = matrix.display

group = displayio.Group()
message = label.Label(
    terminalio.FONT,
    text="HELLO ALEX",
    color=0x404000,
    scale=2,
)
message.anchor_point = (0.5, 0.5)
message.anchored_position = (64, 16)
group.append(message)

display.root_group = group
print("Dual-panel 128x32 text test running: HELLO ALEX")

while True:
    time.sleep(1)
