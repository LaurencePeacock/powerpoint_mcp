import logging
from errors.TableDataValidationException import TableDataValidationException  # Assuming this custom exception exists

logger = logging.getLogger('Table Data Validator')


def validate_table_data(data):
    """
    Validates if a dictionary is in the correct format for a table.

    The expected format is:
    {
        "columns": ["colA", "colB", ...],
        "values": [
            ["row1_valA", "row1_valB", ...],
            ["row2_valA", "row2_valB", ...]
        ]
    }

    Args:
        data (dict): The dictionary to validate.

    Returns:
        tuple: A tuple containing:
               - bool: True if the data is valid, False otherwise.
               - str "Validation successful" or an exception instance with a specific message.
    """
    # 1. Check for presence and type of root object
    if not data:
        return False, TableDataValidationException('No data provided.')
    if not isinstance(data, dict):
        return False, TableDataValidationException("Error: The root object must be a dictionary.")

    # 2. Check for the presence of required keys
    if 'columns' not in data:
        return False, TableDataValidationException("Error: Missing required key: 'columns'.")
    if 'values' not in data:
        return False, TableDataValidationException("Error: Missing required key: 'values'.")

    # 3. Validate the 'columns' structure
    columns = data['columns']
    if not isinstance(columns, list):
        return False, TableDataValidationException("Error: The 'columns' key must be associated with a list.")

    for i, col in enumerate(columns):
        if not isinstance(col, (str, int, float)):
            return False, TableDataValidationException(
                f"Error: Column at index {i} ('{col}') is not a string or number.")

    num_columns = len(columns)

    # 4. Validate the 'values' structure (must be a list of lists)
    values = data['values']
    if not isinstance(values, list):
        return False, TableDataValidationException("Error: The 'values' key must be associated with a list.")

    # 5. Validate each row in 'values'
    for i, row in enumerate(values):
        if not isinstance(row, list):
            return False, TableDataValidationException(f"Error: Row at index {i} in 'values' is not a list.")

        # 6. Check for length consistency against the number of columns
        if len(row) != num_columns:
            return False, TableDataValidationException(
                f"Error: Mismatch in length for row at index {i}. "
                f"It has {len(row)} values, but there are {num_columns} columns."
            )

    logger.info(f"Table data validated successfully. Data: {data}")
    return True, "Validation successful"





# 1. Valid Data
valid_table_data = {
    "columns": ["Name", "Age", "City"],
    "values": [
        ["Alice", 30, "New York"],
        ["Bob", 25, "Los Angeles"],
        ["Charlie", 35, "Chicago"]
    ]
}

# 2. Valid Data (Empty rows)
valid_empty_rows = {
    "columns": ["Product", "Price"],
    "values": []
}

# 3. Invalid Data - Missing 'values' key
invalid_data_1 = {
    "columns": ["Name", "Age", "City"]
}

# 4. Invalid Data - 'columns' is not a list
invalid_data_2 = {
    "columns": "Name, Age, City",
    "values": [
        ["Alice", 30, "New York"]
    ]
}

# 5. Invalid Data - A row is not a list
invalid_data_3 = {
    "columns": ["Name", "Age"],
    "values": [
        ["Alice", 30],
        "Bob, 25"  # This row is invalid
    ]
}

# 6. Invalid Data - Row length mismatch
invalid_data_4 = {
    "columns": ["Name", "Age", "City"],
    "values": [
        ["Alice", 30, "New York"],
        ["Bob", 25]  # This row is missing a value
    ]
}

# --- Demonstrating the validator ---
# print("1. Valid Data:", validate_table_data(valid_table_data))
# print("2. Valid (Empty Rows):", validate_table_data(valid_empty_rows))
# print("3. Invalid (Missing Key):", validate_table_data(invalid_data_1))
# print("4. Invalid (Columns not List):", validate_table_data(invalid_data_2))
# print("5. Invalid (Row not List):", validate_table_data(invalid_data_3))
# print("6. Invalid (Row Length Mismatch):", validate_table_data(invalid_data_4))