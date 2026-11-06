import pytest

from laundry_service import dropoff_status, extra_weight_charge, order_acceptable


@pytest.mark.parametrize(
    ("garment_type", "weight_kg", "speed", "is_member", "expected"),
    [
        ("regular", 4, "standard", False, 0),
        ("regular", 7, "standard", True, 0),
        ("regular", 8, "standard", True, 30),
        ("delicate", 4, "express", True, 0),
        ("bedding", 9, "express", True, 50),
        ("regular", 16, "standard", False, 495),
        ("regular", 16, "express", False, 825),
    ],
)
def test_extra_weight_charge_branches(
    garment_type, weight_kg, speed, is_member, expected
):
    assert (
        extra_weight_charge(garment_type, weight_kg, speed, is_member) == expected
    )


@pytest.mark.parametrize(
    ("garment_type", "weight_kg", "message"),
    [
        ("unknown", 1, "unknown garment type"),
        ("regular", -1, "invalid weight"),
    ],
)
def test_extra_weight_charge_rejects_invalid_inputs(
    garment_type, weight_kg, message
):
    with pytest.raises(ValueError, match=message):
        extra_weight_charge(garment_type, weight_kg, "standard", False)


@pytest.mark.parametrize(
    ("weight_kg", "items", "is_delicate", "expected"),
    [
        (100, 5, True, True),
        (0, 6, True, False),
        (25, 40, False, True),
        (26, 40, False, False),
        (10, 41, False, False),
    ],
)
def test_order_acceptable_branches(weight_kg, items, is_delicate, expected):
    assert order_acceptable(weight_kg, items, is_delicate) is expected


@pytest.mark.parametrize(
    ("minutes_before_closing", "has_bedding", "is_express", "expected"),
    [
        (60, False, False, "accepted"),
        (59, False, False, "late"),
        (39, False, False, "rejected"),
        (90, True, False, "accepted"),
        (89, True, False, "late"),
        (69, True, False, "rejected"),
        (90, False, True, "accepted"),
        (120, True, True, "accepted"),
        (119, True, True, "late"),
        (99, True, True, "rejected"),
    ],
)
def test_dropoff_status_branches(
    minutes_before_closing, has_bedding, is_express, expected
):
    assert (
        dropoff_status(minutes_before_closing, has_bedding, is_express) == expected
    )
