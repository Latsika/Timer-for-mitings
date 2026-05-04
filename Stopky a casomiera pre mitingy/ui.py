import ctypes
import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, messagebox, ttk

from models import CountdownRow


class UIMixin:
    def _build_ui(self):
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill=tk.BOTH, expand=True)

        top = ttk.LabelFrame(main, text="Rezim a Ovladanie", padding=8)
        top.pack(fill=tk.X)
        ttk.Radiobutton(top, text="Stopky", value="stopwatch", variable=self.mode_var, command=self._on_mode_change).pack(side=tk.LEFT, padx=4)
        ttk.Radiobutton(top, text="Countdown", value="countdown", variable=self.mode_var, command=self._on_mode_change).pack(side=tk.LEFT, padx=4)
        ttk.Checkbutton(top, text="Auto-next", variable=self.auto_next_var).pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(top, text="Zamknut editaciu pocas behu", variable=self.lock_edit_var, command=self._apply_lock_state).pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(top, text="Dark mode", variable=self.dark_mode_var, command=self._apply_theme).pack(side=tk.LEFT, padx=10)

        profile = ttk.LabelFrame(main, text="Profily / PPT", padding=8)
        profile.pack(fill=tk.X, pady=(8, 0))
        ttk.Entry(profile, textvariable=self.profile_path_var, width=80).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(profile, text="Ulozit profil", command=self._save_profile_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(profile, text="Nacitat profil", command=self._load_profile_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(profile, text="Export log CSV", command=self._export_history_csv).pack(side=tk.LEFT, padx=2)
        ttk.Button(profile, text="Vytvorit PPT makro navod", command=self._create_ppt_macro_guide).pack(side=tk.LEFT, padx=2)

        self.stopwatch_frame = ttk.LabelFrame(main, text="Stopky", padding=10)
        self.stopwatch_frame.pack(fill=tk.X, pady=(8, 0))
        row = ttk.Frame(self.stopwatch_frame)
        row.pack(fill=tk.X)
        ttk.Label(row, text="Start od HH:MM:SS").pack(side=tk.LEFT)
        self.stopwatch_entry = ttk.Entry(row, textvariable=self.stopwatch_start_var, width=12)
        self.stopwatch_entry.pack(side=tk.LEFT, padx=(6, 10))
        ttk.Button(row, text="Nastavit", command=self._set_stopwatch_start).pack(side=tk.LEFT, padx=2)
        ttk.Button(row, text="Start", command=self._start_stopwatch).pack(side=tk.LEFT, padx=2)
        ttk.Button(row, text="Pause", command=self._pause_stopwatch).pack(side=tk.LEFT, padx=2)
        ttk.Button(row, text="Zastavit", command=self._stop_stopwatch).pack(side=tk.LEFT, padx=2)
        ttk.Button(row, text="Reset", command=self._reset_stopwatch).pack(side=tk.LEFT, padx=2)
        ttk.Label(self.stopwatch_frame, textvariable=self.stopwatch_display_var, font=("Segoe UI", 28, "bold")).pack(anchor=tk.W, pady=(8, 0))

        countdown_box = ttk.LabelFrame(main, text="Countdowny (20)", padding=10)
        countdown_box.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
        header = ttk.Frame(countdown_box)
        header.pack(fill=tk.X)
        for txt, w in [("Nazov", 24), ("Cas HH:MM:SS", 14), ("Zostava", 14), ("Akcie", 44), ("Stav", 12)]:
            ttk.Label(header, text=txt, width=w).pack(side=tk.LEFT)

        shell = ttk.Frame(countdown_box)
        shell.pack(fill=tk.BOTH, expand=True, pady=(4, 0))
        shell.columnconfigure(0, weight=1)
        shell.rowconfigure(0, weight=1)
        self.canvas = tk.Canvas(shell, highlightthickness=0)
        sb = ttk.Scrollbar(shell, orient="vertical", command=self.canvas.yview)
        self.rows_container = ttk.Frame(self.canvas)
        self.rows_container.bind("<Configure>", lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.rows_window = self.canvas.create_window((0, 0), window=self.rows_container, anchor="nw")
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self.rows_window, width=e.width))
        self.canvas.configure(yscrollcommand=sb.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        sb.grid(row=0, column=1, sticky="ns")

        for i in range(self.max_countdowns):
            r = CountdownRow(
                index=i + 1,
                name_var=tk.StringVar(value=f"Casovac {i + 1}"),
                duration_var=tk.StringVar(value="00:05:00"),
                remaining_var=tk.StringVar(value="00:05:00"),
                sound_mode_var=tk.StringVar(value="preset"),
                sound_preset_var=tk.StringVar(value="Classic Beep"),
                sound_file_var=tk.StringVar(value=""),
                widgets=[],
            )
            frame = ttk.Frame(self.rows_container)
            frame.pack(fill=tk.X, pady=1)
            idx = ttk.Label(frame, text=f"{r.index:02d}", width=4)
            idx.pack(side=tk.LEFT)
            name_e = ttk.Entry(frame, textvariable=r.name_var, width=24)
            name_e.pack(side=tk.LEFT, padx=2)
            dur_e = ttk.Entry(frame, textvariable=r.duration_var, width=14)
            dur_e.pack(side=tk.LEFT, padx=2)
            ttk.Label(frame, textvariable=r.remaining_var, width=14).pack(side=tk.LEFT, padx=2)
            ttk.Button(frame, text="Start", command=lambda x=r: self._start_countdown(x)).pack(side=tk.LEFT, padx=1)
            ttk.Button(frame, text="Pause", command=lambda x=r: self._pause_countdown(x)).pack(side=tk.LEFT, padx=1)
            ttk.Button(frame, text="Stop", command=lambda x=r: self._stop_countdown(x)).pack(side=tk.LEFT, padx=1)
            ttk.Button(frame, text="Reset", command=lambda x=r: self._reset_countdown(x)).pack(side=tk.LEFT, padx=1)
            ttk.Button(frame, text="Zvuk", command=lambda x=r: self._open_countdown_sound_dialog(x)).pack(side=tk.LEFT, padx=1)
            r.status_label = ttk.Label(frame, text="Pripraveny", width=12)
            r.status_label.pack(side=tk.LEFT, padx=6)
            r.widgets = [name_e, dur_e]
            self.countdowns.append(r)

        live = ttk.LabelFrame(main, text="LIVE Popup", padding=8)
        live.pack(fill=tk.X, pady=(8, 0))
        ttk.Radiobutton(live, text="Stopky", value="stopwatch", variable=self.live_source_var, command=self._refresh_live_label).pack(side=tk.LEFT, padx=4)
        ttk.Radiobutton(live, text="Countdown", value="countdown", variable=self.live_source_var, command=self._refresh_live_label).pack(side=tk.LEFT, padx=4)
        ttk.Checkbutton(live, text="Always on top", variable=self.live_on_top_var, command=self._toggle_live_on_top).pack(side=tk.LEFT, padx=8)
        ttk.Checkbutton(live, text="Click-through", variable=self.live_click_through_var, command=self._toggle_click_through).pack(side=tk.LEFT, padx=8)
        ttk.Checkbutton(live, text="Zvuk po konci", variable=self.sound_enabled_var).pack(side=tk.LEFT, padx=8)
        ttk.Button(live, text="Fullscreen LIVE", command=self._toggle_live_fullscreen).pack(side=tk.RIGHT, padx=(4, 0))
        ttk.Button(live, text="Zobrazit/Skryt LIVE", command=self._toggle_live_popup).pack(side=tk.RIGHT)

        self._on_mode_change()

    def _build_live_popup(self):
        self.live_popup = tk.Toplevel(self.root)
        self.live_popup.title("LIVE Cas")
        self.live_popup.geometry("620x220+90+90")
        self.live_popup.attributes("-topmost", True)
        self.live_popup.protocol("WM_DELETE_WINDOW", self._hide_live_popup)
        self.live_popup.bind("<F11>", lambda _e: self._toggle_live_fullscreen())
        self.live_popup.bind("<Escape>", lambda _e: self._exit_live_fullscreen())
        self.live_popup.bind("<Configure>", self._on_live_resize)
        wrap = ttk.Frame(self.live_popup, padding=10)
        wrap.pack(fill=tk.BOTH, expand=True)
        wrap.columnconfigure(0, weight=1)
        wrap.rowconfigure(0, weight=1)
        wrap.rowconfigure(1, weight=0)
        wrap.rowconfigure(2, weight=1)
        wrap.rowconfigure(3, weight=0)
        self.live_title_var = tk.StringVar(value="COUNTDOWN")
        self.live_time_var = tk.StringVar(value="00:00:00")
        self.live_label_title = ttk.Label(wrap, textvariable=self.live_title_var, font=("Segoe UI", self.live_title_font_size, "bold"))
        self.live_label_title.grid(row=1, column=0, pady=(4, 0))
        self.live_label_time = ttk.Label(wrap, textvariable=self.live_time_var, font=("Segoe UI", self.live_time_font_size, "bold"), foreground="#1f7a1f")
        self.live_label_time.grid(row=2, column=0, pady=(4, 8), sticky="n")
        self.live_controls = ttk.Frame(wrap)
        self.live_controls.grid(row=3, column=0, pady=(4, 0))
        ttk.Button(self.live_controls, text="-", width=3, command=lambda: self._change_live_font_size(-4)).pack(side=tk.LEFT, padx=4)
        ttk.Button(self.live_controls, text="+", width=3, command=lambda: self._change_live_font_size(4)).pack(side=tk.LEFT, padx=4)
        ttk.Button(self.live_controls, text="Skryt", command=self._hide_live_popup).pack(side=tk.LEFT, padx=(10, 0))

    def _bind_shortcuts(self):
        self.root.bind("<space>", lambda _e: self._shortcut_toggle())
        self.root.bind("s", lambda _e: self._shortcut_stop())
        self.root.bind("n", lambda _e: self._start_next_ready())
        self.root.bind("l", lambda _e: self._toggle_live_popup())
        self.root.bind("<F11>", lambda _e: self._toggle_live_fullscreen())
        self.root.bind("<Escape>", lambda _e: self._exit_live_fullscreen())

    def _apply_theme(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        dark = self.dark_mode_var.get()

        if dark:
            bg = "#1f1f1f"
            surface = "#2a2a2a"
            fg = "#f2f2f2"
            entry_bg = "#333333"
            accent = "#4d7fff"
            self.root.configure(bg=bg)
            self.live_popup.configure(bg=bg)
            self.canvas.configure(bg=bg)
        else:
            bg = "#f0f0f0"
            surface = "#ffffff"
            fg = "#111111"
            entry_bg = "#ffffff"
            accent = "#2e5fff"
            self.root.configure(bg=bg)
            self.live_popup.configure(bg=bg)
            self.canvas.configure(bg=bg)

        style.configure(".", background=bg, foreground=fg)
        style.configure("TFrame", background=bg)
        style.configure("TLabelframe", background=bg, foreground=fg)
        style.configure("TLabelframe.Label", background=bg, foreground=fg)
        style.configure("TLabel", background=bg, foreground=fg)
        style.configure("TButton", background=surface, foreground=fg, borderwidth=1)
        style.map("TButton", background=[("active", accent)])
        style.configure("TCheckbutton", background=bg, foreground=fg)
        style.configure("TRadiobutton", background=bg, foreground=fg)
        style.configure("TEntry", fieldbackground=entry_bg, foreground=fg)
        style.configure("TCombobox", fieldbackground=entry_bg, foreground=fg, background=surface)
        style.map("TCombobox", fieldbackground=[("readonly", entry_bg)], foreground=[("readonly", fg)])

    def _refresh_live_label(self):
        if self.live_source_var.get() == "stopwatch":
            self.live_title_var.set("STOPKY")
            self.live_time_var.set(self.stopwatch_display_var.get())
            self._set_live_color(self.stopwatch_seconds, 0)
            self._schedule_live_font_update()
            return
        row = self._get_selected_live_row()
        if row is None:
            self.live_title_var.set("COUNTDOWN")
            self.live_time_var.set("00:00:00")
            self._set_live_color(0, 0)
            self._schedule_live_font_update()
            return
        self.live_title_var.set(row.name_var.get().upper())
        self.live_time_var.set(row.remaining_var.get())
        self._set_live_color(row.remaining_seconds, row.initial_seconds)
        self._schedule_live_font_update()

    def _get_selected_live_row(self):
        selected = next((r for r in self.countdowns if r.index == self.live_countdown_index), None)
        if selected and selected.running:
            return selected
        running = [r for r in self.countdowns if r.running]
        if not running:
            return selected
        latest = max(running, key=lambda x: x.start_order)
        self.live_countdown_index = latest.index
        return latest

    def _set_live_color(self, remain: int, total: int):
        color = "#1f7a1f"
        if total > 0:
            if remain <= 10:
                color = "#d01010"
            elif remain <= 30:
                color = "#c07000"
        self.live_label_time.configure(foreground=color)

    def _change_live_font_size(self, delta: int):
        self.live_time_font_base = max(24, min(220, self.live_time_font_base + delta))
        self._schedule_live_font_update()

    def _on_live_resize(self, _event):
        self._schedule_live_font_update()

    def _schedule_live_font_update(self):
        if self.live_font_update_job is not None:
            self.live_popup.after_cancel(self.live_font_update_job)
        self.live_font_update_job = self.live_popup.after(25, self._update_live_fonts)

    def _update_live_fonts(self):
        self.live_font_update_job = None
        w = max(80, self.live_popup.winfo_width())
        h = max(80, self.live_popup.winfo_height())
        if w <= 90 or h <= 90:
            return
        available_w = max(40, w - 40)
        title_h = self.live_label_title.winfo_reqheight()
        controls_h = self.live_controls.winfo_reqheight() if hasattr(self, "live_controls") else 0
        available_h = max(20, h - title_h - controls_h - 80)

        scale = self.live_time_font_base / 64.0
        base_target = max(8, min(260, int(min(w * 0.20, h * 0.38) * scale)))
        time_text = self.live_time_var.get() or "00:00:00"
        low, high = 8, base_target
        fit = low
        while low <= high:
            mid = (low + high) // 2
            f = tkfont.Font(family="Segoe UI", size=mid, weight="bold")
            if f.measure(time_text) <= available_w and f.metrics("linespace") <= available_h:
                fit = mid
                low = mid + 1
            else:
                high = mid - 1
        self.live_time_font_size = fit
        self.live_title_font_size = max(12, min(72, int(self.live_time_font_size * 0.28)))
        self.live_label_time.configure(font=("Segoe UI", self.live_time_font_size, "bold"))
        self.live_label_title.configure(font=("Segoe UI", self.live_title_font_size, "bold"))

    def _toggle_live_on_top(self):
        self.live_popup.attributes("-topmost", self.live_on_top_var.get())

    def _toggle_click_through(self):
        hwnd = self.live_popup.winfo_id()
        user32 = ctypes.windll.user32
        style = user32.GetWindowLongW(hwnd, self.GWL_EXSTYLE)
        if self.live_click_through_var.get():
            style = style | self.WS_EX_LAYERED | self.WS_EX_TRANSPARENT
        else:
            style = style & ~self.WS_EX_TRANSPARENT
        user32.SetWindowLongW(hwnd, self.GWL_EXSTYLE, style)

    def _toggle_live_popup(self):
        if self.live_popup.state() == "withdrawn":
            self.live_popup.deiconify()
        else:
            self.live_popup.withdraw()

    def _hide_live_popup(self):
        self._exit_live_fullscreen()
        self.live_popup.withdraw()

    def _toggle_live_fullscreen(self):
        current = bool(self.live_popup.attributes("-fullscreen"))
        self.live_popup.attributes("-fullscreen", not current)
        if not current:
            self.live_popup.deiconify()
            self.live_popup.lift()
            self.live_popup.focus_force()

    def _exit_live_fullscreen(self):
        self.live_popup.attributes("-fullscreen", False)

    def _open_countdown_sound_dialog(self, row):
        d = tk.Toplevel(self.root)
        d.title(f"Zvuk - Casovac {row.index}")
        d.geometry("700x220")
        d.resizable(False, False)
        d.transient(self.root)
        d.grab_set()
        f = ttk.Frame(d, padding=12)
        f.pack(fill=tk.BOTH, expand=True)
        ttk.Label(f, text=f"Casovac {row.index}: {row.name_var.get()}").pack(anchor=tk.W, pady=(0, 8))
        m = ttk.Frame(f); m.pack(fill=tk.X, pady=(0, 8))
        ttk.Radiobutton(m, text="Preset", value="preset", variable=row.sound_mode_var).pack(side=tk.LEFT, padx=4)
        ttk.Radiobutton(m, text="Vlastny WAV", value="custom", variable=row.sound_mode_var).pack(side=tk.LEFT, padx=4)
        p = ttk.Frame(f); p.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(p, text="Preset", width=10).pack(side=tk.LEFT)
        ttk.Combobox(p, textvariable=row.sound_preset_var, values=self.sound_presets, state="readonly", width=45).pack(side=tk.LEFT, padx=4)
        w = ttk.Frame(f); w.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(w, text="WAV", width=10).pack(side=tk.LEFT)
        ttk.Entry(w, textvariable=row.sound_file_var, width=58).pack(side=tk.LEFT, padx=4)
        ttk.Button(w, text="Vybrat", command=lambda: self._pick_sound_file(row.sound_file_var)).pack(side=tk.LEFT, padx=4)
        a = ttk.Frame(f); a.pack(fill=tk.X)
        ttk.Button(a, text="Test", command=lambda: self._test_countdown_sound(row)).pack(side=tk.LEFT)
        ttk.Button(a, text="Zavriet", command=d.destroy).pack(side=tk.RIGHT)

    def _pick_sound_file(self, target_var):
        path = filedialog.askopenfilename(title="Vyber WAV", filetypes=[("WAV files", "*.wav"), ("All files", "*.*")])
        if path:
            target_var.set(path)

    def _test_countdown_sound(self, row):
        if row.sound_mode_var.get() == "custom":
            if not self._play_custom_wav(row.sound_file_var.get().strip()):
                messagebox.showwarning("Zvuk", "Nepodarilo sa prehrat vlastny WAV.")
            return
        if not self._play_builtin_preset(row.sound_preset_var.get().strip()):
            messagebox.showwarning("Zvuk", "Nepodarilo sa prehrat preset.")
