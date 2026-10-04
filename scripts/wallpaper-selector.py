from __future__ import annotations

import argparse
import curses
import locale
import os
import random
import shutil
import subprocess
import sys
import time
from collections import namedtuple
from pathlib import Path

EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff", ".tga"}
DEFAULT_DIR = Path.home() / "Pictures" / "Wallpapers"
CACHE_LINK = Path.home() / ".cache" / "current_wallpaper"

Wall = namedtuple("Wall", "path name real")

# Backend communication
def _awww_alive() -> bool:
    try:
        return subprocess.run(["awww", "query"], capture_output=True).returncode == 0
    except FileNotFoundError:
        raise RuntimeError("awww not found in PATH")


def ensure_daemon() -> None:
    if _awww_alive():
        return
    try:
        subprocess.Popen(
            ["awww-daemon"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except FileNotFoundError:
        raise RuntimeError("awww-daemon not found in PATH")
    for _ in range(30):
        time.sleep(0.1)
        if _awww_alive():
            return
    raise RuntimeError("awww-daemon did not respond")


def link_cache(path: Path) -> None:
    CACHE_LINK.parent.mkdir(parents=True, exist_ok=True)
    tmp = CACHE_LINK.with_name(CACHE_LINK.name + ".tmp")
    try:
        tmp.unlink()
    except FileNotFoundError:
        pass
    os.symlink(path, tmp)
    os.replace(tmp, CACHE_LINK)


def apply_wallpaper(path, opts) -> None:
    path = Path(os.path.abspath(path))
    ensure_daemon()
    cmd = ["awww", "img", str(path)]
    if opts.transition:
        cmd += ["--transition-type", opts.transition,
                "--transition-duration", str(opts.duration)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        err = (r.stderr or r.stdout or "").strip().splitlines()
        raise RuntimeError(err[-1] if err else "awww img failed")
    link_cache(path)


def restore_wallpaper() -> None:
    target = os.path.realpath(CACHE_LINK)
    if not os.path.exists(target):
        raise RuntimeError(f"nothing to restore at {CACHE_LINK}")
    ensure_daemon()
    r = subprocess.run(["awww", "img", target, "--transition-type", "none"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        err = (r.stderr or r.stdout or "").strip().splitlines()
        raise RuntimeError(err[-1] if err else "awww img failed")


def current_real() -> str | None:
    try:
        return os.path.realpath(CACHE_LINK) if CACHE_LINK.exists() else None
    except OSError:
        return None


def scan(directory: Path, recursive: bool) -> list[Wall]:
    it = directory.rglob("*") if recursive else directory.iterdir()
    files = [p for p in it if p.suffix.lower() in EXTS and p.is_file()]
    files.sort(key=lambda p: p.relative_to(directory).as_posix().lower())
    return [Wall(p, p.relative_to(directory).as_posix(), os.path.realpath(p))
            for p in files]


# Image preview handling
def detect_format() -> str:
    env = os.environ
    term = env.get("TERM", "")
    if env.get("TMUX"):
        return "symbols"
    if (env.get("KITTY_WINDOW_ID") or "kitty" in term or "ghostty" in term
            or env.get("TERM_PROGRAM", "").lower() == "ghostty"):
        return "kitty"
    if "foot" in term:
        return "sixel"
    return "symbols"


KITTY_DELETE_ALL = "\x1b_Ga=d,d=A,q=2\x1b\\"


class Previewer:
    def __init__(self, fmt: str):
        self.chafa = shutil.which("chafa")
        self.fmt = detect_format() if fmt == "auto" else fmt
        self.cache: dict = {}

    def render(self, path, w: int, h: int):
        key = (str(path), w, h, self.fmt)
        if key in self.cache:
            return self.cache[key]
        if not self.chafa:
            res = ("chafa not found.\nInstall it to view previews.", True)
        else:
            cmd = [self.chafa, "-f", self.fmt, "-s", f"{w}x{h}", "--animate=off"]
            if self.fmt == "symbols":
                cmd += ["-c", "full"]
            cmd.append(str(path))
            try:
                r = subprocess.run(cmd, stdin=subprocess.DEVNULL,
                                   capture_output=True, timeout=20)
                if r.returncode == 0 and r.stdout:
                    res = (r.stdout.decode("utf-8", "replace"), False)
                else:
                    err = r.stderr.decode("utf-8", "replace").strip().splitlines()
                    res = ("Failed to generate preview:\n" + (err[-1] if err else ""), True)
            except subprocess.TimeoutExpired:
                res = ("Preview timed out.", True)
        if len(self.cache) >= 16:
            self.cache.pop(next(iter(self.cache)))
        self.cache[key] = res
        return res

    def show(self, blob, is_text, x, y, w, h) -> None:
        buf = ["\x1b7"]
        if self.fmt == "kitty":
            buf.append(KITTY_DELETE_ALL)
        blank = " " * w
        for r in range(h):
            buf.append(f"\x1b[{y + r + 1};{x + 1}H{blank}")
        if blob:
            if is_text or self.fmt == "symbols":
                for i, line in enumerate(blob.rstrip("\n").split("\n")[:h]):
                    if is_text:
                        line = line[:w]
                    buf.append(f"\x1b[{y + i + 1};{x + 1}H{line}\x1b[0m")
            else:
                buf.append(f"\x1b[{y + 1};{x + 1}H{blob.rstrip(chr(10) + chr(13))}")
        buf.append("\x1b[0m\x1b8")
        sys.stdout.write("".join(buf))
        sys.stdout.flush()

    def cleanup(self) -> None:
        if self.fmt == "kitty":
            sys.stdout.write(KITTY_DELETE_ALL)
            sys.stdout.flush()


# Interface
Geo = namedtuple("Geo", "rows cols left_w list_h px py pw ph small")


def put(win, y: int, x: int, text: str, attr: int = 0) -> None:
    h, w = win.getmaxyx()
    if y < 0 or y >= h or x >= w:
        return
    text = text[: max(0, w - x - (1 if y == h - 1 else 0))]
    try:
        win.addstr(y, x, text, attr)
    except curses.error:
        pass


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


class App:
    def __init__(self, scr, walls: list[Wall], opts):
        self.scr = scr
        self.walls = walls
        self.opts = opts
        self.prev = Previewer(opts.format)
        self.view = list(walls)
        self.query = ""
        self.idx = 0
        self.top = 0
        self.msg = ""
        self.msg_attr = 0
        self.mode = "normal"
        self.pending = True
        self.cur_real = current_real()

        curses.curs_set(0)
        curses.use_default_colors()
        for i, c in enumerate((curses.COLOR_GREEN, curses.COLOR_RED, curses.COLOR_CYAN), 1):
            curses.init_pair(i, c, -1)
        self.GREEN, self.RED, self.CYAN = (curses.color_pair(i) for i in (1, 2, 3))

        utf8 = "utf" in (locale.getpreferredencoding(False) or "").lower()
        self.dot = "●" if utf8 else "*"
        self.hline = "─" if utf8 else "-"
        self.vline = "│" if utf8 else "|"
        self.ok = "✔" if utf8 else "OK"
        self.bad = "✘" if utf8 else "ERROR"
        self.ell = "…" if utf8 else "~"

        for i, w in enumerate(self.view):
            if w.real == self.cur_real:
                self.idx = i
                break

    def geo(self) -> Geo:
        rows, cols = self.scr.getmaxyx()
        left_w = min(max(cols // 3, 22), 44)
        list_h = max(rows - 4, 0)
        px = left_w + 2
        return Geo(rows, cols, left_w, list_h, px, 3, cols - px - 1,
                   list_h - 1, rows < 10 or cols < 50)

    def refilter(self) -> None:
        cur = self.view[self.idx].path if self.view else None
        q = self.query.lower()
        self.view = [w for w in self.walls if q in w.name.lower()]
        self.idx = 0
        for i, w in enumerate(self.view):
            if w.path == cur:
                self.idx = i
                break
        self.top = 0
        self.pending = True

    def apply(self, w: Wall) -> None:
        self.msg, self.msg_attr = "Applying...", self.CYAN
        self.draw()
        try:
            apply_wallpaper(w.path, self.opts)
            self.cur_real = w.real
            self.msg, self.msg_attr = f"{self.ok} Applied: {w.name}", self.GREEN
        except Exception as e:
            self.msg, self.msg_attr = f"{self.bad} {e}", self.RED

    def draw(self) -> None:
        s = self.scr
        g = self.geo()
        s.erase()
        if g.small:
            put(s, 0, 0, "Terminal too small")
            s.refresh()
            return

        put(s, 0, 1, "Wallpaper Selector", curses.A_BOLD)
        count = f"{len(self.view)}/{len(self.walls)} "
        put(s, 0, g.cols - len(count) - 1, count, self.CYAN)
        put(s, 1, 0, self.hline * g.cols)

        if self.idx < self.top:
            self.top = self.idx
        elif self.idx >= self.top + g.list_h:
            self.top = self.idx - g.list_h + 1

        for r in range(g.list_h):
            i = self.top + r
            if i >= len(self.view):
                break
            w = self.view[i]
            sel = i == self.idx
            is_cur = w.real == self.cur_real
            text = f"   {w.name}"
            if len(text) > g.left_w:
                text = text[: g.left_w - 1] + self.ell
            attr = curses.A_REVERSE if sel else 0
            put(s, 2 + r, 0, text.ljust(g.left_w), attr)
            if is_cur:
                put(s, 2 + r, 1, self.dot, self.GREEN | attr)

        for r in range(2, g.rows - 2):
            put(s, r, g.left_w, self.vline)

        if self.view:
            w = self.view[self.idx]
            try:
                size = human(w.path.stat().st_size)
            except OSError:
                size = "?"
            put(s, 2, g.px, f"{w.name}  ({size})", curses.A_BOLD)
        else:
            put(s, 2, g.px, "No wallpapers found", curses.A_DIM)

        if self.mode == "filter":
            put(s, g.rows - 2, 1, "/" + self.query + "█")
            put(s, g.rows - 1, 1, "Enter confirm · Esc clear filter", curses.A_DIM)
        else:
            if self.msg:
                put(s, g.rows - 2, 1, self.msg, self.msg_attr)
            put(s, g.rows - 1, 1,
                "↑↓/jk navigate · Enter apply · r random · / filter · q quit",
                curses.A_DIM)
        s.refresh()

    def show_preview(self) -> None:
        g = self.geo()
        if g.small or g.pw < 4 or g.ph < 2:
            return
        if not self.view:
            self.prev.show(None, False, g.px, g.py, g.pw, g.ph)
            return
        blob, is_text = self.prev.render(self.view[self.idx].path, g.pw, g.ph)
        self.prev.show(blob, is_text, g.px, g.py, g.pw, g.ph)

    def handle(self, key) -> bool:
        self.msg = ""
        if key == curses.KEY_RESIZE:
            self.scr.clear()
            self.pending = True
            return False

        g = self.geo()
        old = self.idx
        page = max(g.list_h - 1, 1)
        enter = ("\n", "\r", curses.KEY_ENTER)

        if self.mode == "filter":
            if key in enter:
                self.mode = "normal"
            elif key == "\x1b":
                self.query = ""
                self.mode = "normal"
                self.refilter()
            elif key in (curses.KEY_BACKSPACE, "\x7f", "\b"):
                self.query = self.query[:-1]
                self.refilter()
            elif key == curses.KEY_UP:
                self.idx -= 1
            elif key == curses.KEY_DOWN:
                self.idx += 1
            elif isinstance(key, str) and key.isprintable():
                self.query += key
                self.refilter()
        else:
            if key in ("q", "\x1b"):
                return True
            elif key in (curses.KEY_UP, "k"):
                self.idx -= 1
            elif key in (curses.KEY_DOWN, "j"):
                self.idx += 1
            elif key == curses.KEY_PPAGE:
                self.idx -= page
            elif key == curses.KEY_NPAGE:
                self.idx += page
            elif key in (curses.KEY_HOME, "g"):
                self.idx = 0
            elif key in (curses.KEY_END, "G"):
                self.idx = len(self.view) - 1
            elif key in enter:
                if self.view:
                    self.apply(self.view[self.idx])
            elif key == "r":
                if self.view:
                    pool = [i for i, w in enumerate(self.view) if w.real != self.cur_real]
                    self.idx = random.choice(pool or range(len(self.view)))
                    self.apply(self.view[self.idx])
            elif key == "/":
                self.mode = "filter"

        self.idx = max(0, min(self.idx, len(self.view) - 1)) if self.view else 0
        if self.idx != old:
            self.pending = True
        return False

    def run(self) -> None:
        self.scr.keypad(True)
        try:
            while True:
                self.draw()
                self.scr.timeout(110 if self.pending else -1)
                try:
                    key = self.scr.get_wch()
                except curses.error:
                    key = None
                if key is None:
                    if self.pending:
                        self.pending = False
                        self.show_preview()
                    continue
                if self.handle(key):
                    break
        finally:
            self.prev.cleanup()


# Entry point
def main() -> int:
    ap = argparse.ArgumentParser(description="TUI Wallpaper Selector (awww)")
    ap.add_argument("-d", "--dir", type=Path, default=DEFAULT_DIR,
                    help=f"wallpaper directory (default: {DEFAULT_DIR})")
    ap.add_argument("-r", "--recursive", action="store_true", help="include subdirectories")
    ap.add_argument("--format", choices=["auto", "kitty", "sixel", "symbols"],
                    default="auto", help="chafa preview format (default: auto)")
    ap.add_argument("--transition", default="fade",
                    help="awww transition type (fade, simple, wipe, grow, none...)")
    ap.add_argument("--duration", type=float, default=0.6, help="transition duration (s)")
    ap.add_argument("--set", metavar="FILE", help="apply image and exit")
    ap.add_argument("--random", action="store_true", help="apply random wallpaper and exit")
    ap.add_argument("--restore", action="store_true", help="reapply cached wallpaper and exit")
    opts = ap.parse_args()

    try:
        if opts.restore:
            restore_wallpaper()
            return 0
        if opts.set:
            p = Path(opts.set).expanduser()
            if not p.is_file():
                raise RuntimeError(f"file not found: {p}")
            apply_wallpaper(p, opts)
            return 0

        opts.dir = opts.dir.expanduser()
        if not opts.dir.is_dir():
            raise RuntimeError(f"directory not found: {opts.dir}")
        walls = scan(opts.dir, opts.recursive)
        if not walls:
            raise RuntimeError(f"no images found in {opts.dir}")

        if opts.random:
            cur = current_real()
            pool = [w for w in walls if w.real != cur] or walls
            apply_wallpaper(random.choice(pool).path, opts)
            return 0
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        print("error: TUI requires an interactive terminal", file=sys.stderr)
        return 1

    locale.setlocale(locale.LC_ALL, "")
    os.environ.setdefault("ESCDELAY", "25")
    curses.wrapper(lambda scr: App(scr, walls, opts).run())
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)