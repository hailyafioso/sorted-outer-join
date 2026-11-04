"""Align sorted iterables by key, using one lookahead item per input.

Adapted from Taylor Sather's join proposal for boltons:
https://github.com/mahmoud/boltons/pull/43
See LICENSE for redistribution terms.
"""


def join(iterables, key=None, fill=None):
    """Yield tuples aligning the next matching keys from sorted inputs.

    Inputs must be sorted in ascending key order. Duplicate keys are paired
    in input order, without a Cartesian product. Missing items use *fill*.
    *key* defaults to the identity function and is called once per item.
    """
    if key is None:
        key = lambda value: value
    elif not callable(key):
        raise TypeError("expected callable key function")

    try:
        iters = [iter(source) for source in iterables]
    except TypeError:
        raise TypeError("expected an iterable of iterables") from None

    missing = object()
    vals = [missing] * len(iters)
    keys = [missing] * len(iters)
    advance = range(len(iters))

    while True:
        for index in advance:
            try:
                value = next(iters[index])
            except StopIteration:
                vals[index] = keys[index] = missing
            else:
                vals[index] = value
                keys[index] = key(value)

        active = [index for index, value in enumerate(vals) if value is not missing]
        if not active:
            return

        first = min(active, key=keys.__getitem__)
        least = keys[first]
        advance = [index for index in active if index == first or keys[index] == least]
        matched = set(advance)
        yield tuple(value if index in matched else fill
                    for index, value in enumerate(vals))
