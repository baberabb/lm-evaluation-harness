"""
Simple integration test for the Group architecture.

This tests that:
1. Groups can be created with configs
2. StandardGroup and TagGroup work correctly
3. Aggregators compute metrics properly
4. GroupManager coordinates the hierarchy
5. Tasks can track their groups
"""


def test_group_creation():
    """Test basic group creation."""
    try:
        from lm_eval.api.group import GroupConfig, StandardGroup, TagGroup

        # Create a group config
        config = GroupConfig(
            group="math",
            group_alias="Mathematics Tasks",
            task=["gsm8k", "math_qa"],
            aggregate_metric_list=[{"metric": "acc", "aggregation": "mean"}],
        )

        # Create a standard group
        group = StandardGroup(config)
        assert group.name == "math"
        assert group.alias == "Mathematics Tasks"
        print("✓ StandardGroup created successfully")

        # Create a tag group
        tag = TagGroup("reasoning", "Reasoning tasks")
        assert tag.name == "reasoning"
        assert tag.metadata["type"] == "tag"
        print("✓ TagGroup created successfully")

        return True
    except Exception as e:
        print(f"✗ Group creation failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_aggregators():
    """Test aggregator creation and computation."""
    try:
        from lm_eval.api.aggregator import (
            MeanAggregator,
            HarmonicMeanAggregator,
            AggregatorFactory,
        )
        from lm_eval.api.group import GroupConfig, StandardGroup

        # Create group with mean aggregation
        config = GroupConfig(
            group="test_group",
            task=[],
            aggregate_metric_list=[
                {
                    "metric": "acc",
                    "aggregation": "mean",
                    "weight_by_size": True,
                    "filter_list": "none",
                }
            ],
        )

        aggregator = AggregatorFactory.create_aggregator(config)
        assert isinstance(aggregator, MeanAggregator)
        print("✓ MeanAggregator created via factory")

        # Test harmonic mean aggregator
        config2 = GroupConfig(
            group="test_group2",
            task=[],
            aggregate_metric_list=[
                {"metric": "f1", "aggregation": "harmonic_mean", "filter_list": "none"}
            ],
        )

        aggregator2 = AggregatorFactory.create_aggregator(config2)
        assert isinstance(aggregator2, HarmonicMeanAggregator)
        print("✓ HarmonicMeanAggregator created via factory")

        return True
    except Exception as e:
        print(f"✗ Aggregator test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_group_hierarchy():
    """Test group hierarchy and task tracking."""
    try:
        from lm_eval.api.group import GroupConfig, StandardGroup

        # Create parent group
        parent_config = GroupConfig(
            group="reasoning",
            group_alias="Reasoning Benchmarks",
            task=["math_group"],
            aggregate_metric_list=[{"metric": "acc", "aggregation": "mean"}],
        )
        parent_group = StandardGroup(parent_config)

        # Create child group
        child_config = GroupConfig(
            group="math_group",
            group_alias="Math Tasks",
            task=[],
            aggregate_metric_list=[{"metric": "acc", "aggregation": "mean"}],
        )
        child_group = StandardGroup(child_config)

        # Link them
        parent_group.add_child(child_group)

        # Test hierarchy
        assert child_group.parent == parent_group
        assert child_group in parent_group.children
        assert parent_group.depth() == 0
        assert child_group.depth() == 1
        assert not parent_group.is_leaf()

        print("✓ Group hierarchy works correctly")

        # Create mock task
        class MockTask:
            def __init__(self, name):
                self.task_name = name
                self.name = name
                self._groups = []
                self._tags = []

        task = MockTask("gsm8k")
        child_group.add_child(task)

        # Test task tracking
        assert task in child_group.children
        assert child_group in task._groups
        assert child_group.get_all_tasks() == [task]
        assert parent_group.get_all_tasks() == [task]  # Recursive

        print("✓ Task-group bidirectional linking works")

        return True
    except Exception as e:
        print(f"✗ Hierarchy test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_group_manager():
    """Test GroupManager coordination."""
    try:
        from lm_eval.group_manager import GroupManager
        from lm_eval.api.group import GroupConfig

        manager = GroupManager()

        # Register some groups
        config1 = GroupConfig(
            group="reasoning",
            task=["math_group"],
            aggregate_metric_list=[{"metric": "acc", "aggregation": "mean"}],
        )

        config2 = GroupConfig(
            group="math_group",
            task=["gsm8k"],
            aggregate_metric_list=[{"metric": "acc", "aggregation": "mean"}],
        )

        # Build hierarchy
        manager.build_hierarchy({"reasoning": config1, "math_group": config2})

        # Test access
        assert "reasoning" in manager.groups
        assert "math_group" in manager.groups
        assert len(manager.root_groups) == 1
        assert manager.root_groups[0].name == "reasoning"

        print("✓ GroupManager builds hierarchy correctly")

        # Test traversal
        visited = []
        manager.traverse_hierarchy(lambda node: visited.append(getattr(node, "name", None)))
        assert "reasoning" in visited
        assert "math_group" in visited

        print("✓ GroupManager traversal works")

        return True
    except Exception as e:
        print(f"✗ GroupManager test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_metric_computation():
    """Test group metric computation."""
    try:
        from lm_eval.api.group import GroupConfig, StandardGroup

        # Create group
        config = GroupConfig(
            group="test_group",
            task=[],
            aggregate_metric_list=[
                {
                    "metric": "acc",
                    "aggregation": "mean",
                    "weight_by_size": False,
                    "filter_list": "none",
                }
            ],
        )
        group = StandardGroup(config)

        # Create mock tasks
        class MockTask:
            def __init__(self, name):
                self.task_name = name
                self.name = name
                self._groups = []
                self._tags = []

        task1 = MockTask("task1")
        task2 = MockTask("task2")
        group.add_child(task1)
        group.add_child(task2)

        # Mock task results
        task_results = {
            "task1": {"acc,none": 0.8, "samples": 100},
            "task2": {"acc,none": 0.6, "samples": 50},
        }

        # Compute group metrics
        group_metrics = group.compute_metrics(task_results)

        # Check unweighted mean: (0.8 + 0.6) / 2 = 0.7
        assert "acc,none" in group_metrics
        assert abs(group_metrics["acc,none"] - 0.7) < 0.001

        print("✓ Group metric computation works (unweighted mean)")

        # Test weighted mean
        config2 = GroupConfig(
            group="test_group2",
            task=[],
            aggregate_metric_list=[
                {
                    "metric": "acc",
                    "aggregation": "mean",
                    "weight_by_size": True,
                    "filter_list": "none",
                }
            ],
        )
        group2 = StandardGroup(config2)
        group2.add_child(task1)
        group2.add_child(task2)

        group_metrics2 = group2.compute_metrics(task_results)

        # Weighted mean: (0.8*100 + 0.6*50) / (100+50) = 110/150 = 0.733...
        expected = (0.8 * 100 + 0.6 * 50) / 150
        assert abs(group_metrics2["acc,none"] - expected) < 0.001

        print("✓ Group metric computation works (weighted mean)")

        return True
    except Exception as e:
        print(f"✗ Metric computation test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Group Architecture Implementation")
    print("=" * 60)

    tests = [
        ("Group Creation", test_group_creation),
        ("Aggregators", test_aggregators),
        ("Group Hierarchy", test_group_hierarchy),
        ("GroupManager", test_group_manager),
        ("Metric Computation", test_metric_computation),
    ]

    results = []
    for name, test_func in tests:
        print(f"\n{name}:")
        print("-" * 60)
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ {name} crashed: {e}")
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
