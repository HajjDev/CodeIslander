import user_code
import pytest

def test_basic():
    assert user_code.repeat_string("Hi", 3) == "HiHiHi"