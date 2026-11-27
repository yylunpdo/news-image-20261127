#!/usr/bin/env python3
"""THE WORLD TODAY - Friday 27 November 2026.

One image that sums up the world's news of Friday 27 November
2026. Pure Python standard library only: no image files, no
network, no fonts on disk. The program paints every pixel
itself and writes a 1024x1024 PNG. Running it twice gives the
same bytes twice.

The picture: the giant golden globe balloon of the 100th
Macy's Thanksgiving Day Parade, GROUNDED by a huge storm,
tethered low over a rain-lashed New York street instead of
marching. Its skin carries a big red GROUNDED stamp. Below it,
ordinary people in bright rain ponchos point up in awe, phones
raised, while storm clouds, rain and a lightning fork fill the
sky. The storm's toll is written on the street itself:
500,000+ homes without power, hundreds of flights cancelled,
80 million travelling for Thanksgiving.

The headlines in the ticker all happened, or were first
reported, on Friday 27 November 2026:

  * The 100th Macy's Thanksgiving Day Parade in New York is
    grounded by a major storm; 500,000+ homes lose power,
    hundreds of flights are cancelled, 80 million people are
    travelling for Thanksgiving.
  * An Iranian drone strike on Kuwait kills 2 Italian
    workers; Iran denies involvement (NYT / BBC / Reuters /
    NDTV).
  * Israel kills 10 people in Gaza; Hamas weighs a response;
    16 schoolchildren killed this month (Reuters / Guardian).
  * A major fire at a Bangkok oil refinery, several injured.
  * Gukesh vs Sindarov draw a marathon Game 3 of the World
    Chess Championship (India Today / The Hindu).
  * 300+ Russian troops killed backing Mali's junta
    (Guardian).
  * Trump demands a probe into "fake" US GDP figures after
    the revision to 4.3% (Mint).
  * UK net migration lowest since 1997 (NYT).
  * Kim Jong Un vows to add more nuclear weapons.
  * A diesel tanker capsizes near Ibiza, 1 dead (BBC).
  * Musk: every child in the US gets 2 SpaceX shares
    (The Hindu).
  * Ramaphosa wins a legal bid to scrap the impeachment
    report.
  * Black Friday.

Layout, top to bottom (1024x1024): masthead with the date,
the storm scene with the grounded balloon and the poncho
crowd, then the ticker strip with the day's headlines.
"""

import hashlib
import os
import struct
import zlib

W, H = 1024, 1024

# ------------------------------------------------------------------ font
# A 5x7 pixel font. Each glyph is seven strings of five
# characters; "1" paints, "0" stays clear. Capitals, digits and
# the punctuation the picture needs; anything else draws as "?".
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "|": ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
}


def glyph_rows(ch):
    """The seven rows for one character, uppercased."""
    return FONT.get(ch.upper(), FONT["?"])


# ---------------------------------------------------------------- canvas
class Canvas:
    """An RGB picture held as one flat bytearray, three bytes per
    pixel, rows top to bottom. Every helper clips to the page,
    so callers never have to check bounds themselves."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def _off(self, x, y):
        return (y * self.w + x) * 3

    def px(self, x, y, c):
        """Paint a single pixel, silently ignoring off-page ones."""
        if 0 <= x < self.w and 0 <= y < self.h:
            o = self._off(x, y)
            self.buf[o] = c[0]
            self.buf[o + 1] = c[1]
            self.buf[o + 2] = c[2]

    def fill_rect(self, x, y, w, h, c):
        """Paint a solid rectangle, clipped to the page."""
        xa = max(0, x)
        ya = max(0, y)
        xb = min(self.w, x + w)
        yb = min(self.h, y + h)
        if xb <= xa or yb <= ya:
            return
        row = bytes(c) * (xb - xa)
        for yy in range(ya, yb):
            o = self._off(xa, yy)
            self.buf[o:o + (xb - xa) * 3] = row

    def h_line(self, x0, x1, y, c):
        if x1 < x0:
            x0, x1 = x1, x0
        self.fill_rect(x0, y, x1 - x0 + 1, 1, c)

    def v_line(self, x, y0, y1, c):
        if y1 < y0:
            y0, y1 = y1, y0
        self.fill_rect(x, y0, 1, y1 - y0 + 1, c)

    def line(self, x0, y0, x1, y1, c):
        """A Bresenham segment between two points."""
        steep = abs(y1 - y0) > abs(x1 - x0)
        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1
        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0
        dx = x1 - x0
        dy = abs(y1 - y0)
        err = dx // 2
        step = 1 if y0 < y1 else -1
        y = y0
        for x in range(x0, x1 + 1):
            if steep:
                self.px(y, x, c)
            else:
                self.px(x, y, c)
            err -= dy
            if err < 0:
                y += step
                err += dx

    def filled_circle(self, cx, cy, r, c):
        """A solid disc, drawn row by row."""
        r2 = r * r
        for dy in range(-r, r + 1):
            half = int((r2 - dy * dy) ** 0.5)
            self.h_line(cx - half, cx + half, cy + dy, c)

    def circle_outline(self, cx, cy, r, c, thick=2):
        """Only the rim of a disc, `thick` pixels wide."""
        for k in range(thick):
            rr = r - k
            rr2 = rr * rr
            for dy in range(-rr, rr + 1):
                half = int((rr2 - dy * dy) ** 0.5)
                self.px(cx - half, cy + dy, c)
                self.px(cx + half, cy + dy, c)

    def poly(self, pts, c):
        """Draw a polygon's outline."""
        n = len(pts)
        for i in range(n):
            ax, ay = pts[i]
            bx, by = pts[(i + 1) % n]
            self.line(ax, ay, bx, by, c)

    def fill_poly(self, pts, c):
        """Fill a polygon with the even-odd rule; concave shapes
        are fine. Each row takes the crossings in pairs."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        top, bot = min(ys), max(ys)
        n = len(pts)
        for y in range(top, bot + 1):
            xs = []
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                if (y1 <= y < y2) or (y2 <= y < y1):
                    xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                self.h_line(int(xs[k] + 0.5), int(xs[k + 1] + 0.5), y, c)

    def shaded_circle(self, cx, cy, r, top, bot):
        """A disc whose colour runs from `top` to `bot` as y
        grows, so a sphere reads as lit from above."""
        r2 = r * r
        for dy in range(-r, r + 1):
            half = int((r2 - dy * dy) ** 0.5)
            t = (dy + r) / (2.0 * r)
            c = tuple(int(top[i] + (bot[i] - top[i]) * t)
                      for i in range(3))
            self.h_line(cx - half, cx + half, cy + dy, c)

    # ------------------------------------------------------------ text
    def draw_text(self, x, y, s, scale, c, adv=None):
        """Paint text left-aligned; returns the x just past it."""
        if adv is None:
            adv = 6 * scale
        cx = x
        for ch in s:
            rows = glyph_rows(ch)
            for r in range(7):
                row = rows[r]
                for col in range(5):
                    if row[col] == "1":
                        self.fill_rect(cx + col * scale, y + r * scale,
                                       scale, scale, c)
            cx += adv
        return cx

    def text_width(self, s, scale, adv=None):
        """How wide a string paints at this scale."""
        if adv is None:
            adv = 6 * scale
        if not s:
            return 0
        return len(s) * adv - (adv - 5 * scale)

    def text_centered(self, cx, y, s, scale, c, adv=None):
        """Paint text centred on x = cx."""
        self.draw_text(cx - self.text_width(s, scale, adv) // 2,
                       y, s, scale, c, adv)

    def wrap_text(self, s, max_w, scale, adv=None):
        """Greedy word wrap; every line fits in max_w pixels."""
        if adv is None:
            adv = 6 * scale
        lines = []
        cur = ""
        for word in s.split(" "):
            trial = word if not cur else cur + " " + word
            if self.text_width(trial, scale, adv) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines


# ------------------------------------------------------------------- png
def write_png(path, cv):
    """Encode the canvas as an 8-bit RGB PNG; returns its size."""
    raw = b"".join(
        b"\x00" + bytes(cv.buf[y * cv.w * 3:(y + 1) * cv.w * 3])
        for y in range(cv.h))
    blob = zlib.compress(raw, 6)

    def pack(kind, data):
        head = struct.pack(">I", len(data)) + kind + data
        return head + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += pack(b"IHDR", struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0))
    png += pack(b"IDAT", blob)
    png += pack(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

# ------------------------------------------------------------------ data
PAGE_BG = (248, 244, 233)
FG = (26, 26, 26)
ACCENT = (185, 28, 28)
HOT_RED = (226, 38, 38)
DEEP_NAVY = (30, 58, 95)
OFF_WHITE = (250, 250, 248)
STORM_TOP = (16, 20, 44)
STORM_MID = (48, 58, 86)
STORM_LOW = (96, 92, 96)
ROAD = (30, 32, 46)
GOLD_HI = (255, 214, 102)
GOLD_LO = (222, 148, 24)
GOLD_LITE = (255, 238, 170)
GREEN_A = (46, 130, 72)
GREEN_B = (30, 100, 60)
GOLD_SEAM = (176, 118, 18)
RAIN_C = (168, 186, 210)
CLOUD_C = (38, 42, 66)
CLOUD_DK = (24, 27, 46)
BOLT_Y = (255, 240, 140)
GOLD_WORD = (255, 214, 102)


def rng(seed):
    """Deterministic pseudo-random numbers: a tiny LCG with a
    fixed seed, so every run paints the same picture."""
    s = seed
    while True:
        s = (1103515245 * s + 12345) % 2147483648
        yield s


TICKER = (
    "PARADE GROUNDED BY STORM | IRAN DRONE STRIKE KILLS 2 IN KUWAIT | "
    "ISRAEL KILLS 10 IN GAZA | BANGKOK REFINERY FIRE INJURES SEVERAL | "
    "GUKESH-SINDAROV DRAW MARATHON GAME 3 | "
    "300+ RUSSIAN TROOPS KILLED IN MALI | "
    "TRUMP CALLS US GDP 'FAKE' AFTER 4.3% REVISION | "
    "UK NET MIGRATION LOWEST SINCE 1997 | KIM VOWS MORE NUCLEAR WEAPONS | "
    "DIESEL TANKER CAPSIZES OFF IBIZA, 1 DEAD | "
    "MUSK: EVERY US CHILD GETS 2 SPACEX SHARES | "
    "RAMAPHOSA WINS BID TO SCRAP IMPEACHMENT REPORT | BLACK FRIDAY"
)

# Poncho colours for the crowd, cycled in order.
PONCHOS = [
    (226, 38, 38), (29, 78, 216), (21, 128, 61), (245, 158, 11),
    (190, 24, 93), (8, 145, 178), (124, 58, 237), (234, 88, 12),
    (14, 116, 144), (220, 38, 150), (101, 163, 13), (250, 204, 21),
]
# Skin tones for the crowd, cycled in order.
SKINS = [(232, 190, 150), (198, 142, 96), (141, 96, 62), (245, 205, 170)]


# ------------------------------------------------------------------ scene
def paint_sky(cv):
    """A storm sky: dark slate bands, heavy cloud discs, one
    lightning fork, and diagonal rain over the whole scene."""
    top, bot = 94, 700
    bands = 46
    for b in range(bands):
        y0 = top + (bot - top) * b // bands
        y1 = top + (bot - top) * (b + 1) // bands
        t = b / (bands - 1)
        if t < 0.55:
            u = t / 0.55
            c = tuple(int(STORM_TOP[i] + (STORM_MID[i] - STORM_TOP[i]) * u)
                      for i in range(3))
        else:
            u = (t - 0.55) / 0.45
            c = tuple(int(STORM_MID[i] + (STORM_LOW[i] - STORM_MID[i]) * u)
                      for i in range(3))
        cv.fill_rect(0, y0, W, max(1, y1 - y0), c)
    # Cloud discs, kept below the masthead (y >= 94).
    roll = rng(20261127)
    for _ in range(16):
        x = 40 + next(roll) % 944
        y = 160 + next(roll) % 80
        r = 26 + next(roll) % 28
        cv.filled_circle(x, y, r, CLOUD_DK if next(roll) % 2 else CLOUD_C)
    # The lightning fork, upper right.
    fork = [(872, 120), (852, 168), (872, 168), (838, 236),
            (858, 236), (832, 300)]
    for i in range(len(fork) - 1):
        ax, ay = fork[i]
        bx, by = fork[i + 1]
        cv.line(ax, ay, bx, by, BOLT_Y)
        cv.line(ax + 2, ay, bx + 2, by, BOLT_Y)
    # Rain streaks, slanted by the wind.
    roll = rng(99)
    for _ in range(240):
        x = 10 + next(roll) % 1004
        y = 100 + next(roll) % 590
        ln = 8 + next(roll) % 10
        cv.line(x, y, x - 4, y + ln, RAIN_C)


def paint_balloon(cv):
    """The giant golden globe balloon, grounded and looming
    toward the viewer, its skin stamped GROUNDED."""
    cx, cy, r = 512, 500, 250
    cv.shaded_circle(cx, cy, r, GOLD_HI, GOLD_LO)
    # A soft highlight, upper left.
    cv.filled_circle(cx - 96, cy - 105, 68, GOLD_LITE)
    cv.filled_circle(cx - 84, cy - 92, 46, (255, 244, 200))
    # Balloon seams: darker gold chords.
    for off in (-165, -82, 0, 82, 165):
        x = cx + off
        half = int((r * r - off * off) ** 0.5)
        cv.v_line(x, cy - half + 6, cy + half - 6, GOLD_SEAM)
    # Rough continents on the globe.
    cv.fill_poly([(414, 372), (472, 358), (498, 388), (480, 430),
                  (436, 440), (408, 408)], GREEN_A)       # N. America
    cv.fill_poly([(472, 472), (516, 462), (534, 504), (508, 546),
                  (478, 522)], GREEN_B)                    # S. America
    cv.fill_poly([(592, 392), (644, 382), (670, 416), (648, 452),
                  (602, 444)], GREEN_A)                    # Africa
    cv.fill_poly([(626, 340), (732, 322), (768, 364), (732, 398),
                  (662, 390)], GREEN_B)                    # Eurasia
    cv.fill_poly([(682, 516), (744, 506), (762, 540), (700, 550)],
                 GREEN_A)                                  # Australia
    cv.circle_outline(cx, cy, r, (120, 78, 8), 3)
    # The big red GROUNDED stamp across the skin.
    word = "GROUNDED"
    w = cv.text_width(word, 3, 16) + 16
    h = 62
    sx, sy = 512 - w // 2, 452
    cv.fill_rect(sx, sy, w, h, (255, 245, 230))
    cv.fill_rect(sx, sy, w, 4, HOT_RED)
    cv.fill_rect(sx, sy + h - 4, w, 4, HOT_RED)
    cv.fill_rect(sx, sy, 4, h, HOT_RED)
    cv.fill_rect(sx + w - 4, sy, 4, h, HOT_RED)
    cv.draw_text(sx + 8, sy + 8, word, 3, HOT_RED, adv=16)
    cv.draw_text(sx + 8, sy + 36, "100TH MACY'S", 2, HOT_RED, adv=11)


def paint_tethers(cv):
    """Ropes straining from the balloon down to anchors on the
    wet street."""
    for (bx, by, gx, gy) in [(330, 620, 250, 838), (694, 620, 774, 838),
                             (392, 700, 340, 838), (632, 700, 684, 838)]:
        cv.line(bx, by, gx, gy, (220, 210, 180))
        cv.line(bx + 2, by, gx + 2, gy, (220, 210, 180))
    for gx in (250, 340, 684, 774):
        cv.fill_rect(gx - 10, 838, 20, 8, (90, 88, 100))


def paint_people(cv):
    """Ordinary people in bright rain ponchos along the street,
    hoods up, pointing at the grounded balloon in awe, phones
    raised. Rain splashes speckle the wet street."""
    roll = rng(1127)
    base = 838
    for i in range(34):
        x = 30 + i * 29 + (next(roll) % 12)
        hgt = 46 + next(roll) % 18
        poncho = PONCHOS[next(roll) % len(PONCHOS)]
        skin = SKINS[next(roll) % len(SKINS)]
        # The poncho: a wide trapezoid.
        cv.fill_poly([(x - 13, base), (x + 13, base),
                      (x + 8, base - hgt + 16),
                      (x - 8, base - hgt + 16)], poncho)
        # The hood over the head.
        cv.fill_poly([(x - 9, base - hgt + 12), (x + 9, base - hgt + 12),
                      (x + 5, base - hgt - 4),
                      (x - 5, base - hgt - 4)], poncho)
        cv.filled_circle(x, base - hgt + 6, 5, skin)
        # Both arms raised toward the balloon.
        cv.line(x - 8, base - hgt + 20, x - 18, base - hgt - 6, skin)
        cv.line(x + 8, base - hgt + 20, x + 18, base - hgt - 8, skin)
        # A phone in one raised hand, every third person.
        if i % 3 == 0:
            cv.fill_rect(x + 15, base - hgt - 16, 7, 11, FG)
            cv.fill_rect(x + 16, base - hgt - 15, 5, 9, (160, 220, 255))
    # Splashes on the wet street.
    for _ in range(60):
        x = 10 + next(roll) % 1004
        y = 700 + next(roll) % 150
        cv.fill_rect(x, y, 5, 2, (120, 130, 150))


def paint_toll(cv):
    """The storm's toll, written on the dark street band where
    the crowd's heads cannot cover it."""
    cv.draw_text(28, 706, "500,000+ HOMES", 2, OFF_WHITE, adv=11)
    cv.draw_text(28, 720, "WITHOUT POWER", 2, OFF_WHITE, adv=11)
    cv.draw_text(28, 734, "80 MILLION TRAVELLING", 2, GOLD_WORD, adv=11)
    cv.draw_text(812, 706, "100S OF FLIGHTS", 2, OFF_WHITE, adv=11)
    cv.draw_text(812, 720, "CANCELLED", 2, OFF_WHITE, adv=11)
    cv.draw_text(812, 734, "NEW YORK", 2, GOLD_WORD, adv=11)


def build_page():
    cv = Canvas(W, H, PAGE_BG)
    # Masthead: red rule, title, the date in big red type, tagline.
    cv.fill_rect(0, 0, W, 8, ACCENT)
    cv.text_centered(512, 14, "THE WORLD TODAY", 4, FG, adv=22)
    cv.text_centered(512, 46, "FRIDAY 27 NOVEMBER 2026", 3, ACCENT, adv=16)
    cv.text_centered(512, 72, "ONE DAY - ONE IMAGE", 2, DEEP_NAVY, adv=11)
    cv.h_line(16, 1007, 92, FG)
    # The scene.
    paint_sky(cv)
    paint_balloon(cv)
    # Wet street band first, then the tethers over it so they
    # reach the ground instead of vanishing behind the band.
    cv.fill_rect(0, 700, W, 160, ROAD)
    cv.h_line(0, 1023, 700, (90, 90, 110))
    paint_tethers(cv)
    paint_toll(cv)
    paint_people(cv)
    # Ticker strip with the day's headlines.
    cv.fill_rect(0, 860, W, 164, PAGE_BG)
    cv.h_line(0, 1023, 860, ACCENT)
    cv.h_line(0, 1023, 862, ACCENT)
    cv.draw_text(16, 872, "THE DAY IN HEADLINES", 2, ACCENT, adv=11)
    lines = cv.wrap_text(TICKER, 992, 2, adv=11)
    y = 892
    for ln in lines:
        cv.draw_text(16, y, ln, 2, FG, adv=11)
        y += 16
    cv.draw_text(16, 1000,
                 "SOURCES: NYT / BBC / REUTERS / GUARDIAN - EVENTS OF 27 NOV 2026",
                 2, DEEP_NAVY, adv=11)
    return cv, lines


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    cv, lines = build_page()
    n = write_png(os.path.join(outdir, "entry.png"), cv)
    print("ticker lines: %d" % len(lines))
    for ln in lines:
        print("  | %s" % ln)
    print("png bytes: %d" % n)
    assert n <= 1048576, "png over 1 MiB"
    data = open(os.path.join(outdir, "entry.png"), "rb").read()
    print("sha256: %s" % hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
