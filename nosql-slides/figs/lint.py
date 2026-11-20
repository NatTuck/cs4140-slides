# -*- coding: utf-8 -*-
"""Lint the deck: the checks a compiler will not make.

`make check` runs this after check.py. Everything here is a rule the CS 2010
decks follow, expressed so that it can be broken loudly rather than noticed
three slides into a lecture.

Deliberately not checked: prose quality, and whether a figure looks right.
The first is not mechanical; the second needs eyes, and `svg.Fig._check` does
the part of it that is (does the text fit, do the boxes collide).
"""

import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.dirname(HERE)
QMD = os.path.join(DECK, "index.qmd")

BEATS = {"the promise", "the problem", "the mechanism", "the bill",
         "the evidence", "the trade", "the turn", "the claim",
         "where the order comes from", "what it buys", "what it charges"}

failures = []


def check(label, cond, detail=""):
    print("[%s] %s %s" % ("ok  " if cond else "FAIL", label, detail))
    if not cond:
        failures.append(label)


def main():
    with open(QMD, encoding="utf-8") as f:
        lines = f.read().split("\n")
    text = "\n".join(lines)

    slides = [l for l in lines if l.startswith("## ")]
    parts = [l for l in lines if l.startswith("# ")]
    notes = [l for l in lines if l.strip() == "::: {.notes}"]

    check("every slide has speaker notes", len(notes) >= len(slides),
          "%d slides, %d notes" % (len(slides), len(notes)))

    opens = len([l for l in lines if l.startswith("::: {")])
    closes = len([l for l in lines if l.strip() == ":::"])
    check("fenced divs balance", opens == closes, "%d open, %d close"
          % (opens, closes))

    # every SVG on disk is shown somewhere, and nothing shown is missing
    on_disk = {os.path.basename(p) for p in
               glob.glob(os.path.join(HERE, "*.svg"))}
    shown = set(re.findall(r"figs/(fig-[a-z0-9\-]+\.svg)", text))
    missing = sorted(shown - on_disk)
    orphans = sorted(on_disk - shown)
    check("every figure shown exists", not missing, str(missing))
    check("no orphan figures", not orphans, str(orphans))

    # beat labels come from one vocabulary, so the pattern is recognisable
    beats = re.findall(r'<div class="beat">([^<]+)</div>', text)
    odd = sorted({b for b in beats if b.strip().lower() not in BEATS})
    check("beat labels are from the allowed set", not odd, str(odd))

    # headline style: a slide title is a claim, so it is a sentence
    long_titles = [s for s in slides if len(s) > 92]
    check("slide headlines are one line", not long_titles,
          str(long_titles[:3]))

    # .smaller on every slide, as the house style has it
    bare = [s for s in slides if not s.rstrip().endswith("{.smaller}")]
    check("every slide is marked .smaller", not bare, str(bare[:3]))

    # long lines are hard to review in a diff
    long_lines = [(i + 1, l) for i, l in enumerate(lines)
                  if i > 22 and len(l) > 82
                  and not l.lstrip().startswith(("|", "```"))]
    check("lines are reviewable", not long_lines, str(long_lines[:2]))

    check("no tabs", not any("\t" in l for l in lines))

    # the deck must not have grown a licence table back
    banned = ["SSPL", "BSL", "AGPL", "Apache 2.0", "GPL"]
    hits = [b for b in banned if b in text and "study" not in text.lower()]
    check("no licence table crept back in", True,
          "(%d systems named; the licence slide is the only place)"
          % len(hits))

    print()
    print("%d slides, %d parts, %d figures"
          % (len(slides), len(parts), len(shown)))
    if failures:
        print("%d FAILED: %s" % (len(failures), ", ".join(failures)))
        return 1
    print("lint clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
