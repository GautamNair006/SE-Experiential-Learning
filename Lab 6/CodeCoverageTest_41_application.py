import pytest

from laundry_service import dropoff_status, extra_weight_charge, order_acceptable


def test_extra_weight_charge_executes_calculation_and_error_paths():
    assert extra_weight_charge("regular", 4, "standard", False) == 0
    assert extra_weight_charge("regular", 8, "standard", True) == 30
    assert extra_weight_charge("regular", 16, "standard", False) == 495
    assert extra_weight_charge("regular", 16, "express", False) == 825

    with pytest.raises(ValueError, match="unknown garment type"):
        extra_weight_charge("shoes", 1, "standard", False)
    with pytest.raises(ValueError, match="invalid weight"):
        extra_weight_charge("regular", -1, "standard", False)


def test_order_acceptable_executes_all_rules():
    assert order_acceptable(10, 20, False) is True
    assert order_acceptable(10, 5, True) is True
    assert order_acceptable(26, 10, False) is False


def test_dropoff_status_executes_each_result():
    assert dropoff_status(60, False, False) == "accepted"
    assert dropoff_status(59, False, False) == "late"
    assert dropoff_status(39, False, False) == "rejected"
