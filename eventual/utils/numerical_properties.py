def normalize_value(value: float, min_val: float, max_val: float) -> float:
    """
    Normalize a value to a range between 0 and 1.

    Args:
        value (float): The value to normalize.
        min_val (float): The minimum value in the range.
        max_val (float): The maximum value in the range.

    Returns:
        float: The normalized value.
    """
    if max_val == min_val:
        return 0.0  # Avoid division by zero
    return (value - min_val) / (max_val - min_val)

def compute_delta(previous_state: float, current_state: float) -> float:
    """
    Compute the delta between two states.

    Args:
        previous_state (float): The previous state of the concept.
        current_state (float): The current state of the concept.

    Returns:
        float: The delta between the two states.
    """
    return current_state - previous_state