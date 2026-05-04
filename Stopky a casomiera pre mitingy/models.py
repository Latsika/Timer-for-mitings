from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk


def format_seconds(total_seconds: int) -> str:
    total_seconds = max(0, int(total_seconds))
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def parse_time_to_seconds(value: str) -> int:
    parts = value.strip().split(":")
    if len(parts) != 3:
        raise ValueError("Pouzi format HH:MM:SS")
    h, m, s = (int(p) for p in parts)
    if h < 0 or not (0 <= m < 60) or not (0 <= s < 60):
        raise ValueError("Neplatny cas")
    return h * 3600 + m * 60 + s


@dataclass
class CountdownRow:
    index: int
    name_var: tk.StringVar
    duration_var: tk.StringVar
    remaining_var: tk.StringVar
    sound_mode_var: tk.StringVar
    sound_preset_var: tk.StringVar
    sound_file_var: tk.StringVar
    running: bool = False
    remaining_seconds: int = 0
    initial_seconds: int = 0
    start_order: int = 0
    status_label: ttk.Label = None
    widgets: list = None
