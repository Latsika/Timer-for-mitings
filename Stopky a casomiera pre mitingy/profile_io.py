import csv
import json
import re
import time
from pathlib import Path
from tkinter import filedialog, messagebox


class ProfileIOMixin:
    def _save_profile_dialog(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")], title="Ulozit profil")
        if not path:
            return
        self._save_profile(Path(path))

    def _load_profile_dialog(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")], title="Nacitat profil")
        if not path:
            return
        self._load_profile(Path(path), quiet=False)

    def _save_profile(self, path: Path):
        data = {
            "stopwatch_start": self.stopwatch_start_var.get(),
            "auto_next": self.auto_next_var.get(),
            "sound_enabled": self.sound_enabled_var.get(),
            "countdowns": [{
                "name": r.name_var.get(),
                "duration": r.duration_var.get(),
                "sound_mode": r.sound_mode_var.get(),
                "sound_preset": r.sound_preset_var.get(),
                "sound_file": r.sound_file_var.get(),
            } for r in self.countdowns]
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        self.profile_path_var.set(str(path))
        messagebox.showinfo("Profil", f"Profil ulozeny:\n{path}")

    def _load_profile(self, path: Path, quiet: bool):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            if not quiet:
                messagebox.showerror("Profil", f"Nepodarilo sa nacitat profil:\n{exc}")
            return
        self.stopwatch_start_var.set(data.get("stopwatch_start", "00:00:00"))
        self.auto_next_var.set(bool(data.get("auto_next", False)))
        self.sound_enabled_var.set(bool(data.get("sound_enabled", True)))
        items = data.get("countdowns", [])
        for i, row in enumerate(self.countdowns):
            src = items[i] if i < len(items) else {}
            row.name_var.set(src.get("name", row.name_var.get()))
            row.duration_var.set(src.get("duration", "00:05:00"))
            row.remaining_var.set(row.duration_var.get())
            row.remaining_seconds = 0
            row.running = False
            row.status_label.config(text="Pripraveny")
            row.sound_mode_var.set(src.get("sound_mode", "preset"))
            row.sound_preset_var.set(src.get("sound_preset", "Classic Beep"))
            row.sound_file_var.set(src.get("sound_file", ""))
        self.profile_path_var.set(str(path))
        if not quiet:
            messagebox.showinfo("Profil", f"Profil nacitany:\n{path}")

    def _log_event(self, row, action: str):
        self.history.append({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "timer_index": row.index,
            "timer_name": row.name_var.get(),
            "action": action,
            "remaining": row.remaining_var.get(),
        })

    def _export_history_csv(self):
        if not self.history:
            messagebox.showinfo("Log", "Zatial nie je co exportovat.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")], title="Export logu")
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["timestamp", "timer_index", "timer_name", "action", "remaining"])
            w.writeheader()
            w.writerows(self.history)
        messagebox.showinfo("Log", f"Export hotovy:\n{path}")

    def _get_latest_built_exe(self) -> Path:
        dist = Path.cwd() / "dist"
        pattern = re.compile(r"^StopkyMiting_v(\d+)\.exe$")
        candidates = []
        if dist.exists():
            for path in dist.glob("StopkyMiting_v*.exe"):
                m = pattern.match(path.name)
                if m:
                    candidates.append((int(m.group(1)), path))
        if candidates:
            return max(candidates, key=lambda item: item[0])[1]
        return dist / "StopkyMiting_v8.exe"

    def _create_ppt_macro_guide(self):
        exe_path = self._get_latest_built_exe()
        profile = self.profile_path_var.get().strip() or str(Path.cwd() / "meeting-profile.json")
        txt = (
            "VBA makro pre PowerPoint (vloz do Module):\n\n"
            "Sub SpustitStopky()\n"
            f"    Shell \"\"\"{exe_path}\"\" --profile \"\"\"{profile}\"\"\", vbNormalFocus\n"
            "End Sub\n"
        )
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text", "*.txt")], title="Ulozit PPT navod")
        if not path:
            return
        Path(path).write_text(txt, encoding="utf-8")
        messagebox.showinfo("PPT", f"Navod ulozeny:\n{path}")
