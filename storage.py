import csv
import re
from datetime import date
from pathlib import Path

CSV_PATH = Path(__file__).parent / "trading_journal.csv"
FIELDS = ["date", "tested", "session_type", "win_ratio", "profit_loss", "best_trade", "notes"]


def parse_profit_loss(value):
    """Parse a P/L string into a total. Supports single values or comma/semicolon-separated lists.

    Single-token commas are treated as decimal separators (Polish style); multi-token
    input is summed. Returns None if any token fails to parse.
    """
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    if ";" not in text and text.count(",") <= 1:
        try:
            return float(text.replace(" ", "").replace(",", ".").lstrip("+"))
        except ValueError:
            pass
    tokens = [t for t in re.split(r"[,;]", text) if t.strip()]
    if not tokens:
        return None
    total = 0.0
    for tok in tokens:
        try:
            total += float(tok.strip().replace(" ", "").lstrip("+"))
        except ValueError:
            return None
    return total


def format_profit_loss(value):
    if value is None:
        return ""
    if value == int(value):
        value = int(value)
    return f"+{value}" if value > 0 else str(value)


def _ensure_file():
    if not CSV_PATH.exists():
        with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=FIELDS).writeheader()


def _key(d):
    return d.isoformat() if hasattr(d, "isoformat") else str(d)


def load_sessions():
    _ensure_file()
    sessions = {}
    with CSV_PATH.open("r", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            sessions[row["date"]] = row
    return sessions


def save_session(session_date, tested, session_type="", win_ratio="", profit_loss="", best_trade="", notes=""):
    _ensure_file()
    sessions = load_sessions()
    k = _key(session_date)
    sessions[k] = {
        "date": k,
        "tested": "True" if tested else "False",
        "session_type": session_type,
        "win_ratio": str(win_ratio),
        "profit_loss": str(profit_loss),
        "best_trade": best_trade,
        "notes": notes,
    }
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for row in sorted(sessions.values(), key=lambda r: r["date"]):
            writer.writerow(row)


def get_session(session_date):
    return load_sessions().get(_key(session_date))
