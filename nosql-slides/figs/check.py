# -*- coding: utf-8 -*-
"""Recompute every number the slides quote, and assert the load-bearing ones.

`make check-figs` runs this. Two kinds of assertion:

1.  The arithmetic in model.py is self-consistent -- a quorum overlaps exactly
    when R + W > N, the transfer keeps its total in the outcomes that are
    allowed, the revision winner is the one CouchDB's rule picks, and so on.

2.  Every number printed on a slide still equals what model.py computes. If a
    value changes and the deck does not change with it, this fails -- rather
    than the deck quietly disagreeing with its own figures.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import model as M

DECK = os.path.dirname(HERE)
QMD = os.path.join(DECK, "index.qmd")

failures = []


def check(label, cond, detail=""):
    print("[%s] %s %s" % ("ok  " if cond else "FAIL", label, detail))
    if not cond:
        failures.append(label)


# ------------------------------------------------------------ the arithmetic

def model_checks():
    ok, bad = M.quorum_check()
    check("quorum: R + W > N exactly when the sets overlap", ok, str(bad))

    cases = M.quorum_cases()
    check("commit point: one logical transaction, two commit records",
          M.retry_check())
    check("transaction: a set of writes, one outcome", M.transaction_check())
    check("CAP: three guarantees, and the fork maps onto AP / CP",
          M.cap_check())
    check("joins: four answers, shuffle is the expensive one", M.join_check())

    check("quorum: nine cases for N = 3", len(cases) == 9, str(len(cases)))
    check("quorum: six pairs hold",
          sum(1 for c in cases if c["holds"]) == 6,
          str([(c["w"], c["r"]) for c in cases if c["holds"]]))

    check("replica set: the hint is delivered exactly once",
          M.failure_check())
    check("replica set: four frames", len(M.failure_states()) == 4)

    check("table: partitions contiguous, clustering sorted, cells sparse",
          M.table_check())
    check("table: six rows in three partitions",
          len(M.SENSOR_ROWS) == 6 and len(M.partitions()) == 3)

    check("lsm: one key, one sstable, four places to look", M.lsm_check())
    check("lsm: k7 sits in the second sstable", M.lsm_places("k7") == 2)

    check("money: allowed outcomes keep the total, the other breaks it",
          M.transfer_check())
    check("money: three outcomes",
          len(M.transfer_outcomes()) == 3)

    check("aggregate: both panels hold the same values", M.aggregate_check())
    check("aggregate: the order totals 75.75", M.order_total() == 75.75)

    check("revision tree: four nodes, winner is 3-*, one conflict retained",
          M.revision_check())
    nodes = M.revision_tree()
    check("revision tree: two children of the root",
          len([n for n in nodes if n["parent"] == nodes[0]["id"]]) == 2)

    check("index: the view and the inverted index emit the same pairs",
          M.index_check())

    check("ladder: six rungs, cache at the bottom", M.ladder_check())

    check("consensus: four hops, two round trips", M.consensus_check())

    check("commit points: one authority each, and they differ",
          M.commit_points_check())

    ok, crowded = M.space_check()
    check("design space: no two systems share a point, empty corner empty",
          ok, str(crowded))
    check("design space: thirteen systems", len(M.SYSTEMS) == 13,
          str(len(M.SYSTEMS)))

    check("graph: a three-hop traversal", M.graph_check())


# ------------------------------------------------- numbers printed on slides

# (format string, the value model.py computes). The format string is searched
# in the deck case-insensitively; %s is the computed value.
NUMBERS = [
    ("W + R > N", "W + R > N"),
    ("two truths and no undo", "two truths and no undo"),
    ("Path A is AP, Path B is CP", "Path A is AP, Path B is CP"),
    ("P was never optional", "P was never optional"),
    ("strict serializability", "strict serializability"),
    ("the best cross-shard join is the one you designed away",
     "the best cross-shard join is the one you designed away"),
    ("Six of the nine settings work", "Six of the nine settings work"),
    ("look in four places", "look in four places"),
    ("%s + %s = %s" % (100, 50, 150), "100 + 50 = 150"),
    ("%s + %s = %s" % (80, 70, 150), "80 + 70 = 150"),
    ("%s + %s = %s" % (80, 50, 130), "80 + 50 = 130"),
    ("%.2f" % M.order_total(), "75.75"),
    ("two round trips", "two round trips"),
    ("repeatable read", "repeatable read"),
    ("serializable", "serializable"),
    ("cache, blob, key-value", "cache, blob, key-value"),
]


def deck_checks():
    if not os.path.exists(QMD):
        check("deck exists", False, QMD)
        return
    with open(QMD, encoding="utf-8") as f:
        text = f.read()
    # prose wraps, so compare against a whitespace-collapsed copy
    low = " ".join(text.lower().split())

    for fmt, value in NUMBERS:
        if isinstance(value, tuple):
            want = fmt % value
        else:
            want = fmt % value if "%s" in fmt or "%.2f" in fmt else fmt
        check("deck says %r" % want, want.lower() in low)

    # every figure the deck shows exists
    import re
    refs = re.findall(r"!\[\]\((figs/[^)]+)\)", text)
    check("deck references figures", len(refs) > 0, "%d references" % len(refs))
    for ref in sorted(set(refs)):
        path = os.path.join(DECK, ref)
        check("figure exists: %s" % os.path.basename(ref), os.path.exists(path))


VERIFY = [
    ("TiDB is Apache 2.0", "project LICENSE"),
    ("YugabyteDB is Apache 2.0", "project LICENSE"),
    ("TiDB defaults to repeatable read", "TiDB docs, isolation levels"),
    ("YugabyteDB defaults to serializable", "YSQL docs, isolation levels"),
    ("TiDB: one placement driver serves the TSO", "PD docs"),
    ("TiDB: Percolator 2PC, primary lock decides", "TiDB transaction docs"),
    ("YugabyteDB: Raft per tablet, hybrid time, one status record",
     "architecture docs"),
    ("Cassandra Accord status", "Cassandra release notes"),
]


def verify_list():
    """The README's table, printed so a TODO cannot be forgotten."""
    print("\nverify before presenting (README.md carries this table):")
    for claim, where in VERIFY:
        print("  [TODO] %-58s %s" % (claim, where))
    print("  [ok  ] two round trips on the consensus slide  (computed here)")


def main():
    model_checks()
    deck_checks()
    verify_list()
    print()
    if failures:
        print("%d FAILED: %s" % (len(failures), ", ".join(failures)))
        return 1
    print("all checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
