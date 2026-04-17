# Backtest Reminder & Trading Journal — Założenia Aplikacji

## Cel
Codzienny reminder o backtestowaniu + prosty dziennik tradingowy z kalendarzem i historią wyników.

---

## Powiadomienie

- Odpala się codziennie o **21:00** 
- Format: Windows Toast Notification (nie zabiera focusa)
- Powiadomienie zawiera dwa przyciski:
  - ✅ **Tak, testowałem**
  - ❌ **Nie testowałem dzisiaj**
- Kliknięcie przycisku zapisuje odpowiedź i opcjonalnie otwiera kalendarz/formularz

---

## Formularz po kliknięciu "Tak, testowałem"

Użytkownik może uzupełnić szczegóły sesji:

| Pole | Typ | Opis |
|---|---|---|
| Data | auto | Uzupełniana automatycznie |
| Typ sesji | radio | **Backtesting** / **Live Trading** |
| Win Ratio | liczba (%) | np. 65% |
| Profit/Loss | liczba | np. +120 / -45 (w walucie lub pipsach) |
| Najlepsze zagranie | tekst | Krótki opis wyróżniającego się trade'a |
| Notatki | tekst | Dowolne uwagi, obserwacje |

---

## Zapis danych

- Dane zapisywane do pliku **CSV** (`trading_journal.csv`)
- Jedna sesja = jeden wiersz
- Kolumny CSV:
  ```
  date, tested, session_type, win_ratio, profit_loss, best_trade, notes
  ```
- Plik CSV tworzony automatycznie jeśli nie istnieje

---

## Kalendarz (widok główny)

- Okno Python (np. `tkinter` lub `customtkinter`)
- Widok miesięczny — siatka dni
- Każdy dzień kolorowany:
  - 🟢 **Zielony** — testowałem (backtesting lub live)
  - 🔴 **Czerwony** — nie testowałem
  - ⚪ **Szary** — brak danych (dzień w przyszłości lub przed startem)
- Kliknięcie w dzień pokazuje szczegóły sesji z tego dnia (jeśli były)
- Rozróżnienie ikoną lub etykietą: **B** = Backtesting, **L** = Live Trading

---

## Struktura plików

```
BacktestReminder/
├── backtest_reminder.py       # Główny skrypt — timer + powiadomienie
├── calendar_view.py           # Okno kalendarza (tkinter)
├── journal_form.py            # Formularz wpisu po powiadomieniu
├── trading_journal.csv        # Dane (auto-tworzony)
├── start_backtest_reminder.bat # Autostart Windows
└── cloud.md                   # Ten plik — dokumentacja
```

---

## Stack techniczny

- **Python 3.x**
- `tkinter` — GUI kalendarza i formularza (wbudowany w Pythona, zero instalacji)
- `csv` — zapis/odczyt danych (wbudowany)
- `datetime` — obsługa dat
- `subprocess` / `ctypes` — Windows Toast Notification
- Opcjonalnie: `customtkinter` dla ładniejszego UI

---

## Todo / Przyszłe rozszerzenia

- [ ] Wykres win ratio w czasie (matplotlib)
- [ ] Statystyki tygodniowe / miesięczne
- [ ] Streak counter ("5 dni z rzędu!")
- [ ] Eksport do PDF / Excel
- [ ] Filtrowanie kalendarza po typie sesji (Backtesting vs Live)