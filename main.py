import tkinter as tk
import time
from datetime import datetime

BG = "#4B5E71"
PANEL = "#1b1f21"
FG = "#f2f4f3"
MUTED = "#a4afaa"
ACCENT = "#8ee0bd"
BUTTON = "#2c3431"

root = tk.Tk()
root.overrideredirect(True)
root.attributes("-topmost", True)
root.attributes("-alpha", 0.9)
root.configure(bg=BG)

root.update_idletasks()
compact_size = (300, 74)
expanded_size = (360, 342)
x = root.winfo_screenwidth() - compact_size[0] - 30
y = root.winfo_screenheight() - compact_size[1] - 70
root.geometry(f"{compact_size[0]}x{compact_size[1]}+{x}+{y}")
root.minsize(280, 74)

mode = "work"
expanded = False
work_started_at = None
work_elapsed = 0.0
countdown_total = 0.0
countdown_remaining = 0.0
countdown_started_at = None
interval_started_at = None
interval_ended_at = None
drag_origin = None
resize_origin = None


def format_duration(seconds):
    seconds = max(0, int(seconds))
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"


def current_work_elapsed():
    if work_started_at is None:
        return work_elapsed
    return work_elapsed + time.monotonic() - work_started_at


def current_countdown_remaining():
    if countdown_started_at is None:
        return countdown_remaining
    return max(0, countdown_remaining - (time.monotonic() - countdown_started_at))


def set_mode(new_mode):
    global mode
    if mode == new_mode:
        return
    if work_started_at is not None:
        stop_work()
    if countdown_started_at is not None:
        pause_countdown()
    mode = new_mode
    refresh()


def start_work():
    global work_started_at, interval_started_at, interval_ended_at
    if work_started_at is None:
        if interval_started_at is None or interval_ended_at is not None:
            interval_started_at = datetime.now()
            interval_ended_at = None
        work_started_at = time.monotonic()
    refresh()


def stop_work():
    global work_started_at, work_elapsed, interval_ended_at
    if work_started_at is not None:
        work_elapsed += time.monotonic() - work_started_at
        work_started_at = None
        interval_ended_at = datetime.now()
    refresh()


def reset_work():
    global work_started_at, work_elapsed, interval_started_at, interval_ended_at
    work_started_at = None
    work_elapsed = 0.0
    interval_started_at = None
    interval_ended_at = None
    refresh()


def start_countdown(minutes=None):
    global countdown_total, countdown_remaining, countdown_started_at
    if minutes is not None:
        countdown_started_at = None
        countdown_total = max(1, minutes) * 60
        countdown_remaining = countdown_total
    elif countdown_total <= 0 or countdown_remaining <= 0:
        countdown_started_at = None
        countdown_total = 5 * 60
        countdown_remaining = countdown_total
    if countdown_started_at is None:
        countdown_started_at = time.monotonic()
    refresh()


def pause_countdown():
    global countdown_remaining, countdown_started_at
    if countdown_started_at is not None:
        countdown_remaining = current_countdown_remaining()
        countdown_started_at = None
    refresh()


def reset_countdown():
    global countdown_remaining, countdown_started_at
    countdown_started_at = None
    countdown_remaining = countdown_total
    refresh()


def countdown_preset(minutes):
    start_countdown(minutes)


def apply_custom_time():
    try:
        minutes = int(custom_minutes.get())
    except ValueError:
        custom_minutes.set("")
        return
    if minutes > 0:
        set_mode("countdown")
        start_countdown(minutes)


def toggle_expanded():
    global expanded
    expanded = not expanded
    width, height = expanded_size if expanded else compact_size
    root.geometry(f"{width}x{height}+{root.winfo_x()}+{root.winfo_y()}")
    refresh()


def begin_drag(event):
    global drag_origin
    drag_origin = (event.x_root - root.winfo_x(), event.y_root - root.winfo_y())


def drag_window(event):
    if drag_origin is not None:
        root.geometry(
            f"+{event.x_root - drag_origin[0]}+{event.y_root - drag_origin[1]}"
        )


def end_drag(_event):
    global drag_origin
    drag_origin = None


def begin_resize(event):
    global resize_origin
    resize_origin = (
        event.x_root,
        event.y_root,
        root.winfo_width(),
        root.winfo_height(),
    )


def resize_window(event):
    if resize_origin is None:
        return
    start_x, start_y, start_width, start_height = resize_origin
    width = max(280, start_width + event.x_root - start_x)
    min_height = 342 if expanded else 74
    height = max(min_height, start_height + event.y_root - start_y)
    root.geometry(f"{width}x{height}+{root.winfo_x()}+{root.winfo_y()}")


def end_resize(_event):
    global resize_origin
    resize_origin = None


def make_button(parent, text, command, *, accent=False, width=None):
    return tk.Button(
        parent,
        text=text,
        command=command,
        width=width,
        bg=ACCENT if accent else BUTTON,
        fg=BG if accent else FG,
        activebackground=ACCENT if accent else "#3a4540",
        activeforeground=BG if accent else FG,
        relief="flat",
        bd=0,
        padx=10,
        pady=6,
        font=("Segoe UI", 9, "bold"),
        cursor="hand2",
    )


header = tk.Frame(root, bg=BG, height=28)
header.pack(fill="x", padx=12, pady=(7, 0))
header.pack_propagate(False)
title = tk.Label(
    header, text="FOCUS TIMER", bg=BG, fg=MUTED, font=("Segoe UI", 8, "bold")
)
title.pack(side="left")
title.bind("<Button-1>", begin_drag)
title.bind("<B1-Motion>", drag_window)
title.bind("<ButtonRelease-1>", end_drag)
expand_button = make_button(header, "+", toggle_expanded, width=2)
expand_button.pack(side="right", padx=(6, 0))
close_button = make_button(header, "x", lambda: root.destroy(), width=2)
close_button.pack(side="right")

display_row = tk.Frame(root, bg=BG)
display_row.pack(fill="x", padx=12)
timer_label = tk.Label(
    display_row, text="00:00:00", bg=BG, fg=FG, font=("Segoe UI", 24, "bold")
)
timer_label.pack(side="left")
status_label = tk.Label(
    display_row, text="READY", bg=BG, fg=ACCENT, font=("Segoe UI", 8, "bold")
)
status_label.pack(side="right", anchor="s", pady=(0, 7))

details = tk.Frame(root, bg=BG)
mode_row = tk.Frame(details, bg=BG)
mode_row.pack(fill="x", padx=12, pady=(11, 8))
work_mode_button = make_button(mode_row, "Work session", lambda: set_mode("work"))
work_mode_button.pack(side="left", padx=(0, 6))
countdown_mode_button = make_button(
    mode_row, "Countdown", lambda: set_mode("countdown")
)
countdown_mode_button.pack(side="left")

control_row = tk.Frame(details, bg=BG)
control_row.pack(fill="x", padx=12, pady=(0, 9))
start_button = make_button(control_row, "Start", start_work, accent=True)
start_button.pack(side="left", padx=(0, 6))
stop_button = make_button(control_row, "Stop", stop_work)
stop_button.pack(side="left", padx=(0, 6))
reset_button = make_button(control_row, "Reset", reset_work)
reset_button.pack(side="left")

interval_label = tk.Label(
    details,
    text="Work interval: not started",
    bg=BG,
    fg=MUTED,
    anchor="w",
    font=("Segoe UI", 9),
)
interval_label.pack(fill="x", padx=12, pady=(0, 10))

presets = tk.Frame(details, bg=BG)
presets.pack(fill="x", padx=12, pady=(0, 8))
for preset in (5, 10, 20):
    make_button(
        presets, f"{preset} min", lambda value=preset: countdown_preset(value)
    ).pack(side="left", padx=(0, 6))
custom_minutes = tk.StringVar()
custom_entry = tk.Entry(
    presets,
    textvariable=custom_minutes,
    width=6,
    bg=PANEL,
    fg=FG,
    insertbackground=FG,
    relief="flat",
    justify="center",
    font=("Segoe UI", 10),
)
custom_entry.pack(side="left", ipady=6, padx=(2, 5))
custom_entry.insert(0, "min")
custom_entry.bind("<FocusIn>", lambda _event: custom_minutes.set(""))
custom_entry.bind("<Return>", lambda _event: apply_custom_time())
make_button(presets, "Set", apply_custom_time).pack(side="left")

countdown_controls = tk.Frame(details, bg=BG)
countdown_controls.pack(fill="x", padx=12)
countdown_start_button = make_button(
    countdown_controls, "Start timer", start_countdown, accent=True
)
countdown_start_button.pack(side="left", padx=(0, 6))
countdown_pause_button = make_button(countdown_controls, "Pause", pause_countdown)
countdown_pause_button.pack(side="left", padx=(0, 6))
countdown_reset_button = make_button(countdown_controls, "Reset", reset_countdown)
countdown_reset_button.pack(side="left")

resize_grip = tk.Label(
    root, text="◢", bg=BG, fg=MUTED, cursor="size_nw_se", font=("Segoe UI", 10)
)
resize_grip.place(relx=1.0, rely=1.0, anchor="se", x=-3, y=-1)
resize_grip.bind("<Button-1>", begin_resize)
resize_grip.bind("<B1-Motion>", resize_window)
resize_grip.bind("<ButtonRelease-1>", end_resize)


def refresh():
    if mode == "work":
        running = work_started_at is not None
        timer_label.config(text=format_duration(current_work_elapsed()))
        status_label.config(
            text="WORKING" if running else "PAUSED" if work_elapsed else "READY"
        )
        start_button.config(
            text="Running" if running else "Start",
            state="disabled" if running else "normal",
        )
        interval_controls = "Work interval: not started"
        if interval_started_at is not None:
            end_time = "now" if running else interval_ended_at.strftime("%I:%M %p")
            interval_controls = f"Started {interval_started_at.strftime('%I:%M %p')}  ·  Ended {end_time}"
        interval_label.config(text=interval_controls)
    else:
        remaining = current_countdown_remaining()
        running = countdown_started_at is not None
        timer_label.config(text=format_duration(remaining))
        status_label.config(
            text=(
                "TIME UP"
                if remaining <= 0
                else (
                    "COUNTING DOWN"
                    if running
                    else "PAUSED" if countdown_total else "READY"
                )
            )
        )
        interval_label.config(
            text=f"Countdown length: {format_duration(countdown_total)}"
        )
    work_mode_button.config(
        bg=ACCENT if mode == "work" else BUTTON, 
        fg=BG if mode == "work" else FG
    )
    countdown_mode_button.config(
        bg=ACCENT if mode == "countdown" else BUTTON,
        fg=BG if mode == "countdown" else FG,
    )
    if expanded:
        details.pack(fill="both", expand=True)
        expand_button.config(text="−")
    else:
        details.pack_forget()
        expand_button.config(text="+")


def tick():
    refresh()
    root.after(250, tick)


root.bind("<Escape>", lambda _event: root.destroy())
refresh()
root.after(250, tick)
root.mainloop()
