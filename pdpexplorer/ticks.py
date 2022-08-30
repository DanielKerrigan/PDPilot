#!/usr/bin/env python
# coding: utf-8

"""
The code in this file is ported from d3-array.

https://github.com/d3/d3-array/blob/main/src/ticks.js
https://github.com/d3/d3-array/blob/main/src/nice.js

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

Porting notes:

In JavaScript, Math.log(0) returns -Infinity.
In Python, math.log(0) results in an error.
"""

import math


e10 = math.sqrt(50)
e5 = math.sqrt(10)
e2 = math.sqrt(2)


def tick_increment(start, stop, count):
    """Like d3.tickStep, except requires that start is always less than or equal to stop,
    and if the tick step for the given start, stop and count would be less than one,
    returns the negative inverse tick step instead. This method is always guaranteed
    to return an integer, and is used by d3.ticks to guarantee that the returned tick
    values are represented as precisely as possible in IEEE 754 floating point.

    https://github.com/d3/d3-array#tickIncrement"""
    if count <= 0:
        return math.inf

    step = (stop - start) / count

    if step == 0:
        return -math.inf

    power = math.floor(math.log10(step))
    error = step / (10**power)

    # tick step >= 1
    if power >= 0:
        base_step = 10**power
        if error >= e10:
            return 10 * base_step
        elif error >= e5:
            return 5 * base_step
        elif error >= e2:
            return 2 * base_step
        else:
            return base_step
    # tick step < 1
    else:
        base_step = -(10**-power)
        if error >= e10:
            return base_step / 10
        elif error >= e5:
            return base_step / 5
        elif error >= e2:
            return base_step / 2
        else:
            return base_step


def ticks(start, stop, count):
    """Returns an array of approximately count + 1 uniformly-spaced,nicely-rounded
    values between start and stop (inclusive). Each value is a power of ten
    multiplied by 1, 2 or 5. See also d3.tickIncrement, d3.tickStep and linear.ticks.

    Ticks are inclusive in the sense that they may include the specified start and
    stop values if (and only if) they are exact, nicely-rounded values consistent
    with the inferred step. More formally, each returned tick t satisfies
    start ≤ t and t ≤ stop.

    https://github.com/d3/d3-array#ticks"""

    if start == stop and count > 0:
        return [start]

    reverse = stop < start
    if reverse:
        start, stop = stop, start

    step = tick_increment(start, stop, count)
    if step == 0 or math.isinf(step):
        return []

    if step > 0:
        r0 = round(start / step)
        r1 = round(stop / step)

        if r0 * step < start:
            r0 += 1

        if r1 * step > stop:
            r1 -= 1

        tick_values = [(r0 + i) * step for i in range(r1 - r0 + 1)]
    else:
        step = -step
        r0 = round(start * step)
        r1 = round(stop * step)

        if r0 / step < start:
            r0 += 1

        if r1 / step > stop:
            r1 -= 1

        tick_values = [(r0 + i) / step for i in range(r1 - r0 + 1)]

    if reverse:
        tick_values.reverse()

    return tick_values


def nice(start, stop, count):
    """Returns a new interval [niceStart, niceStop] covering the given interval
    [start, stop] and where niceStart and niceStop are guaranteed to align
    with the corresponding tick step. Like d3.tickIncrement, this requires
    that start is less than or equal to stop.

    https://github.com/d3/d3-array#nice"""

    prestep = 0

    while True:
        step = tick_increment(start, stop, count)

        if step == prestep or step == 0 or math.isinf(step):
            return [start, stop]
        elif step > 0:
            start = math.floor(start / step) * step
            stop = math.ceil(stop / step) * step
        elif step < 0:
            start = math.ceil(start * step) / step
            stop = math.floor(stop * step) / step

        prestep = step
