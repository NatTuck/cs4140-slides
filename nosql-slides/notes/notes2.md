Here is the outline for the rest of the deck, picking up after the cross-host joins slide. It keeps every example within the **open, runnable** constraint, handles the license shifts you need to know about (CockroachDB, ScyllaDB, ArangoDB, MinIO), and gives document databases the heavy coverage the narrative has been building toward.

---

# NoSQL Databases — Rest of Deck Outline

**Picking up from:** slide 17 (cross-host joins). The arc so far has established Postgres/ACID → the single commit point → multi-master difficulty → sharding → Cassandra’s two axes → CAP/PACELC → the precision beat on “partial ACID.” The remaining slides answer: *what other shapes exist once the table is no longer the unit, and what happens when someone rebuilds the commit point anyway?*

---

## Part V — More wide-column points (slides 18–21)

### Slide 18 — HBase: the CP wide-column point

**Slide message:** Same Bigtable data model as Cassandra, opposite consistency choice and opposite operational coupling.

- HBase is an Apache 2.0, distributed, versioned, column-oriented store modeled after Bigtable.
- Architecture: **dedicated master and region-server roles**, backed by **HDFS**. This is the structural difference from Cassandra’s peer-to-peer, no-dedicated-node design.
- Consistency: **strong consistency by default**, not eventual. The trade-off table is clean: HBase = strong consistency, moderate write throughput, moderate latency, weaker cross-region replication story; Cassandra = eventual consistency, high write throughput, low latency, strong cross-region replication story.
- **Speaker note:** HBase is the slide that proves the wide-column data model does **not** dictate the CAP choice. Cassandra chose AP; HBase chose CP. The data model is shared; the coordination philosophy is not.
- **2026 status:** actively maintained; 2.5.15 released June 2026.

### Slide 19 — Accumulo: cell-level security, and what it costs

**Slide message:** A wide-column store can buy a guarantee the others do not offer — at a steep operational price.

- Accumulo is an Apache 2.0 sorted, distributed key-value store based on Bigtable.
- Differentiator: **fine-grained access control down to the individual cell** — something HBase does not provide — plus the ability to handle cell values larger than memory.
- Operational cost: deep Java expertise, careful cluster management, and a **HDFS dependency** that can cascade into unavailability if the NameNode fails. It inherits HDFS’s lack of graceful degradation.
- **Slide line:** Accumulo is the “security vs operational fragility” point in the wide-column family. You can buy cell-level authorization, but you accept a much narrower operational envelope.

### Slide 20 — Kudu: the analytics/random-access hybrid

**Slide message:** Not every wide-column design point is about CAP. Kudu is about **storage format and workload**.

- Kudu is Apache 2.0, columnar, and designed to **fuse fast columnar scans (Parquet/ORC-like) with low-latency random row access** — the thing pure HDFS-based analytics engines and pure HBase-style stores each fail to do well.
- Trade-off: **not as fast as HDFS at bulk batch scans, not as fast as HBase at pure random reads/writes**, but it sits in the middle for **real-time analytics on mutable data**.
- It does **not** offer multi-row transactional APIs — it is not a replacement for a relational transaction boundary.
- **Slide line:** Kudu belongs on a **workload axis**, not a CAP axis. It shows that “wide-column” is a family of storage engines, not a single consistency story.

### Slide 21 — Riak: convergence without quorum (CRDTs)

**Slide message:** This is the initial-reference example that took the *other* path to convergence — not quorum, not transactions, but data types that merge.

- Riak is a Dynamo-style, leaderless key-value store with **built-in CRDT data types** (counters, sets, maps, registers).
- The design point: instead of `R + W > N` quorum coordination or a global commit point, **replicas converge by merging CRDT state**. This is eventual consistency with a mathematical convergence guarantee for the CRDT-typed values, rather than last-write-wins per column.
- **2026 status and license:** development continues as **OpenRiak** under the Erlang Ecosystem Foundation, Apache 2.0. CRDT data types are still present, but the project has signaled that Riak 4.0 object-merging work “may change the future support status of CRDT data-types” — footnote this.
- **Slide line:** Riak is the third answer to divergence. Cassandra converges by quorum and last-write-wins; CouchDB converges by retaining revision branches; Riak converges by **mergeable data types**. Each is a different position on how much coordination you are willing to pay for.

### Slide 22 — Wide-column family matrix (one slide, four columns)

| System | License | CAP posture | Coordination model | The specific trade-off |
|---|---|---|---|---|
| **Cassandra** | Apache 2.0 | AP (tunable) | Leaderless, per-query quorum | Consistency as a runtime dial |
| **HBase** | Apache 2.0 | CP | Master + region servers, HDFS | Strong consistency, heavier ops coupling |
| **Accumulo** | Apache 2.0 | CP | Master + tablet servers, HDFS | Cell-level security at the cost of fragility |
| **Kudu** | Apache 2.0 | (workload axis) | Raft-replicated tablets | Columnar scans + random access, no multi-row txns |
| **Riak** | Apache 2.0 (OpenRiak) | AP | Leaderless, CRDT convergence | Mergeable types instead of quorum |

**Speaker note:** This is the slide that answers “is Cassandra the only example?” No — it is the **AP, peer-to-peer point**. The family contains CP, security-focused, analytics-focused, and CRDT-focused points, all open and runnable.

**License footnote:** ScyllaDB is **no longer the clean open example**. ScyllaDB OSS 6.2 was the final AGPL release; current releases are **source-available** under the ScyllaDB Software License, with free use capped at 10 TB / 50 vCPUs per organization. If you mention ScyllaDB, put it on a “license caution” slide, not the main matrix.

---

## Part VI — Document databases (slides 23–34)

This is the heavy section. The narrative payoff is that document stores answer the “do you need a table?” question with a **design principle** — the aggregate — rather than with an absence.

### Slide 23 — What a document database actually is

**Slide message:** The document is the **aggregate**, not “JSON instead of rows.”

- The defining property is not the format. It is that a whole nested structure is **one addressable, atomically-mutable value**.
- Domain examples: user profile with embedded addresses, product with variants, order with line items.
- **The structural reason documents fit this:** you gave up joins, so you gave up reassembling a relation at read time. The document store’s answer is: **do not decompose in the first place**. Ship the aggregate whole.

### Slide 24 — The relocated commit point

**Slide message:** Document databases did not abandon ACID. They **moved the commit point to the document**.

- Single-document writes are atomic and usually durable. CouchDB gives per-document atomicity via MVCC; RethinkDB guarantees single-document atomicity across fields.
- What you lose is **cross-document atomicity** — unless the system added it later, at a cost.
- The design rule that follows: **if two pieces of data must be updated atomically, they belong in the same document.**
- **Failure mode to name:** if the aggregate boundary is wrong, you discover it when you need a multi-document transaction — and then you are running a document database as a worse relational database. Most production document-store pain traces back to this.

### Slide 25 — Schema-on-read, and why “schemaless” is a lie

**Slide message:** The schema moved into the application; it did not disappear.

- **Schema-on-write** (relational): the database rejects malformed data at insert time.
- **Schema-on-read** (document): the database accepts anything; the application interprets it.
- Every mature document store eventually re-added validation — the tell:
    - **CouchDB**: `validate_doc_update` functions, JavaScript that runs on write and rejects by throwing.
    - **RavenDB**: schema validation as a configuration concern.
- **Slide line:** “Schemaless” describes the **absence of a centralized constraint**, not the absence of structure. What you actually get is **schema drift**: multiple historical shapes coexisting in one collection, with the application carrying the compatibility logic.

### Slide 26 — CouchDB: multiple sources of truth, taken seriously

**Slide message:** This is the initial-reference example that made replication the *primary* design constraint, not an afterthought.

- **Multi-master by default**: any replica accepts writes; replication is pairwise, resumable, bidirectional, with no primary.
- Every document carries a **revision tree**, not a single version number — because concurrent edits create branches.
- On replication, CouchDB compares revision trees, transfers only missing revisions, and **deterministically** picks a winner (highest revision count, then lexicographic revision ID).
- **The losers are not deleted.** They are retained and accessible via `_conflicts`. Nothing is silently lost; the application can inspect and reconcile.
- **2026 status:** Apache CouchDB 3.5.3 shipped October 2026; steady, well-understood technology, best when sync and availability matter more than ad-hoc query power.

### Slide 27 — PouchDB: offline-first at the edge

**Slide message:** The document model is what makes **partition tolerance at the client** tractable.

- PouchDB is a JavaScript document store that runs in the browser or Node and **speaks CouchDB’s replication protocol** — a browser and a server sync bidirectionally.
- Structural reason it works: a self-contained document has **no referential integrity to violate**. Syncing a relational row while offline risks dangling foreign keys; syncing an aggregate is just merging an aggregate.
- Combined with revision trees and retained conflicts, the client becomes a **genuine replica**, not a cache.
- **Slide line:** This is CAP’s P axis at the edge of the network, not just between datacenters — and it is the strongest argument that document databases are not “relational with nested rows.”

### Slide 28 — CouchDB map/reduce views: the index is the query plan

**Slide message:** A genuinely different indexing design point from “secondary indexes on fields.”

- The only index mechanism is an **incrementally maintained materialized view**, defined by a JavaScript `map` function.
- CouchDB runs the function over every document, sorts emitted key/value pairs into a **persistent B-tree on disk**, and updates it incrementally as documents change.
- Queries are **range scans over that B-tree** — fast and predictable, but only for questions the view was designed for.
- **Trade-off:** no ad-hoc queries, but incremental index maintenance and a durable index artifact, not an in-memory structure rebuilt on restart. This is the same “design around the access pattern” discipline as Cassandra, expressed through a **materialized function** rather than a partition key.

### Slide 29 — RethinkDB: the query subscribes to change

**Slide message:** A design point nobody else occupies — **push queries** as the primary contract.

- **Changefeeds** turn a query into a live stream: `r.table('orders').changes()` emits every insert, update, and delete; `r.table('orders').filter(...).changes()` emits only matching changes. The client holds a cursor, not a polling loop.
- Different contract from replication: not “sync the whole dataset” (CouchDB), not “send me the current value” (KV), but **“keep telling me what changed, incrementally.”**
- RethinkDB also has **tunable consistency** — `write_acks` per table (default `majority`), selectable read modes — so it is the document store that also carries the C-vs-A dial story. Jepsen confirmed linearizable single-key operations under majority reads and writes; default reads may be stale.
- **Caveat to footnote:** maintenance velocity is low. Last tagged release is 2.4.4 (December 2023), with only fixes and CI work since; commits still land. Present it as a design lesson, not a production recommendation.

### Slide 30 — RavenDB: ACID documents, non-transactional indexes

**Slide message:** The outlier that proves document stores *can* do multi-document transactions — by decomposing the problem differently.

- RavenDB is **fully ACID-compliant** and provides **multi-document transactions by default**, not as an opt-in bolt-on. License: **AGPLv3** for the server, MIT for client APIs.
- **The second interesting trade:** its **indexes are non-transactional and eventually consistent by design**. You get ACID on the documents, but a query served from an index may be stale relative to the write you just committed.
- **Slide line:** RavenDB decomposes consistency into **document consistency** (strong) and **index freshness** (eventual). That is a genuinely different decomposition from “transactions everywhere” or “transactions nowhere,” and it is worth a slide of its own.

### Slide 31 — OpenSearch: the inverted index is a different contract

**Slide message:** Same document unit, opposite index structure — and it changes what the database is *for*.

- OpenSearch is **Apache 2.0**, community-driven, under the Linux Foundation.
- **Inverted index**: term → list of documents. Optimized for **relevance-ranked retrieval**, where you do not know exactly what you are asking for.
- Contrast with CouchDB/RethinkDB: B-tree over a computed key, optimized for **exact and range lookups**, where you do know.
- Write cost: an inverted index touches many postings per document, so **writes are expensive and reads are flexible** — the inverse of the wide-column model.
- **Slide line:** The primary access pattern is “give me the top-k most relevant,” not “give me the document with this key.” That is a fundamentally different contract, and it explains why search engines exist as a separate category even though they store documents.

### Slide 32 — XML document databases: the other document model

**Slide message:** “Document” originally meant a *marked-up* document, and the model is genuinely different from JSON.

- **BaseX** (BSD) and **eXist-db** (LGPL) are open, runnable **native XML stores** with **XQuery** as the query language.
- Data model: ordered, mixed-content trees with schema defined by XSD/RELAX NG — not JSON objects.
- **Why this slide earns its place:** it reframes the audience’s assumption that document databases are a reaction to relational databases. The replication-and-sync problem was solved in document stores before the relational world cared about distribution; CouchDB’s design choices read differently once you know they inherit a 1989 Lotus Notes lineage rather than rebelling against SQL.

### Slide 33 — MongoDB and ArangoDB: license caution, and what “document” no longer means

**Slide message:** Two examples from the original brief that cannot be main-slide examples under the open-software constraint — and what that teaches.

- **MongoDB**: still **SSPL**, never added an open option. Present it as a **historical reference point** for single-document atomicity and the document model, not as a runnable example. If you need an open document API over a relational engine, **FerretDB** (Apache 2.0) exists — but it is a **translation proxy over PostgreSQL**, not a storage-engine replacement. It proves API portability, not design equivalence.
- **ArangoDB**: **no longer Apache 2.0**. As of version 3.12, the source moved to **BSL 1.1**, and the Community Edition is free only for **non-commercial/internal use with a 100 GiB dataset limit**. It is still the best example of a document store that **restored joins and graph traversal** (AQL supports document-to-document joins and graph traversals across a cluster), but it belongs on a **license-caution slide**, not the main matrix.
- **Slide line:** “Open document database” is now a narrower set than it was five years ago. CouchDB, PouchDB, RethinkDB, RavenDB, OpenSearch, BaseX, and eXist-db are the open points that remain.

### Slide 34 — What document databases teach

**Slide message:** The question was never “documents or tables.” It was **“what is the unit of atomicity, and who enforces the invariants that cross it?”**

- Document stores answer: **the aggregate, and the application.**
- Relational stores answer: **the transaction, and the database.**
- Everything else — JSON, joins, multi-document transactions, validation — is a configuration choice on top of that one decision.
- **Convergence note:** the boundary has blurred in both directions. PostgreSQL `JSONB` gives you a document column inside an ACID database with joins; **Gel** (Apache 2.0) puts a typed object model on a relational foundation; FerretDB/DocumentDB put a document API over PostgreSQL.

---

## Part VII — Key → blob stores (slides 35–37)

### Slide 35 — What a blob store actually is

**Slide message:** The floor of the access-depth hierarchy — and not a database in the query sense.

- A blob store maps `(bucket, key)` to an **opaque byte sequence**. The value is **never queried or indexed**, only stored and retrieved whole.
- Partial updates are typically impossible; you replace the whole object.
- Contrast with a document store: a document’s value is **indexable and partially updatable**; a blob’s value is **opaque**, and the key must be known to retrieve it.
- **Slide line:** Blob stores are the point where the database stops understanding the data at all. That is not a failure — it is the correct design for large immutable objects, backups, media, and data-lake payloads.

### Slide 36 — Open blob-store examples

**Slide message:** The open options exist, and the license landscape matters.

| System | License | Design point |
|---|---|---|
| **SeaweedFS** | Apache 2.0 | Fast distributed storage for blobs, objects, files, data lakes; O(1) disk seek; S3 API |
| **Garage** | AGPLv3 | S3-compatible, self-hosted, small-to-medium geo-distributed deployments |
| **Ceph** | LGPL 2.1/3.0 | Full distributed storage system (object, block, file) |
| **MinIO** | AGPLv3 | S3-compatible object store; **caveat:** the community edition was archived/EOL’d in 2026, and the main repo is archived as of April 2026 — footnote or avoid as a primary example |

- **Slide line:** SeaweedFS is the clean Apache-2.0 example for a blob/object store; Garage is the AGPL self-hosting example; Ceph is the heavyweight LGPL example. MinIO belongs on a “license and maintenance caution” footnote, not the main slide.

### Slide 37 — Why blob stores are the floor, not the destination

**Slide message:** Giving up joins does not force you down to `key → blob`. It opens a **spectrum of access depth**, and blob is the simplest point on it.

- The hierarchy: **blob** (opaque value) → **pure KV** (opaque value plus key-level addressing) → **wide-column** (partition key + clustering key, typed cells, range scans) → **document** (aggregate-level addressing, indexable fields) → **relational** (set-level addressing, joins, declarative invariants).
- Each step up buys more query surface and costs more coordination or structure.
- **Slide line:** The interesting design question is not “how do we get to blobs?” It is **“how much structure do we need to keep, and where do we put the transaction boundary?”**

---

## Part VIII — CockroachDB: the trade-off inverted (slides 38–41)

This is the capstone. CockroachDB was one of the initial reference examples — “the thing that exists when it shouldn’t.” It exists because it **pays the coordination cost Cassandra refused**.

### Slide 38 — How CockroachDB works

**Slide message:** A distributed SQL database that rebuilds a single logical commit point using consensus.

- Architecture: data is split into **ranges**, each replicated (typically three ways), and each range is a **Raft group** that elects a leader (a **leaseholder** for reads).
- SQL layer on top of a **transactional key-value store**; **serializable isolation by default**; **Postgres wire protocol**.
- **Hybrid logical clocks** provide global ordering without a single physical clock.
- **License caveat — must be on the slide:** CockroachDB moved from BSL/MIT to the **CockroachDB Software License (CSL)**; it is **source-available, not OSI open source** (non-production use is free). Under the deck’s constraint, it is a **design lesson**, not a runnable recommendation. Pair it with **YugabyteDB** (Apache 2.0) as the fully open implementation of the same Raft-per-tablet, distributed-SQL idea.

### Slide 39 — How it changes the trade-off

**Slide message:** The whole deck has been about what you give up when you distribute the commit point. CockroachDB is the system that **refuses to give it up** — and pays for it in a different currency.

- Cassandra’s answer: **remove the global commit point**, expose quorum as a per-query dial, give up joins and cross-partition transactions.
- CockroachDB’s answer: **rebuild the global commit point** as a Raft-replicated logical entity. Every range has a leader; every transaction gets a serializable order; every write pays the consensus round trip.
- **The currency it pays in:** **latency** (especially cross-region), **operational complexity** (Raft groups, leaseholders, range rebalancing), and **the license constraint** (source-available, not OSI).
- **The currency it buys with:** **ACID + horizontal scale + geo-replication** in one system — the thing the earlier slides said was “virtually impossible” with multi-master asynchronous replication.

### Slide 40 — The “thing that exists when it shouldn’t” — and its open twin

**Slide message:** CockroachDB is the counterexample that proves the rule: distributed ACID is possible if you are willing to pay coordination on every commit.

- The initial framing was right: it is the database that “shouldn’t” exist if you accept the standard trade-off. It exists because **Raft + range-level consensus** makes a single logical commit point survivable across failures.
- But the honest 2026 slide has to say: **the open implementation of this idea is YugabyteDB** (Apache 2.0), not CockroachDB. YugabyteDB uses Raft per tablet, distributed SQL, and PostgreSQL compatibility — the same “pay consensus for ACID at scale” design point, under an OSI license.
- **Slide line:** If you want the design lesson, CockroachDB is the clearest articulation of the idea. If you want the runnable, open example of the same idea, YugabyteDB is the one that satisfies the deck’s constraint.

### Slide 41 — Closing matrix: the whole deck in one slide

| Design point | Open example(s) | What it gives up | What it buys |
|---|---|---|---|
| Single-node ACID | PostgreSQL | Horizontal write scale | One commit point, joins, invariants |
| AP wide-column | Cassandra | Joins, cross-partition txns, global “C” | Tunable quorum, linear write scale |
| CP wide-column | HBase, Accumulo | Cassandra’s write throughput and cross-region AP story | Strong consistency, cell-level security |
| CRDT convergence | Riak (OpenRiak) | Strong consistency, ad-hoc queries | Mergeable types, leaderless availability |
| Document / aggregate | CouchDB, PouchDB, RethinkDB, RavenDB, OpenSearch | Cross-aggregate joins (mostly), some multi-doc txns | Aggregate atomicity, sync, push queries, search |
| Key → blob | SeaweedFS, Garage, Ceph | All query and indexing | Durable opaque object storage |
| Distributed SQL (consensus) | YugabyteDB (Apache 2.0); CockroachDB (CSL, design reference) | Latency on every commit, operational complexity | Serializable ACID + horizontal scale + geo-replication |

**Final slide line:**

> Every system on this slide is an answer to the same question: **where do you put the commit point, and what do you make the application pay for?** Postgres puts it on one node and gives you joins. Cassandra removes it and gives you a dial. CouchDB moves it to the document and gives you sync. Riak replaces it with mergeable types. CockroachDB/YugabyteDB rebuild it with consensus and charge you latency. Blob stores remove the question entirely. The design space is not a list of products — it is a list of **positions on that one trade-off**.

---

## Speaker notes: license reality check (put this in an appendix slide)

| System | Status | What to say |
|---|---|---|
| **CockroachDB** | CSL (source-available, not OSI) | Design lesson; pair with YugabyteDB for the open version |
| **ScyllaDB** | Source-available since 2025.1; OSS 6.2 was final AGPL | License-caution slide only |
| **ArangoDB** | BSL 1.1 since 3.12; Community Edition free only for non-commercial use ≤100 GiB | License-caution slide only |
| **MinIO** | AGPLv3; community edition archived/EOL’d in 2026 | Footnote or avoid; use SeaweedFS/Garage/Ceph instead |
| **MongoDB** | SSPL; never added an open option | Historical reference only |
| **RethinkDB** | Apache 2.0; last release 2.4.4 (Dec 2023), low velocity | Design lesson, not production recommendation |
| **CouchDB** | Apache 2.0; 3.5.3 October 2026 | Fully valid example |
| **HBase / Accumulo / Kudu / Cassandra / Riak** | Apache 2.0 | Fully valid examples |
| **RavenDB** | AGPLv3 (server) / MIT (clients) | Valid open example with a strong copyleft |
| **OpenSearch** | Apache 2.0 | Valid open example |
| **SeaweedFS / Garage / Ceph** | Apache 2.0 / AGPLv3 / LGPL | Valid open blob-store examples |

---

## One sequencing note

If time is tight, the slides I would protect are **26–27 (CouchDB + PouchDB)**, **30 (RavenDB)**, **31 (OpenSearch)**, **36–37 (blob stores)**, and **38–39 (CockroachDB)**. Those carry the argument: document databases make a real design choice rather than an absence, blob stores are the floor rather than the destination, and CockroachDB is the capstone that shows what happens when someone refuses the trade-off the rest of the deck accepted. The HBase/Accumulo/Kudu slides are excellent breadth, but they are the ones that can compress into a single matrix if the clock runs out.
