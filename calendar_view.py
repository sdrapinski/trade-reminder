import calendar
from datetime import date
from tkinter import messagebox

import customtkinter as ctk

import storage
from journal_form import JournalForm

MONTHS_PL = [
    "Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec",
    "Lipiec", "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień",
]
DAYS_PL = ["Pn", "Wt", "Śr", "Cz", "Pt", "Sb", "Nd"]

COLOR_TESTED = "#2e7d32"
COLOR_TESTED_HOVER = "#388e3c"
COLOR_NOT_TESTED = "#c62828"
COLOR_NOT_TESTED_HOVER = "#d32f2f"
COLOR_EMPTY = "#3a3a3a"
COLOR_EMPTY_HOVER = "#4a4a4a"
COLOR_TODAY_BORDER = "#ffd54f"


class CalendarApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Trade Reminder — Dziennik")
        self.geometry("780x660")
        today = date.today()
        self.year = today.year
        self.month = today.month
        self._build_header()
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.pack(padx=20, pady=10, fill="both", expand=True)
        self._build_legend()
        self._render()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 5))
        ctk.CTkButton(header, text="◀", width=40, command=self._prev_month).pack(side="left")
        self.title_label = ctk.CTkLabel(header, text="", font=ctk.CTkFont(size=22, weight="bold"))
        self.title_label.pack(side="left", expand=True)
        ctk.CTkButton(header, text="▶", width=40, command=self._next_month).pack(side="right")
        ctk.CTkButton(header, text="+ Wpis dziś", width=110, command=self._add_today).pack(side="right", padx=10)

    def _build_legend(self):
        legend = ctk.CTkFrame(self, fg_color="transparent")
        legend.pack(fill="x", padx=20, pady=(0, 15))
        for color, text in [
            (COLOR_TESTED, "Testowałem"),
            (COLOR_NOT_TESTED, "Nie testowałem"),
            (COLOR_EMPTY, "Brak danych"),
        ]:
            item = ctk.CTkFrame(legend, fg_color="transparent")
            item.pack(side="left", padx=10)
            ctk.CTkLabel(item, text="  ", fg_color=color, corner_radius=4, width=20).pack(side="left", padx=(0, 6))
            ctk.CTkLabel(item, text=text).pack(side="left")

    def _prev_month(self):
        self.month -= 1
        if self.month < 1:
            self.month = 12
            self.year -= 1
        self._render()

    def _next_month(self):
        self.month += 1
        if self.month > 12:
            self.month = 1
            self.year += 1
        self._render()

    def _add_today(self):
        form = JournalForm(self, on_save=self._render, tested=True)
        form.grab_set()

    def _render(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()
        self.title_label.configure(text=f"{MONTHS_PL[self.month - 1]} {self.year}")
        sessions = storage.load_sessions()

        for i in range(7):
            self.grid_frame.columnconfigure(i, weight=1, uniform="day")
            ctk.CTkLabel(self.grid_frame, text=DAYS_PL[i], font=ctk.CTkFont(weight="bold")).grid(row=0, column=i, pady=4)

        cal = calendar.Calendar(firstweekday=0)
        today = date.today()
        row = 1
        for week in cal.monthdayscalendar(self.year, self.month):
            self.grid_frame.rowconfigure(row, weight=1)
            for col, day in enumerate(week):
                if day == 0:
                    continue
                d = date(self.year, self.month, day)
                session = sessions.get(d.isoformat())
                fg, hover, suffix = self._colors_for(session)
                border = 3 if d == today else 0
                btn = ctk.CTkButton(
                    self.grid_frame,
                    text=f"{day}{suffix}",
                    fg_color=fg,
                    hover_color=hover,
                    text_color="white",
                    border_width=border,
                    border_color=COLOR_TODAY_BORDER,
                    corner_radius=8,
                    font=ctk.CTkFont(size=14, weight="bold"),
                    command=lambda dt=d: self._day_clicked(dt),
                )
                btn.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")
            row += 1

    @staticmethod
    def _colors_for(session):
        if session is None:
            return COLOR_EMPTY, COLOR_EMPTY_HOVER, ""
        if session["tested"] != "True":
            return COLOR_NOT_TESTED, COLOR_NOT_TESTED_HOVER, ""
        if session["session_type"] == "Live":
            pl = storage.parse_profit_loss(session.get("profit_loss", ""))
            if pl is None:
                return COLOR_TESTED, COLOR_TESTED_HOVER, "\nL"
            suffix = f"\n{storage.format_profit_loss(pl)}"
            if pl < 0:
                return COLOR_NOT_TESTED, COLOR_NOT_TESTED_HOVER, suffix
            return COLOR_TESTED, COLOR_TESTED_HOVER, suffix
        return COLOR_TESTED, COLOR_TESTED_HOVER, "\nB"

    def _day_clicked(self, d):
        session = storage.get_session(d)
        if session is None:
            if d == date.today():
                self._add_today()
            else:
                messagebox.showinfo("Brak danych", f"Brak wpisu dla {d.isoformat()}")
            return
        if session["tested"] == "False":
            msg = "Dzień bez testów."
            if session["notes"]:
                msg += f"\n\nNotatki: {session['notes']}"
        else:
            pl_raw = session["profit_loss"] or "—"
            pl_total = storage.parse_profit_loss(session["profit_loss"])
            pl_line = pl_raw if pl_total is None or "," not in pl_raw and ";" not in pl_raw else f"{pl_raw}   (suma: {storage.format_profit_loss(pl_total)})"
            msg = (
                f"Typ: {session['session_type']}\n"
                f"Win ratio: {session['win_ratio']}%\n"
                f"P/L: {pl_line}\n"
                f"Najlepsze zagranie: {session['best_trade'] or '—'}\n"
                f"Notatki: {session['notes'] or '—'}"
            )
        messagebox.showinfo(f"Sesja {d.isoformat()}", msg)


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = CalendarApp()
    app.mainloop()
