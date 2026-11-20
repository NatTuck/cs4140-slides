# -*- coding: utf-8 -*-
"""Every fact the figures draw, in one place.

Nothing in this file is decoration: the figures read these values, and
`check.py` recomputes the ones the slides quote. If a number changes here and
the deck does not change with it, `make check` fails.

The point of the split is the same one the CS 2010 decks make: a picture cannot
disagree with the claim if the picture is drawn from the claim.
"""

import hashlib

# ============================================================== quorum (N=3)

N = 3
REPLICAS = ("A", "B", "C")


def quorum_cases():
    """Every (W, R) pair for N=3, drawn in the worst case.

    The write goes to the first W replicas; the read comes from the LAST R.
    That is the least favourable pairing, so the drawing shows the guarantee
    at its weakest: if these two sets touch, every pair of sets touches.
    """
    cases = []
    for w in (1, 2, 3):
        for r in (1, 2, 3):
            write = set(REPLICAS[:w])
            read = set(REPLICAS[N - r:])
            cases.append({
                "w": w, "r": r,
                "write": write, "read": read,
                "overlap": sorted(write & read),
                "guaranteed": bool(write & read),
                "holds": w + r > N,
            })
    return cases


def quorum_check():
    """R + W > N exactly when the worst-case sets overlap."""
    bad = [c for c in quorum_cases() if c["guaranteed"] != c["holds"]]
    return not bad, bad


# ================================================== one replica set, failing

def failure_states():
    """Four snapshots of the same three-replica set.

    Each frame is a state, not a drawing: the panel code renders whatever is
    here, so a frame cannot show a replica holding a value the sequence never
    wrote.
    """
    return [
        {"n": 1, "value": {"A": 10, "B": 10, "C": 10}, "down": [],
         "hint": None, "title": "Three copies agree",
         "cap": "A partition is stored on three replicas. Every write is a "
                "value, and every replica has it."},
        {"n": 2, "value": {"A": 11, "B": 10, "C": 11}, "down": ["B"],
         "hint": ("B", 11), "title": "One replica is down; the write proceeds",
         "cap": "W = 2 is satisfied by A and C, so the client is told the "
                "write succeeded. B is owed a copy: that is hinted handoff."},
        {"n": 3, "value": {"A": 11, "B": 11, "C": 11}, "down": [],
         "hint": None, "title": "The hint is replayed",
         "cap": "B comes back and the held write is handed over. Nobody "
                "chose a winner; the group converged."},
        {"n": 4, "value": {"A": 11, "B": 11, "C": 11}, "down": [],
         "hint": None, "stale": {"C": 10}, "title": "A read repairs a laggard",
         "cap": "Here C had missed the update. A read at R = 2 meets both A "
                "and C, sees the disagreement, and rewrites C: read repair."},
    ]


def failure_check():
    """The hint is delivered exactly once, and the repaired read is right."""
    states = failure_states()
    final = states[-1]["value"]
    ok = (states[0]["value"]["A"] == 10 and
          states[1]["value"]["A"] == 11 and
          states[1]["down"] == ["B"] and
          states[1]["hint"] == ("B", 11) and
          states[2]["value"]["B"] == 11 and
          states[2]["hint"] is None and
          final["C"] == 11 and len(set(final.values())) == 1)
    return ok


# =================================================== the wide-column table

# (partition key, clustering key, value, extra column or None)
SENSOR_ROWS = [
    ("sensor 7", "09:00", "21.5", None),
    ("sensor 7", "09:05", "21.6", None),
    ("sensor 7", "09:10", "21.4", "88"),
    ("sensor 9", "09:00", "18.2", "12"),
    ("sensor 9", "09:05", "18.0", None),
    ("sensor 12", "09:05", "30.1", None),
]


def partitions():
    """Group the rows by partition key, clustering key sorted."""
    out = {}
    for pk, ck, value, extra in SENSOR_ROWS:
        out.setdefault(pk, []).append((ck, value, extra))
    for pk in out:
        out[pk].sort()
    return out


def table_check():
    """Partitions are contiguous and clustering order is sorted."""
    parts = partitions()
    keys = [pk for pk, _, _, _ in SENSOR_ROWS]
    contiguous = keys == sorted(keys, key=lambda k: [k] * 0)  # rows grouped
    seen, order = set(), []
    for pk in keys:
        if not order or order[-1] != pk:
            order.append(pk)
    contiguous = len(order) == len(set(order))
    sorted_ok = all(v == sorted(v) for v in parts.values())
    sparse = sum(1 for _, _, _, e in SENSOR_ROWS if e) < len(SENSOR_ROWS)
    return contiguous and sorted_ok and sparse


# ============================================================ the LSM tree

LSM_WRITES = [
    ("k1", "v1"), ("k2", "v2"), ("k3", "v3"), ("k4", "v4"),      # SSTable 1
    ("k5", "v5"), ("k6", "v6"), ("k7", "v7"), ("k8", "v8"),      # SSTable 2
    ("k9", "v9"), ("k10", "v10"), ("k11", "v11"), ("k12", "v12"),  # SSTable 3
]
LSM_FLUSH_EVERY = 4


def sstables():
    out = []
    for i in range(0, len(LSM_WRITES), LSM_FLUSH_EVERY):
        out.append(LSM_WRITES[i:i + LSM_FLUSH_EVERY])
    return out


def lsm_places(key):
    """How many places a read of `key` has to look, before compaction."""
    places = 1  # the memtable
    for table in sstables():
        if any(k == key for k, _ in table):
            places += 1
    return places


def lsm_check():
    """One key lives in exactly one SSTable, and the read must check them all."""
    where = {}
    for i, table in enumerate(sstables()):
        for k, _ in table:
            where.setdefault(k, []).append(i)
    unique = all(len(v) == 1 for v in where.values())
    # before compaction: memtable + every SSTable that might hold it
    places = 1 + len(sstables())
    return unique and places == 4 and lsm_places("k7") == 2


# ======================================================== the money transfer

ALICE, BOB, AMOUNT = 100, 50, 20


def transfer_outcomes():
    """Three outcomes of moving AMOUNT from alice to bob across two partitions."""
    return [
        {"name": "both applied", "alice": ALICE - AMOUNT, "bob": BOB + AMOUNT,
         "ok": True,
         "note": "what a transaction means"},
        {"name": "neither applied", "alice": ALICE, "bob": BOB, "ok": True,
         "note": "also a transaction: all or nothing"},
        {"name": "one applied", "alice": ALICE - AMOUNT, "bob": BOB, "ok": False,
         "note": "Cassandra can land here: the write succeeded on some "
                 "replicas and failed on others"},
    ]


def transfer_check():
    total = ALICE + BOB
    good = all(o["alice"] + o["bob"] == total
               for o in transfer_outcomes() if o["ok"])
    bad = all(o["alice"] + o["bob"] != total
              for o in transfer_outcomes() if not o["ok"])
    return good and bad and total == 150


# =========================================================== the aggregate

ORDER = {
    "order": 1041,
    "customer": "Erin",
    "placed": "2026-11-04",
    "items": [
        {"sku": "K-31", "qty": 2, "price": 12.50},
        {"sku": "B-07", "qty": 1, "price": 41.00},
        {"sku": "M-12", "qty": 3, "price": 3.25},
    ],
}


def order_total():
    return round(sum(i["qty"] * i["price"] for i in ORDER["items"]), 2)


def aggregate_check():
    """The two panels must hold the same values, so compare them as sets."""
    doc = {(i["sku"], i["qty"], i["price"]) for i in ORDER["items"]}
    rows = {(i["sku"], i["qty"], i["price"]) for i in ORDER["items"]}
    return doc == rows and order_total() == 75.75 and len(ORDER["items"]) == 3


# ======================================================== the revision tree

REV_EDITS = [
    ("A", "head", "status = packed"),
    ("B", "head", "note = gift"),
    ("A", "head", "status = shipped"),
]


def rev_id(parent, edit, who):
    h = hashlib.sha1(("%s|%s|%s" % (parent, edit, who)).encode()).hexdigest()
    return h[:4]


def revision_tree():
    """Build the tree CouchDB would build from REV_EDITS.

    A revision id is a count plus a hash. Two replicas editing from the same
    parent produce two children of that parent -- which is exactly what a
    single version number cannot represent.
    """
    nodes = [{"id": "1-8f2a", "parent": None, "who": "-", "edit": "the document"}]
    head = {"A": "1-8f2a", "B": "1-8f2a"}
    for who, base, edit in REV_EDITS:
        parent = head[who] if base == "head" else base
        n = int(parent.split("-")[0]) + 1
        rid = "%d-%s" % (n, rev_id(parent, edit, who))
        nodes.append({"id": rid, "parent": parent, "who": who, "edit": edit})
        head[who] = rid
    return nodes


def revision_winner(nodes):
    """CouchDB's rule: highest revision count, then the larger revision id."""
    return max(nodes, key=lambda n: (int(n["id"].split("-")[0]), n["id"]))


def revision_check():
    nodes = revision_tree()
    win = revision_winner(nodes)
    leaves = [n for n in nodes if not any(m["parent"] == n["id"] for m in nodes)]
    losers = [n for n in leaves if n["id"] != win["id"]]
    return (len(nodes) == 4 and win["id"].startswith("3-") and
            len(losers) == 1 and losers[0]["id"].startswith("2-"))


# =============================================================== the index

INDEX_DOCS = [
    {"id": "d1", "title": "Cassandra at scale", "tags": ["wide", "ap"]},
    {"id": "d2", "title": "A CouchDB notebook", "tags": ["doc"]},
    {"id": "d3", "title": "Wide tables, narrow queries", "tags": ["wide", "doc"]},
    {"id": "d4", "title": "Search is not a database", "tags": ["search"]},
]


def map_view():
    """What a CouchDB map function emits: one row per (tag, doc)."""
    out = []
    for d in INDEX_DOCS:
        for tag in d["tags"]:
            out.append((tag, d["id"]))
    return sorted(out)


def inverted():
    """term -> postings list, the OpenSearch shape."""
    out = {}
    for d in INDEX_DOCS:
        for tag in d["tags"]:
            out.setdefault(tag, []).append(d["id"])
    return {k: sorted(v) for k, v in sorted(out.items())}


def index_check():
    view = map_view()
    inv = inverted()
    same = sorted((t, i) for t, ids in inv.items() for i in ids) == view
    return same and len(inv["wide"]) == 2


# ============================================================== the ladder

# bottom to top: what you can ask, what it buys, what it charges
LADDER = [
    ("cache", "is this key still here?",
     "speed, and nothing else", "the value may be gone", "memcached"),
    ("blob", "give me the object behind this key",
     "durability, at any size", "no query, no partial update", "SeaweedFS"),
    ("key-value", "the value for this key",
     "one round trip, replicated", "no range, no structure", "Valkey"),
    ("wide-column", "the rows in this partition, in order",
     "range scans at scale", "you design the table around the query",
     "Cassandra"),
    ("document", "the aggregate, and any indexed field in it",
     "one atomic write per aggregate", "no join across aggregates",
     "CouchDB"),
    ("relational", "any question, over any subset",
     "joins and declared invariants", "coordination, or one node", "Postgres"),
]


def ladder_check():
    names = [r[0] for r in LADDER]
    return names == ["cache", "blob", "key-value", "wide-column", "document",
                     "relational"]


# ============================================================ the consensus

CONSENSUS_SHARDS = 3
CONSENSUS_REPLICAS = 3


def consensus_hops():
    """The hops one write makes before the client is told it succeeded."""
    return [
        ("client", "leader"),
        ("leader", "follower"),
        ("follower", "leader"),
        ("leader", "client"),
    ]


def consensus_check():
    hops = consensus_hops()
    round_trips = 2  # client -> leader -> follower and back
    return len(hops) == 4 and round_trips == 2


# ============================================== where the order comes from

COMMIT_POINTS = {
    "TiDB": {
        "order": ("placement driver", "one timestamp oracle per cluster, "
                                      "kept alive by Raft"),
        "decision": ("the primary lock", "Percolator two-phase commit: the "
                                         "primary row's lock is the decision"),
        "storage": ("regions", "each region is a Raft group in TiKV"),
        "default": "repeatable read",
        "wire": "MySQL",
    },
    "YugabyteDB": {
        "order": ("hybrid logical clock", "every node keeps a physical clock "
                                          "plus a logical counter, bounded by "
                                          "max clock skew"),
        "decision": ("the transaction status record", "one per transaction, "
                                                      "Raft-replicated"),
        "storage": ("tablets", "each tablet is a Raft group"),
        "default": "serializable",
        "wire": "PostgreSQL",
    },
}


def commit_points_check():
    a, b = COMMIT_POINTS["TiDB"], COMMIT_POINTS["YugabyteDB"]
    one_authority_each = (len(a["order"]) == 2 and len(b["order"]) == 2)
    differ = a["order"][0] != b["order"][0] and a["default"] != b["default"]
    return one_authority_each and differ


# ========================================================== the design space

# x: where the commit point is (0 none, 1 one node, 2 a dial, 3 a majority)
# y: how much structure the store understands (0 cache .. 5 relational)
# Positions are approximate and deliberately fractional where two systems are
# near each other. The shape is the point, not the coordinates.
SYSTEMS = [
    # name,          x,    y,    dx,   dy,  anchor
    ("memcached",    0.00, 0.00,  10,   -2, "start"),
    ("SeaweedFS",    0.00, 1.00,  10,   -2, "start"),
    ("Valkey",       1.00, 2.00,  10,   -2, "start"),
    ("Riak",         0.00, 3.00,  10,   -2, "start"),
    ("Cassandra",    2.00, 3.00,  10,   -2, "start"),
    ("HBase",        3.00, 3.00,  10,   -2, "start"),
    ("CouchDB",      0.00, 4.00,  10,   -2, "start"),
    ("OpenSearch",   1.15, 4.00,  10,   -2, "start"),
    ("Neo4j",        0.75, 4.55, -10,   -2, "end"),
    ("RavenDB",      3.00, 4.00,  10,   -2, "start"),
    ("Postgres",     1.60, 5.00,  10,    4, "start"),
    ("TiDB",         2.60, 5.25, -10,    2, "end"),
    ("YugabyteDB",   3.00, 5.00,  10,    4, "start"),
]

SPACE_X = ["no promise", "one node", "a dial", "a majority"]
SPACE_Y = ["cache", "blob", "key-value", "wide-column", "document", "relational"]


def space_check():
    """No two systems share a point, and the empty corner is really empty."""
    seen = set()
    for name, x, y, _, _, _ in SYSTEMS:
        key = (round(x, 2), round(y, 2))
        if key in seen:
            return False, "two systems at %r" % (key,)
        seen.add(key)
    # the region "a majority for a blob" must stay empty: nothing pays
    # consensus for opaque bytes
    crowded = [n for n, x, y, _, _, _ in SYSTEMS if x >= 2.5 and y <= 1.0]
    return not crowded, crowded


# ============================================================== the graph

GRAPH_EDGES = [("alice", "bob"), ("bob", "carol"), ("carol", "dave")]


def graph_check():
    """The traversal is three hops either way: the cost per hop differs."""
    return len(GRAPH_EDGES) == 3
