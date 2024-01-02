import polars as pl
import pytest

from src.processors import DataProcessor


# Test for set_dataframes method
@pytest.mark.parametrize(
    "barcodes, orders, expected_merged, test_id",
    [
        # Happy path tests
        (
            {"barcode": ["A1"], "order_id": [10]},
            {"order_id": [10], "customer_id": [1]},
            {"order_id": [10], "customer_id": [1], "barcode": ["A1"]},
            "happy_path_single",
        ),
        (
            {"barcode": ["A1", "B2", "C3"], "order_id": [10, 20, 30]},
            {"order_id": [10, 20, 30], "customer_id": [1, 2, 3]},
            {
                "order_id": [10, 20, 30],
                "customer_id": [1, 2, 3],
                "barcode": ["A1", "B2", "C3"],
            },
            "happy_path_simple",
        ),
        (
            {"barcode": ["A1", "B2", "C3"], "order_id": [10, 20, 30]},
            {"order_id": [10, 20, 30, 40, 50, 60], "customer_id": [1, 2, 3, 4, 5, 6]},
            {
                "order_id": [10, 20, 30, 40, 50, 60],
                "customer_id": [1, 2, 3, 4, 5, 6],
                "barcode": ["A1", "B2", "C3", None, None, None],
            },
            "edge_case_missing_barcodes",
        ),
    ],
)
def test_set_valid_dataframes(barcodes, orders, expected_merged, test_id):
    # Arrange
    processor = DataProcessor()

    # Act
    actual_result = processor.set_dataframes(pl.DataFrame(barcodes), pl.DataFrame(orders))

    # Assert
    assert actual_result["is_ok"], f"Failed test ID: {test_id}"
    assert "error" not in actual_result, f"Failed test ID: {test_id}"
    assert processor.merged_df.equals(pl.DataFrame(expected_merged)), f"Failed test ID: {test_id}"


@pytest.mark.parametrize(
    "barcodes, orders, test_id",
    [
        # Error case: non-matching columns
        (
            {"barcode": ["A1"], "orders": [10]},
            {"orders": [10], "customers": [1]},
            "error_case_1",
        ),
    ],
)
def test_set_invalid_dataframes(barcodes, orders, test_id):
    # Arrange
    processor = DataProcessor()

    # Act
    actual_result = processor.set_dataframes(pl.DataFrame(barcodes), pl.DataFrame(orders))
    print(actual_result)
    print(actual_result["error"])

    # Assert
    assert actual_result["is_ok"] is False, f"Failed test ID: {test_id}"
    assert "error" in actual_result, f"Failed test ID: {test_id}"
