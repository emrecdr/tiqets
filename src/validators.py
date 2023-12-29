from typing import Optional

import polars as pl

from models.validator import ValidationError, ValidationResult


class DataValidator:
    """Validates if there are duplicate values or missing values in the specified column."""

    def validate_barcodes(self, df: pl.DataFrame, column: str) -> ValidationResult:
        """Validates that dataset not includes duplicate barcodes."""

        try:
            duplicated_barcodes = self._get_duplicated_barcodes(df, column)
            if duplicated_barcodes is None:
                return dict(is_valid=True)

            # there are duplicated values in the specified column
            return {
                "is_valid": False,
                "errors": [
                    ValidationError(
                        "Duplicate barcodes found", duplicated_barcodes.to_dicts()
                    )
                ],
                "data": df.unique(subset=[column], keep="none", maintain_order=True),
            }
        except Exception as exc:
            return {
                "is_valid": False,
                "errors": [
                    ValidationError(
                        f"Error occured during validation: {exc!s}", df.to_dicts()
                    )
                ],
                "data": df.clear(),
            }

    def validate_orders(self, df: pl.DataFrame, column: str) -> ValidationResult:
        """Checks that all orders have a corresponding barcode."""
        orphan_orders = self._get_orders_wo_barcodes(df, column)
        if orphan_orders is None:
            return dict(is_valid=True)

        #  there are missing values in the specified column.
        return {
            "is_valid": False,
            "errors": [
                ValidationError(
                    "Orders without barcodes found", orphan_orders.to_dicts()
                )
            ],
            "data": df.drop_nulls(subset=column),
        }

    @staticmethod
    def _get_duplicated_barcodes(
        df: pl.DataFrame, column: str
    ) -> Optional[pl.DataFrame]:
        """Returns if there are duplicated values in the specified column."""
        if df[column].is_duplicated().any():
            # return duplicate barcodes
            return df.filter(df[column].is_duplicated())

    @staticmethod
    def _get_orders_wo_barcodes(
        df: pl.DataFrame, column: str
    ) -> Optional[pl.DataFrame]:
        """Returns if there are missing values in the specified column."""
        if df[column].is_null().any():
            # return orders without barcodes
            return df.filter(pl.col(column).is_null())
