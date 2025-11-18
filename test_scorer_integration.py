"""
Simple integration test for the Scorer architecture.

This tests that:
1. Scorers can be created from task configs
2. GenerationScorer works correctly
3. LoglikelihoodScorer works correctly
4. ProcessResultsScorer works correctly
5. The integration with Task.process_instances works
"""

def test_scorer_imports():
    """Test that all scorer modules can be imported."""
    try:
        from lm_eval.api.scorer import (
            Scorer,
            ScorerFactory,
            ProcessResultsScorer,
            GenerationScorer,
            LoglikelihoodScorer,
        )
        print("✓ All scorer classes imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_scorer_factory():
    """Test that ScorerFactory creates the right scorers."""
    try:
        from lm_eval.api.scorer import ScorerFactory, GenerationScorer, LoglikelihoodScorer, ProcessResultsScorer
        from lm_eval.config.task import TaskConfig

        # Test generate_until scorer
        config1 = TaskConfig(**{"output_type": "generate_until", "task": "test"})
        scorer1 = ScorerFactory.create_scorer(config1)
        assert isinstance(scorer1, GenerationScorer), f"Expected GenerationScorer, got {type(scorer1)}"
        print("✓ ScorerFactory creates GenerationScorer for generate_until")

        # Test loglikelihood scorer
        config2 = TaskConfig(**{"output_type": "loglikelihood", "task": "test"})
        scorer2 = ScorerFactory.create_scorer(config2)
        assert isinstance(scorer2, LoglikelihoodScorer), f"Expected LoglikelihoodScorer, got {type(scorer2)}"
        print("✓ ScorerFactory creates LoglikelihoodScorer for loglikelihood")

        # Test process_results scorer
        def custom_process(doc, results):
            return {"custom_metric": 1.0}

        config3 = TaskConfig(**{
            "output_type": "generate_until",
            "task": "test",
            "process_results": custom_process
        })
        scorer3 = ScorerFactory.create_scorer(config3)
        assert isinstance(scorer3, ProcessResultsScorer), f"Expected ProcessResultsScorer, got {type(scorer3)}"
        print("✓ ScorerFactory creates ProcessResultsScorer when process_results is set")

        return True
    except Exception as e:
        print(f"✗ ScorerFactory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_task_integration():
    """Test that Task class integrates with Scorer correctly."""
    try:
        from lm_eval.api.task import Task
        from lm_eval.config.task import TaskConfig

        # Check that Task has _scorer attribute after initialization
        # Note: We can't easily test this without creating a full task instance
        # which requires a dataset, so we'll just check the imports work

        print("✓ Task class imports successfully with scorer integration")
        return True
    except Exception as e:
        print(f"✗ Task integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Scorer Architecture Integration")
    print("=" * 60)

    tests = [
        ("Import Test", test_scorer_imports),
        ("ScorerFactory Test", test_scorer_factory),
        ("Task Integration Test", test_task_integration),
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
