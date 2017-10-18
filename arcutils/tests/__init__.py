# -*- coding: utf-8 -*-

from pkg_resources import resource_filename

import pytest

import arcutils

def test(*args):
    options = [resource_filename('arcutils', 'tests')]
    options.extend(list(args))
    return pytest.main(options)
