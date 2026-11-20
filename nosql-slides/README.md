# One Commit Point

One lecture on why NoSQL exists. Not a survey of products — an argument with
examples attached.

The thesis, in one sentence: **the ACID transaction assumes a single commit
point, and a single commit point does not survive multiple writers across
machines.** Everything else — documents, wide columns, blobs, CRDTs,
consistency levels, CAP — is downstream of what a system chose to give up in
order to distribute that point, or to avoid needing one.

## Layout

- `index.qmd` — the deck (Quarto revealjs, 48 slides).
- `custom.scss` — the teal theme, plus `.beat`, `.claim`, `.ledger`, `.cap`,
  and the `.steps` rule that stacks stepped figures.
- `assets/fonts/` + `assets/fonts.css` — the bundled fonts, so the deck needs
  no network. See the comment at the top of `fonts.css` for why `@font-face`
  cannot live in `custom.scss`.
- `figs/svg.py` — drawing primitives, a text-width estimator, and the layout
  asserts (`fit()`, `region()`).
- `figs/model.py` — every value the figures draw and the slides quote.
- `figs/makefigs.py` — all 29 SVGs, from those values.
- `figs/check.py` — `make check-figs`: recomputes the arithmetic and asserts
  that every number printed on a slide still equals what the model computes.
- `figs/lint.py` — `make check`: notes on every slide, balanced divs, no
  orphan figures, one vocabulary for beat labels.
- `notes/` — the two source note files, unmodified.
- `REGISTER.patch` — the two edits that add this deck to the site. **Already
  applied**; kept as a record of what registration means.

## The story in five moves

1. A commit point is one decision — visible, durable, ordered — and Postgres
   implements it as one record in one log.
2. Having it twice is the problem: a lost reply and a retry give one
   transaction two commit points and no undo.
3. So you fork: converge later (AP), or wait for a majority (CP). That is CAP,
   and its "C" is not ACID's "C".
4. The join is what pays for sharding, and Cassandra deletes it on purpose.
5. Once the table is only a view, the point moves — into a document, into a
   bucket, or back behind a consensus group.

Each system gets the same four beats, labelled on the slide: **the problem**,
**the mechanism**, **the bill**, **the evidence**. The deck is written to be
read cold; the speaker notes are extra, not required.

## Numbers on the slides

| part | the number |
|---|---|
| quorum | six of nine `(W, R)` pairs for N = 3 hold; three do not |
| replica set | four frames; the hint is delivered exactly once |
| the table | six rows, three partitions, sparse cells |
| the LSM | twelve writes, three SSTables, **four places** for one read |
| the transfer | `100 + 50 = 150` before and after; `80 + 50 = 130` is reachable |
| the aggregate | three line items, totalling 75.75 |
| revision tree | four revisions, winner `3-*`, one branch retained as a conflict |
| the index | four documents, five `(tag, doc)` pairs, two shapes |
| consensus | **two round trips** before the client is told yes |
| the commit point | one record, three jobs, one instant of visibility |
| the retry | one logical transaction, **two** commit records, no undo |
| the transaction | a set of writes with exactly one outcome |
| CAP | three guarantees; Path A is AP and Path B is CP |
| the joins | four answers; shuffle is the expensive one |
| the design space | thirteen systems on two axes; one empty corner |

## Verify before presenting

Licensing bites, and the capstone is entirely about two systems' internals. The
table is the README's job, not a slide's.

| claim on the slide | check against | status |
|---|---|---|
| TiDB is Apache 2.0 | project LICENSE | TODO |
| YugabyteDB is Apache 2.0 | project LICENSE | TODO |
| TiDB defaults to repeatable read | TiDB docs, isolation levels | TODO |
| YugabyteDB defaults to serializable | YSQL docs, isolation levels | TODO |
| TiDB: one placement driver serves the timestamp (TSO), HA by Raft | PD docs | TODO |
| TiDB: Percolator 2PC, the primary lock is the decision | TiDB transaction docs | TODO |
| YugabyteDB: Raft per tablet, hybrid logical clocks, one status record | architecture docs | TODO |
| Cassandra Accord status | Cassandra release notes | TODO |
| the two round trips on the consensus slide | derived by `figs/model.py`, asserted by `check.py` | computed |

`make check` prints this list; a `TODO` means the deck is not ready to show.

## What was deliberately dropped

| dropped | why |
|---|---|
| A licence table on a slide | slide 41 makes the argument once; a table invites corrections and dates the deck in weeks |
| CockroachDB | its licence moved. It was the capstone example until it left, which is now the licence slide's own evidence |
| MongoDB, ArangoDB, ScyllaDB, MinIO, FerretDB, DynamoDB, Pinecone | not open, so not examples. Named nowhere except in the argument on slide 41 |
| HBase, Accumulo, Kudu, Riak as four slides | compressed to one: the family point survives, the catalogue does not |
| XML document stores, RethinkDB changefeeds | each needs a paragraph of history to earn its place |
| Vector databases, streams, time series | named in the closing slide as shapes not covered |
| Benchmark percentages | paper and vendor claims the deck would then have to defend |
| A lab handout | this is a conceptual overview, not project support |

## Rebuilding

```
make figs        # regenerate every SVG
make check       # the arithmetic, the deck's numbers, and the lint
make render      # build the deck
```

The figures are generated, not drawn by hand. Text in the SVGs uses a font
stack rather than the page's webfonts, so the deck works offline.

### A note on how the figures were verified

They could not be looked at while they were built, so the checking is
mechanical instead:

- `svg.Fig` records the boxes it draws and fails on `save()` if two overlap or
  if a string runs past the box it was given, using an advance-width estimate.
- `convert fig.svg -trim` is asserted to leave a margin, which catches content
  spilling off the canvas.
- A self-check inside `makefigs` compares the labels a figure draws against
  the data it drew them from. The first draft of `fig-cassandra-model` sorted
  partition keys as strings, so every bracket carried the wrong label — the
  kind of bug that is invisible to a compiler and obvious to a reader. The
  check is what would have caught it.
- One visual pass by a human is still owed. It has not happened.
