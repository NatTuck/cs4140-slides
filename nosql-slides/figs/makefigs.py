# -*- coding: utf-8 -*-
"""Draw every figure for the deck from the values in model.py.

    python3 figs/makefigs.py

Each figure is a standalone SVG with no external fonts, so the deck works
offline. The figures are generated, not drawn by hand: change a value in
model.py and the picture changes with it.

Layout is checked, not eyeballed -- see svg.Fig._check. Text is measured with
an advance table, boxes are asserted not to overlap, and every string given a
box must fit inside it. That is the substitute for a person looking at the
output.
"""

import os

import svg
from svg import (Fig, TEAL, TEAL_W, TEAL_PALE, AMBER, AMBER_W, RED, RED_W,
                 BLUE, BLUE_W, VIOLET, VIOLET_W, GREEN, GREEN_W, INK, MID,
                 GRAY, RULE, PALE, WHITE, caption, ledger, node, arrow, legend,
                 grid_table)
import model as M

OUT = os.path.dirname(os.path.abspath(__file__))


def save(fig):
    fig.save(os.path.join(OUT, fig.name))


# ===================================================== 1. the commit point

def fig_commit_point():
    f = Fig(940, 450, "fig-commit-point.svg")
    y = 168

    f.line(60, y, 880, y, RULE, 2)
    f.circle(92, y, 9, WHITE, MID, 2.4)
    f.txt(92, y - 26, "BEGIN", 12, "middle", MID, bold=True)

    for i, label in enumerate(("write 1", "write 2", "write 3")):
        x = 210 + i * 112
        f.rect(x, y - 18, 88, 36, PALE, RULE, 1.2, rx=4)
        f.txt(x + 44, y + 5, label, 11, "middle", INK, mono=True)

    f.rect(566, y - 34, 160, 68, TEAL, TEAL, 0, rx=6)
    f.txt(646, y - 6, "commit record", 13, "middle", WHITE, bold=True)
    f.txt(646, y + 16, "fsync", 11, "middle", TEAL_W, mono=True)
    f.txt(646, y - 52, "the decision", 12, "middle", TEAL, bold=True)

    f.line(730, 96, 730, 330, AMBER, 2.4, "7,5")
    f.txt(742, 108, "visible", 12, "start", AMBER, bold=True)
    f.txt(742, 124, "from here", 12, "start", AMBER, bold=True)

    f.region(120, 250, 210, 64, "before")
    f.rect(120, 250, 210, 64, WHITE, RULE, 1.4, rx=6)
    f.txt(225, 276, "a reader before", 12, "middle", GRAY)
    f.txt(225, 296, "sees nothing", 12, "middle", GRAY)

    f.region(770, 250, 160, 64, "after")
    f.rect(770, 250, 160, 64, TEAL_PALE, TEAL, 1.4, rx=6)
    f.txt(850, 276, "a reader after", 12, "middle", TEAL)
    f.txt(850, 296, "sees all of it", 12, "middle", TEAL)

    f.line(225, 246, 225, 200, GRAY, 1.4, "5,4")
    f.line(850, 246, 850, 200, TEAL, 1.4, "5,4")

    caption(f, 60, 366, 820,
            "One record turns a set of writes into one decision. Before it the "
            "writes do not exist; after it they all exist, in one order, on "
            "disk.")
    save(f)


def fig_two_commits():
    f = Fig(940, 510, "fig-two-commits.svg")
    f.txt(40, 42, "One transaction, two commit points", 19, "start", TEAL,
          bold=True)

    for i, (what, why) in enumerate(M.RETRY_STEPS):
        y = 96 + i * 48
        f.txt(40, y, "%d" % (i + 1), 13, "start", TEAL, bold=True)
        f.txt(64, y, what, 12.5, "start", INK)
        f.txt(64, y + 18, why, 11, "start", GRAY)

    for node, y, tone, wash, label in (
            ("node A", 90, TEAL, TEAL_PALE, "committed"),
            ("node B", 262, RED, RED_W, "committed too")):
        f.region(480, y, 200, 150, node)
        f.rect(480, y, 200, 150, WHITE, tone, 1.8, rx=6)
        f.txt(492, y + 22, node, 12, "start", tone, bold=True)
        for k in range(4):
            yy = y + 40 + k * 18
            f.line(492, yy, 668, yy, RULE, 1)
        f.rect(492, y + 40 + 4 * 18 - 9, 176, 18, wash, tone, 1.4, rx=3)
        f.txt(580, y + 40 + 4 * 18 + 4, label, 11, "middle", tone, bold=True)

    f.line(700, 96, 716, 96, RED, 2)
    f.line(700, 406, 716, 406, RED, 2)
    f.line(716, 96, 716, 406, RED, 2)
    f.txt(726, 236, "two", 12, "start", RED, bold=True)
    f.txt(726, 254, "commit", 12, "start", RED, bold=True)
    f.txt(726, 272, "points", 12, "start", RED, bold=True)

    caption(f, 40, 424, 860,
            "Neither node is broken. Copying bytes is not the hard part; "
            "having exactly one decision is. Every node that can fsync a "
            "commit record is a second commit point.")
    save(f)


def fig_transaction():
    f = Fig(940, 380, "fig-transaction.svg")
    y = 140

    f.line(70, y, 640, y, RULE, 2)
    f.circle(92, y, 9, WHITE, MID, 2.4)
    f.txt(92, y - 24, "BEGIN", 12, "middle", MID, bold=True)

    for i in range(3):
        x = 190 + i * 130
        f.rect(x, y - 18, 104, 36, PALE, RULE, 1.2, rx=4)
        f.txt(x + 52, y + 5, "write %d" % (i + 1), 11, "middle", INK, mono=True)

    f.line(190, y + 56, 544, y + 56, TEAL, 2)
    f.line(190, y + 50, 190, y + 62, TEAL, 2)
    f.line(544, y + 50, 544, y + 62, TEAL, 2)
    f.txt(367, y + 82, "the unit: one outcome for the whole set", 12, "middle",
          TEAL, bold=True)

    f.path("M 640 %d L 676 %d L 700 %d" % (y, y, y - 52), "none", TEAL, 2,
           arrow=True)
    f.path("M 640 %d L 676 %d L 700 %d" % (y, y, y + 52), "none", RED, 2,
           arrow=True)

    f.rect(704, y - 78, 160, 52, TEAL_PALE, TEAL, 2, rx=6)
    f.txt(784, y - 56, "COMMIT", 13, "middle", TEAL, bold=True)
    f.txt(784, y - 38, "all of it", 11, "middle", MID)

    f.rect(704, y + 26, 160, 52, RED_W, RED, 2, rx=6)
    f.txt(784, y + 48, "ABORT", 13, "middle", RED, bold=True)
    f.txt(784, y + 66, "none of it", 11, "middle", MID)

    caption(f, 60, 296, 820,
            "The unit is a set of writes, not a write. That is why \"single-row "
            "atomicity\" later in the lecture is a much smaller promise than it "
            "sounds.")
    save(f)


# ======================================================== 2. multi-master

def fig_multimaster():
    f = Fig(900, 470, "fig-multimaster.svg")
    for i, (cx, mx, label) in enumerate(((90, 60, "client 1"), (650, 620, "client 2"))):
        f.rect(cx, 40, 150, 46, PALE, RULE, 1.2, rx=6)
        f.txt(cx + 75, 68, label, 13, "middle", MID)

    f.rect(60, 130, 210, 90, TEAL_PALE, TEAL, 2, rx=8)
    f.txt(165, 160, "master 1", 15, "middle", TEAL, bold=True)
    f.txt(165, 182, "accepts writes", 12, "middle", MID)
    f.txt(165, 200, "no global order", 12, "middle", RED)

    f.rect(620, 130, 210, 90, TEAL_PALE, TEAL, 2, rx=8)
    f.txt(725, 160, "master 2", 15, "middle", TEAL, bold=True)
    f.txt(725, 182, "accepts writes", 12, "middle", MID)
    f.txt(725, 200, "no global order", 12, "middle", RED)

    arrow(f, 165, 86, 165, 126, RULE, 1.6)
    arrow(f, 725, 86, 725, 126, RULE, 1.6)

    # the disputed row
    f.rect(330, 300, 240, 90, WHITE, RED, 2.4, rx=8)
    f.txt(450, 330, "row 42", 15, "middle", INK, bold=True)
    f.txt(450, 352, "balance = 80", 13, "middle", MID)
    f.txt(450, 372, "balance = 70", 13, "middle", MID)

    arrow(f, 210, 224, 372, 296, RED, 2, None, "t1", 12, 0.5, -8)
    arrow(f, 690, 224, 528, 296, RED, 2, None, "t2", 12, 0.5, -8)

    f.txt(450, 274, "both transactions are correct alone", 12, "middle", RED)
    f.line(276, 175, 616, 175, RED, 2, "6,5")
    f.txt(446, 165, "no total order between the two masters", 12, "middle", RED)

    caption(f, 60, 410, 780,
            "Two nodes accepting writes means two orders, and nothing that "
            "reconciles them. Last-write-wins is a policy, not a fix.")
    save(f)


# ================================================================ 3. fork

def fig_fork():
    f = Fig(900, 440, "fig-fork.svg")
    f.rect(310, 40, 280, 64, WHITE, INK, 2, rx=8)
    f.txt(450, 68, "no global commit point", 15, "middle", INK, bold=True)
    f.txt(450, 88, "so coordination is a choice", 12, "middle", GRAY)

    f.path("M 450 104 L 450 130 L 230 130 L 230 168", "none", MID, 1.8, arrow=True)
    f.path("M 450 104 L 450 130 L 670 130 L 670 168", "none", MID, 1.8, arrow=True)

    f.region(70, 172, 320, 160, "path a")
    f.rect(70, 172, 320, 160, AMBER_W, AMBER, 2, rx=8)
    f.txt(86, 200, "Path A: converge later", 15, "start", AMBER, bold=True)
    for i, line in enumerate(("every replica accepts reads and writes",
                              "reads may be stale",
                              "conflicting writes must be reconciled",
                              "no \"latest write\" guarantee")):
        f.txt(86, 228 + i * 22, "· " + line, 12, "start", INK)

    f.region(510, 172, 320, 160, "path b")
    f.rect(510, 172, 320, 160, TEAL_W, TEAL, 2, rx=8)
    f.txt(526, 200, "Path B: wait for a majority", 15, "start", TEAL, bold=True)
    for i, line in enumerate(("W acks on write, R on read",
                              "if W + R > N the sets must overlap",
                              "strong, without a master",
                              "the latency is explicit")):
        f.txt(526, 228 + i * 22, "· " + line, 12, "start", INK)

    f.txt(450, 364, "The dial between these two paths is the whole design space.",
          14, "middle", TEAL, bold=True)

    caption(f, 70, 384, 760,
            "Not \"pick two of three\": partitions happen. The choice is only "
            "what you do while one is happening.")
    save(f)


# ============================================================== 4. quorum

def fig_quorum():
    CW, CH, GAP, X0, Y0 = 300, 152, 12, 120, 86
    f = Fig(X0 + 3 * (CW + GAP) + 20, Y0 + 3 * (CH + GAP) + 70,
            "fig-quorum.svg")

    for i in range(3):
        for j in range(3):
            c = [q for q in M.quorum_cases() if q["w"] == i + 1 and q["r"] == j + 1][0]
            x = X0 + j * (CW + GAP)
            y = Y0 + i * (CH + GAP)
            tone, wash = (TEAL, TEAL_PALE) if c["holds"] else (RED, RED_W)
            f.rect(x, y, CW, CH, wash, tone, 2, rx=8)
            f.txt(x + 16, y + 26, "W = %d    R = %d" % (c["w"], c["r"]), 15,
                  "start", tone, bold=True)

            for k, rep in enumerate(M.REPLICAS):
                sx = x + 16 + k * 54
                inw, inr = rep in c["write"], rep in c["read"]
                fill = TEAL if inw else WHITE
                stroke = AMBER if inr else RULE
                f.rect(sx, y + 42, 46, 36, fill, stroke, 3 if inr else 1.2, rx=5)
                f.txt(sx + 23, y + 66, rep, 15, "middle",
                      WHITE if inw else MID, bold=True)
                if inw and inr:
                    f.txt(sx + 23, y + 92, "both", 10, "middle", TEAL, bold=True)

            if c["holds"]:
                f.txt(x + 200, y + 62, "the sets must", 12, "start", TEAL)
                f.txt(x + 200, y + 78, "touch", 12, "start", TEAL)
            else:
                f.txt(x + 200, y + 62, "they can miss", 12, "start", RED)
                f.txt(x + 200, y + 78, "each other", 12, "start", RED)

            verdict = ("%d + %d > 3" % (c["w"], c["r"])) + ("  holds" if c["holds"] else "  fails")
            f.txt(x + 16, y + 126, verdict, 13, "start", tone, bold=True)
            f.txt(x + 16, y + 144,
                  "a read always sees the write" if c["holds"]
                  else "a read can miss the write", 11, "start", GRAY)

    legend(f, X0, 50, [(TEAL, "the write touched this replica"),
                       (WHITE, "untouched by the write")], 12, 330)
    f.rect(X0 + 700, 41, 16, 12, WHITE, AMBER, 3, rx=3)
    f.txt(X0 + 722, 52, "the read looked here", 12, "start", MID)

    caption(f, X0, Y0 + 3 * (CH + GAP) + 6, 3 * (CW + GAP) - GAP,
            "Drawn in the worst case: the write touches the first W replicas, "
            "the read the last R. If those two touch, every pair touches — so "
            "the condition is exactly W + R > N.")
    save(f)


# ========================================================= 5. shard a join

def fig_shard_join():
    f = Fig(900, 450, "fig-shard-join.svg")
    for i, (x, name, rows) in enumerate((
            (60, "shard 1  (customer < 500)",
             [("customer", "balance"), ("alice  312", "100")]),
            (500, "shard 2  (customer >= 500)",
             [("customer", "balance"), ("bob    712", "50")]))):
        f.region(x, 110, 340, 150, name)
        f.rect(x, 110, 340, 150, WHITE, TEAL, 2, rx=8)
        f.txt(x + 16, 136, name, 13, "start", TEAL, bold=True)
        for r, row in enumerate(rows):
            yy = 160 + r * 40
            f.rect(x + 16, yy, 150, 34, PALE, RULE, 1, rx=4)
            f.rect(x + 172, yy, 152, 34, PALE, RULE, 1, rx=4)
            f.txt(x + 26, yy + 22, row[0], 13, "start", INK, mono=True)
            f.txt(x + 182, yy + 22, row[1], 13, "start", INK, mono=True)

    f.txt(450, 200, "no", 13, "middle", RED, bold=True)
    f.txt(450, 220, "join", 13, "middle", RED, bold=True)

    f.line(230, 262, 230, 316, RED, 2, "5,4")
    f.line(670, 262, 670, 316, RED, 2, "5,4")
    f.line(230, 316, 670, 316, RED, 2)
    f.txt(450, 340, "100 + 50 = 150", 15, "middle", RED, bold=True)
    f.txt(450, 360, "the invariant needs both rows, in one place", 12, "middle", RED)

    caption(f, 60, 384, 780,
            "Sharding does not make the join inconvenient. It removes the "
            "mechanism that made the invariant checkable.")
    save(f)


# ================================================= 6. the wide-column table

def fig_cassandra_model():
    cols = ["clustering", "value", "battery"]
    widths = [150, 130, 130]
    f = Fig(880, 500, "fig-cassandra-model.svg")
    x0, y0, rh = 340, 132, 40

    grid_table(f, x0, y0, cols, [
        [ck, v, e or "\u2014"] for pk, ck, v, e in M.SENSOR_ROWS
    ], widths, rh, size=14)

    # One bracket per partition, in the order the rows arrive. The first draft
    # of this figure sorted the keys as strings, so "sensor 12" came first and
    # every bracket was labelled with the wrong group. Hence the check.
    parts = M.partitions()
    order, row = [], 0
    for pk in parts:
        n = len(parts[pk])
        top = y0 + rh + row * rh
        f.line(x0 - 24, top + 3, x0 - 24, top + n * rh - 3, TEAL, 2)
        f.line(x0 - 24, top + 3, x0 - 12, top + 3, TEAL, 2)
        f.line(x0 - 24, top + n * rh - 3, x0 - 12, top + n * rh - 3, TEAL, 2)
        f.txt(x0 - 36, top + n * rh / 2 + 5, pk, 13, "end", TEAL, bold=True)
        order.append(pk)
        row += n

    seen = []
    for pk, _ck, _v, _e in M.SENSOR_ROWS:
        if not seen or seen[-1] != pk:
            seen.append(pk)
    if order != seen:
        raise SystemExit("cassandra-model: bracket labels %r != row groups %r"
                         % (order, seen))

    f.txt(x0 - 36, y0 + 14, "partition key", 11, "end", GRAY)
    f.txt(x0, y0 - 18, "the key is the address, so it is not repeated in every "
                       "row", 12, "start", GRAY)

    f.txt(x0 + sum(widths) + 16, y0 + rh + 26, "\u2014 means", 11, "start", GRAY)
    f.txt(x0 + sum(widths) + 16, y0 + rh + 42, "the cell is", 11, "start", GRAY)
    f.txt(x0 + sum(widths) + 16, y0 + rh + 58, "absent", 11, "start", GRAY)

    caption(f, 60, 424, 780,
            "Grouped by partition, sorted inside it, with cells that need not "
            "exist. That is what wide-column means: the table is designed "
            "around the query.")
    save(f)


# ================================================================ 7. LSM

def fig_lsm():
    f = Fig(940, 460, "fig-lsm.svg")
    f.region(50, 120, 170, 130, "log")
    f.rect(50, 120, 170, 130, PALE, RULE, 1.5, rx=6)
    f.txt(64, 144, "commit log", 13, "start", INK, bold=True)
    f.txt(64, 162, "append only", 11, "start", GRAY)
    for i in range(7):
        f.line(64, 176 + i * 10, 206, 176 + i * 10, RULE, 1)

    arrow(f, 224, 185, 262, 185, MID, 1.6)

    f.region(266, 120, 170, 130, "memtable")
    f.rect(266, 120, 170, 130, TEAL_PALE, TEAL, 2, rx=6)
    f.txt(280, 144, "memtable", 13, "start", TEAL, bold=True)
    f.txt(280, 162, "in memory, sorted", 11, "start", GRAY)
    for i in range(4):
        f.rect(280 + (i % 2) * 74, 174 + (i // 2) * 32, 66, 26, WHITE, TEAL, 1, rx=3)
        f.txt(313 + (i % 2) * 74, 191 + (i // 2) * 32, "k%d" % (i + 1), 11,
              "middle", MID, mono=True)

    arrow(f, 440, 185, 486, 185, MID, 1.6)

    for i, table in enumerate(M.sstables()):
        y = 96 + i * 58
        f.region(490, y, 250, 48, "sstable %d" % (i + 1))
        f.rect(490, y, 250, 48, WHITE, BLUE, 1.6, rx=6)
        f.txt(502, y + 20, "SSTable %d" % (i + 1), 12, "start", BLUE, bold=True)
        f.txt(502, y + 38, "%s .. %s" % (table[0][0], table[-1][0]), 11,
              "start", GRAY, mono=True)

    f.line(760, 200, 800, 200, MID, 1.6)
    f.txt(806, 196, "compaction", 12, "start", MID)
    f.txt(806, 212, "merges them", 11, "start", GRAY)

    f.rect(60, 300, 760, 74, AMBER_W, AMBER, 1.8, rx=8)
    f.txt(78, 328, "A read for k7 has to look in four places", 15, "start",
          AMBER, bold=True)
    f.txt(78, 352, "the memtable, then every SSTable that might hold it. That "
                   "is read amplification, and it is the bill for cheap writes.",
          12, "start", INK)

    caption(f, 60, 396, 760,
            "Writes never read: they append to the log and the memtable. The "
            "cost is deferred to compaction and to every later read.")
    save(f)


# =========================================================== 8. two axes

def fig_two_axes():
    f = Fig(900, 520, "fig-two-axes.svg")
    x0, y0, cw, ch = 240, 90, 150, 48
    parts = ["a", "b", "c", "d", "e", "f"]
    f.txt(x0 + 1.5 * cw, 56, "replication: how many copies must agree", 13,
          "middle", TEAL, bold=True)
    for j, rep in enumerate(("replica 1", "replica 2", "replica 3")):
        f.txt(x0 + j * cw + cw / 2, y0 - 10, rep, 12, "middle", MID)

    f.txt_rot(x0 - 150, y0 + 3 * ch, "partitioning: who owns this key", 13, TEAL)

    for i, part in enumerate(parts):
        lit = (i == 2)
        for j in range(3):
            x, y = x0 + j * cw, y0 + i * ch
            f.rect(x + 2, y + 2, cw - 4, ch - 4,
                   TEAL_PALE if lit else WHITE, RULE, 1.2, rx=4)
            if lit:
                f.txt(x + cw / 2, y + ch / 2 + 5, "copy %d" % (j + 1), 12,
                      "middle", TEAL)
        f.txt(x0 - 16, y0 + i * ch + ch / 2 + 5, "partition " + part, 12,
              "end", INK if not lit else TEAL)

    f.rect(x0 - 4, y0 + 2 * ch, 3 * cw + 8, ch, "none", TEAL, 3, rx=6)
    f.txt(x0 + 1.5 * cw, y0 + 2 * ch - 10,
          "the replica set for partition c: three copies of one partition", 12,
          "middle", TEAL, bold=True)

    f.txt(x0 + 1.5 * cw, y0 + 6 * ch + 34,
          "R + W > M is asked here, inside this row — never globally", 13,
          "middle", TEAL, bold=True)

    caption(f, 60, y0 + 6 * ch + 56, 780,
            "The two axes are independent: partitioning decides who owns the "
            "key, replication decides how many copies must agree. A quorum is "
            "a question about one row.")
    save(f)


# ================================================== 9. a failing replica set

FW, FH = 1000, 520


def _replica_frame(state):
    f = Fig(FW, FH, "fig-failure-%02d.svg" % state["n"])
    f.txt(40, 44, state["title"], 20, "start", TEAL, bold=True)
    f.txt(FW - 40, 44, "frame %d of %d" % (state["n"], len(M.failure_states())),
          12, "end", GRAY)

    # the client
    f.rect(40, 150, 150, 70, PALE, RULE, 1.4, rx=6)
    f.txt(115, 180, "client", 14, "middle", MID, bold=True)
    f.txt(115, 200, "writes v = 11", 11, "middle", GRAY)

    xs = {"A": 380, "B": 560, "C": 740}
    for rep in M.REPLICAS:
        cx = xs[rep]
        down = rep in state["down"]
        val = state["value"][rep]
        stroke = RULE if down else TEAL
        fill = PALE if down else WHITE
        f.region(cx - 55, 130, 110, 110, rep)
        f.rect(cx - 55, 130, 110, 110, fill, stroke, 2.4 if not down else 1.2,
               rx=8, dash="6,5" if down else None)
        f.txt(cx, 160, "replica " + rep, 13, "middle", GRAY if down else TEAL,
              bold=True)
        f.txt(cx, 200, "down" if down else str(val), 24, "middle",
              GRAY if down else INK, bold=True)
        f.txt(cx, 224, "value", 10, "middle", GRAY)

        if not down:
            arrow(f, 192, 185, cx - 60, 185, TEAL, 1.6)
        else:
            f.line(192, 185, cx - 60, 185, RULE, 1.4, "6,5")

    if state.get("stale"):
        for rep, v in state["stale"].items():
            f.txt(xs[rep], 262, "read sees %d" % v, 12, "middle", AMBER, bold=True)

    if state["hint"]:
        rep, v = state["hint"]
        f.rect(500, 300, 300, 56, AMBER_W, AMBER, 1.8, rx=6)
        f.txt(512, 322, "held for replica %s: v = %d" % (rep, v), 13, "start",
              AMBER, bold=True)
        f.txt(512, 342, "hinted handoff", 11, "start", MID)
        arrow(f, 650, 296, xs[rep], 246, AMBER, 1.6, "5,4")

    caption(f, 40, 400, FW - 80, state["cap"])
    return f


def fig_failures():
    for state in M.failure_states():
        save(_replica_frame(state))


# ============================================================== 10. money

def fig_money():
    f = Fig(940, 450, "fig-money.svg")
    f.rect(70, 90, 200, 110, WHITE, TEAL, 2, rx=8)
    f.txt(170, 118, "alice", 15, "middle", TEAL, bold=True)
    f.txt(170, 148, "100", 26, "middle", INK, bold=True)
    f.txt(170, 172, "partition 1", 11, "middle", GRAY)

    f.rect(420, 90, 200, 110, WHITE, TEAL, 2, rx=8)
    f.txt(520, 118, "bob", 15, "middle", TEAL, bold=True)
    f.txt(520, 148, "50", 26, "middle", INK, bold=True)
    f.txt(520, 172, "partition 2", 11, "middle", GRAY)

    arrow(f, 276, 130, 414, 130, AMBER, 2.4, None)
    f.txt(345, 120, "move 20", 12, "middle", AMBER, bold=True)
    f.txt(345, 152, "two partitions", 10, "middle", RED)

    f.txt(740, 120, "one invariant:", 12, "middle", MID)
    f.txt(740, 146, "the total", 12, "middle", MID)
    f.txt(740, 168, "stays 150", 14, "middle", INK, bold=True)

    y = 250
    f.txt(70, y, "three outcomes", 13, "start", TEAL, bold=True)
    for i, o in enumerate(M.transfer_outcomes()):
        yy = y + 26 + i * 44
        tone, wash = (TEAL, TEAL_PALE) if o["ok"] else (RED, RED_W)
        f.rect(70, yy, 800, 38, wash, tone, 1.4, rx=5)
        f.txt(84, yy + 24, o["name"], 13, "start", tone, bold=True)
        f.txt(300, yy + 24, "%d + %d = %d" % (o["alice"], o["bob"],
                                              o["alice"] + o["bob"]), 14,
              "start", INK, mono=True)
        f.txt(560, yy + 24, "the invariant holds" if o["ok"]
              else "the invariant is broken", 12, "start", tone)
        f.txt(742, yy + 24, "✓" if o["ok"] else "✗", 15, "start", tone, bold=True)

    caption(f, 70, 396, 800,
            "All-or-nothing is what makes the arithmetic safe. A write that "
            "lands on some replicas and fails on others has no undo log, so "
            "the third row is reachable.")
    save(f)


# ========================================================== 11. aggregate

def fig_aggregate():
    f = Fig(980, 490, "fig-aggregate.svg")
    f.txt(40, 40, "as relations: the order is assembled at read time", 13,
          "start", GRAY)
    f.txt(520, 40, "as one document: it is shipped whole", 13, "start", GRAY)

    f.region(40, 56, 440, 340, "relations")
    for i, (name, rows) in enumerate((
            ("orders", [("1041", "Erin")]),
            ("line_items", [("K-31", "2"), ("B-07", "1"), ("M-12", "3")]),
            ("customers", [("Erin", "PSU")]))):
        y = 76 + i * 104
        f.rect(60, y, 180, 88, WHITE, BLUE, 1.6, rx=6)
        f.txt(72, y + 20, name, 12, "start", BLUE, bold=True)
        for r, row in enumerate(rows):
            f.txt(72, y + 40 + r * 16, "  ".join(row), 11, "start", INK, mono=True)

    for i in range(2):
        f.line(242, 120 + i * 104, 330, 120 + i * 104, BLUE, 1.6, "5,4",
               arrow=True)
    f.txt(286, 100, "join", 11, "middle", BLUE)
    f.txt(286, 214, "join", 11, "middle", BLUE)
    f.txt(400, 240, "3 tables", 12, "middle", BLUE, bold=True)
    f.txt(400, 258, "3 joins", 12, "middle", BLUE, bold=True)
    f.txt(400, 276, "1 answer", 12, "middle", BLUE, bold=True)

    f.line(490, 60, 490, 396, RULE, 1.5, "7,6")

    f.region(520, 56, 420, 340, "document")
    f.rect(540, 76, 380, 240, TEAL_PALE, TEAL, 2, rx=8)
    f.txt(556, 100, "{", 13, "start", TEAL, mono=True)
    lines = [('"order": 1041', 118), ('"customer": "Erin"', 138),
             ('"items": [', 158)]
    for text, y in lines:
        f.txt(572, y, text, 12, "start", INK, mono=True)
    yy = 178
    for item in M.ORDER["items"]:
        f.txt(588, yy, '{ "sku": "%s", "qty": %d, "price": %.2f }'
              % (item["sku"], item["qty"], item["price"]), 12, "start", INK,
              mono=True)
        yy += 20
    f.txt(572, yy, "]", 12, "start", INK, mono=True)
    f.txt(556, yy + 20, "}", 13, "start", TEAL, mono=True)

    f.txt(730, 340, "one read", 12, "middle", TEAL, bold=True)
    f.txt(730, 358, "one atomic write", 12, "middle", TEAL, bold=True)
    f.txt(730, 376, "total %.2f" % M.order_total(), 12, "middle", INK)

    caption(f, 40, 410, 900,
            "Same values, two shapes. The document store did not stop "
            "decomposing for fun: it gave up the join, so it must not need one.")
    save(f)


# ======================================================= 12. revision tree

TW, TH = 1000, 470


def _rev_frame(nodes, step, title, cap, winner=None, loser=None):
    f = Fig(TW, TH, "fig-revision-%02d.svg" % step)
    f.txt(40, 44, title, 20, "start", TEAL, bold=True)
    f.txt(TW - 40, 44, "frame %d of 4" % step, 12, "end", GRAY)

    pos = {}
    depth = {}
    for n in nodes:
        depth[n["id"]] = 0 if n["parent"] is None else depth[n["parent"]] + 1
    by_depth = {}
    for n in nodes:
        by_depth.setdefault(depth[n["id"]], []).append(n["id"])

    for d, ids in by_depth.items():
        for i, rid in enumerate(sorted(ids)):
            span = len(ids)
            cx = 500 + (i - (span - 1) / 2.0) * 300
            pos[rid] = (cx, 130 + d * 100)

    for n in nodes:
        if n["parent"]:
            x1, y1 = pos[n["parent"]]
            x2, y2 = pos[n["id"]]
            f.path("M %.0f %.0f C %.0f %.0f, %.0f %.0f, %.0f %.0f"
                   % (x1, y1 + 26, x1, y1 + 70, x2, y2 - 70, x2, y2 - 26),
                   "none", RULE, 1.6, arrow=True)

    for n in nodes:
        cx, cy = pos[n["id"]]
        is_win = winner and n["id"] == winner
        is_lose = loser and n["id"] == loser
        stroke = TEAL if is_win else (AMBER if is_lose else RULE)
        fill = TEAL_PALE if is_win else (AMBER_W if is_lose else WHITE)
        f.rect(cx - 92, cy - 26, 184, 54, fill, stroke, 2.4 if (is_win or is_lose) else 1.4, rx=6)
        f.txt(cx, cy - 6, n["id"], 13, "middle", INK, bold=True, mono=True)
        f.txt(cx, cy + 14, n["edit"], 11, "middle", MID)

    if winner:
        cx, cy = pos[winner]
        f.txt(cx, cy + 46, "the winner", 11, "middle", TEAL, bold=True)
    if loser:
        cx, cy = pos[loser]
        f.txt(cx, cy + 46, "retained as a conflict", 11, "middle", AMBER,
              bold=True)

    caption(f, 40, 400, TW - 80, cap)
    return f


def fig_revision():
    nodes = M.revision_tree()
    root = nodes[0]["id"]
    a1 = [n for n in nodes if n["who"] == "A"][0]["id"]
    b1 = [n for n in nodes if n["who"] == "B"][0]["id"]
    a2 = [n for n in nodes if n["who"] == "A"][1]["id"]

    frames = [
        ([nodes[0]], 1, "One document, one revision",
         "Every document carries a revision id: a count and a hash. A single "
         "version number would be enough if only one node ever wrote."),
        ([n for n in nodes if n["id"] in (root, a1, b1)], 2,
         "Two replicas edit from the same parent",
         "Both nodes accept writes, so both revisions are legitimate. The "
         "history is a tree, not a line -- and neither branch is wrong."),
        ([n for n in nodes if n["id"] in (root, a1, b1, a2)], 3,
         "One branch gets longer",
         "Replica A edits again. Nothing is lost yet: the two branches are "
         "simply different histories of the same document."),
        (nodes, 4, "Replication picks a winner and keeps the loser",
         "Highest revision count wins, then the larger revision id. The other "
         "branch is not deleted: it stays readable as a conflict for the "
         "application to reconcile.", a2, b1),
    ]
    for nodes_, step, title, cap, *rest in frames:
        win = rest[0] if rest else None
        lose = rest[1] if len(rest) > 1 else None
        save(_rev_frame(nodes_, step, title, cap, win, lose))


# ============================================================= 13. indexes

def fig_index():
    f = Fig(980, 470, "fig-index.svg")
    f.txt(40, 40, "a materialized view: exact and range", 13, "start", TEAL,
          bold=True)
    f.txt(520, 40, "an inverted index: relevance", 13, "start", VIOLET,
          bold=True)

    f.region(40, 56, 440, 330, "view")
    f.rect(60, 70, 400, 54, TEAL_PALE, TEAL, 1.6, rx=6)
    f.txt(72, 90, "map(doc) -> emit(doc.tags, doc.id)", 12, "start", INK,
          mono=True)
    f.txt(72, 108, "runs once per document, incrementally", 11, "start", GRAY)

    rows = [(t, i) for t, i in M.map_view()]
    y = 144
    for i, (tag, doc) in enumerate(rows[:6]):
        yy = y + i * 30
        f.rect(60, yy, 150, 26, WHITE, RULE, 1, rx=3)
        f.rect(214, yy, 100, 26, WHITE, RULE, 1, rx=3)
        f.txt(70, yy + 18, tag, 12, "start", INK, mono=True)
        f.txt(224, yy + 18, doc, 12, "start", MID, mono=True)
    f.txt(60, y - 8, "key", 10, "start", GRAY)
    f.txt(214, y - 8, "value", 10, "start", GRAY)
    f.rect(60, y + 6 * 30 - 8, 254, 14, TEAL_W, TEAL, 1, rx=3)
    f.txt(330, y + 40, "a range scan", 11, "start", TEAL)
    f.txt(330, y + 58, "walks this order", 11, "start", TEAL)

    f.line(490, 60, 490, 386, RULE, 1.5, "7,6")

    f.region(520, 56, 420, 330, "inverted")
    inv = M.inverted()
    y = 74
    for i, (term, ids) in enumerate(inv.items()):
        yy = y + i * 44
        f.rect(540, yy, 110, 34, WHITE, VIOLET, 1.2, rx=4)
        f.txt(595, yy + 22, term, 12, "middle", VIOLET, bold=True, mono=True)
        arrow(f, 656, yy + 17, 682, yy + 17, VIOLET, 1.4)
        for j, doc in enumerate(ids):
            f.rect(688 + j * 60, yy, 54, 34, VIOLET_W, VIOLET, 1, rx=4)
            f.txt(715 + j * 60, yy + 22, doc, 11, "middle", INK, mono=True)

    f.txt(540, 300, "one term, every document that has it.", 12, "start", MID)
    f.txt(540, 320, "A write touches many postings;", 12, "start", MID)
    f.txt(540, 340, "a read is cheap and ranked.", 12, "start", MID)

    caption(f, 40, 396, 900,
            "Both are indexes, and they answer different questions: \"the rows "
            "in this range\" against \"the best few, in any order\". The second "
            "one costs more to write.")
    save(f)


# =============================================================== 14. graph

def fig_graph():
    f = Fig(940, 440, "fig-graph.svg")
    f.txt(40, 40, "as relations: each hop is an index lookup", 13, "start", GRAY)
    f.txt(520, 40, "as a graph: each hop is a pointer", 13, "start", GRAY)

    f.region(40, 56, 430, 300, "rel")
    f.rect(60, 76, 380, 150, WHITE, BLUE, 1.6, rx=6)
    f.txt(72, 96, "edges (from, to)", 12, "start", BLUE, bold=True)
    for i, (a, b) in enumerate(M.GRAPH_EDGES):
        f.txt(72, 120 + i * 22, "%s  →  %s" % (a, b), 12, "start", INK, mono=True)
    for i in range(3):
        f.txt(300, 120 + i * 22, "index", 10, "start", BLUE)
        f.rect(290, 108 + i * 22, 56, 18, BLUE_W, BLUE, 1, rx=3)

    f.txt(60, 258, "alice → bob → carol → dave", 13, "start", INK, bold=True)
    f.txt(60, 282, "3 hops, 3 lookups", 12, "start", BLUE)
    f.txt(60, 306, "and the plan is chosen at query time", 11, "start", GRAY)

    f.line(486, 60, 486, 360, RULE, 1.5, "7,6")

    f.region(520, 56, 380, 300, "graph")
    xs = [570, 680, 790, 890]
    names = ["alice", "bob", "carol", "dave"]
    for i, (x, name) in enumerate(zip(xs, names)):
        f.circle(x, 170, 34, VIOLET_W, VIOLET, 2)
        f.txt(x, 176, name[:3], 12, "middle", INK, bold=True)
        if i:
            arrow(f, x - 66, 170, x - 38, 170, VIOLET, 2)
    f.txt(560, 240, "the edge is a record, with pointers", 12, "start", VIOLET)
    f.txt(560, 262, "3 hops, 3 pointer chases", 12, "start", VIOLET)
    f.txt(560, 284, "but a traversal cannot be split across nodes", 11, "start", RED)

    caption(f, 40, 366, 860,
            "A graph store is what you build when you refuse to give up the "
            "join: it stores the relationship as a record. The bill is that "
            "partitioning a traversal is the hard part.")
    save(f)


# ============================================================== 15. ladder

def fig_access_depth(lit=None):
    W, H = 900, 640
    name = "fig-access-depth.svg" if lit is None else "fig-access-%d.svg" % lit
    f = Fig(W, H, name)

    bx, bw, bh, gap, y0 = 250, 520, 74, 12, 56
    rungs = list(reversed(M.LADDER))  # relational at the top

    top = y0
    bot = y0 + len(rungs) * bh + (len(rungs) - 1) * gap
    f.line(222, bot - 14, 222, top + 4, TEAL, 2, arrow=True)
    f.txt_rot(204, (top + bot) / 2, "more structure", 12, TEAL)
    f.line(806, top + 14, 806, bot - 4, GRAY, 2, arrow=True)
    f.txt_rot(824, (top + bot) / 2, "less coordination", 12, GRAY)

    for i, (rname, ask, buys, costs, example) in enumerate(rungs):
        y = y0 + i * (bh + gap)
        on = (lit is not None and i == len(rungs) - 1 - lit)
        fill = TEAL if on else (PALE if rname != "cache" else "#fbfbfd")
        f.rect(bx, y, bw, bh, fill, TEAL if on else RULE, 2.4 if on else 1.4,
               rx=6, dash="7,5" if rname == "cache" else None)
        f.txt(bx + 18, y + 28, rname, 17, "start", WHITE if on else INK, bold=True)
        f.txt(bx + 18, y + 50, ask, 11.5, "start",
              TEAL_W if on else MID)
        f.txt(bx + 18, y + 67, "buys " + buys, 11, "start",
              TEAL_W if on else GRAY)
        f.txt(bx + bw - 16, y + 28, example, 11, "end",
              TEAL_W if on else GRAY, italic=True)
        f.txt(bx + bw - 16, y + 50, "costs " + costs, 11, "end",
              TEAL_W if on else AMBER)

    f.txt(bx + bw / 2, H - 26,
          "each step up buys query surface and costs coordination or structure",
          12, "middle", MID)
    save(f)


# ============================================================ 16. consensus

def fig_consensus():
    f = Fig(940, 460, "fig-consensus.svg")
    f.txt(40, 40, "every shard is its own consensus group", 13, "start", GRAY)

    x0, y0, cw, ch = 260, 90, 180, 52
    for i in range(M.CONSENSUS_SHARDS):
        for j in range(M.CONSENSUS_REPLICAS):
            x, y = x0 + j * (cw + 8), y0 + i * (ch + 14)
            leader = (j == 0)
            lit = (i == 1 and j == 0)
            f.rect(x, y, cw, ch, TEAL_PALE if lit else WHITE,
                   TEAL if leader else RULE, 2.4 if lit else 1.2, rx=5)
            f.txt(x + 10, y + 22, "shard %d" % (i + 1) if j == 0 else "", 11,
                  "start", GRAY)
            f.txt(x + cw / 2, y + 36, "leader" if leader else "replica", 12,
                  "middle", TEAL if leader else MID, bold=leader)
        f.txt(x0 - 16, y0 + i * (ch + 14) + ch / 2 + 4,
              "Raft group %d" % (i + 1), 12, "end", TEAL)

    f.rect(40, 150, 130, 64, PALE, RULE, 1.4, rx=6)
    f.txt(105, 178, "client", 13, "middle", MID, bold=True)
    f.txt(105, 196, "one write", 11, "middle", GRAY)

    arrow(f, 176, 182, 256, 182, TEAL, 2)
    f.txt(216, 172, "1", 11, "middle", TEAL, bold=True)

    f.line(440, 216, 440, 300, TEAL, 2, arrow=True)
    f.line(440, 300, 700, 300, TEAL, 2, arrow=True)
    f.txt(570, 292, "replicate to a majority", 11, "middle", TEAL)
    f.txt(216, 214, "the leader must hear from a majority before it answers",
          11, "start", GRAY)

    f.rect(40, 330, 860, 74, AMBER_W, AMBER, 1.8, rx=8)
    f.txt(58, 358, "A write costs two round trips before the client is told it "
                   "succeeded", 14, "start", AMBER, bold=True)
    f.txt(58, 382, "and that is on every commit, on every shard, for the whole "
                   "life of the system. The price is paid in milliseconds, "
                   "forever.", 12, "start", INK)

    caption(f, 40, 414, 860,
            "No global lock and no single log: the order comes from each "
            "group's leader, and the transaction layer stitches the groups "
            "together.")
    save(f)


# ================================================== 17. where order comes from

def fig_commit_points():
    f = Fig(980, 450, "fig-commit-points.svg")
    panels = [("TiDB", 40), ("YugabyteDB", 500)]
    for name, x in panels:
        cp = M.COMMIT_POINTS[name]
        f.region(x, 46, 440, 320, name)
        f.rect(x, 46, 440, 320, WHITE, TEAL, 2, rx=8)
        f.txt(x + 16, 72, name, 16, "start", TEAL, bold=True)
        f.txt(x + 424, 72, cp["wire"] + " wire", 11, "end", GRAY)

        rows = [("the order comes from", cp["order"]),
                ("the decision is", cp["decision"]),
                ("the data sits in", cp["storage"])]
        for i, (label, (short, detail)) in enumerate(rows):
            yy = 92 + i * 86
            f.txt(x + 16, yy, label, 10, "start", GRAY)
            f.rect(x + 16, yy + 8, 408, 66, TEAL_PALE if i == 0 else PALE,
                   TEAL if i == 0 else RULE, 1.8 if i == 0 else 1, rx=5)
            f.txt(x + 28, yy + 30, short, 13, "start",
                  TEAL if i == 0 else INK, bold=True)
            f.para(x + 28, yy + 50, 386, detail, 10.5, MID)

        f.txt(x + 16, 356, "default isolation: " + cp["default"], 12, "start",
              AMBER, bold=True)

    caption(f, 40, 380, 900,
            "Both systems pay for coordination. They disagree about where the "
            "order lives: in one authority that hands out timestamps, or in "
            "each transaction's own record.")
    save(f)


# ================================================================== 19. CAP

def fig_cap():
    f = Fig(940, 440, "fig-cap.svg")
    f.txt(40, 42, "During a partition, each side must answer somehow", 15,
          "start", GRAY)

    f.region(90, 80, 260, 96, "node 1")
    f.rect(90, 80, 260, 96, WHITE, TEAL, 2, rx=8)
    f.txt(220, 116, "node 1", 15, "middle", TEAL, bold=True)
    f.txt(220, 140, "has the row", 11, "middle", GRAY)

    f.region(590, 80, 260, 96, "node 2")
    f.rect(590, 80, 260, 96, WHITE, TEAL, 2, rx=8)
    f.txt(720, 116, "node 2", 15, "middle", TEAL, bold=True)
    f.txt(720, 140, "has the other copy", 11, "middle", GRAY)

    f.path("M 360 128 L 400 128", "none", RED, 2.4, "5,4")
    f.path("M 540 128 L 580 128", "none", RED, 2.4, "5,4")
    f.path("M 420 96 L 444 160 L 470 96 L 496 160", "none", RED, 2.4)
    f.txt(470, 76, "the partition", 13, "middle", RED, bold=True)
    f.txt(470, 184, "P is not a knob you set", 11, "middle", GRAY)
    f.txt(470, 200, "it is a property of the network", 11, "middle", GRAY)

    f.rect(150, 250, 280, 96, AMBER_W, AMBER, 2, rx=8)
    f.txt(290, 280, "refuse the request", 14, "middle", AMBER, bold=True)
    f.txt(290, 304, "consistent, and unavailable", 11, "middle", INK)
    f.txt(290, 326, "CP", 13, "middle", AMBER, bold=True)

    f.rect(510, 250, 280, 96, TEAL_PALE, TEAL, 2, rx=8)
    f.txt(650, 280, "answer, possibly stale", 14, "middle", TEAL, bold=True)
    f.txt(650, 304, "available, and inconsistent", 11, "middle", INK)
    f.txt(650, 326, "AP", 13, "middle", TEAL, bold=True)

    f.line(220, 178, 220, 246, RULE, 1.4, "5,4")
    f.line(720, 178, 720, 246, RULE, 1.4, "5,4")

    caption(f, 60, 362, 820,
            "That is the whole theorem: during a partition you cannot have "
            "both. Path A of the fork is AP; Path B is CP.")
    save(f)


# =========================================================== 20. join fixes

def fig_joins():
    f = Fig(1000, 440, "fig-joins.svg")
    titles = ["co-locate", "broadcast", "shuffle"]
    subs = ["put the two tables on the same key",
            "copy the small side to every node",
            "re-partition both sides by the join key"]

    for i in range(3):
        x = 30 + i * 330
        f.region(x, 56, 310, 300, titles[i])
        f.rect(x, 56, 310, 300, WHITE, RULE, 1.4, rx=8)
        f.txt(x + 155, 84, titles[i], 15, "middle", TEAL, bold=True)
        f.txt(x + 155, 104, subs[i], 10.5, "middle", GRAY)

    # 1. co-locate
    x = 30
    f.rect(x + 30, 128, 250, 130, PALE, TEAL, 1.6, rx=6)
    f.txt(x + 155, 148, "one node", 10, "middle", GRAY)
    f.rect(x + 48, 162, 96, 74, WHITE, TEAL, 1.2, rx=4)
    f.txt(x + 96, 190, "orders", 11, "middle", INK, bold=True)
    f.txt(x + 96, 210, "keyed by", 10, "middle", GRAY)
    f.txt(x + 96, 224, "customer", 10, "middle", GRAY)
    f.rect(x + 166, 162, 96, 74, WHITE, TEAL, 1.2, rx=4)
    f.txt(x + 214, 190, "customers", 11, "middle", INK, bold=True)
    f.txt(x + 214, 210, "keyed by", 10, "middle", GRAY)
    f.txt(x + 214, 224, "customer", 10, "middle", GRAY)
    arrow(f, x + 148, 199, x + 162, 199, TEAL, 1.6)
    f.txt(x + 155, 286, "the join never leaves the node", 11, "middle", TEAL)

    # 2. broadcast
    x = 360
    for j, (label, tx) in enumerate((("node 1", x + 34), ("node 2", x + 176))):
        f.rect(tx, 176, 100, 100, PALE, RULE, 1.2, rx=4)
        f.txt(tx + 50, 196, label, 10, "middle", GRAY)
        f.rect(tx + 14, 210, 72, 50, WHITE, TEAL, 1.2, rx=4)
        f.txt(tx + 50, 240, "facts", 11, "middle", INK)
    f.rect(x + 116, 132, 78, 28, AMBER_W, AMBER, 1.4, rx=4)
    f.txt(x + 155, 151, "dim table", 10, "middle", AMBER, bold=True)
    for tx in (x + 84, x + 226):
        arrow(f, x + 155, 164, tx, 206, AMBER, 1.4, "4,4")
    f.txt(x + 155, 296, "one copy of the small side", 11, "middle", AMBER)

    # 3. shuffle
    x = 690
    for j, tx in enumerate((x + 24, x + 166)):
        f.rect(tx, 132, 120, 144, PALE, RULE, 1.2, rx=4)
        f.txt(tx + 60, 152, "node %d" % (j + 1), 10, "middle", GRAY)
        for k in range(3):
            f.rect(tx + 12, 164 + k * 34, 96, 26, WHITE, TEAL, 1, rx=3)
            f.txt(tx + 60, 182 + k * 34, "rows %d" % (k + 1), 10, "middle", INK)
    arrow(f, x + 146, 200, x + 164, 250, RED, 1.6, "4,4")
    arrow(f, x + 164, 214, x + 146, 264, RED, 1.6, "4,4")
    f.txt(x + 155, 296, "both sides move, across the network", 11, "middle", RED)

    caption(f, 30, 368, 940,
            "The best cross-shard join is the one you designed away. After "
            "that: copy the small side, or move both sides and pay for the "
            "network.")
    save(f)


# ========================================================= 18. design space

def fig_space():
    f = Fig(1000, 640, "fig-space.svg")
    x0, y0 = 250, 96
    pw, ph = 700, 450

    # frame
    f.line(x0, y0, x0, y0 + ph, RULE, 1.5)
    f.line(x0, y0 + ph, x0 + pw, y0 + ph, RULE, 1.5)

    def px(xv):
        return x0 + xv / 3.0 * pw

    def py(yv):
        return y0 + ph - yv / 5.0 * ph

    for i, label in enumerate(M.SPACE_X):
        f.line(px(i), y0, px(i), y0 + ph, RULE, 0.8, "4,6")
        f.txt(px(i), y0 + ph + 22, label, 12, "middle", MID)
    f.txt(x0 + pw / 2, y0 + ph + 48,
          "where the commit point is", 13, "middle", TEAL, bold=True)

    for i, label in enumerate(M.SPACE_Y):
        f.line(x0, py(i), x0 + pw, py(i), RULE, 0.8, "4,6")
        f.txt(x0 - 14, py(i) + 4, label, 12, "end", MID)
    f.txt_rot(x0 - 96, y0 + ph / 2, "how much structure it understands", 13, TEAL)

    # the empty corner, named
    f.rect(px(2.55), py(1.0), px(3) - px(2.55), py(0) - py(1.0), "#fdfaf5",
           AMBER, 1.4, rx=6, dash="6,5")
    f.txt(px(2.78), py(0.55), "nobody pays", 11, "middle", AMBER)
    f.txt(px(2.78), py(0.32), "consensus", 11, "middle", AMBER)
    f.txt(px(2.78), py(0.12), "for a blob", 11, "middle", AMBER)

    for name, xv, yv, dx, dy, anchor in M.SYSTEMS:
        x, y = px(xv), py(yv)
        tone = TEAL if xv >= 2 else (AMBER if xv < 1 else MID)
        f.circle(x, y, 6, WHITE, tone, 2.4)
        f.txt(x + dx, y + dy, name, 11.5, anchor, INK, bold=True)

    f.txt(px(0.05), py(4.72), "structure", 11, "start", GRAY, italic=True)
    f.txt(px(0.05), py(4.56), "without", 11, "start", GRAY, italic=True)
    f.txt(px(0.05), py(4.40), "coordination", 11, "start", GRAY, italic=True)

    f.txt(px(2.98), py(4.72), "consensus,", 11, "end", GRAY, italic=True)
    f.txt(px(2.98), py(4.56), "and it costs", 11, "end", GRAY, italic=True)

    caption(f, 40, 588, 920,
            "The two axes are the two questions this lecture asked. The "
            "vertical spread at each rung is the point: the data model does "
            "not pick the coordination. Positions are approximate.")
    save(f)


# ==================================================================== main

def main():
    fig_commit_point()
    fig_two_commits()
    fig_transaction()
    fig_multimaster()
    fig_fork()
    fig_quorum()
    fig_shard_join()
    fig_cassandra_model()
    fig_lsm()
    fig_two_axes()
    fig_failures()
    fig_money()
    fig_aggregate()
    fig_revision()
    fig_index()
    fig_graph()
    fig_access_depth()
    # A lit variant per rung is available (`fig_access_depth(lit=i)`), which is
    # how a part header could show where you are. The deck uses only the cache
    # rung, so only that variant is written -- an orphan figure is a file the
    # lint would have to forgive.
    fig_access_depth(lit=0)
    fig_consensus()
    fig_commit_points()
    fig_cap()
    fig_joins()
    fig_space()


if __name__ == "__main__":
    main()
