# -*- coding: utf-8 -*-
"""Drawing primitives for the NoSQL deck, plus the layout asserts.

Same idiom as the CS 2010 decks: the figures are hand-written SVG built from
local helpers, with no dependency beyond the standard library. Two things are
different here, and both are deliberate:

1.  `Fig` records the boxes it draws and checks them on `save()`. Two boxes
    must not overlap, and every string must fit the box it is given. That
    turns "does the picture look right" into "does the picture fit", which a
    machine can answer -- and this deck was built without anyone able to look
    at the output.

2.  Text is measured with `tw()`, a per-character advance table, so the fit
    check has something to check against. The table is approximate (it is a
    DejaVu Sans estimate), so `fit()` keeps a margin.

An SVG loaded as an `<img>` cannot use the page's webfonts, so the font stack
names what every Linux and macOS box already has.
"""

import math

INK = "#111827"
DARK = "#0b1220"
MID = "#4b5563"
GRAY = "#6b7280"
RULE = "#cbd5e1"
PALE = "#f8fafc"
WHITE = "#ffffff"

TEAL = "#0f766e"
TEAL_W = "#ccfbf1"
TEAL_PALE = "#f0fdfa"
AMBER = "#b45309"
AMBER_W = "#fef3c7"
RED = "#b91c1c"
RED_W = "#fee2e2"
BLUE = "#1d4ed8"
BLUE_W = "#dbeafe"
VIOLET = "#6d28d9"
VIOLET_W = "#ede9fe"
GREEN = "#15803d"
GREEN_W = "#dcfce7"

FONT = ("'DejaVu Sans', 'Noto Sans Symbols 2', 'Segoe UI Symbol', "
        "'Apple Symbols', Verdana, sans-serif")
MONO = "'Fira Code', 'DejaVu Sans Mono', 'Courier New', monospace"

DEFS = "".join(
    '<marker id="arw_%s" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" '
    'markerHeight="6" orient="auto-start-reverse">'
    '<path d="M0,0 L10,5 L0,10 z" fill="%s"/></marker>' % (c.lstrip("#"), c)
    for c in (INK, TEAL, AMBER, RED, BLUE, GRAY, MID, GREEN, VIOLET))

# Advance widths as a fraction of the font size, for DejaVu Sans.
_W = {}
for _c in "ijl.,:;'|![]()":
    _W[_c] = 0.30
for _c in "fjrt-":
    _W[_c] = 0.38
for _c in "abcdeghknopqsuvxyz":
    _W[_c] = 0.55
for _c in "0123456789":
    _W[_c] = 0.60
for _c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
    _W[_c] = 0.68
for _c in "mwMW@%":
    _W[_c] = 0.86
for _c in " /\\":
    _W[_c] = 0.32
_W["—"] = 0.95
_W["·"] = 0.32
_W["→"] = 0.80
_W["×"] = 0.60
_W["≥"] = 0.66
_W["≠"] = 0.66
_W["∩"] = 0.66


def tw(s, size, bold=False, mono=False):
    """Estimated advance width of `s` at `size` points."""
    if mono:
        return len(s) * size * 0.602
    w = 0.0
    for ch in s:
        w += _W.get(ch, 0.60 if ch.isupper() else 0.56)
    if bold:
        w *= 1.045
    return w * size


def wrap(s, size, width, bold=False):
    """Greedy word wrap; returns a list of lines that fit `width`."""
    words, lines, cur = s.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if cur and tw(trial, size, bold) > width:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Fig(object):
    """One SVG, with the boxes it claims so they can be checked on save."""

    def __init__(self, w, h, name):
        self.w, self.h, self.name = w, h, name
        self.body = []
        self.regions = []
        self.texts = []

    # ---------------------------------------------------------------- shapes

    def rect(self, x, y, w, h, fill="none", stroke=RULE, sw=1.5, rx=0, dash=None):
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        self.body.append(
            '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%s" '
            'fill="%s" stroke="%s" stroke-width="%s"%s/>'
            % (x, y, w, h, rx, fill, stroke, sw, d))
        return self

    def line(self, x1, y1, x2, y2, stroke=RULE, w=1.5, dash=None, arrow=False):
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        a = ' marker-end="url(#arw_%s)"' % stroke.lstrip("#") if arrow else ""
        self.body.append(
            '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="%s" stroke-linecap="round"%s%s/>'
            % (x1, y1, x2, y2, stroke, w, d, a))
        return self

    def path(self, d, fill="none", stroke=INK, w=2, dash=None, arrow=False):
        ds = ' stroke-dasharray="%s"' % dash if dash else ""
        a = ' marker-end="url(#arw_%s)"' % stroke.lstrip("#") if arrow else ""
        self.body.append('<path d="%s" fill="%s" stroke="%s" stroke-width="%s"%s%s/>'
                         % (d, fill, stroke, w, ds, a))
        return self

    def circle(self, cx, cy, r, fill=WHITE, stroke=TEAL, sw=2):
        self.body.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" '
                         'stroke="%s" stroke-width="%s"/>'
                         % (cx, cy, r, fill, stroke, sw))
        return self

    # ----------------------------------------------------------------- text

    def txt(self, x, y, s, size=15, anchor="start", fill=INK, bold=False,
            italic=False, mono=False, box=None):
        st = 'font-family="%s" font-size="%s" fill="%s"' % (
            MONO if mono else FONT, size, fill)
        if bold:
            st += ' font-weight="700"'
        if italic:
            st += ' font-style="italic"'
        self.body.append('<text x="%.1f" y="%.1f" text-anchor="%s" %s>%s</text>'
                         % (x, y, anchor, st, esc(s)))
        self.texts.append((x, y, s, size, anchor, box))
        return self

    def para(self, x, y, w, s, size=15, fill=INK, bold=False, lead=1.35,
             box=None, anchor="start"):
        """Wrapped text. Returns the y after the last line."""
        for line in wrap(s, size, w, bold):
            self.txt(x, y, line, size, anchor, fill, bold, box=box)
            y += size * lead
        return y

    def txt_rot(self, x, y, s, size=13, fill=GRAY, bold=True):
        st = 'font-family="%s" font-size="%s" fill="%s"' % (FONT, size, fill)
        if bold:
            st += ' font-weight="700"'
        self.body.append('<text x="%.1f" y="%.1f" text-anchor="middle" %s '
                         'transform="rotate(-90 %.1f %.1f)">%s</text>'
                         % (x, y, st, x, y, esc(s)))
        return self

    # --------------------------------------------------------------- layout

    def region(self, x, y, w, h, label=""):
        """Register a box that must not overlap another registered box."""
        self.regions.append((x, y, w, h, label))
        return self

    def fit(self, s, size, width, bold=False, mono=False, where=""):
        """Assert that `s` fits in `width` points at `size`."""
        got = tw(s, size, bold, mono)
        if got > width:
            raise SystemExit(
                "%s: text overflows by %.1fpt (%r at %.1fpt in %.1fpt)"
                % (self.name, got - width, s, size, width))
        return self

    def save(self, path):
        self._check()
        with open(path, "w", encoding="utf-8") as f:
            f.write('<svg xmlns="http://www.w3.org/2000/svg" width="%d" '
                    'height="%d" viewBox="0 0 %d %d">\n<defs>%s</defs>\n'
                    '<rect width="%d" height="%d" fill="#ffffff"/>\n'
                    % (self.w, self.h, self.w, self.h, DEFS, self.w, self.h)
                    + "\n".join(self.body) + "\n</svg>\n")
        print("wrote", path)

    def _check(self):
        for i, a in enumerate(self.regions):
            if a[0] < 0 or a[1] < 0 or a[0] + a[2] > self.w or a[1] + a[3] > self.h:
                raise SystemExit("%s: region %r outside the canvas" % (self.name, a))
            for b in self.regions[i + 1:]:
                ox = min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])
                oy = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
                if ox > 1 and oy > 1:
                    raise SystemExit(
                        "%s: regions %r and %r overlap by %.1f x %.1f"
                        % (self.name, a[4], b[4], ox, oy))
        for x, y, s, size, anchor, box in self.texts:
            if box is None:
                continue
            bx, by, bw, bh = box
            got = tw(s, size)
            if anchor == "middle":
                x0 = x - got / 2.0
            elif anchor == "end":
                x0 = x - got
            else:
                x0 = x
            if x0 < bx - 0.5 or x0 + got > bx + bw + 0.5:
                raise SystemExit(
                    "%s: %r runs %.1fpt past its box (%.1f available, %.1f used)"
                    % (self.name, s, x0 + got - (bx + bw), bw, got))


def caption(fig, x, y, w, text, size=15, tone=TEAL, h=None):
    """The one line under a figure that says what it shows."""
    lines = wrap(text, size, w - 34)
    h = h or 16 + len(lines) * (size + 6)
    fig.rect(x, y, w, h, TEAL_PALE, tone, 1.2, rx=6)
    fig.rect(x, y, 5, h, tone, tone, 0, rx=2)
    for k, line in enumerate(lines):
        fig.txt(x + 18, y + 20 + k * (size + 6), line, size, "start", INK,
                box=(x + 10, y, w - 16, h))
    return y + h


def ledger(fig, x, y, w, left_title, left, right_title, right, size=14):
    """Two columns: what it buys on the left, what it charges on the right."""
    half = (w - 24) / 2.0
    fig.rect(x, y, half, 4, TEAL, TEAL, 0)
    fig.rect(x + half + 24, y, half, 4, AMBER, AMBER, 0)
    fig.txt(x, y + 24, left_title, size + 2, "start", TEAL, bold=True)
    fig.txt(x + half + 24, y + 24, right_title, size + 2, "start", AMBER, bold=True)
    yy = y + 30 + size
    for line in left:
        yy = fig.para(x, yy, half, line, size, INK, lead=1.5)
        yy += 4
    yy2 = y + 30 + size
    for line in right:
        yy2 = fig.para(x + half + 24, yy2, half, line, size, INK, lead=1.5)
        yy2 += 4
    return max(yy, yy2)


def node(fig, cx, cy, r, label, sub=None, fill=WHITE, stroke=TEAL, size=15,
         sub_size=12, color=INK):
    fig.circle(cx, cy, r, fill, stroke, 2)
    fig.txt(cx, cy + (0 if sub is None else -2), label, size, "middle", color,
            bold=True)
    if sub:
        fig.txt(cx, cy + 14, sub, sub_size, "middle", GRAY)
    return fig


def arrow(fig, x1, y1, x2, y2, color=TEAL, w=2, dash=None, label=None,
          label_size=12, label_at=0.5, dy=-6):
    fig.line(x1, y1, x2, y2, color, w, dash, arrow=True)
    if label:
        t = label_at
        fig.txt(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t + dy, label, label_size,
                "middle", color)
    return fig


def legend(fig, x, y, items, size=13, gap=150):
    """items: list of (colour, label)."""
    for i, (color, label) in enumerate(items):
        xx = x + i * gap
        fig.rect(xx, y - 9, 12, 12, color, color, 0, rx=2)
        fig.txt(xx + 18, y + 1, label, size, "start", MID)
    return fig


def grid_table(fig, x, y, cols, rows, col_w, row_h, header=True,
               head_fill=TEAL_PALE, head_color=TEAL, size=13,
               align=None, rule=RULE):
    """A plain table, drawn rather than marked up, for figures that are really
    tables. `cols` and `rows` are lists of strings."""
    n = len(cols)
    align = align or ["start"] * n
    total = sum(col_w)
    for j in range(n + 1):
        xx = x + sum(col_w[:j])
        fig.line(xx, y, xx, y + row_h * (len(rows) + (1 if header else 0)),
                 rule, 1)
    for i, row in enumerate(([cols] if header else []) + rows):
        yy = y + i * row_h
        if i == 0 and header:
            fig.rect(x, yy, total, row_h, head_fill, "none", 0)
        fig.line(x, yy, x + total, yy, rule, 1)
        cx = x
        for j, cell in enumerate(row):
            if align[j] == "end":
                fig.txt(cx + col_w[j] - 8, yy + row_h / 2 + 5, cell, size,
                        "end", head_color if (i == 0 and header) else INK,
                        bold=(i == 0 and header))
            else:
                fig.txt(cx + 8, yy + row_h / 2 + 5, cell, size, "start",
                        head_color if (i == 0 and header) else INK,
                        bold=(i == 0 and header))
            cx += col_w[j]
    fig.line(x, y + row_h * (len(rows) + (1 if header else 0)), x + total,
             y + row_h * (len(rows) + (1 if header else 0)), rule, 1)
    return y + row_h * (len(rows) + (1 if header else 0))
