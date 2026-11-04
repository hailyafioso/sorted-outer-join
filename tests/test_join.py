import itertools
import unittest

from sorted_outer_join import join


class JoinTests(unittest.TestCase):
    def test_original_three_input_example(self):
        expected = [(0, 0, None), (1, 1, None), (2, 2, None), (3, 3, None)]
        expected += [(4, None, None)]
        expected += [(value, None, value) for value in range(5, 10)]
        expected += [(None, None, value) for value in range(10, 15)]
        self.assertEqual(list(join([range(10), range(4), range(5, 15)])), expected)

    def test_custom_key_advances_and_finishes(self):
        left = [(1, "left"), (3, "left")]
        right = [(1, "right"), (2, "right")]
        rows = join([left, right], key=lambda item: item[0])
        self.assertEqual(list(itertools.islice(rows, 4)), [
            ((1, "left"), (1, "right")),
            (None, (2, "right")),
            ((3, "left"), None),
        ])
        self.assertEqual(list(rows), [])

    def test_no_inputs(self):
        self.assertEqual(list(join([])), [])

    def test_empty_inputs(self):
        self.assertEqual(list(join([[], [], []])), [])
        self.assertEqual(list(join([[], [1, 2], []])), [
            (None, 1, None), (None, 2, None),
        ])

    def test_none_is_a_real_value(self):
        missing = object()
        rows = join([[None, 2], [0]], key=lambda item: 0 if item is None else item,
                    fill=missing)
        self.assertEqual(list(rows), [(None, 0), (2, missing)])

    def test_duplicate_keys_pair_in_input_order(self):
        self.assertEqual(list(join([[1, 1, 1, 2], [1, 1, 3]])), [
            (1, 1), (1, 1), (1, None), (2, None), (None, 3),
        ])

    def test_key_is_evaluated_once_per_item(self):
        seen = []

        def key(value):
            seen.append(value)
            return value[0]

        left = [(1, "left"), (4, "left")]
        right = [(2, "right"), (3, "right")]
        self.assertEqual(len(list(join([left, right], key=key))), 4)
        self.assertCountEqual(seen, left + right)

    def test_iterators_are_not_read_ahead_after_yield(self):
        seen = []

        def source():
            for value in range(3):
                seen.append(value)
                yield value

        rows = join([source(), [0, 2]])
        self.assertEqual(seen, [])
        self.assertEqual(next(rows), (0, 0))
        self.assertEqual(seen, [0])
        self.assertEqual(next(rows), (1, None))
        self.assertEqual(seen, [0, 1])

    def test_infinite_inputs_can_be_consumed_incrementally(self):
        rows = join([itertools.count(0, 2), itertools.count(1, 2)])
        self.assertEqual(list(itertools.islice(rows, 4)), [
            (0, None), (None, 1), (2, None), (None, 3),
        ])

    def test_input_container_can_be_an_iterator(self):
        self.assertEqual(list(join(iter([iter([1]), iter([2])]))), [
            (1, None), (None, 2),
        ])

    def test_invalid_key(self):
        with self.assertRaisesRegex(TypeError, "callable key"):
            list(join([[1]], key=42))

    def test_invalid_iterable(self):
        for value in (42, [42]):
            with self.subTest(value=value):
                with self.assertRaisesRegex(TypeError, "iterable of iterables"):
                    list(join(value))

    def test_input_errors_are_preserved(self):
        def broken():
            yield 1
            raise RuntimeError("source failed")

        rows = join([broken()])
        self.assertEqual(next(rows), (1,))
        with self.assertRaisesRegex(RuntimeError, "source failed"):
            next(rows)


if __name__ == "__main__":
    unittest.main()
