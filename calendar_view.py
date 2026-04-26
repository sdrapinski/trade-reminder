import calendar
from datetime import date, timedelta
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

COLOR_GOOD = "#a5d6a7"
COLOR_BAD = "#ef9a9a"
COLOR_REWARD = "#fbc02d"
COLOR_INFO = "#90caf9"

SKIP_THRESHOLD = 4
KM_PER_SKIPPED_DAY = 3
REWARD_TEXT = "🏆 Nagroda: zasłużony cheat meal / nowa książka tradingowa / wolny weekend bez ekranu"


class CalendarApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Trade Reminder — Dziennik")
        self.geometry("820x860")
        today = date.today()
        self.year = today.year
        self.month = today.month
        self._build_header()
        self._build_legend()
        self._build_stats()
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.pack(padx=20, pady=10, fill="both", expand=True)
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
        legend.pack(fill="x", padx=20, pady=(0, 5))
        for color, text in [
            (COLOR_TESTED, "Testowałem"),
            (COLOR_NOT_TESTED, "Nie testowałem"),
            (COLOR_EMPTY, "Brak danych"),
        ]:
            item = ctk.CTkFrame(legend, fg_color="transparent")
            item.pack(side="left", padx=10)
            ctk.CTkLabel(item, text="  ", fg_color=color, corner_radius=4, width=20).pack(side="left", padx=(0, 6))
            ctk.CTkLabel(item, text=text).pack(side="left")

    def _build_stats(self):
        self.stats_frame = ctk.CTkFrame(self)
        self.stats_frame.pack(fill="x", padx=20, pady=(5, 15), side="bottom")

        ctk.CTkLabel(
            self.stats_frame,
            text="Statystyki",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(anchor="w", padx=15, pady=(10, 4))

        counters = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
        counters.pack(fill="x", padx=15, pady=(0, 6))
        self.week_label = ctk.CTkLabel(counters, text="", anchor="w", font=ctk.CTkFont(size=13))
        self.week_label.pack(side="left", padx=(0, 30))
        self.month_label = ctk.CTkLabel(counters, text="", anchor="w", font=ctk.CTkFont(size=13))
        self.month_label.pack(side="left")

        self.live_pl_label = ctk.CTkLabel(
            self.stats_frame, text="", anchor="w", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.live_pl_label.pack(fill="x", padx=15, pady=(0, 6))

        self.penalty_label = ctk.CTkLabel(
            self.stats_frame, text="", anchor="w", font=ctk.CTkFont(size=13, weight="bold"), wraplength=760, justify="left"
        )
        self.penalty_label.pack(fill="x", padx=15, pady=(2, 4))

        self.reward_label = ctk.CTkLabel(
            self.stats_frame, text="", anchor="w", font=ctk.CTkFont(size=13), wraplength=760, justify="left"
        )
        self.reward_label.pack(fill="x", padx=15, pady=(0, 12))

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
        self._update_stats(sessions)

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

    def _update_stats(self, sessions):
        today = date.today()
        journal_start = self._journal_start(sessions)

        wk_start = today - timedelta(days=today.weekday())
        wk_end = wk_start + timedelta(days=6)
        wk_eval_end = min(wk_end, today)
        wk_tested, wk_skipped = self._count(sessions, wk_start, wk_eval_end, journal_start)
        self.week_label.configure(
            text=f"Tydzień {wk_start.strftime('%d.%m')}–{wk_end.strftime('%d.%m')}:  "
                 f"✅ {wk_tested}    ❌ {wk_skipped}"
        )

        mo_first = date(self.year, self.month, 1)
        mo_last = date(self.year, self.month, calendar.monthrange(self.year, self.month)[1])
        mo_eval_end = min(mo_last, today)
        if mo_first > today:
            mo_tested, mo_skipped = 0, 0
        else:
            mo_tested, mo_skipped = self._count(sessions, mo_first, mo_eval_end, journal_start)
        self.month_label.configure(
            text=f"{MONTHS_PL[self.month - 1]} {self.year}:  ✅ {mo_tested}    ❌ {mo_skipped}"
        )

        live_total, live_days = self._live_pl_for_month(sessions)
        if live_days == 0:
            self.live_pl_label.configure(
                text=f"💼 Live P/L ({MONTHS_PL[self.month - 1]}): brak sesji Live",
                text_color=COLOR_INFO,
            )
        else:
            color = COLOR_GOOD if live_total >= 0 else COLOR_BAD
            self.live_pl_label.configure(
                text=f"💼 Live P/L ({MONTHS_PL[self.month - 1]}): "
                     f"{storage.format_profit_loss(live_total)}  ({live_days} sesji Live)",
                text_color=color,
            )

        if wk_skipped >= SKIP_THRESHOLD:
            km = KM_PER_SKIPPED_DAY * wk_skipped
            self.penalty_label.configure(
                text=f"🏃 KARA: {wk_skipped} dni opuszczonych w tym tygodniu → "
                     f"musisz przebiec {km} km ({KM_PER_SKIPPED_DAY} km × {wk_skipped}).",
                text_color=COLOR_BAD,
            )
        else:
            margin = SKIP_THRESHOLD - 1 - wk_skipped
            self.penalty_label.configure(
                text=f"✅ Tydzień w normie ({wk_skipped} opuszczonych, margines: {margin} przed karą biegową).",
                text_color=COLOR_GOOD,
            )

        self._update_reward(sessions, today, journal_start)

    def _update_reward(self, sessions, today, journal_start):
        weeks = self._month_weeks(self.year, self.month)
        bad = []
        pending = []
        for ws, we in weeks:
            if ws > today:
                pending.append((ws, we))
                continue
            eval_end = min(we, today)
            _, skipped = self._count(sessions, ws, eval_end, journal_start)
            if skipped >= SKIP_THRESHOLD:
                bad.append((ws, we, skipped))
            elif we > today:
                pending.append((ws, we))

        is_past = (self.year, self.month) < (today.year, today.month)
        is_future = (self.year, self.month) > (today.year, today.month)

        if is_future:
            self.reward_label.configure(
                text="📅 Miesiąc w przyszłości — nagroda jeszcze do zdobycia.",
                text_color=COLOR_INFO,
            )
            return

        if bad:
            ws, we, sk = bad[0]
            self.reward_label.configure(
                text=f"💔 Nagroda przepadła — tydzień {ws.strftime('%d.%m')}–{we.strftime('%d.%m')} "
                     f"miał {sk} dni opuszczonych ({SKIP_THRESHOLD}+ = brak nagrody).",
                text_color=COLOR_BAD,
            )
            return

        if pending:
            self.reward_label.configure(
                text=f"🎯 W zasięgu! {len(pending)} tygodni do końca miesiąca — utrzymaj <{SKIP_THRESHOLD} opuszczonych dni "
                     f"w każdym i odblokujesz: {REWARD_TEXT}",
                text_color=COLOR_REWARD,
            )
            return

        if is_past:
            self.reward_label.configure(
                text=f"🏆 NAGRODA ZDOBYTA! Każdy tydzień {MONTHS_PL[self.month - 1]} pozytywny. {REWARD_TEXT}",
                text_color=COLOR_REWARD,
            )
        else:
            self.reward_label.configure(
                text=f"🏆 Wszystkie tygodnie pozytywne (na ten moment). Dotrzyj do końca miesiąca i bierz: {REWARD_TEXT}",
                text_color=COLOR_REWARD,
            )

    def _live_pl_for_month(self, sessions):
        total = 0.0
        days = 0
        prefix = f"{self.year:04d}-{self.month:02d}-"
        for key, s in sessions.items():
            if not key.startswith(prefix):
                continue
            if s.get("tested") != "True" or s.get("session_type") != "Live":
                continue
            pl = storage.parse_profit_loss(s.get("profit_loss", ""))
            if pl is None:
                continue
            total += pl
            days += 1
        return total, days

    @staticmethod
    def _journal_start(sessions):
        if not sessions:
            return None
        try:
            return min(date.fromisoformat(k) for k in sessions.keys())
        except ValueError:
            return None

    @staticmethod
    def _count(sessions, start, end, journal_start):
        tested = 0
        skipped = 0
        d = start
        while d <= end:
            if journal_start is None or d < journal_start:
                d += timedelta(days=1)
                continue
            s = sessions.get(d.isoformat())
            if s and s.get("tested") == "True":
                tested += 1
            else:
                skipped += 1
            d += timedelta(days=1)
        return tested, skipped

    @staticmethod
    def _month_weeks(year, month):
        first = date(year, month, 1)
        last = date(year, month, calendar.monthrange(year, month)[1])
        monday = first - timedelta(days=first.weekday())
        weeks = []
        while monday <= last:
            weeks.append((monday, monday + timedelta(days=6)))
            monday += timedelta(days=7)
        return weeks

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
