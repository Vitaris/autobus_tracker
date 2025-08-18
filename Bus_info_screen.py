import tkinter as tk
from random import random
from random import choice

import schedule
import logging
from daily_scheduler import DailyScheduler

HEADER_TEXTS = ["ODCHOD", "SMER", "MEŠKÁ"]
HEADER_HEIGHT = 100  # Height of the header in pixels
COLUMNS_RATIOS = [0.14, 0.74, 0.12]
ROWS = 6  # Number of rows to display (excluding header)

# Per‑cell background colors (None = uses global BG_COLOR)
CELL_BG_COLORS = [
    (None, None),
    ("#004400", "#220000"),   # Row 1 (index 1)
    ("#003366", "#331100"),   # Row 2 (index 2)
]

# Cells that should flash: (row_index, col_index): {alt: alt_color, interval: ms}
# This example flashes the Pezinok delay cell (row 1, col 1).
FLASH_CELLS = {
    (1, 1): {"alt": "#ff0000", "interval": 700},
}

LINE_COLOR = "white"
TEXT_COLOR = "white"
BG_COLOR = "black"

# Will hold rectangle item IDs for each cell: (r, c) -> canvas id
CELL_RECTS = {}

logger = logging.getLogger("autobus_tracker")
logger.info("Bus delay monitor starting")

scheduler_pezinok = DailyScheduler("bus_527_Pezinok.json")
scheduler_bratislava = DailyScheduler("bus_527_Bratislava.json")
screen_content = scheduler_pezinok.get_screen_content()
screen_content.update(scheduler_bratislava.get_screen_content())

# sort screen_content by selectedDeparture
screen_content = dict(sorted(screen_content.items(), key=lambda item: item[1]['selectedDeparture']))


def draw_header(canvas):
    canvas.delete("all")
    CELL_RECTS.clear()

    w = canvas.winfo_width()
    h = canvas.winfo_height()

    cols = len(HEADER_TEXTS)
    col_width = w / cols
    row_height = (h - HEADER_HEIGHT) / ROWS

    # Draw header background rectangle
    canvas.create_rectangle(0, 0, w, HEADER_HEIGHT, fill='#206020')

    # Header horizontal line
    canvas.create_line(0, HEADER_HEIGHT, w, HEADER_HEIGHT, fill=LINE_COLOR, width=4)

    # Write header texts
    cx = 0
    for idx, header in enumerate(HEADER_TEXTS):
        cx += w * COLUMNS_RATIOS[idx] / 2 # Add first half of the column width
        canvas.create_text(
            cx, HEADER_HEIGHT / 2,
            text=header,
            fill=TEXT_COLOR,
            font=("Segoe UI", 40, "bold")
        )
        cx += w * COLUMNS_RATIOS[idx] / 2 # Add second half of the column width

    # Columns lines
    x = 0
    for i in range(1, cols):
        x += w * COLUMNS_RATIOS[i - 1]
        canvas.create_line(x, HEADER_HEIGHT, x, h, fill=LINE_COLOR, width=1)

    # Timetable texts
    cx = col_width / 2
    cy = HEADER_HEIGHT + row_height / 2  # start below header

    # Get ordered list of trips (preserves previous sorting)
    items = list(screen_content.items())

    for row_idx in range(ROWS):
        trip_id, info = items[row_idx]
        col_texts = [
            info.get('selectedDeparture', ''),
            info.get('finalStop', ''),
            info.get('delay', f'{choice([1, 3, 5, 20])}')         # placeholder
        ]
        x = 0
        for col_idx, text in enumerate(col_texts):
            x += w * COLUMNS_RATIOS[col_idx] / 2 # Add first half of the column width
            if col_idx == 1:
                anchor = "w"
                cx = x - w * COLUMNS_RATIOS[col_idx] / 2 + 10
            else:
                anchor = "center"
                cx = x
            canvas.create_text(
                cx, cy,
                text=text,
                fill=TEXT_COLOR,
                font=("Segoe UI", 72, "bold"),
                anchor=anchor
            )
            x += w * COLUMNS_RATIOS[col_idx] / 2  # Add second half of the column width
        cy += row_height

def main():
    root = tk.Tk()
    root.title("Bus Info Screen")
    root.configure(bg=BG_COLOR)
    root.attributes("-fullscreen", True)
    root.bind("<Escape>", lambda e: root.destroy())
    root.bind("q", lambda e: root.destroy())

    canvas = tk.Canvas(root, bg=BG_COLOR, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    canvas.bind("<Configure>", lambda e: draw_header(canvas))


    def tick():
        schedule.run_pending()
        root.after(1000, tick)


    root.after(1000, tick)
    root.mainloop()

if __name__ == "__main__":
    main()