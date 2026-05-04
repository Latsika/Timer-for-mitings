import argparse
import tkinter as tk
from pathlib import Path

from audio import AudioMixin
from models import format_seconds
from profile_io import ProfileIOMixin
from timers import TimersMixin
from ui import UIMixin


class MeetingTimerApp(UIMixin, TimersMixin, AudioMixin, ProfileIOMixin):
    WS_EX_LAYERED = 0x00080000
    WS_EX_TRANSPARENT = 0x00000020
    GWL_EXSTYLE = -20

    def __init__(self, root: tk.Tk, startup_profile: str | None = None):
        self.root = root
        self.root.title("Stopky a Casomiera pre Mitingy")
        self.root.geometry("1300x780")
        self.root.minsize(1020, 600)

        self.sound_presets = [
            "Classic Beep", "Double Beep", "Triple Beep", "High Ping", "Low Ping",
            "Rising Tone", "Falling Tone", "Alarm Short", "Alarm Long", "Notification",
            "Ta-Da", "Voice: Time is up", "Voice: Hey your time is up, did you hear me?",
            "Voice: Wrap it up please", "Voice: Next speaker now",
        ]

        self.mode_var = tk.StringVar(value="countdown")
        self.stopwatch_running = False
        self.stopwatch_seconds = 0
        self.stopwatch_start_seconds = 0
        self.stopwatch_display_var = tk.StringVar(value="00:00:00")
        self.stopwatch_start_var = tk.StringVar(value="00:00:00")
        self.max_countdowns = 20
        self.countdowns = []
        self.live_source_var = tk.StringVar(value="countdown")
        self.live_on_top_var = tk.BooleanVar(value=True)
        self.live_click_through_var = tk.BooleanVar(value=False)
        self.dark_mode_var = tk.BooleanVar(value=False)
        self.auto_next_var = tk.BooleanVar(value=False)
        self.sound_enabled_var = tk.BooleanVar(value=True)
        self.lock_edit_var = tk.BooleanVar(value=False)
        self.live_countdown_index = 1
        self.live_last_started_order = 0
        self.live_time_font_base = 64
        self.live_time_font_size = 64
        self.live_title_font_size = 18
        self.live_font_update_job = None
        self.history = []
        self.profile_path_var = tk.StringVar(value="")

        self._build_ui()
        self._build_live_popup()
        self._bind_shortcuts()
        self._apply_theme()
        self._tick()
        if startup_profile:
            self._load_profile(Path(startup_profile), quiet=False)


def parse_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--profile", type=str, default=None)
    return parser.parse_args()


def main():
    args = parse_args()
    root = tk.Tk()
    app = MeetingTimerApp(root, startup_profile=args.profile)
    app.stopwatch_seconds = app.stopwatch_start_seconds
    app.stopwatch_display_var.set(format_seconds(app.stopwatch_seconds))
    root.mainloop()


if __name__ == "__main__":
    main()
