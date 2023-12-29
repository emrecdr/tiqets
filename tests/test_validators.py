import pytest
import polars as pl
from src.validators import DataValidator
from src.models.validator import ValidationError, ValidationResult


# Test DataValidator.validate_barcodes method valid results
@pytest.mark.parametrize(
    "input_data, expected_result, test_id",
    [
        # Happy path valid tests
        (
            {"barcode": ["A1"], "order": [10]},
            {"is_valid": True},
            "happy_unique_1item",
        ),
        (
            {"barcode": ["A1", "B2", "C3"], "order": [10, 20, 30]},
            {"is_valid": True},
            "happy_unique",
        ),
    ],
)
def test_validate_valid_barcodes(input_data, expected_result, test_id):
    # Arrange
    validator = DataValidator()

    # Act
    actual_result = validator.validate_barcodes(pl.DataFrame(input_data), "barcode")

    # Assert
    assert (
        actual_result["is_valid"] == expected_result["is_valid"]
    ), f"Failed test ID: {test_id}"

    assert "errors" not in expected_result
    assert "data" not in expected_result


# Test DataValidator.validate_barcodes method invalid results
@pytest.mark.parametrize(
    "input_data, expected_result, test_id",
    [
        # Happy path invalid results tests
        (
            {"barcode": ["A1", "A1", "B2", "C3", "A1"], "order": [10, 11, 20, 30, 12]},
            {
                "is_valid": False,
                "errors": [
                    ValidationError(
                        "Duplicate barcodes found",
                        [
                            {"barcode": "A1", "order": 10},
                            {"barcode": "A1", "order": 11},
                            {"barcode": "A1", "order": 12},
                        ],
                    )
                ],
                "data": {"barcode": ["B2", "C3"], "order": [20, 30]},
            },
            "happy_duplicates",
        ),
        # Edge cases
        (
            {"barcode": [], "order": []},
            {
                "is_valid": False,
                "errors": [ValidationError("Error occured during validation:", [])],
                "data": {"barcode": [], "order": []},
            },
            "edge_empty_df",
        ),
        (
            {"barcode": ["A1", "A1", "A1"], "order": [10, 11, 12]},
            {
                "is_valid": False,
                "errors": [
                    ValidationError(
                        "Duplicate barcodes found",
                        [
                            {"barcode": "A1", "order": 10},
                            {"barcode": "A1", "order": 11},
                            {"barcode": "A1", "order": 12},
                        ],
                    )
                ],
                "data": {"barcode": [], "order": []},
            },
            "edge_all_duplicates",
        ),
    ],
)
def test_validate_invalid_barcodes(input_data, expected_result, test_id):
    # Arrange
    validator = DataValidator()

    # Act
    actual_result = validator.validate_barcodes(pl.DataFrame(input_data), "barcode")

    # Assert
    assert (
        actual_result["is_valid"] == expected_result["is_valid"]
    ), f"Failed test ID: {test_id}"

    assert "errors" in expected_result
    for idx, actual_error in enumerate(actual_result["errors"]):
        assert actual_error.error_message.startswith(
            expected_result["errors"][idx].error_message
        ), f"Failed test ID: {test_id}"

        assert (
            actual_error.failed_rows == expected_result["errors"][idx].failed_rows
        ), f"Failed test ID: {test_id}"

    assert "data" in expected_result
    assert actual_result["data"].equals(
        pl.DataFrame(expected_result["data"])
    ), f"Failed test ID: {test_id}"


# Test DataValidator.validate_orders method
@pytest.mark.parametrize(
    "input_data, expected_result, test_id",
    [
        # Happy path tests
        (
            {
                "barcode": [1000, 2000, 3000],
                "order": [10, 20, 30],
                "customer": [1, 2, 3],
            },
            {"is_valid": True},
            "happy_complete_data",
        ),
        (
            {
                "barcode": [1000, 2000, None, 4000],
                "order": [10, 20, 30, 40],
                "customer": [1, 2, 3, 4],
            },
            {
                "is_valid": False,
                "errors": [
                    ValidationError(
                        "Orders without barcodes found",
                        [{"barcode": None, "order": 30, "customer": 3}],
                    )
                ],
                "data": {
                    "barcode": [1000, 2000, 4000],
                    "order": [10, 20, 40],
                    "customer": [1, 2, 4],
                },
            },
            "happy_missing_data",
        ),
        # Edge cases
        # (
        #     {"order": [], "customer": []},
        #     {"is_valid": True},
        #     "edge_empty_df",
        # ),
        # (
        #     {"order": [10, 20], "customer": [None, None]},
        #     {
        #         "is_valid": False,
        #         "errors": [
        #             ValidationError(
        #                 "Orders without barcodes found",
        #                 [
        #                     {"order": "Order1", "customer": None},
        #                     {"order": "Order2", "customer": None},
        #                 ],
        #             )
        #         ],
        #         "data": {"order": [], "barcode": []},
        #     },
        #     "edge_all_missing",
        # ),
    ],
)
def test_validate_orders(input_data, expected_result, test_id):
    # Arrange
    validator = DataValidator()

    # Act
    actual_result = validator.validate_orders(pl.DataFrame(input_data), "barcode")

    # Assert
    # assert actual_result["data"].equals(
    #     pl.DataFrame(expected_result["data"]), f"Failed test ID: {test_id}")

    assert "errors" in expected_result
    for idx, actual_error in enumerate(actual_result["errors"]):
        assert actual_error.error_message.startswith(
            expected_result["errors"][idx].error_message
        ), f"Failed test ID: {test_id}"

    assert (
        actual_error.failed_rows == expected_result["errors"][idx].failed_rows
    ), f"Failed test ID: {test_id}"

    assert "data" in expected_result
    assert actual_result["data"].equals(
        pl.DataFrame(expected_result["data"])
    ), f"Failed test ID: {test_id}"
