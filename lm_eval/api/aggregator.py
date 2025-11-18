"""
Aggregator classes for computing group-wide metrics from task results.

The Aggregator pattern separates hierarchy management (handled by Group classes)
from metric aggregation logic. This makes it easy to add new aggregation strategies
beyond simple mean (harmonic mean, geometric mean, pass@k, custom functions, etc.)
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from lm_eval.api.group import Group, GroupConfig


class Aggregator(ABC):
    """
    An Aggregator computes group-wide metrics from task results.

    Responsibilities:
    - Collect metrics from child tasks/groups
    - Apply aggregation function (mean, weighted mean, harmonic, etc.)
    - Handle different metric types appropriately
    - Support filter-specific aggregation

    This is the base class - subclasses implement specific aggregation strategies.
    """

    def __init__(self, config: "GroupConfig"):
        """
        Initialize aggregator with group configuration.

        Args:
            config: GroupConfig containing aggregation settings
        """
        self.config = config
        self.agg_metric_configs = config.aggregate_metric_list or []

    @abstractmethod
    def aggregate(
        self, group: "Group", task_results: dict[str, dict[str, float]]
    ) -> dict[str, float]:
        """
        Aggregate task results into group metrics.

        Args:
            group: The group to aggregate for
            task_results: Dict mapping task_name -> {metric: value}

        Returns:
            Dict of aggregated metrics for the group
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement aggregate"
        )


class NoOpAggregator(Aggregator):
    """
    Aggregator that does nothing.

    Used for groups that don't define aggregate_metric_list.
    """

    def aggregate(
        self, group: "Group", task_results: dict[str, dict[str, float]]
    ) -> dict[str, float]:
        """Return empty dict - no aggregation configured."""
        return {}


class MeanAggregator(Aggregator):
    """
    Aggregates metrics using (weighted) arithmetic mean.

    This is the most common aggregation strategy and matches the current
    behavior of lm-evaluation-harness.

    Supports:
    - Weighted mean (by sample size)
    - Unweighted mean
    - Per-filter aggregation
    """

    def aggregate(
        self, group: "Group", task_results: dict[str, dict[str, float]]
    ) -> dict[str, float]:
        """
        Compute weighted or unweighted mean across tasks.

        Args:
            group: Group to aggregate
            task_results: Task results dict

        Returns:
            Dict of aggregated group metrics
        """
        if not self.agg_metric_configs:
            return {}  # No aggregation configured

        group_metrics = {}
        tasks = group.get_all_tasks()

        for agg_config in self.agg_metric_configs:
            metric_name = agg_config.metric
            weight_by_size = agg_config.weight_by_size
            filter_list = agg_config.filter_list

            # Handle both single filter and list of filters
            if isinstance(filter_list, str):
                filter_list = [filter_list]

            # Aggregate for each filter
            for filter_name in filter_list:
                # Build metric key (format: "metric,filter")
                metric_key = f"{metric_name},{filter_name}"

                # Collect metric values and sizes
                values = []
                weights = []

                for task in tasks:
                    # Get task name - handle both Task objects and strings
                    task_name = getattr(task, "task_name", None) or getattr(
                        task, "name", str(task)
                    )

                    if task_name not in task_results:
                        continue

                    # Get metric value for this filter
                    if metric_key in task_results[task_name]:
                        values.append(task_results[task_name][metric_key])

                        # Get sample size for weighting
                        if weight_by_size:
                            weights.append(
                                task_results[task_name].get("samples", 1)
                            )
                        else:
                            weights.append(1)

                # Compute weighted mean
                if values:
                    group_metrics[metric_key] = sum(
                        v * w for v, w in zip(values, weights)
                    ) / sum(weights)

        return group_metrics


class HarmonicMeanAggregator(Aggregator):
    """
    Aggregates using harmonic mean.

    Useful for metrics like F1-score where harmonic mean is more appropriate
    than arithmetic mean, especially when dealing with imbalanced datasets.

    Formula: n / sum(1/x_i)

    Note: Only works with positive values. Returns 0 if any value is 0.
    """

    def aggregate(
        self, group: "Group", task_results: dict[str, dict[str, float]]
    ) -> dict[str, float]:
        """
        Compute harmonic mean across tasks.

        Args:
            group: Group to aggregate
            task_results: Task results dict

        Returns:
            Dict of aggregated group metrics
        """
        group_metrics = {}
        tasks = group.get_all_tasks()

        for agg_config in self.agg_metric_configs:
            metric_name = agg_config.metric
            filter_list = agg_config.filter_list

            if isinstance(filter_list, str):
                filter_list = [filter_list]

            for filter_name in filter_list:
                metric_key = f"{metric_name},{filter_name}"

                values = []
                for task in tasks:
                    task_name = getattr(task, "task_name", None) or getattr(
                        task, "name", str(task)
                    )

                    if (
                        task_name in task_results
                        and metric_key in task_results[task_name]
                    ):
                        values.append(task_results[task_name][metric_key])

                # Harmonic mean: n / sum(1/x_i)
                # Only valid for positive values
                if values and all(v > 0 for v in values):
                    group_metrics[metric_key] = len(values) / sum(
                        1 / v for v in values
                    )
                elif values:
                    # If any value is 0, harmonic mean is 0
                    group_metrics[metric_key] = 0.0

        return group_metrics


class GeometricMeanAggregator(Aggregator):
    """
    Aggregates using geometric mean.

    Useful for metrics that are multiplicative in nature or when you want
    to emphasize lower scores more than arithmetic mean would.

    Formula: (product of all x_i) ^ (1/n)

    Note: Only works with non-negative values.
    """

    def aggregate(
        self, group: "Group", task_results: dict[str, dict[str, float]]
    ) -> dict[str, float]:
        """
        Compute geometric mean across tasks.

        Args:
            group: Group to aggregate
            task_results: Task results dict

        Returns:
            Dict of aggregated group metrics
        """
        import math

        group_metrics = {}
        tasks = group.get_all_tasks()

        for agg_config in self.agg_metric_configs:
            metric_name = agg_config.metric
            filter_list = agg_config.filter_list

            if isinstance(filter_list, str):
                filter_list = [filter_list]

            for filter_name in filter_list:
                metric_key = f"{metric_name},{filter_name}"

                values = []
                for task in tasks:
                    task_name = getattr(task, "task_name", None) or getattr(
                        task, "name", str(task)
                    )

                    if (
                        task_name in task_results
                        and metric_key in task_results[task_name]
                    ):
                        values.append(task_results[task_name][metric_key])

                # Geometric mean: (product of x_i) ^ (1/n)
                if values and all(v >= 0 for v in values):
                    # Use log to avoid overflow
                    log_sum = sum(math.log(v + 1e-10) for v in values)
                    group_metrics[metric_key] = math.exp(log_sum / len(values))

        return group_metrics


class PassAtKAggregator(Aggregator):
    """
    Aggregates using pass@k metric for code generation.

    Computes the probability that at least one of k samples passes.

    Formula: pass@k = 1 - C(n-c, k) / C(n, k)
    where n = total samples, c = correct samples, k = number to consider

    This is commonly used for code generation benchmarks like HumanEval.
    """

    def __init__(self, config: "GroupConfig", k: int = 1):
        """
        Initialize pass@k aggregator.

        Args:
            config: GroupConfig
            k: Number of samples to consider (default: 1)
        """
        super().__init__(config)
        self.k = k

    def aggregate(
        self, group: "Group", task_results: dict[str, dict[str, float]]
    ) -> dict[str, float]:
        """
        Compute pass@k across tasks.

        Args:
            group: Group to aggregate
            task_results: Task results dict

        Returns:
            Dict of aggregated group metrics
        """
        # This is a simplified implementation
        # Full implementation would need access to sample-level data
        # For now, just compute mean as a placeholder
        group_metrics = {}
        tasks = group.get_all_tasks()

        for agg_config in self.agg_metric_configs:
            metric_name = agg_config.metric
            filter_list = agg_config.filter_list

            if isinstance(filter_list, str):
                filter_list = [filter_list]

            for filter_name in filter_list:
                metric_key = f"{metric_name},{filter_name}"

                values = []
                for task in tasks:
                    task_name = getattr(task, "task_name", None) or getattr(
                        task, "name", str(task)
                    )

                    if (
                        task_name in task_results
                        and metric_key in task_results[task_name]
                    ):
                        values.append(task_results[task_name][metric_key])

                if values:
                    # Simplified: just average the pass@k values
                    # TODO: Implement proper pass@k aggregation with sample data
                    group_metrics[metric_key] = sum(values) / len(values)

        return group_metrics


class CustomAggregator(Aggregator):
    """
    Allows user-defined aggregation functions.

    Useful for domain-specific metrics or complex aggregation logic
    that doesn't fit into standard patterns.

    The user-provided function receives the group and task results,
    and can implement any custom aggregation logic.
    """

    def __init__(self, config: "GroupConfig", agg_fn: Callable):
        """
        Initialize with custom aggregation function.

        Args:
            config: GroupConfig
            agg_fn: Callable that takes (group, task_results) and returns metrics dict
        """
        super().__init__(config)
        self.agg_fn = agg_fn

    def aggregate(
        self, group: "Group", task_results: dict[str, dict[str, float]]
    ) -> dict[str, float]:
        """
        Delegate to user-provided function.

        Args:
            group: Group to aggregate
            task_results: Task results dict

        Returns:
            Dict of aggregated group metrics from custom function
        """
        return self.agg_fn(group, task_results)


class AggregatorFactory:
    """
    Factory for creating appropriate Aggregator based on group configuration.

    This factory examines the group config and creates the right aggregator
    type (mean, harmonic, geometric, pass@k, custom) based on the configuration.
    """

    @staticmethod
    def create_aggregator(config: "GroupConfig") -> Aggregator:
        """
        Create aggregator from group configuration.

        Args:
            config: GroupConfig containing aggregation settings

        Returns:
            Appropriate Aggregator instance

        Raises:
            ValueError: If aggregation type is unknown
        """
        if not config.aggregate_metric_list:
            return NoOpAggregator(config)  # No aggregation configured

        # Check first aggregation config to determine type
        first_agg = config.aggregate_metric_list[0]
        agg_type = first_agg.aggregation

        if agg_type == "mean":
            return MeanAggregator(config)
        elif agg_type == "harmonic_mean":
            return HarmonicMeanAggregator(config)
        elif agg_type == "geometric_mean":
            return GeometricMeanAggregator(config)
        elif agg_type == "pass@k":
            # Extract k from kwargs if provided
            k = first_agg.kwargs.get("k", 1) if hasattr(first_agg, "kwargs") else 1
            return PassAtKAggregator(config, k=k)
        elif callable(agg_type):
            return CustomAggregator(config, agg_fn=agg_type)
        else:
            raise ValueError(
                f"Unknown aggregation type: {agg_type}. "
                f"Expected one of: mean, harmonic_mean, geometric_mean, pass@k, or a callable"
            )
