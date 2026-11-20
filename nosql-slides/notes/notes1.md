```markdown
# NoSQL Databases: Why They Exist

**Presentation notes — working draft**

---

## Thesis

NoSQL is not a family of products. It is a family of **answers to a single structural problem**: the ACID transaction assumes a single commit point, and a single commit point does not survive contact with multiple writers across multiple machines.

Everything else — documents, wide columns, blobs, CRDTs, consistency levels, CAP — is downstream of what a system chose to give up in order to distribute that commit point (or to avoid needing one).

---

## Hard constraints on examples

**Proprietary / service-only software is not a valid example.** Every system on a slide must be obtainable, inspectable, and runnable by the audience. This is a constraint on the *design lesson*, not just on licensing sentiment: a managed service's internals are not available to study, so its "design trade-off" is really a marketing claim.

Consequences:

- **DynamoDB is out** — managed only. Its MRSC / global-tables consistency story is interesting but unverifiable from outside.
- **Pinecone is out** — service only, no self-hosted path.
- **MongoDB is out** — SSPL, source-available but not OSI-approved, and it has never added back an open option the way Elastic and Redis did. Every Community Server release since 2018-10-16 is SSPL.
- **FerretDB is not the MongoDB replacement for this talk.** It is a stateless proxy speaking the Mongo wire protocol over PostgreSQL (or SQLite). It proves the *API* is portable, not that the *design* is. The interesting part of Mongo was the replica-set protocol and per-operation consistency dials — a Postgres backend erases exactly that. Do not put it on a slide as "open MongoDB"; if mentioned at all, it belongs on a slide about API compatibility ≠ same system.

---

## The narrative spine

One line per beat:

1. Postgres is ACID.
2. What does ACID actually promise?
3. ACID is tractable because of a **single commit point**.
4. Multiple writers destroy the single commit point → multi-master is a nightmare.
5. The fork: **eventual consistency** or **wait-for-majority**.
6. **Sharding** stretches one commit point across machines — but gives up easy joins.
7. Losing joins costs you ACID's "C," not just convenience.
8. If we don't need ACID transactions, we can do something like **Cassandra** — still tables, relaxed model.
9. Cassandra has **two orthogonal axes**: partitioning and replication.
10. **CAP** formalizes the fork — and P was never optional.
11. Cassandra's **consistency levels are exactly the C-vs-A dial**.
12. How Cassandra does transactions and joins, and exactly how it fails ACID.
13. *Is "partially ACID" even coherent?* — precision beat.
14. If you've given up transactions and joins, **do you really need a table?**
15. Three storage shapes: **document / wide-column / blob**.
16. Cross-host joins: what the current best answer actually is.
17. The wider 2026 example set, each with one specific trade-off.

---

## Slide-by-slide

### 1. The starting point: Postgres is ACID

Say: Postgres is the reference implementation of the thing we're departing from. Not because it's old, but because it makes one clean promise: **the database decides a single commit point, and every reader sees a consistent snapshot of committed data.**

This is the load-bearing sentence for the whole talk. Everything that follows is an argument about what happens when you can't have one commit point.

---

### 2. What ACID actually promises

Define the letters precisely — the audience needs the precision later, when we start arguing about which ones Cassandra has.

- **Atomicity** — all-or-nothing. If any part fails, the database is left as if the transaction never began.
- **Consistency** — the transaction moves the database from one valid state to another, enforcing declared invariants (keys, foreign keys, CHECK constraints).
- **Isolation** — concurrent transactions don't see each other's uncommitted work; the database imposes a serialization order.
- **Durability** — once committed, it survives crash, power loss, restart.

Speaker note: flag here that **"C" is the odd one out.** A, I, and D are properties of the *mechanism*. C is a property of the *data model* — it only means something if you have declarative invariants to enforce. Park this; we come back to it at slide 13.

---

### 3. The single commit point is the load-bearing wall

In Postgres, ACID is enforced by **one primary node that owns the commit point.**

- One node decides the serialization order.
- One node can evaluate a global invariant, because it can see all the affected rows.
- One node's log is the durability record.

This is what makes ACID cheap enough to be the default. It is also the thing that does not distribute.

---

### 4. Multi-master replication vs ACID

Multi-master means more than one node accepts writes. That immediately permits **conflicting concurrent transactions** on different nodes: two inserts on the same key, two updates to the same row, two transactions that each assume they are the only writer.

To preserve ACID under multi-master you need a **global serialization order across all masters**, and isolation that holds across nodes, not just within one. That requires one of:

- **Eager / synchronous coordination** — distributed locking, consensus (Paxos/Raft), or synchronous replication to a quorum before commit. Correct, but pays communication latency and loses availability when nodes or links fail. Eager replication is complex and becomes a bottleneck.
- **Lazy / asynchronous replication** — commit locally, replicate later. Fast and available, but only loosely consistent, and it violates ACID: conflicts and stale reads become possible.

The Postgres community has been blunt: maintaining ACID across multi-master replication is "virtually impossible" with any semblance of performance. Conflict resolution gets intractable as node count and inter-node latency grow.

**Punchline:** ACID is not hard because Postgres is old. ACID is hard because *a single global commit point does not scale across multiple writers without coordination that costs latency and availability.*

---

### 5. The fork: eventual consistency or quorum

Once global ACID across writers is priced out, you get two paths.

**Path A — eventual consistency.** Each replica accepts reads and writes independently. Replicas diverge during normal operation and converge later. Reads may be stale; conflicting writes must be reconciled. High availability, low latency, no "latest write" guarantee.

**Path B — quorum / wait-for-majority.** With **N** replicas, require **W** acknowledgements on write and **R** on read. If **W + R > N**, the read set and write set must overlap, so every read touches at least one replica holding the latest write. This is strong consistency without a single master — coordination bounded to a quorum, with the latency cost made explicit.

If W and R are smaller than that, the guarantee weakens and you slide back toward Path A. **The dial between the two paths is the whole design space.**

---

### 6. Sharding: stretching the single commit point

Sharding answers a different question from replication: *who owns this key?* It scales capacity and write throughput by splitting the key space.

But it costs you something specific and structural: **the join.** A join across shards requires either shipping data across the network or coordinating across partitions. And losing the join is not a convenience loss — it is the loss of the mechanism by which ACID's "C" was enforced. You cannot evaluate a cross-entity invariant if you cannot see both entities in one place.

This is the hinge of the talk. Say it explicitly: **sharding doesn't just make joins inconvenient; it removes the tool that made global consistency checkable.**

---

### 7. Cassandra: the AP answer

Cassandra is what you build when you accept the trade. It is natively leaderless, partitioned, and replicated — and it **refuses cross-partition coordination by design**: no cross-partition transactions, no distributed joins, no foreign keys.

The bargain: linear write scaling and tunable quorum consistency, in exchange for giving up joins, cross-partition transactions, and ad-hoc query flexibility.

Everything downstream in the talk is Cassandra living with that bargain.

---

### 8. What Cassandra actually stores

It is **not** a document store with columns instead of JSON, and **not** an opaque blob store. It is a **partition-addressed, sorted wide-column engine** — effectively a two-dimensional key-value store.

- The **partition key** determines which node owns the data.
- Inside a partition, rows are ordered by optional **clustering columns**.
- A **column** is a single typed datum in a row. Columns are sparse — different rows can have different columns. That sparseness is what "wide-column" means.
- Storage is an **LSM tree**: writes go to a commit log and an in-memory memtable, flush to immutable **SSTables** sorted on disk, and compaction merges them in the background. Writes are cheap (append-only, no read-before-write); the cost shows up as read and write amplification during compaction.

**The performance model depends entirely on the query supplying the partition key.** You design the table around the query, not the entity.

---

### 9. Two orthogonal axes

This deserves its own diagram.

**Axis 1 — Partitioning.** *Who owns this key?* Scales capacity and write throughput. In Cassandra, the partition key maps to placement via the token ring (vnodes/tablets).

**Axis 2 — Replication.** *How many copies of each partition, and how many must agree?* Buys availability, durability, read scale. In Cassandra, **replication factor** is set per keyspace, and can differ per table and per datacenter.

The picture: **many partitions, each stored on M replicas.** The quorum question (`R + W > M`) is asked *inside each partition's replica set*, never globally.

**Imprecision to avoid:** don't say "N partitions" as if N is fixed. A partition is a data unit defined by the partition key; the count is a function of your data and key cardinality and changes as data grows. What's fixed is the token ring mapping. Say "many partitions, each replicated M times."

**Failure handling splits along the same two axes.** A node failure affects every partition it hosts, and those partitions' replica groups must compensate. Cassandra does this with **hinted handoff** (temporary writes held for a down replica), **read repair** (fixing stale replicas on read), and **anti-entropy repair** (background Merkle-tree comparison). That's the convergence machinery operating *inside* the replica group — distinct from the placement problem.

---

### 10. Consistency levels = the C/A dial

Cassandra exposes the trade at **query time**, per operation:

`ONE`, `TWO`, `THREE`, `QUORUM`, `ALL`, `LOCAL_QUORUM`, `EACH_QUORUM`, `ANY`

The docs frame this explicitly as a per-operation trade-off between consistency and availability, built on the `R + W > N` mechanism. ScyllaDB documents the same idea in operational language: a consistency level is a **dynamic value set by the client per operation**, dictating how many replicas must acknowledge before the coordinator returns success, and stronger settings mean more acknowledgements and lower chance of inconsistent results, at the cost of speed.

`LOCAL_QUORUM` is the practical setting for multi-DC deployments: majority *within the local datacenter's* replicas, so you don't pay cross-region latency for every write.

**Contrast worth a slide:** where the quorum lives in the design differs by system.

- **Dynamo-style** (Cassandra, ScyllaDB, Riak) — a runtime, per-operation dial, chosen by the client.
- **Raft-style** (CockroachDB, YugabyteDB, FoundationDB) — a fixed design-time majority per range/partition group. You don't dial it per query; the system pays coordination cost uniformly in exchange for strict serializability.

Same two-axis architecture, two different consistency philosophies. That's a better slide than "quorum is always a dial."

---

### 11. CAP, then PACELC

**CAP:** in a distributed system experiencing a **network partition**, you cannot simultaneously guarantee **Consistency** (every read sees the latest write) and **Availability** (every request gets a non-error response). Since partitions are unavoidable, the real choice is **CP** (sacrifice availability to stay consistent) or **AP** (stay available, serve possibly stale data).

**The framing to state explicitly: P was never optional.** It's not a knob you set; it's a fact of running on a network. The "choice" is only ever what you do *when* it happens — which is why it's misleading to describe a system as "CP" or "AP" as though that were a feature list.

**PACELC** is the sharper 2026 framing: if **P**artition, choose **A** or **C**; **E**lse, in normal operation, choose **L**atency or **C**onsistency. Even with a healthy network, strong consistency costs latency, because a write waits for enough replicas to acknowledge. That's why the quorum formula matters in the everyday case, not just during failures.

---

### 12. Cassandra's transactions and joins

**Transactions — three mechanisms, none general-purpose:**

- **Logged batches** — atomicity only *within a single partition*. All-or-nothing if every statement targets the same partition key. Atomic but **not isolated**: concurrent operations can interleave. So: "all writes land or none do, within one partition," with no isolation.
- **Lightweight transactions (LWT)** — linearizable compare-and-set for a *single partition*, via Paxos. `INSERT ... IF NOT EXISTS` gives serializable-level isolation for one row/partition. Costs four round trips coordinator↔replicas, and **cannot be combined with batches** — LWT's isolation requirement is incompatible with batch non-isolation.
- **Accord transactions** *(newer — verify current GA status before citing)* — a protocol providing general-purpose ACID across multiple partitions and keys. Worth a footnote as the exception that proves the rule: Cassandra added ACID as an opt-in layer on top of its architecture rather than rebuilding the core around it.

Practical pattern in the classic model: **check-then-batch** — `SELECT` to validate, logged `BATCH` to write atomically, accepting a race window between the two.

**Joins — it doesn't.** No joins, no foreign keys. Official position: "You cannot perform joins in Cassandra. If you have designed a data model and find that you need something like a join, you'll have to either do the work on the client side, or create a denormalized second table that represents the join results for you."

The alternative is **query-driven denormalization**: one table per query pattern, data duplicated across tables so every query is a single-partition read. Cost: redundancy and write amplification. Benefit: no query ever coordinates across nodes.

**Joins are pushed to the application or eliminated at write time.**

---

### 13. How Cassandra fails to be completely ACID

Not uniform across the four letters — **AID at row/partition scope, C only in a qualified sense.**

- **Atomicity — partial.** Single-row writes are atomic. Multi-row/multi-partition atomicity is absent without a same-partition batch. Critically, **no rollback across replicas**: if a write succeeds on one replica and fails on another at `QUORUM`, Cassandra reports failure to the client but does not undo the successful replica's write. No cluster-spanning undo log.
- **Isolation — row-level only.** A reader can't see a partially written row. But there is **no multi-statement isolation**; concurrent batches interleave. LWT gives isolation for one partition, not across partitions or a batch.
- **Durability — at the replica level.** Commit log + memtable before acknowledgement, so a single replica's write survives crash. But that's durability of the *local write*, not of a *committed transaction across the cluster* — there is no cluster-wide commit point to be durable.
- **Consistency — the qualified letter.** Cassandra cannot offer ACID's "C" because it has no cross-partition invariants, no foreign keys, and no global commit point. What it offers instead is **tunable convergence**: not "the database is always in a valid state" but "if you wait and reconcile, replicas converge."

**The canonical example:** moving money between two accounts. The invariant is that the total balance is unchanged. Enforcing it requires reading both accounts (cross-partition) and committing atomically. Cassandra can't, so it can't provide the "C" that example needs.

Cassandra's own docs make the link explicit: because it "does not support joins or foreign keys," it "consequently does not offer consistency in the ACID sense."

---

### 14. Precision beat: is "partially ACID" coherent?

**Answer: not in a formal sense — and the imprecision is worth naming on a slide, because it's where a lot of NoSQL marketing lives.**

Two separate questions get conflated:

1. **Does ACID require the relational model?** No. Atomicity, isolation, durability are independent of data model. A 2022 IEEE paper calls it a "misconception" that the relational model requires ACID; LWN puts it bluntly: "ACID has nothing to do with relational algebra." There is no logical contradiction in a non-relational system providing *some* ACID guarantees.

2. **Can the "C" be delivered without the mechanisms the relational model provides?** Largely no. In the relational world, "consistency" is defined by **declarative, global invariants** — primary keys, foreign keys, CHECK constraints, the relational structure itself. The database can enforce them because it has a single commit point and a join-capable engine to evaluate whether the invariant holds across all affected rows. Remove joins and the global commit point, and you've removed the enforcement machinery, not just the syntax.

**Formally:** ACID is a property of a *transaction*, and a transaction satisfies the set or it doesn't. There's no formal "50% ACID transaction." The dbdebunk project lists "NoSQL databases are partially ACID compliant" among the misconceptions it exists to debunk.

**The precise framing** comes from the **Highly Available Transactions** line of work (Bailis et al.): ACID is not a monolith; there's a spectrum of isolation levels and transactional guarantees, and even systems that call themselves "ACID" often default to weak isolation that violates strict serializability. CAP is frequently misread as a broad result about ACID, when it formally concerns **linearizability**, a specific consistency model.

**Slide line:**

> Cassandra doesn't offer "partial ACID" formally. It offers a **specific subset of transactional guarantees** — partition-level atomicity, row-level isolation, local durability — and explicitly declines the global "C." That "C" is the promise that a transaction preserves application invariants across the whole dataset, and enforcing it needs exactly what Cassandra gave up: joins to evaluate cross-entity predicates, foreign keys to declare them, and a global commit point to make them atomic. The relational model doesn't *define* ACID, but it makes the "C" tractable. Without it, "consistency" collapses into "replicas eventually converge" — a different promise entirely.

---

### 15. The turn: if you've given up transactions and joins, do you really need a table?

Cassandra's answer: **yes, but a table redefined.** Not a normalized relation with invariants — a **query-shaped, denormalized partition**. Once you accept that the table is a pre-joined materialized view keyed by access pattern, the next question is natural.

If the unit is no longer *a row in a relation* but *an aggregate fetched by key*, why impose a schema at all?

That's the door to document stores and blob stores.

---

### 16. Three storage shapes

**Document stores** (CouchDB, Couchbase, Firestore, DocumentDB) — self-describing JSON/BSON trees. The unit is a whole aggregate: a user profile, a catalog entry. Access pattern is "fetch or update this entire document." Give up cross-document joins and (historically) cross-document ACID. Indexes can be built on any field inside the document.

**Wide-column stores** (Cassandra, ScyllaDB, HBase, Bigtable) — sparse rows with dynamic columns inside partitions. Access pattern is "range scan within a partition." Give up ad-hoc queries, joins, non-key filtering. You design the table around the query.

**Blob stores** (S3, Azure Blob, object storage) — opaque byte sequences addressed by `(bucket, key)`. The value is never queried or indexed, only stored and retrieved whole. Not a database in the query sense: durable, scalable bucket for large binary objects, partial updates typically impossible (replace whole object).

**The clean distinction between the last two:** a document store's value is **indexable and partially updatable**; a blob store's value is **opaque and the key must be known to retrieve it**. Wide-column sits between — more structure than a blob, less query surface than a document store.

---

### 17. Cross-host joins: what the current best answer actually is

Not a single query technique. A two-tier strategy.

**Tier 1 — design it away (co-location).** If two tables are always joined on a key, shard both on that key. Matching rows land on the same node; the distributed join becomes a local join. Implementations: **YugabyteDB** colocated tables / tablegroups; **Citus** co-located distributed tables; **Alibaba PolarDB-X** cost-based optimizer prioritizing co-located joins. Trade-off: you constrain schema design — you effectively get one chance to pick the shard key.

**Tier 2 — query-time data movement, chosen by a cost-based optimizer.**

- **Broadcast join** — one side is small (dimension/lookup table). Send a full copy to every node holding a shard of the large table. ClickHouse and Huawei DDM call these broadcast/replicated tables; Citus calls them **reference tables**.
- **Shuffle (redistribution) join** — large-to-large, neither side small. Re-partition both tables by join key across the network so matches land together. Most expensive: network transfer, serialization, remote I/O. Last resort.

**2026 frontier — making the fallback less painful** *(research-stage; verify before asserting numbers)*:

- **CockroachDB locality-optimized lookup join** — resolve locally first, issue remote lookup only if needed. Reported large reductions in remote lookups when access is mostly local.
- **Bala-Join** — adaptive hash join for geo-distributed SQL, balancing communication and computation dynamically; benchmarks reported at 25–61% throughput improvement over standard distributed hash join.
- **PAC-Tree** — hierarchical data placement: replicate fact tables with diverse distribution keys at an upper level to improve co-location, fine-grained partitioning below for intra-shard data skipping; reported up to 45.7% latency reduction.

**Slide line:**

> The best answer to a cross-shard join is to not have one. Primary strategy is **design-time co-location**. When unavoidable, a cost-based choice between **broadcast** (small table) and **shuffle** (large tables). 2026 work makes the fallback smarter — adaptive and locality-aware — but it remains a costly compromise next to a co-located design.

---

### 18. The wider example set (all open, all runnable)

Keep the classics, add the 2026 material.

**Classics — what they taught us:**

- **CouchDB** — multi-master replication, multiple sources of truth. Maintenance mode; 3.5.3 was primarily a security release, and a 4.0 effort resurfaced after an earlier FoundationDB port was abandoned. Still a valid design lesson; no longer where innovation happens.
- **Riak** — Dynamo-style availability + built-in CRDTs. Basho collapsed in 2017; bet365 bought the IP and open-sourced the enterprise features; development continues as **OpenRiak** under the Erlang Ecosystem Foundation. CRDT data types still present, but Riak 4.0 work on object merging "may change the future support status of CRDT data-types." Excellent case study, tiny ecosystem.
- **CockroachDB / YugabyteDB** — distributed SQL that pays the coordination cost to keep serializable transactions across regions. **Note the license split:** CockroachDB core is BSL/source-available; **YugabyteDB is Apache 2.0** and tells nearly the same story. Under the no-proprietary constraint, lead with YugabyteDB.

**2026 additions, each with one specific trade-off:**

- **ScyllaDB** — same API, different engine. C++ rewrite of Cassandra, shard-per-core; tablet-based scaling benchmarked well above Cassandra's vNode-based scaling; goes beyond Cassandra compatibility with search, CDC, object-storage integrations. Trade-off: API compatibility vs storage-engine innovation — you keep CQL and the data model, accept a different operational model and a smaller ecosystem.
- **SurrealDB** — multi-model convergence. Documents, graphs, vectors, relational tables, time series, geospatial in one engine, with ACID across every model and a single query language. Directly challenges polyglot persistence: instead of Mongo + Neo4j + a vector DB, accept a younger engine for transactional consistency across models. **Verify the current license before putting it on a slide** — it has moved over time.
- **Valkey** — open governance. Community fork of Redis after the license change; BSD; now includes full-text search, aggregation, vector similarity, Bloom filters, and is targeting semantic caching / RAG. Trade-off: proprietary feature velocity vs vendor-neutral governance.
- **One open vector DB — Milvus, Qdrant, or Weaviate** — the specialization trade-off. Milvus for distributed scale-out architecture; Qdrant for single-binary Rust + heavy filtering; Weaviate for built-in hybrid BM25+vector. Contrast against `pgvector` or Valkey's vector search for the **integration vs specialization** argument.
- **Neo4j** — index-free adjacency vs horizontal scale-out, now with vector search on nodes, Cypher 25 / GQL alignment, GraphRAG features. Note: GPLv3 community edition / commercial enterprise — say which you mean.
- **FoundationDB** — the opposite extreme from tunable quorum: Apache 2.0, no knobs, strict serializable transactions, documented 5-second transaction limit. Good slide on why "just add Raft" isn't free.
- **RethinkDB** — if the talk needs a *document* store with tunable consistency. Open source, horizontally scalable, `write_acks` per table, selectable read mode; Jepsen confirms linearizable single-key ops under majority reads and writes, default reads may be stale. **Caveat:** maintenance velocity is low — latest tag 2.4.4 (late 2024), 2.4.5 builds in newer distro repos, commits still landing. Footnote it.

---

## Reference: example database matrix

| System | Shape | Partition axis | Replication / consistency | License | The trade-off it illustrates |
|---|---|---|---|---|---|
| PostgreSQL | Relational | (single node / via extensions) | Synchronous or async streaming; single writer | PostgreSQL License | The baseline: ACID via one commit point |
| Cassandra | Wide-column | Partition key → token ring | RF per keyspace; per-query consistency levels | Apache 2.0 | C-vs-A as a runtime dial |
| ScyllaDB | Wide-column | Shard-per-core, tablets | Same model, different engine | AGPL / source-available (verify) | API compatibility vs engine rewrite |
| Riak | KV / wide-column | Consistent hashing | N/R/W per bucket; CRDTs | Apache 2.0 (OpenRiak) | Convergence without coordination |
| CouchDB | Document | Shard ranges | Multi-master, revision trees | Apache 2.0 | Multiple sources of truth |
| RethinkDB | Document | Shard + replica per table | `write_acks` per table | Apache 2.0 | Document model + tunable consistency |
| CockroachDB | Distributed SQL | Range-based | Fixed Raft majority per range | BSL (source-available) | Paying coordination cost for serializability |
| YugabyteDB | Distributed SQL | Hash/range, colocated tables | Raft per tablet | Apache 2.0 | Same story, fully open |
| FoundationDB | Ordered KV | Sharded by key range | Fixed, strict serializable | Apache 2.0 | No knobs at all |
| SurrealDB | Multi-model | (verify) | ACID across models | Verify | Convergence of data models |
| Valkey | KV + search/vector | Cluster slots | Async + wait | BSD | Open governance |
| Milvus / Qdrant / Weaviate | Vector | Shard/segment | Configurable | Apache 2.0 / BSD-family | Specialization vs integration |
| Neo4j | Graph | (clustering) | Raft-based | GPLv3 community / commercial | Index-free adjacency vs scale-out |

---

## Reference: the two axes

```
        REPLICATION AXIS  (how many copies, how many must agree)
        M = 1        M = 3, W=1        M = 3, W=2 (QUORUM)      M = 3, W=3 (ALL)
          |             |                    |                       |
P   ┌─────┼─────────────┼────────────────────┼───────────────────────┤
A   │     |             |                    |                       |
R 1 │  single      fast writes,         R+W>M holds:          slowest,
T   │  node        stale/rolled-back    strong reads          zero tolerance
I   │              reads possible        (if R=2)              for loss
T   │
I 10│  ...         ...                  ...                   ...
O   │
N 100│ ...         ...                  ...                   ...
    └─────────────────────────────────────────────────────────────
```

The quorum question (`R + W > M`) is asked **inside each partition's replica set**, never globally. Whether it is a per-query dial (Dynamo-style) or a fixed majority (Raft-style) is a separate decision layered on top.

---

## Things to verify before presenting

- **Cassandra Accord** — current release status and whether it should be "new in 6.0" or "available."
- **ScyllaDB license** — AGPL vs source-available has shifted; confirm before the slide.
- **SurrealDB license** — has moved over time; do not assert "open source" without checking.
- **All benchmark numbers** — MongoDB 9.0 throughput claims, CockroachDB v26.x cluster/tpmC figures, ScyllaDB tablet scaling multiples, Bala-Join and PAC-Tree percentages. These are vendor or paper claims; present as "reported," not as measured fact.
- **RethinkDB** — confirm current release state if you use it; frame as maintained-but-slow.

---

## Deliberately dropped, and why

| Dropped | Reason |
|---|---|
| MongoDB | SSPL; never added an open option |
| FerretDB as "open MongoDB" | Postgres proxy — proves API portability, not the design |
| DynamoDB | Managed service only; internals unverifiable |
| Pinecone | Service only, no self-hosted path |
| "N partitions" as fixed | Imprecise — partition count is data-dependent |
| "Partially ACID" as a category | Formally incoherent; replace with "specific subset of guarantees" |
| CAP as "pick two of three" | P is not optional; use CAP-then-PACELC |
```

The two things I'd flag as most worth tightening before you build slides: the **"partially ACID" precision beat (slide 14)** is the strongest intellectual moment in the deck and deserves real screen time, and the **slide 12/13 pair** should stay adjacent — the mechanism and its failure modes read much better as one argument than as two slides.
