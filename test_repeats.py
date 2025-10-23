#!/usr/bin/env python
"""Quick test script to verify repeat aggregation functionality."""

import sys

print("Testing repeat aggregation imports...")

# Test 1: Import repeat aggregation registry
try:
    from lm_eval.api.registry import (
        repeat_agg_registry,
        get_repeat_aggregation,
        register_repeat_aggregation,
    )
    print("✓ Successfully imported repeat aggregation registry")
except ImportError as e:
    print(f"✗ Failed to import repeat aggregation registry: {e}")
    sys.exit(1)

# Test 2: Check that repeat aggregation functions are registered
try:
    repeat_funcs = ["first", "mean", "max", "min", "majority", "any_correct", "all_correct"]
    for func_name in repeat_funcs:
        func = get_repeat_aggregation(func_name)
        print(f"✓ Found repeat aggregation: {func_name}")
except KeyError as e:
    print(f"✗ Missing repeat aggregation function: {e}")
    sys.exit(1)

# Test 3: Test repeat aggregation functions
print("\nTesting repeat aggregation functions...")
scores = [0.5, 0.8, 0.3, 0.9, 0.6]
predictions = ["answer1", "answer2", "answer1", "answer3", "answer1"]

# Test first
first_fn = get_repeat_aggregation("first")
result = first_fn(scores)
assert result == 0.5, f"Expected 0.5, got {result}"
print(f"✓ repeat_first([0.5, 0.8, 0.3, 0.9, 0.6]) = {result}")

# Test mean
mean_fn = get_repeat_aggregation("mean")
result = mean_fn(scores)
expected = sum(scores) / len(scores)
assert abs(result - expected) < 0.001, f"Expected {expected}, got {result}"
print(f"✓ repeat_mean([0.5, 0.8, 0.3, 0.9, 0.6]) = {result}")

# Test max
max_fn = get_repeat_aggregation("max")
result = max_fn(scores)
assert result == 0.9, f"Expected 0.9, got {result}"
print(f"✓ repeat_max([0.5, 0.8, 0.3, 0.9, 0.6]) = {result}")

# Test majority
majority_fn = get_repeat_aggregation("majority")
result = majority_fn(scores, predictions=predictions)
# "answer1" appears 3 times (indices 0, 2, 4), first occurrence has score 0.5
assert result == 0.5, f"Expected 0.5, got {result}"
print(f"✓ repeat_majority with majority='answer1' = {result}")

# Test any_correct
any_correct_fn = get_repeat_aggregation("any_correct")
result = any_correct_fn([0.0, 0.0, 1.0, 0.0])
assert result == 1.0, f"Expected 1.0, got {result}"
print(f"✓ repeat_any_correct([0.0, 0.0, 1.0, 0.0]) = {result}")

result = any_correct_fn([0.0, 0.5, 0.3])
assert result == 0.0, f"Expected 0.0, got {result}"
print(f"✓ repeat_any_correct([0.0, 0.5, 0.3]) = {result}")

# Test all_correct
all_correct_fn = get_repeat_aggregation("all_correct")
result = all_correct_fn([1.0, 1.0, 1.0])
assert result == 1.0, f"Expected 1.0, got {result}"
print(f"✓ repeat_all_correct([1.0, 1.0, 1.0]) = {result}")

result = all_correct_fn([1.0, 0.0, 1.0])
assert result == 0.0, f"Expected 0.0, got {result}"
print(f"✓ repeat_all_correct([1.0, 0.0, 1.0]) = {result}")

# Test 4: MetricConfig with repeat aggregation
print("\nTesting MetricConfig with repeat_aggregation...")
try:
    from lm_eval.config.metric import MetricConfig

    config = MetricConfig(
        name="test_metric",
        fn=lambda x: x,
        aggregation_fn=lambda x: sum(x) / len(x),
        repeat_aggregation_fn="mean",
    )

    # Test that repeat_aggregation property resolves correctly
    repeat_agg = config.repeat_aggregation
    assert repeat_agg is not None, "repeat_aggregation should not be None"

    # Test compute_repeat_aggregation method
    result = config.compute_repeat_aggregation([0.5, 0.8, 0.3])
    expected = (0.5 + 0.8 + 0.3) / 3
    assert abs(result - expected) < 0.001, f"Expected {expected}, got {result}"
    print(f"✓ MetricConfig.compute_repeat_aggregation([0.5, 0.8, 0.3]) = {result}")

except Exception as e:
    print(f"✗ Failed to test MetricConfig: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✓ All tests passed!")
print("\nRepeat aggregation functionality is working correctly.")
