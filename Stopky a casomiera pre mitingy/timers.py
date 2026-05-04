from models import format_seconds, parse_time_to_seconds


class TimersMixin:
    def _tick(self):
        if self.stopwatch_running:
            self.stopwatch_seconds += 1
            self.stopwatch_display_var.set(format_seconds(self.stopwatch_seconds))

        finished = []
        for row in self.countdowns:
            if row.running and row.remaining_seconds > 0:
                row.remaining_seconds -= 1
                row.remaining_var.set(format_seconds(row.remaining_seconds))
                if row.remaining_seconds == 0:
                    row.running = False
                    row.status_label.config(text="KONIEC")
                    finished.append(row)
                    self._log_event(row, "finish")
                    self._play_end_sound(row)

        if finished and self.auto_next_var.get():
            self._start_next_ready()

        self._apply_lock_state()
        self._refresh_live_label()
        self.root.after(1000, self._tick)

    def _on_mode_change(self):
        if self.mode_var.get() == "stopwatch":
            self.stopwatch_frame.pack(fill="x", pady=(8, 0))
        else:
            self.stopwatch_frame.pack_forget()

    def _set_stopwatch_start(self):
        try:
            self.stopwatch_start_seconds = parse_time_to_seconds(self.stopwatch_start_var.get())
            if not self.stopwatch_running:
                self.stopwatch_seconds = self.stopwatch_start_seconds
                self.stopwatch_display_var.set(format_seconds(self.stopwatch_seconds))
        except ValueError as exc:
            from tkinter import messagebox
            messagebox.showerror("Chyba", str(exc))

    def _start_stopwatch(self):
        self.stopwatch_running = True

    def _pause_stopwatch(self):
        self.stopwatch_running = False

    def _stop_stopwatch(self):
        self.stopwatch_running = False
        self.stopwatch_seconds = 0
        self.stopwatch_display_var.set("00:00:00")

    def _reset_stopwatch(self):
        self.stopwatch_running = False
        self.stopwatch_seconds = self.stopwatch_start_seconds
        self.stopwatch_display_var.set(format_seconds(self.stopwatch_seconds))

    def _start_countdown(self, row):
        if row.running:
            return
        self._pause_other_countdowns(row)
        if row.remaining_seconds <= 0:
            try:
                row.initial_seconds = parse_time_to_seconds(row.duration_var.get())
            except ValueError as exc:
                from tkinter import messagebox
                messagebox.showerror("Chyba", f"{row.name_var.get()}: {exc}")
                return
            row.remaining_seconds = row.initial_seconds
            row.remaining_var.set(format_seconds(row.remaining_seconds))
        row.running = True
        row.status_label.config(text="Bezi")
        self.live_last_started_order += 1
        row.start_order = self.live_last_started_order
        self.live_countdown_index = row.index
        self._log_event(row, "start")

    def _pause_other_countdowns(self, keep_row):
        for other in self.countdowns:
            if other is keep_row:
                continue
            if other.running:
                other.running = False
                other.status_label.config(text="Pauza")
                self._log_event(other, "pause_auto")

    def _pause_countdown(self, row):
        if row.running:
            row.running = False
            row.status_label.config(text="Pauza")
            self._log_event(row, "pause")

    def _stop_countdown(self, row):
        row.running = False
        row.remaining_seconds = 0
        row.remaining_var.set("00:00:00")
        row.status_label.config(text="Stop")
        self._log_event(row, "stop")

    def _reset_countdown(self, row):
        row.running = False
        try:
            row.initial_seconds = parse_time_to_seconds(row.duration_var.get())
        except ValueError as exc:
            from tkinter import messagebox
            messagebox.showerror("Chyba", f"{row.name_var.get()}: {exc}")
            return
        row.remaining_seconds = row.initial_seconds
        row.remaining_var.set(format_seconds(row.remaining_seconds))
        row.status_label.config(text="Pripraveny")
        self._log_event(row, "reset")

    def _start_next_ready(self):
        for row in self.countdowns:
            if not row.running and row.remaining_seconds == 0:
                self._start_countdown(row)
                return

    def _shortcut_toggle(self):
        if self.live_source_var.get() == "stopwatch" or self.mode_var.get() == "stopwatch":
            self.stopwatch_running = not self.stopwatch_running
            return
        row = self._get_selected_live_row()
        if row is None:
            self._start_next_ready()
            return
        if row.running:
            self._pause_countdown(row)
        else:
            self._start_countdown(row)

    def _shortcut_stop(self):
        if self.live_source_var.get() == "stopwatch" or self.mode_var.get() == "stopwatch":
            self._stop_stopwatch()
            return
        row = self._get_selected_live_row()
        if row:
            self._stop_countdown(row)

    def _apply_lock_state(self):
        locked = self.lock_edit_var.get() and (self.stopwatch_running or any(r.running for r in self.countdowns))
        state = "disabled" if locked else "normal"
        try:
            self.stopwatch_entry.configure(state=state)
        except Exception:
            pass
        for row in self.countdowns:
            for w in row.widgets:
                try:
                    w.configure(state=state)
                except Exception:
                    pass
