"""Constants used across the lm_eval API.

This module defines commonly used string constants to avoid magic strings
scattered throughout the codebase. Using these constants improves:
- Type safety (IDE autocompletion)
- Refactoring safety (change in one place)
- Documentation (constants are self-documenting)
"""

# Filter names
# These are used to identify different filter configurations applied to model outputs.
# The "none" filter is the default and typically means no filtering is applied.
FILTER_NONE = "none"

# Metric/Aggregation names
# These are used for special metric handling modes.
# The "bypass" metric is used when evaluation should skip standard metric computation.
METRIC_BYPASS = "bypass"

# Aggregation methods
AGGREGATION_MEAN = "mean"
AGGREGATION_BYPASS = "bypass"
