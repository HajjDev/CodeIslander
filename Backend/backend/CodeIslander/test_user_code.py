# Backend/backend/CodeIslander/test_user_code.py

import user_code
import pytest

# --- Test cases for the add(a, b) function ---

def test_add_positive_numbers():
    """Tests if the function can add two positive numbers."""
    assert user_code.add(2, 3) == 5, "Failed to add 2 + 3"

def test_add_negative_numbers():
    """Tests if the function can add two negative numbers."""
    assert user_code.add(-5, -3) == -8, "Failed to add -5 + -3"

def test_add_mixed_numbers():
    """Tests if the function can add a positive and a negative number."""
    assert user_code.add(10, -5) == 5, "Failed to add 10 + -5"

def test_add_zero():
    """Tests adding zero to a number."""
    assert user_code.add(10, 0) == 10, "Failed to add 10 + 0"

def test_floating_point_addition():
    """
    ** THIS IS THE CORRECTED TEST **
    Tests if the function correctly handles floating-point addition.
    We use pytest.approx() to compare floating-point numbers because
    0.1 + 0.2 is not exactly 0.3 in computer math.
    """
    assert user_code.add(0.1, 0.2) == pytest.approx(0.3)