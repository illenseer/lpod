# traod aka TRAnslate Ordered Disjunctions

`traod` is a parser for Logic Programs with Ordered Disjunctions and translates
them into logic programs, which can be handled by `metalpod` or
[`asprin`](http://potassco.sourceforge.net/labs.html#asprin).

## Installation
It is recommended to install traod into a virtualenv, e.g.:

    virtualenv venv
    source venv/bin/activate

Install `traod`:

    python setup.py install

## Usage

    traod [OPTIONS] FILENAME

### Options:
`-b, --backend [metalpod|asprin]`
  Backend to solve LPOD instance.
  Default: `metalpod`

`-s, --strategy [pareto|incl|card]`
  Strategy for LPOD instance.
  Default: `pareto`

`-g, --generator [split|cabalar]`
  Generator for LPOD instance: Split programs or Cabalar translation.
  Default: `split`

## LPOD Syntax
The operator '×' for ordered disjunction is represented by ';;'.

An example for the notation of a LPOD:

    a ;; b :- c.
    d ;; e ;; f.
    c.
