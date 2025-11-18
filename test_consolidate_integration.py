"""
Test the new consolidate_group_results_v2 with GroupManager.
"""

from collections import defaultdict

from lm_eval.api.group import ConfigurableGroup, GroupConfig
from lm_eval.evaluator_utils import consolidate_group_results_v2


# Mock Task class to avoid import dependencies
class MockTask:
    def __init__(self, name):
        self.task_name = name
        self.name = name
        self._groups = []
        self._tags = []


def test_consolidate_with_simple_group():
    """Test consolidate_group_results_v2 with a simple group."""
    # Create mock tasks
    task1 = MockTask("task1")
    task2 = MockTask("task2")

    # Create group config
    group_config = ConfigurableGroup(
        config={
            "group": "test_group",
            "group_alias": "Test Group",
            "task": ["task1", "task2"],
            "aggregate_metric_list": [
                {"metric": "acc", "aggregation": "mean", "filter_list": "none"}
            ],
        }
    )

    # Create task_dict structure
    task_dict = {group_config: {"task1": task1, "task2": task2}}

    # Create mock results
    results = {
        "task1": {"acc,none": 0.8, "samples": 100},
        "task2": {"acc,none": 0.6, "samples": 50},
    }

    versions = {}

    # Run consolidation
    results, versions, show_group_table, task_aggregation_list = (
        consolidate_group_results_v2(results, versions, task_dict)
    )

    # Check results
    assert "test_group" in results
    assert "acc,none" in results["test_group"]

    # Unweighted mean: (0.8 + 0.6) / 2 = 0.7
    expected = 0.7
    assert abs(results["test_group"]["acc,none"] - expected) < 0.001

    # Check samples
    assert results["test_group"]["samples"] == 150

    # Check show_group_table
    assert show_group_table is True

    # Check task_aggregation_list
    assert "test_group" in task_aggregation_list
    assert set(task_aggregation_list["test_group"]) == {"task1", "task2"}

    print("✓ Simple group consolidation works!")


def test_consolidate_with_weighted_mean():
    """Test consolidate_group_results_v2 with weighted mean."""
    # Create mock tasks
    task1 = MockTask("task1")
    task2 = MockTask("task2")

    # Create group config with weight_by_size
    group_config = ConfigurableGroup(
        config={
            "group": "test_group",
            "task": ["task1", "task2"],
            "aggregate_metric_list": [
                {
                    "metric": "acc",
                    "aggregation": "mean",
                    "weight_by_size": True,
                    "filter_list": "none",
                }
            ],
        }
    )

    # Create task_dict structure
    task_dict = {group_config: {"task1": task1, "task2": task2}}

    # Create mock results
    results = {
        "task1": {"acc,none": 0.8, "samples": 100},
        "task2": {"acc,none": 0.6, "samples": 50},
    }

    versions = {}

    # Run consolidation
    results, versions, show_group_table, task_aggregation_list = (
        consolidate_group_results_v2(results, versions, task_dict)
    )

    # Weighted mean: (0.8*100 + 0.6*50) / 150 = 110/150 = 0.733...
    expected = (0.8 * 100 + 0.6 * 50) / 150
    assert abs(results["test_group"]["acc,none"] - expected) < 0.001

    print("✓ Weighted mean consolidation works!")


def test_consolidate_with_harmonic_mean():
    """Test consolidate_group_results_v2 with harmonic mean."""
    # Create mock tasks
    task1 = MockTask("task1")
    task2 = MockTask("task2")

    # Create group config with harmonic_mean
    group_config = ConfigurableGroup(
        config={
            "group": "test_group",
            "task": ["task1", "task2"],
            "aggregate_metric_list": [
                {
                    "metric": "f1",
                    "aggregation": "harmonic_mean",
                    "filter_list": "none",
                }
            ],
        }
    )

    # Create task_dict structure
    task_dict = {group_config: {"task1": task1, "task2": task2}}

    # Create mock results
    results = {
        "task1": {"f1,none": 0.8, "samples": 100},
        "task2": {"f1,none": 0.6, "samples": 50},
    }

    versions = {}

    # Run consolidation
    results, versions, show_group_table, task_aggregation_list = (
        consolidate_group_results_v2(results, versions, task_dict)
    )

    # Harmonic mean: 2 / (1/0.8 + 1/0.6) = 2 / (1.25 + 1.667) = 2 / 2.917 = 0.686
    expected = 2 / (1 / 0.8 + 1 / 0.6)
    assert abs(results["test_group"]["f1,none"] - expected) < 0.001

    print("✓ Harmonic mean consolidation works!")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing consolidate_group_results_v2 Integration")
    print("=" * 60)

    tests = [
        ("Simple group", test_consolidate_with_simple_group),
        ("Weighted mean", test_consolidate_with_weighted_mean),
        ("Harmonic mean", test_consolidate_with_harmonic_mean),
    ]

    results = []
    for name, test_func in tests:
        print(f"\n{name}:")
        print("-" * 60)
        try:
            test_func()
            results.append((name, True))
        except Exception as e:
            print(f"✗ {name} failed: {e}")
            import traceback

            traceback.print_exc()
            results.append((name, False))

    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)

    for name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {name}: {status}")

    all_passed = all(result for _, result in results)
    print("\n" + ("=" * 60))

    if all_passed:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
