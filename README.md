# SortedJoin

Join sorted iterables by a shared key, keeping one lookahead item per input.

```python
from sorted_outer_join import join

left = [(1, "a"), (3, "c")]
right = [(2, "b"), (3, "d")]

for row in join([left, right], key=lambda item: item[0]):
    print(row)
# ((1, 'a'), None)
# (None, (2, 'b'))
# ((3, 'c'), (3, 'd'))
```

Copy `sorted_outer_join.py` into your project. Python 3.9 or later; no dependencies.

Each input must already be sorted by mutually comparable keys. Equal keys are
aligned in input order: repeated keys are paired one item at a time, rather than
expanded into a SQL-style Cartesian product. Missing items use `None`, or a
custom `fill` value. A key function is evaluated once for each item consumed.

```python
missing = object()
rows = join([[None], [0]], key=lambda item: 0, fill=missing)
assert list(rows) == [(None, 0)]
```

The iterator keeps O(number of inputs) items in memory and scans the input heads
for each output row. It does not read the remaining inputs into memory.

Run the tests:

```console
python -m unittest discover -s tests -v
```

Adapted from [Taylor Sather's sorted-join proposal for boltons](https://github.com/mahmoud/boltons/pull/43).
This version fixes advancement with custom keys, distinguishes missing items from
real `None` values, caches keys, and supports a custom fill value. The original
license is preserved in [LICENSE](LICENSE).
