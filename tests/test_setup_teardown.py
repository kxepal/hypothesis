# coding=utf-8

# Copyright (C) 2013-2015 David R. MacIver (david@drmaciver.com)

# This file is part of Hypothesis (https://github.com/DRMacIver/hypothesis)

# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.

# END HEADER

from __future__ import division, print_function, absolute_import, \
    unicode_literals

import pytest
from hypothesis import given, strategy, assume


class HasSetupAndTeardown(object):

    def __init__(self):
        self.setups = 0
        self.teardowns = []

    def __repr__(self):
        return 'HasSetupAndTeardown()'

    def setup_example(self):
        self.setups += 1

    def teardown_example(self, example):
        self.teardowns.append(example)

    def __copy__(self):
        return self

    def __deepcopy__(self, mapping):
        return self

    @given(int)
    def give_me_an_int(self, x):
        pass

    @given(str)
    def give_me_a_string(myself, x):
        pass

    @given(int)
    def give_me_a_positive_int(self, x):
        assert x >= 0

    @given(strategy(int).map(lambda x: x.nope))
    def fail_in_reify(self, x):
        pass

    @given(int)
    def assume_some_stuff(self, x):
        assume(x > 0)

    @given(strategy(int).filter(lambda x: x > 0))
    def assume_in_reify(self, x):
        pass


def test_calls_setup_and_teardown_on_self_as_first_argument():
    x = HasSetupAndTeardown()
    x.give_me_an_int()
    x.give_me_a_string()
    assert x.setups > 0
    assert len(x.teardowns) == x.setups
    assert any(isinstance(t[0][1]['x'], int) for t in x.teardowns)
    assert any(isinstance(t[0][1]['x'], str) for t in x.teardowns)


def test_calls_setup_and_teardown_on_self_unbound():
    x = HasSetupAndTeardown()
    HasSetupAndTeardown.give_me_an_int(x)
    assert x.setups > 0
    assert len(x.teardowns) == x.setups


def test_calls_setup_and_teardown_on_explicit_call():
    x = HasSetupAndTeardown()
    x.give_me_an_int(1)
    assert x.setups == 1
    assert len(x.teardowns) == 1


def test_calls_setup_and_teardown_on_failure():
    x = HasSetupAndTeardown()
    with pytest.raises(AssertionError):
        x.give_me_a_positive_int()
    assert x.setups > 0
    assert len(x.teardowns) == x.setups
    assert x.teardowns[-1][1]['x'] == -1


def test_still_tears_down_on_failed_reify():
    x = HasSetupAndTeardown()
    with pytest.raises(AttributeError):
        x.fail_in_reify()
    assert x.setups > 0
    assert len(x.teardowns) == x.setups


def test_still_tears_down_on_failed_assume():
    x = HasSetupAndTeardown()
    x.assume_some_stuff()
    assert x.setups > 0
    assert len(x.teardowns) == x.setups


def test_still_tears_down_on_failed_assume_in_reify():
    x = HasSetupAndTeardown()
    x.assume_in_reify()
    assert x.setups > 0
    assert len(x.teardowns) == x.setups
