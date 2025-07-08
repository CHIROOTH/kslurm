from __future__ import absolute_import

import pytest

from kslurm.models.formatters import gpu as fmt


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("gpu", "1"),
        ("gpu=2", "2"),
        ("gpu=h100", "h100:1"),
        ("gpu=h100:2", "h100:2"),
        ("gpu=foo:0", "foo:1"),
        ("gpu=bar:999", "bar:999"),
    ],
)
def test_gpu_formatter(raw, expected):
    assert fmt(raw) == expected


# check for edge cases :
# invalid input ("gpu=foo:-1", "gpu=bad:abc", "gpu=", non-strings)
@pytest.mark.parametrize(
    "raw, expected",
    [
        ("gpu=foo:-1", "foo:1"),
        ("gpu=foo:abc", "foo:1"),
        ("gpu=bar:", "bar:1"),
    ],
)
def test_gpu_formatter_invalid_counts(raw, expected):
    assert fmt(raw) == expected


@pytest.mark.parametrize(
    "bad_input",
    [
        "foo",
        "gpu2",
    ],
)
def test_gpu_formatter_malformed_input(bad_input):
    with pytest.raises(IndexError):
        fmt(bad_input)
