import tkinter as tk
from datetime import date
from tkinter import messagebox

import customtkinter as ctk

import storage


class JournalForm(ctk.CTkToplevel):
    def __init__(self, master=None, on_save=None, tested=True):
        super().__init__(master)
        self.on_save = on_save
        self.tested = tested
        self.title("Nowa sesja" if tested else "Dzień bez testów")
        self.geometry("480x640")
        self.resizable(False, False)
        self._build()
        self.after(100, self.lift)

    def _build(self):
        ctk.CTkLabel(
            self,
            text="Nowy wpis w dzienniku" if self.tested else "Oznacz dzień jako bez testów",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=(20, 6))

        ctk.CTkLabel(self, text=f"Data: {date.today().isoformat()}", font=ctk.CTkFont(size=13)).pack(pady=(0, 10))

        if not self.tested:
            ctk.CTkLabel(self, text="Możesz dodać notatkę, dlaczego dziś odpuściłeś.").pack(pady=10)
            self.notes = ctk.CTkTextbox(self, width=360, height=140)
            self.notes.pack(pady=10)
            ctk.CTkButton(self, text="Zapisz", command=self._save).pack(pady=20)
            return

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=30)

        ctk.CTkLabel(body, text="Typ sesji").pack(anchor="w", pady=(10, 2))
        self.session_type = tk.StringVar(value="Backtesting")
        radios = ctk.CTkFrame(body, fg_color="transparent")
        radios.pack(anchor="w")
        ctk.CTkRadioButton(radios, text="Backtesting", variable=self.session_type, value="Backtesting").pack(side="left", padx=(0, 20))
        ctk.CTkRadioButton(radios, text="Live Trading", variable=self.session_type, value="Live").pack(side="left")

        ctk.CTkLabel(body, text="Win Ratio (%)").pack(anchor="w", pady=(12, 2))
        self.win_ratio = ctk.CTkEntry(body, placeholder_text="np. 65")
        self.win_ratio.pack(fill="x")

        ctk.CTkLabel(body, text="Profit / Loss").pack(anchor="w", pady=(12, 2))
        self.profit_loss = ctk.CTkEntry(body, placeholder_text="np. +120 lub +50, -20, +30")
        self.profit_loss.pack(fill="x")
        self.pl_preview = ctk.CTkLabel(body, text="", font=ctk.CTkFont(size=12), anchor="e")
        self.pl_preview.pack(fill="x", pady=(2, 0))
        self.profit_loss.bind("<KeyRelease>", self._update_pl_preview)

        ctk.CTkLabel(body, text="Najlepsze zagranie").pack(anchor="w", pady=(12, 2))
        self.best_trade = ctk.CTkEntry(body, placeholder_text="krótki opis")
        self.best_trade.pack(fill="x")

        ctk.CTkLabel(body, text="Notatki").pack(anchor="w", pady=(12, 2))
        self.notes = ctk.CTkTextbox(body, height=110)
        self.notes.pack(fill="x")

        ctk.CTkButton(self, text="Zapisz", command=self._save, height=40).pack(pady=20, padx=30, fill="x")

    def _update_pl_preview(self, _event=None):
        raw = self.profit_loss.get().strip()
        if not raw:
            self.pl_preview.configure(text="")
            return
        total = storage.parse_profit_loss(raw)
        if total is None:
            self.pl_preview.configure(text="nieprawidłowy format", text_color="#ef9a9a")
            return
        color = "#a5d6a7" if total >= 0 else "#ef9a9a"
        self.pl_preview.configure(text=f"suma: {storage.format_profit_loss(total)}", text_color=color)

    def _save(self):
        try:
            if self.tested:
                storage.save_session(
                    date.today(),
                    tested=True,
                    session_type=self.session_type.get(),
                    win_ratio=self.win_ratio.get().strip(),
                    profit_loss=self.profit_loss.get().strip(),
                    best_trade=self.best_trade.get().strip(),
                    notes=self.notes.get("1.0", "end").strip(),
                )
            else:
                storage.save_session(
                    date.today(),
                    tested=False,
                    notes=self.notes.get("1.0", "end").strip(),
                )
            if self.on_save:
                self.on_save()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Błąd zapisu", str(e))


def _standalone(tested=True):
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    root.withdraw()
    form = JournalForm(root, tested=tested)
    form.grab_set()
    form.wait_window()
    root.destroy()


if __name__ == "__main__":
    import sys
    _standalone(tested="--no" not in sys.argv)
