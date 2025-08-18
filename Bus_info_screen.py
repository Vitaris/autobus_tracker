import tkinter as tk
import schedule
import logging
from daily_scheduler import DailyScheduler

HEADER_TEXTS = ["ODCHOD", "SMER", "AKTUÁLNE", "MEŠKANIE"]
ROWS = 8

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
    row_height = h / ROWS

    # Draw rectangle above the header
    canvas.create_rectangle(0, 0, w, row_height, fill='#303030')

    # Header line
    canvas.create_line(0, row_height, w, row_height, fill=LINE_COLOR, width=4)

    # Columns lines
    for i in range(1, cols):
        x = i * col_width
        canvas.create_line(x, row_height, x, h, fill=LINE_COLOR, width=1)


    # Write header texts
    cx = col_width / 2
    i = 0
    for header in HEADER_TEXTS:
        canvas.create_text(
            cx, row_height / 2,
            text=HEADER_TEXTS[i],
            fill=TEXT_COLOR,
            font=("Segoe UI", 32, "bold")
        )
        cx += col_width
        i += 1




    cx = col_width / 2
    cy = row_height + row_height / 2  # start below header
    # Get ordered list of trips (preserves previous sorting)
    items = list(screen_content.items())
    max_rows = min(ROWS - 1, len(items))
    columns_ratio  = [-0.45, -1.1, 0, 0]
    for row_idx in range(max_rows):
        trip_id, info = items[row_idx]
        # Example columns: SMER(finalStop), ODCHOD(selectedDeparture), AKTUÁLNE(blank), MEŠKANIE(blank)
        col_texts = [
            info.get('selectedDeparture', ''),
            info.get('finalStop', ''),
            info.get('current', ''),      # placeholder
            info.get('delay', '')         # placeholder
        ]
        for col_idx, text in enumerate(col_texts):
            x = (col_idx + 0.5) * col_width
            x += col_width * columns_ratio[col_idx] # Adjust width based on ratio
            canvas.create_text(
                x, cy,
                text=text,
                fill=TEXT_COLOR,
                font=("Segoe UI", 64, "bold"),
                anchor="w"

            )
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