import argparse
import subprocess
import sys
from datetime import date
from pathlib import Path

from winotify import Notification, audio

import storage

HERE = Path(__file__).parent.resolve()
YES_BAT = HERE / "_action_yes.bat"
NO_BAT = HERE / "_action_no.bat"
OPEN_BAT = HERE / "_action_open.bat"


def _file_url(path):
    return "file:///" + str(path).replace("\\", "/")


def show_reminder():
    toast = Notification(
        app_id="Trade Reminder",
        title="Backtestowałeś dziś?",
        msg="Kliknij odpowiedź — dziennik czeka.",
        duration="long",
        launch=_file_url(OPEN_BAT),
    )
    toast.add_actions(label="Tak, testowałem", launch=_file_url(YES_BAT))
    toast.add_actions(label="Nie testowałem", launch=_file_url(NO_BAT))
    toast.set_audio(audio.Default, loop=False)
    toast.show()


def handle_yes():
    if storage.get_session(date.today()) is None:
        storage.save_session(date.today(), tested=True, session_type="Backtesting")
    _launch_detached([sys.executable, str(HERE / "journal_form.py")])


def handle_no():
    storage.save_session(date.today(), tested=False)


def handle_open():
    _launch_detached([sys.executable, str(HERE / "calendar_view.py")])


def _launch_detached(cmd):
    creationflags = 0
    if sys.platform == "win32":
        creationflags = 0x00000008  # DETACHED_PROCESS
    subprocess.Popen(cmd, close_fds=True, creationflags=creationflags)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", nargs="?", default="show", choices=["show", "yes", "no", "open"])
    args = parser.parse_args()
    {"show": show_reminder, "yes": handle_yes, "no": handle_no, "open": handle_open}[args.action]()


if __name__ == "__main__":
    main()
