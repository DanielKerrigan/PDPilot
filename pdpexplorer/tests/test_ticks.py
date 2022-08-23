"""
The code in this file is ported from d3-array.

https://github.com/d3/d3-array/blob/main/test/nice-test.js
https://github.com/d3/d3-array/blob/main/test/tickIncrement-test.js
https://github.com/d3/d3-array/blob/main/test/ticks-test.js

Copyright 2010-2022 Mike Bostock

Permission to use, copy, modify, and/or distribute this software for any purpose
with or without fee is hereby granted, provided that the above copyright notice
and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF
THIS SOFTWARE.
"""

import math
from pdpexplorer.ticks import nice, ticks, tick_increment

# tick_increment


def tick_increment_not_positive_count():
    assert tick_increment(0, 1, -1) == math.inf
    assert tick_increment(0, 1, 0) == math.inf


def tick_increment_inf_count():
    assert tick_increment(0, 1, math.inf) == -math.inf


def test_tick_increment():
    assert tick_increment(0, 1, 10) == -10
    assert tick_increment(0, 1, 9) == -10
    assert tick_increment(0, 1, 8) == -10
    assert tick_increment(0, 1, 7) == -5
    assert tick_increment(0, 1, 6) == -5
    assert tick_increment(0, 1, 5) == -5
    assert tick_increment(0, 1, 4) == -5
    assert tick_increment(0, 1, 3) == -2
    assert tick_increment(0, 1, 2) == -2
    assert tick_increment(0, 1, 1) == 1
    assert tick_increment(0, 10, 10) == 1
    assert tick_increment(0, 10, 9) == 1
    assert tick_increment(0, 10, 8) == 1
    assert tick_increment(0, 10, 7) == 2
    assert tick_increment(0, 10, 6) == 2
    assert tick_increment(0, 10, 5) == 2
    assert tick_increment(0, 10, 4) == 2
    assert tick_increment(0, 10, 3) == 5
    assert tick_increment(0, 10, 2) == 5
    assert tick_increment(0, 10, 1) == 10
    assert tick_increment(-10, 10, 10) == 2
    assert tick_increment(-10, 10, 9) == 2
    assert tick_increment(-10, 10, 8) == 2
    assert tick_increment(-10, 10, 7) == 2
    assert tick_increment(-10, 10, 6) == 5
    assert tick_increment(-10, 10, 5) == 5
    assert tick_increment(-10, 10, 4) == 5
    assert tick_increment(-10, 10, 3) == 5
    assert tick_increment(-10, 10, 2) == 10
    assert tick_increment(-10, 10, 1) == 20


# ticks


def test_ticks_start_equals_stop_non_positive_count():
    assert ticks(1, 1, -1) == []
    assert ticks(1, 1, 0) == []


def test_ticks_start_equals_stop_positive_count():
    assert ticks(1, 1, 1) == [1]
    assert ticks(1, 1, 10) == [1]


def test_ticks_non_positive_count():
    assert ticks(0, 1, 0) == []
    assert ticks(0, 1, -1) == []


def test_ticks_infinity_count():
    assert ticks(0, 1, math.inf) == []


def test_ticks_infinity_count():
    assert ticks(0, 1, math.inf) == []


def test_ticks_remainsin_domain():
    assert ticks(0, 2.2, 3) == [0, 1, 2]


def test_ticks():
    assert ticks(0, 1, 10) == [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    assert ticks(0, 1, 9) == [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    assert ticks(0, 1, 8) == [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    assert ticks(0, 1, 7) == [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    assert ticks(0, 1, 6) == [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    assert ticks(0, 1, 5) == [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    assert ticks(0, 1, 4) == [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    assert ticks(0, 1, 3) == [0.0, 0.5, 1.0]
    assert ticks(0, 1, 2) == [0.0, 0.5, 1.0]
    assert ticks(0, 1, 1) == [0.0, 1.0]
    assert ticks(0, 10, 10) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert ticks(0, 10, 9) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert ticks(0, 10, 8) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert ticks(0, 10, 7) == [0, 2, 4, 6, 8, 10]
    assert ticks(0, 10, 6) == [0, 2, 4, 6, 8, 10]
    assert ticks(0, 10, 5) == [0, 2, 4, 6, 8, 10]
    assert ticks(0, 10, 4) == [0, 2, 4, 6, 8, 10]
    assert ticks(0, 10, 3) == [0, 5, 10]
    assert ticks(0, 10, 2) == [0, 5, 10]
    assert ticks(0, 10, 1) == [0, 10]
    assert ticks(-10, 10, 10) == [-10, -8, -6, -4, -2, 0, 2, 4, 6, 8, 10]
    assert ticks(-10, 10, 9) == [-10, -8, -6, -4, -2, 0, 2, 4, 6, 8, 10]
    assert ticks(-10, 10, 8) == [-10, -8, -6, -4, -2, 0, 2, 4, 6, 8, 10]
    assert ticks(-10, 10, 7) == [-10, -8, -6, -4, -2, 0, 2, 4, 6, 8, 10]
    assert ticks(-10, 10, 6) == [-10, -5, 0, 5, 10]
    assert ticks(-10, 10, 5) == [-10, -5, 0, 5, 10]
    assert ticks(-10, 10, 4) == [-10, -5, 0, 5, 10]
    assert ticks(-10, 10, 3) == [-10, -5, 0, 5, 10]
    assert ticks(-10, 10, 2) == [-10, 0, 10]
    assert ticks(-10, 10, 1) == [
        0,
    ]


def test_ticks_reverse():
    assert ticks(1, 0, 10) == ticks(0, 1, 10)[::-1]
    assert ticks(1, 0, 9) == ticks(0, 1, 9)[::-1]
    assert ticks(1, 0, 8) == ticks(0, 1, 8)[::-1]
    assert ticks(1, 0, 7) == ticks(0, 1, 7)[::-1]
    assert ticks(1, 0, 6) == ticks(0, 1, 6)[::-1]
    assert ticks(1, 0, 5) == ticks(0, 1, 5)[::-1]
    assert ticks(1, 0, 4) == ticks(0, 1, 4)[::-1]
    assert ticks(1, 0, 3) == ticks(0, 1, 3)[::-1]
    assert ticks(1, 0, 2) == ticks(0, 1, 2)[::-1]
    assert ticks(1, 0, 1) == ticks(0, 1, 1)[::-1]
    assert ticks(10, 0, 10) == ticks(0, 10, 10)[::-1]
    assert ticks(10, 0, 9) == ticks(0, 10, 9)[::-1]
    assert ticks(10, 0, 8) == ticks(0, 10, 8)[::-1]
    assert ticks(10, 0, 7) == ticks(0, 10, 7)[::-1]
    assert ticks(10, 0, 6) == ticks(0, 10, 6)[::-1]
    assert ticks(10, 0, 5) == ticks(0, 10, 5)[::-1]
    assert ticks(10, 0, 4) == ticks(0, 10, 4)[::-1]
    assert ticks(10, 0, 3) == ticks(0, 10, 3)[::-1]
    assert ticks(10, 0, 2) == ticks(0, 10, 2)[::-1]
    assert ticks(10, 0, 1) == ticks(0, 10, 1)[::-1]
    assert ticks(10, -10, 10) == ticks(-10, 10, 10)[::-1]
    assert ticks(10, -10, 9) == ticks(-10, 10, 9)[::-1]
    assert ticks(10, -10, 8) == ticks(-10, 10, 8)[::-1]
    assert ticks(10, -10, 7) == ticks(-10, 10, 7)[::-1]
    assert ticks(10, -10, 6) == ticks(-10, 10, 6)[::-1]
    assert ticks(10, -10, 5) == ticks(-10, 10, 5)[::-1]
    assert ticks(10, -10, 4) == ticks(-10, 10, 4)[::-1]
    assert ticks(10, -10, 3) == ticks(-10, 10, 3)[::-1]
    assert ticks(10, -10, 2) == ticks(-10, 10, 2)[::-1]
    assert ticks(10, -10, 1) == ticks(-10, 10, 1)[::-1]


# nice


def test_nice_start_equals_stop():
    assert nice(1, 1, -1) == [1, 1]
    assert nice(1, 1, 0) == [1, 1]
    assert nice(1, 1, 1) == [1, 1]
    assert nice(1, 1, 10) == [1, 1]


def test_nice_not_positive_count():
    assert nice(0, 1, -1) == [0, 1]
    assert nice(0, 1, 0) == [0, 1]


def test_nice_infinity_count():
    assert nice(0, 1, math.inf) == [0, 1]


def test_nice():
    assert nice(0.132, 0.876, 1000) == [0.132, 0.876]
    assert nice(0.132, 0.876, 100) == [0.13, 0.88]
    assert nice(0.132, 0.876, 30) == [0.12, 0.88]
    assert nice(0.132, 0.876, 10) == [0.1, 0.9]
    assert nice(0.132, 0.876, 6) == [0.1, 0.9]
    assert nice(0.132, 0.876, 5) == [0, 1]
    assert nice(0.132, 0.876, 1) == [0, 1]
    assert nice(132, 876, 1000) == [132, 876]
    assert nice(132, 876, 100) == [130, 880]
    assert nice(132, 876, 30) == [120, 880]
    assert nice(132, 876, 10) == [100, 900]
    assert nice(132, 876, 6) == [100, 900]
    assert nice(132, 876, 5) == [0, 1000]
    assert nice(132, 876, 1) == [0, 1000]
