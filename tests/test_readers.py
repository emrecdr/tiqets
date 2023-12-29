import pytest
from pathlib import Path
from src.models.errors import AppReaderError
from src.readers import CSVReader


# Define a fixture for creating a temporary CSV file
@pytest.fixture()
def tmp_csv(tmp_path):
    def _tmp_csv(content: str, filename: str = "data"):
        file_path = tmp_path / f"test_{filename}.csv"
        file_path.write_text(content)
        return file_path

    return _tmp_csv


# Happy path tests with various realistic test values
@pytest.mark.parametrize(
    "file_content, test_id",
    [
        ("col1,col2\n1,2\n3,4", "happy_path_2col_2row"),
        ("a,b,c\n1,2,3\n4,5,6", "happy_path_3col_2row"),
        ("header1,header2\nstring1,string2", "happy_path_str_2col_1row"),
    ],
)
def test_read_csv_happy_path(tmp_csv, file_content, test_id):
    # Arrange
    file_path = tmp_csv(file_content, test_id)

    # Act
    result_df = CSVReader.read(file_path)

    # Assert
    assert not result_df.is_empty()
    tmp_data_rows = file_content.splitlines()
    expected = (
        max(0, len(tmp_data_rows) - 1),
        tmp_data_rows[0].count(",") + 1,
    )
    assert result_df.shape == expected, f"Failed test ID: {test_id}"


# Edge cases
@pytest.mark.parametrize(
    "file_content, expected_shape, test_id",
    [
        ("col1,col2", (0, 2), "edge_case_no_data"),
        ("col1,col2,col3\n\n\n", (0, 3), "edge_case_empty_lines"),
        ("\t", (0, 1), "edge_case_almost_empty_file_almost"),
        (" \n\n\n\n", (3, 1), "edge_case_empty_rows"),
    ],
)
def test_read_csv_edge_cases(tmp_csv, file_content, expected_shape, test_id):
    # Arrange
    file_path = tmp_csv(file_content, test_id)

    # Act
    result_df = CSVReader.read(file_path)

    # Assert
    assert result_df.shape == expected_shape, f"Failed test ID: {test_id}"


# Error cases
@pytest.mark.parametrize(
    "file_content, test_id",
    [("", "empty_file_simple")],
)
def test_read_csv_empty_files(tmp_csv, file_content, test_id):
    # Arrange
    file_path = tmp_csv(file_content, test_id)

    # Act & Assert
    with pytest.raises(Exception) as excinfo:
        _ = CSVReader.read(file_path)
    assert str(excinfo.value).startswith(
        "Unable to read file"
    ), f"Failed test ID: {test_id}"


@pytest.mark.parametrize(
    "file_path, test_id",
    [
        (Path("/path/to/nonexistent/test_file.csv"), "error_case_nonexistent_file"),
        (123, "error_case_invalid_file_path_type"),
        (None, "error_case_none_file_path"),
    ],
)
def test_read_csv_error_cases(file_path, test_id):
    # Act & Assert
    with pytest.raises(Exception) as excinfo:
        _ = CSVReader.read(file_path)
    assert str(excinfo.value).startswith(
        "Unable to read file"
    ), f"Failed test ID: {test_id}"
