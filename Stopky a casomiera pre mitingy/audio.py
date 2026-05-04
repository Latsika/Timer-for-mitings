import subprocess
import winsound


class AudioMixin:
    def _play_end_sound(self, row):
        if not self.sound_enabled_var.get():
            return
        if row.sound_mode_var.get() == "custom":
            if self._play_custom_wav(row.sound_file_var.get().strip()):
                return
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            return
        if not self._play_builtin_preset(row.sound_preset_var.get().strip()):
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)

    def _play_custom_wav(self, path: str) -> bool:
        if not path:
            return False
        try:
            winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            return True
        except RuntimeError:
            return False

    def _play_builtin_preset(self, preset: str) -> bool:
        if preset == "Classic Beep":
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION); return True
        if preset == "Double Beep":
            self._tone([(900, 150), (900, 150)], 70); return True
        if preset == "Triple Beep":
            self._tone([(1000, 120), (1000, 120), (1000, 120)], 60); return True
        if preset == "High Ping":
            winsound.Beep(1400, 280); return True
        if preset == "Low Ping":
            winsound.Beep(500, 320); return True
        if preset == "Rising Tone":
            self._tone([(700, 110), (950, 110), (1200, 150)], 40); return True
        if preset == "Falling Tone":
            self._tone([(1200, 110), (900, 110), (700, 150)], 40); return True
        if preset == "Alarm Short":
            self._tone([(1100, 200), (900, 200), (1100, 200), (900, 200)], 30); return True
        if preset == "Alarm Long":
            self._tone([(1000, 380), (700, 330), (1000, 380)], 40); return True
        if preset == "Notification":
            self._tone([(850, 140), (1150, 170)], 40); return True
        if preset == "Ta-Da":
            self._tone([(900, 120), (1200, 120), (1500, 230)], 30); return True
        if preset == "Voice: Time is up":
            self._speak("Time is up."); return True
        if preset == "Voice: Hey your time is up, did you hear me?":
            self._speak("Hey, your time is up. Did you hear me?"); return True
        if preset == "Voice: Wrap it up please":
            self._speak("Wrap it up please."); return True
        if preset == "Voice: Next speaker now":
            self._speak("Next speaker now."); return True
        return False

    def _tone(self, notes: list[tuple[int, int]], gap: int):
        for f, d in notes:
            winsound.Beep(f, d)
            if gap > 0:
                winsound.Beep(37, gap)

    def _speak(self, text: str):
        safe = text.replace("'", "''")
        cmd = (
            "[void][Reflection.Assembly]::LoadWithPartialName('System.Speech');"
            "$s=New-Object System.Speech.Synthesis.SpeechSynthesizer;"
            f"$s.Speak('{safe}')"
        )
        try:
            subprocess.Popen(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd], creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception:
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
