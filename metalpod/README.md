# metalpod

`metalpod` is a meta-programming and saturation based approach to solve
Logic Programs with Ordered Disjunctions. It is based on
[`metasp`](http://potassco.sourceforge.net/labs.html#metasp). It shares
`meta.lp` and `metaD.lp` with `metasp`, `metaO.lp`, where the optimization is
handled, is completely different.

## Usage
For a LPOD, e.g. `test.lp`:

    a ;; b ;; c :- p.
    d ;; e.
    p :- not q.
    q :- not p.
    :- a, d.

First generate an instance with `traod`, then create an meta program of it with
`clingo` and `reify` and solve it with `clingo` combined with `meta.lp`,
`metaD.lp` and `metaO.lp`:

    traod --backend metalpod --generator [split|cabalar] --strategy [pareto|incl|card] test.lp | \
    clingo --pre | \
    reify -c | \
    clingo -Wno-atom-undefined meta.lp metaD.lp metaO.lp - 0
