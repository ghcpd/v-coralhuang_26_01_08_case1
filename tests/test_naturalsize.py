from mini_humanize.sizecodec import naturalsize


def test_zero_and_negative_zero():
    assert naturalsize(0, strip_trailing_zeros=True) == "0 B"
    assert naturalsize(-0.0, strip_trailing_zeros=True) == "0 B"


def test_basic_formatting_defaults():
    assert naturalsize(1536, binary=True) == "1.5 KiB"
    assert naturalsize(1536, binary=False) == "1.5 kB"
    assert naturalsize(1000 * 1000) == "1.0 MB"


def test_strip_trailing_zeros_behavior():
    assert naturalsize(1000.0, strip_trailing_zeros=True) == "1 kB"
    assert naturalsize(1024.0, binary=True, strip_trailing_zeros=True) == "1 KiB"
