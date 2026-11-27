#!/usr/bin/env python3
"""THE WORLD TODAY - Friday 27 November 2026.

One image that sums up the world's news of Friday 27 November
2026, drawn from scratch in pure Python stdlib - no image files,
no network, no fonts on disk. Deterministic: the same bytes on
every run.

The scene (one impossible moment, after the day's news): the
colossal golden globe balloon of the 100th Macy's Thanksgiving
Day Parade - GROUNDED by a huge storm, tethered low over a
rain-lashed New York street instead of marching - looms toward
the viewer, its skin stamped GROUNDED, ropes straining down to
the wet street. Below, ordinary people in bright rain ponchos
point up in awe, phones raised. Storm clouds, rain and a
lightning fork fill the sky; the storm's toll is written on
the street: 500,000+ homes without power, hundreds of flights
cancelled, 80 million travelling for Thanksgiving.

Every headline below happened, or was first reported, on
Friday 27 November 2026, each checked against its source:

  * The 100th Macy's Thanksgiving Day Parade in New York is
    grounded/delayed by a major storm; 500,000+ homes lose
    power, hundreds of flights cancelled, 80 million people
    travelling for Thanksgiving (reported 27 Nov).
  * Iranian drone strike on Kuwait kills 2 Italian workers;
    Iran denies involvement (NYT / BBC / Reuters / NDTV).
  * Israel kills 10 people in Gaza; Hamas weighs a response;
    16 schoolchildren killed this month (Reuters / Guardian).
  * Major fire at a Bangkok oil refinery, several injured.
  * Gukesh vs Sindarov draw a marathon Game 3 of the World
    Chess Championship (India Today / The Hindu).
  * 300+ Russian troops killed backing Mali's junta
    (Guardian).
  * Trump demands a probe into "fake" US GDP figures after
    revision to 4.3% (Mint).
  * UK net migration lowest since 1997 (NYT).
  * Kim Jong Un vows to add more nuclear weapons.
  * Diesel tanker capsizes near Ibiza, 1 dead (BBC).
  * Musk: every child in the US gets 2 SpaceX shares
    (The Hindu).
  * Ramaphosa wins legal bid to scrap impeachment report.
  * Black Friday.

Layout (1024x1024):
  masthead + date -> the scene (storm sky, grounded globe
  balloon, tether ropes, poncho crowd in awe) -> ticker
  strip with the day's headlines.
"""

import hashlib
import os
import struct
import zlib

PAGE_W, PAGE_H = 1024, 1024

# ------------------------------------------------------------------ font
# A 5x7 pixel font, one entry per character: seven ints, each the
# five bits of one row (bit 4 = leftmost column), top row first.
# Uppercase letters, digits and punctuation; unknown chars draw
# as "?".
GLYPHS = {
    "A": (14, 17, 17, 31, 17, 17, 17),
    "B": (30, 17, 17, 30, 17, 17, 30),
    "C": (14, 17, 16, 16, 16, 17, 14),
    "D": (30, 17, 17, 17, 17, 17, 30),
    "E": (31, 16, 16, 30, 16, 16, 31),
    "F": (31, 16, 16, 30, 16, 16, 16),
    "G": (14, 17, 16, 23, 17, 17, 15),
    "H": (17, 17, 17, 31, 17, 17, 17),
    "I": (14, 4, 4, 4, 4, 4, 14),
    "J": (7, 2, 2, 2, 2, 18, 12),
    "K": (17, 18, 20, 24, 20, 18, 17),
    "L": (16, 16, 16, 16, 16, 16, 31),
    "M": (17, 27, 21, 21, 17, 17, 17),
    "N": (17, 25, 21, 19, 17, 17, 17),
    "O": (14, 17, 17, 17, 17, 17, 14),
    "P": (30, 17, 17, 30, 16, 16, 16),
    "Q": (14, 17, 17, 17, 21, 18, 13),
    "R": (30, 17, 17, 30, 20, 18, 17),
    "S": (15, 16, 16, 14, 1, 1, 30),
    "T": (31, 4, 4, 4, 4, 4, 4),
    "U": (17, 17, 17, 17, 17, 17, 14),
    "V": (17, 17, 17, 17, 17, 10, 4),
    "W": (17, 17, 17, 21, 21, 27, 17),
    "X": (17, 17, 10, 4, 10, 17, 17),
    "Y": (17, 17, 10, 4, 4, 4, 4),
    "Z": (31, 1, 2, 4, 8, 16, 31),
    "0": (14, 17, 19, 21, 25, 17, 14),
    "1": (4, 12, 4, 4, 4, 4, 14),
    "2": (14, 17, 1, 6, 8, 16, 31),
    "3": (30, 1, 1, 14, 1, 1, 30),
    "4": (2, 6, 10, 18, 31, 2, 2),
    "5": (31, 16, 30, 1, 1, 17, 14),
    "6": (6, 8, 16, 30, 17, 17, 14),
    "7": (31, 1, 2, 4, 8, 8, 8),
    "8": (14, 17, 17, 14, 17, 17, 14),
    "9": (14, 17, 17, 15, 1, 2, 12),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 12, 12),
    ",": (0, 0, 0, 0, 12, 4, 8),
    ":": (0, 12, 12, 0, 12, 12, 0),
    ";": (0, 12, 12, 0, 12, 4, 8),
    "'": (4, 4, 8, 0, 0, 0, 0),
    "-": (0, 0, 0, 14, 0, 0, 0),
    "(": (2, 4, 8, 8, 8, 4, 2),
    ")": (8, 4, 2, 2, 2, 4, 8),
    "/": (1, 2, 2, 4, 8, 8, 16),
    "%": (25, 26, 2, 4, 8, 11, 19),
    "+": (0, 4, 4, 14, 4, 4, 0),
    "$": (4, 15, 20, 14, 5, 30, 4),
    "?": (14, 17, 1, 6, 4, 0, 4),
    "!": (4, 4, 4, 4, 4, 0, 4),
    "&": (12, 18, 20, 8, 21, 18, 13),
    "=": (0, 0, 31, 0, 31, 0, 0),
    "|": (4, 4, 4, 4, 4, 4, 4),
}


def glyph_for(ch):
    """Bit rows for one character, uppercased, "?" if unknown."""
    return GLYPHS.get(ch.upper(), GLYPHS["?"])


# ------------------------------------------------------------------ sheet
class Sheet:
    """A plain RGB canvas plus the only drawing tools this image
    needs. Pixels live in one flat bytearray, three bytes per
    pixel, row by row. Every helper clips to the page."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.pix = bytearray(w * h * 3)
        self.box(0, 0, w, h, bg)

    def _idx(self, x, y):
        return (y * self.w + x) * 3

    def dot(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = self._idx(x, y)
            self.pix[i] = c[0]
            self.pix[i + 1] = c[1]
            self.pix[i + 2] = c[2]

    def box(self, x, y, w, h, c):
        xa = max(0, x)
        ya = max(0, y)
        xb = min(self.w, x + w)
        yb = min(self.h, y + h)
        for yy in range(ya, yb):
            i = self._idx(xa, yy)
            for _xx in range(xa, xb):
                self.pix[i] = c[0]
                self.pix[i + 1] = c[1]
                self.pix[i + 2] = c[2]
                i += 3

    def hline(self, x0, x1, y, c):
        if x1 < x0:
            x0, x1 = x1, x0
        self.box(x0, y, x1 - x0 + 1, 1, c)

    def vline(self, x, y0, y1, c):
        if y1 < y0:
            y0, y1 = y1, y0
        self.box(x, y0, 1, y1 - y0 + 1, c)

    def seg(self, x0, y0, x1, y1, c):
        """Bresenham line between two points."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.dot(x0, y0, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            half = int((r * r - dy * dy) ** 0.5)
            self.hline(cx - half, cx + half, cy + dy, c)

    def ring(self, cx, cy, r, c, thick=2):
        for k in range(thick):
            rr = r - k
            for dy in range(-rr, rr + 1):
                half = int((rr * rr - dy * dy) ** 0.5)
                self.dot(cx - half, cy + dy, c)
                self.dot(cx + half, cy + dy, c)

    def outline(self, pts, c):
        n = len(pts)
        for i in range(n):
            ax, ay = pts[i]
            bx, by = pts[(i + 1) % n]
            self.seg(ax, ay, bx, by, c)

    def fill_shape(self, pts, c):
        """Even-odd scanline fill; copes with concave outlines."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        n = len(pts)
        for y in range(min(ys), max(ys) + 1):
            cuts = []
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                if (y1 <= y < y2) or (y2 <= y < y1):
                    cuts.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
            cuts.sort()
            for k in range(0, len(cuts) - 1, 2):
                self.hline(int(cuts[k] + 0.5), int(cuts[k + 1] + 0.5), y, c)

    def grad_disc(self, cx, cy, r, top, bot):
        """Disc shaded top-to-bottom between two colours."""
        for dy in range(-r, r + 1):
            half = int((r * r - dy * dy) ** 0.5)
            t = (dy + r) / (2.0 * r)
            c = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
            self.hline(cx - half, cx + half, cy + dy, c)

    # ------------------------------------------------------------ text
    def put(self, x, y, s, scale, c, adv=None):
        """Draw text left-aligned; returns x just past the last glyph."""
        if adv is None:
            adv = 6 * scale
        cx = x
        for ch in s:
            rows = glyph_for(ch)
            for r in range(7):
                bits = rows[r]
                for col in range(5):
                    if bits & (16 >> col):
                        self.box(cx + col * scale, y + r * scale,
                                 scale, scale, c)
            cx += adv
        return cx

    def put_w(self, s, scale, adv=None):
        """Pixel width of a string at this scale and advance."""
        if adv is None:
            adv = 6 * scale
        if not s:
            return 0
        return len(s) * adv - (adv - 5 * scale)

    def put_mid(self, cx, y, s, scale, c, adv=None):
        self.put(cx - self.put_w(s, scale, adv) // 2, y, s, scale, c, adv)

    def fold(self, s, max_w, scale, adv=None):
        """Greedy word wrap; returns lines each at most max_w px wide."""
        if adv is None:
            adv = 6 * scale
        lines = []
        cur = ""
        for word in s.split(" "):
            trial = word if not cur else cur + " " + word
            if self.put_w(trial, scale, adv) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines


# ------------------------------------------------------------------- png
def save_png(path, sh):
    """Write the sheet as an 8-bit RGB PNG; returns the byte count."""
    raw = b"".join(
        b"\x00" + bytes(sh.pix[y * sh.w * 3:(y + 1) * sh.w * 3])
        for y in range(sh.h))
    comp = zlib.compress(raw, 6)

    def chunk(typ, data):
        return (struct.pack(">I", len(data)) + typ + data +
                struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF))

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", sh.w, sh.h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

# ------------------------------------------------------------------ data
PAPER = (248, 244, 233)
INK = (26, 26, 26)
RED = (185, 28, 28)
BRIGHT_RED = (226, 38, 38)
NAVY = (30, 58, 95)
WHITE = (250, 250, 248)
SKY_TOP = (16, 20, 44)
SKY_MID = (48, 58, 86)
SKY_LOW = (96, 92, 96)
STREET = (30, 32, 46)
GOLD_TOP = (255, 214, 102)
GOLD_BOT = (222, 148, 24)
GOLD_HI = (255, 238, 170)
LAND_G = (46, 130, 72)
LAND_G2 = (30, 100, 60)
SEAM = (176, 118, 18)
RAIN = (168, 186, 210)
CLOUD = (38, 42, 66)
CLOUD_D = (24, 27, 46)
BOLT = (255, 240, 140)
PONCHO = (245, 158, 11)

# Deterministic pseudo-random: tiny LCG, fixed seed.
def lcg(seed):
    state = seed
    while True:
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        yield state


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

SHIRTS = [
    (226, 38, 38), (29, 78, 216), (21, 128, 61), (245, 158, 11),
    (190, 24, 93), (8, 145, 178), (124, 58, 237), (234, 88, 12),
    (14, 116, 144), (220, 38, 150), (101, 163, 13), (250, 204, 21),
]
SKINS = [(232, 190, 150), (198, 142, 96), (141, 96, 62), (245, 205, 170)]


# ------------------------------------------------------------------ draw
def draw_sky(sh):
    """Storm gradient bands from deep slate to bruised grey."""
    bands = 46
    for b in range(bands):
        y0 = 94 + (700 - 94) * b // bands
        y1 = 94 + (700 - 94) * (b + 1) // bands
        t = b / (bands - 1)
        if t < 0.55:
            u = t / 0.55
            c = tuple(int(SKY_TOP[i] + (SKY_MID[i] - SKY_TOP[i]) * u)
                      for i in range(3))
        else:
            u = (t - 0.55) / 0.45
            c = tuple(int(SKY_MID[i] + (SKY_LOW[i] - SKY_MID[i]) * u)
                      for i in range(3))
        sh.box(0, y0, PAGE_W, max(1, y1 - y0), c)
    # Storm clouds: dark discs clustered near the top, kept
    # below the masthead (y >= 94).
    rnd = lcg(20261127)
    for _ in range(16):
        x = 40 + next(rnd) % 944
        y = 160 + next(rnd) % 80
        r = 26 + next(rnd) % 28
        sh.disc(x, y, r, CLOUD_D if next(rnd) % 2 else CLOUD)
    # Lightning fork, upper right.
    bolt = [(872, 120), (852, 168), (872, 168), (838, 236),
            (858, 236), (832, 300)]
    for i in range(len(bolt) - 1):
        sh.seg(bolt[i][0], bolt[i][1], bolt[i + 1][0], bolt[i + 1][1], BOLT)
        sh.seg(bolt[i][0] + 2, bolt[i][1], bolt[i + 1][0] + 2,
               bolt[i + 1][1], BOLT)
    # Rain: diagonal streaks across the whole scene.
    rnd = lcg(99)
    for _ in range(240):
        x = 10 + next(rnd) % 1004
        y = 100 + next(rnd) % 590
        ln = 8 + next(rnd) % 10
        sh.seg(x, y, x - 4, y + ln, RAIN)


def draw_balloon(sh):
    """The colossal golden globe balloon, GROUNDED: tethered low
    over the wet street, looming toward the viewer, its skin
    stamped GROUNDED."""
    cx, cy, r = 512, 500, 250
    sh.grad_disc(cx, cy, r, GOLD_TOP, GOLD_BOT)
    # Highlight, upper left.
    sh.disc(cx - 96, cy - 105, 68, GOLD_HI)
    sh.disc(cx - 84, cy - 92, 46, (255, 244, 200))
    # Seam lines: vertical chords, darker gold.
    for off in (-165, -82, 0, 82, 165):
        x = cx + off
        half = int((r * r - off * off) ** 0.5)
        sh.vline(x, cy - half + 6, cy + half - 6, SEAM)
    # Continents, rough blobs on the globe.
    sh.fill_shape([(414, 372), (472, 358), (498, 388), (480, 430),
                   (436, 440), (408, 408)], LAND_G)          # N. America
    sh.fill_shape([(472, 472), (516, 462), (534, 504), (508, 546),
                   (478, 522)], LAND_G2)                       # S. America
    sh.fill_shape([(592, 392), (644, 382), (670, 416), (648, 452),
                   (602, 444)], LAND_G)                        # Africa
    sh.fill_shape([(626, 340), (732, 322), (768, 364), (732, 398),
                   (662, 390)], LAND_G2)                       # Eurasia
    sh.fill_shape([(682, 516), (744, 506), (762, 540), (700, 550)],
                  LAND_G)                                      # Australia
    # Outline of the globe.
    sh.ring(cx, cy, r, (120, 78, 8), 3)
    # Big red GROUNDED stamp across the balloon skin.
    word = "GROUNDED"
    w = sh.put_w(word, 3, 16) + 16
    h = 62
    sx, sy = 512 - w // 2, 452
    sh.box(sx, sy, w, h, (255, 245, 230))
    sh.box(sx, sy, w, 4, BRIGHT_RED)
    sh.box(sx, sy + h - 4, w, 4, BRIGHT_RED)
    sh.box(sx, sy, 4, h, BRIGHT_RED)
    sh.box(sx + w - 4, sy, 4, h, BRIGHT_RED)
    sh.put(sx + 8, sy + 8, word, 3, BRIGHT_RED, adv=16)
    sh.put(sx + 8, sy + 36, "100TH MACY'S", 2, BRIGHT_RED, adv=11)


def draw_ropes(sh):
    """Tether ropes straining from the balloon down to the wet
    street, held by handlers."""
    for (bx, by, gx, gy) in [(330, 620, 250, 838), (694, 620, 774, 838),
                             (392, 700, 340, 838), (632, 700, 684, 838)]:
        sh.seg(bx, by, gx, gy, (220, 210, 180))
        sh.seg(bx + 2, by, gx + 2, gy, (220, 210, 180))
    # Ground anchors.
    for gx in (250, 340, 684, 774):
        sh.box(gx - 10, 838, 20, 8, (90, 88, 100))


def draw_crowd(sh):
    """Ordinary people in bright rain ponchos along the street,
    pointing up at the grounded balloon in awe, phones raised."""
    rnd = lcg(1127)
    y_base = 838
    for i in range(34):
        x = 30 + i * 29 + (next(rnd) % 12)
        hgt = 46 + next(rnd) % 18
        shirt = SHIRTS[next(rnd) % len(SHIRTS)]
        skin = SKINS[next(rnd) % len(SKINS)]
        # Poncho: wide trapezoid.
        sh.fill_shape([(x - 13, y_base), (x + 13, y_base),
                       (x + 8, y_base - hgt + 16),
                       (x - 8, y_base - hgt + 16)], shirt)
        # Hood over the head.
        sh.fill_shape([(x - 9, y_base - hgt + 12), (x + 9, y_base - hgt + 12),
                       (x + 5, y_base - hgt - 4),
                       (x - 5, y_base - hgt - 4)], shirt)
        sh.disc(x, y_base - hgt + 6, 5, skin)
        # Arms raised toward the balloon.
        sh.seg(x - 8, y_base - hgt + 20, x - 18, y_base - hgt - 6, skin)
        sh.seg(x + 8, y_base - hgt + 20, x + 18, y_base - hgt - 8, skin)
        # Phone in one raised hand, every third person.
        if i % 3 == 0:
            sh.box(x + 15, y_base - hgt - 16, 7, 11, INK)
            sh.box(x + 16, y_base - hgt - 15, 5, 9, (160, 220, 255))
    # Rain splashes on the wet street.
    for _ in range(60):
        x = 10 + next(rnd) % 1004
        y = 700 + next(rnd) % 150
        sh.box(x, y, 5, 2, (120, 130, 150))


def draw_street_labels(sh):
    """The storm's toll, written on the dark street band."""
    sh.put(28, 706, "500,000+ HOMES", 2, WHITE, adv=11)
    sh.put(28, 720, "WITHOUT POWER", 2, WHITE, adv=11)
    sh.put(28, 734, "80 MILLION TRAVELLING", 2, (255, 214, 102), adv=11)
    sh.put(812, 706, "100S OF FLIGHTS", 2, WHITE, adv=11)
    sh.put(812, 720, "CANCELLED", 2, WHITE, adv=11)
    sh.put(812, 734, "NEW YORK", 2, (255, 214, 102), adv=11)


def draw():
    sh = Sheet(PAGE_W, PAGE_H, PAPER)
    # Masthead.
    sh.box(0, 0, PAGE_W, 8, RED)
    sh.put_mid(512, 14, "THE WORLD TODAY", 4, INK, adv=22)
    sh.put_mid(512, 46, "FRIDAY 27 NOVEMBER 2026", 3, RED, adv=16)
    sh.put_mid(512, 72, "ONE DAY - ONE IMAGE", 2, NAVY, adv=11)
    sh.hline(16, 1007, 92, INK)
    # Scene.
    draw_sky(sh)
    draw_balloon(sh)
    # Street band, then ropes over it so the tethers reach the
    # wet street instead of vanishing behind the band.
    sh.box(0, 700, PAGE_W, 160, STREET)
    sh.hline(0, 1023, 700, (90, 90, 110))
    draw_ropes(sh)
    draw_street_labels(sh)
    draw_crowd(sh)
    # Ticker strip.
    sh.box(0, 860, PAGE_W, 164, PAPER)
    sh.hline(0, 1023, 860, RED)
    sh.hline(0, 1023, 862, RED)
    sh.put(16, 872, "THE DAY IN HEADLINES", 2, RED, adv=11)
    lines = sh.fold(TICKER, 992, 2, adv=11)
    y = 892
    for ln in lines:
        sh.put(16, y, ln, 2, INK, adv=11)
        y += 16
    sh.put(16, 1000, "SOURCES: NYT / BBC / REUTERS / GUARDIAN - EVENTS OF 27 NOV 2026",
           2, NAVY, adv=11)
    return sh, lines


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    sh, lines = draw()
    n = save_png(os.path.join(outdir, "entry.png"), sh)
    print("ticker lines: %d" % len(lines))
    for ln in lines:
        print("  | %s" % ln)
    print("png bytes: %d" % n)
    assert n <= 1048576, "png over 1 MiB"
    data = open(os.path.join(outdir, "entry.png"), "rb").read()
    print("sha256: %s" % hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
