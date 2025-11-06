import logging
from errors import ChartDataConverterException

logger = logging.getLogger('Chart Data Validator')



def validate_chart_data(data):
    """
        Validates if a dictionary is in the correct format for a charting library.

        The expected format is:
        {
            "categories": ["cat1", "cat2", ...],
            "series": [
                {"name": "series_name_1", "values": [10, 20, ...]},
                {"name": "series_name_2", "values": [30, 40, ...]}
            ]
        }

        Args:
            data (dict): The dictionary to validate (from parsed JSON).

        Returns:
            tuple: A dictionary containing:
                   - bool: True if the data is valid, False otherwise.
                   - str: "Validation successful" or instance of ChartDataConverterException with specific message.
        """
    try:
        if not data:
            return False, ChartDataConverterException('No Json data provided')

        # 1. Check if the root object is a dictionary
        if not isinstance(data, dict):
            return False, ChartDataConverterException("Error: The root JSON object must be a dictionary.")

        # 2. Check for the presence of 'categories' and 'series' keys
        if 'categories' not in data:
            return False, ChartDataConverterException("Error: Missing required key: 'categories'.")
        if 'series' not in data:
            return False, ChartDataConverterException("Error: Missing required key: 'series'.")

        # 3. Validate the 'categories' structure
        categories = data['categories']
        if not isinstance(categories, list):
            return False, ChartDataConverterException("Error: The 'categories' key must be a list.")

        num_categories = len(categories)

        # 4. Validate the 'series' structure
        series = data['series']
        if not isinstance(series, list):
            return False, ChartDataConverterException("Error: The 'series' key must be a list.")

        if not series:
            return False, ChartDataConverterException("Error: The 'series' list cannot be empty.")

        # 5. Validate each item within the 'series' list
        for i, s in enumerate(series):
            if not isinstance(s, dict):
                return False, ChartDataConverterException(f"Error: Item at index {i} in 'series' is not a dictionary.")

            if 'name' not in s:
                return False, ChartDataConverterException(f"Error: Item at index {i} in 'series' is missing the 'name' key.")
            if not isinstance(s['name'], str):
                return False, ChartDataConverterException(f"Error: The 'name' for series at index {i} must be a string.")

            if 'values' not in s:
                return False, ChartDataConverterException(f"Error: Item at index {i} in 'series' is missing the 'values' key.")
            if not isinstance(s['values'], list):
                return False, ChartDataConverterException(f"Error: The 'values' for series at index {i} must be a list.")

            # 6. Validate that all values in the 'values' list are numbers
            for val_index, value in enumerate(s['values']):
                if not isinstance(value, (int, float)):
                    return False, ChartDataConverterException(f"Error: Value at index {val_index} in series '{s['name']}' is not a number.")

            # 7. Check for length consistency
            if len(s['values']) != num_categories:
                return False, ChartDataConverterException(f"Error: Mismatch in length for series '{s['name']}'. "
                               f"It has {len(s['values'])} values but there are {num_categories} categories.")

            #8. Check that the series dictionary has a values key not data
            for i, series in enumerate(data["series"]):
                try:
                    if data["series"][i]["values"]:
                        continue
                except Exception as e:
                    print('Values is not a key of the "series" dictionary on the chart data')
                    print(data)
                try:
                    if data["series"][i]["data"]:
                        data["series"][i]['values'] = data["series"][i].pop('data')
                        print(data)
                except Exception as e:
                    print('Data is not a key of the "series" dictionary on the chart data')


        logger.info(f"Chart data validated successfully. Chart data: {data}")
        return True, "Validation successful"
    except ChartDataConverterException as e:
        raise e

# 1. Valid Data (Multiple Series)
valid_data = {
    "categories": ["Jan", "Feb", "Mar"],
    "series": [
        {"name": "Product A", "values": [100, 120, 150]},
        {"name": "Product B", "values": [80, 90, 75]}
    ]
}

# 2. Invalid Data - 'series' is not a list
invalid_data_1 = {
    "categories": ["Jan", "Feb", "Mar"],
    "series": {"name": "Product A", "values": [100, 120, 150]}
}

# 3. Invalid Data - Missing 'name' in a series
invalid_data_2 = {
    "categories": ["Jan", "Feb", "Mar"],
    "series": [
        {"values": [100, 120, 150]}
    ]
}

# 4. Invalid Data - Length mismatch between values and categories
invalid_data_3 = {
    "categories": ["Jan", "Feb", "Mar"],
    "series": [
        {"name": "Product A", "values": [100, 120]}
    ]
}

# 5. Invalid Data - A value is not a number
invalid_data_4 = {
    "categories": ["Jan", "Feb", "Mar"],
    "series": [
        {"name": "Product A", "values": [100, "invalid", 150]}
    ]
}


