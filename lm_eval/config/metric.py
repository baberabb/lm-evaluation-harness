from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any


@dataclass
class MetricConfig:
    """Encapsulates information about a single metric.

    This is the canonical representation for metrics used throughout lm_eval,
    both in the registry and when parsing from YAML configs.
    """

    name: str
    fn: Callable = lambda x: x
    kwargs: Mapping[str, Any] = field(default_factory=dict)
    aggregation_fn: Callable = lambda x: x
    repeat_aggregation_fn: Callable | str | None = None  # NEW: for aggregating across repeats
    is_bypass: bool = False
    higher_is_better: bool = True
    hf_evaluate: bool = False
    output_type: str = "generate_until"
    requires: list[str] | None = None

    # Backward compatibility aliases
    @property
    def compute(self) -> Callable | None:
        """Alias for fn to maintain backward compatibility with MetricSpec."""
        return self.fn

    @compute.setter
    def compute(self, value: Callable) -> None:
        """Setter for compute to maintain backward compatibility."""
        self.fn = value

    @property
    def aggregate(self) -> Callable | None:
        """Alias for aggregation_fn to maintain backward compatibility with MetricSpec."""
        return self.aggregation_fn

    @aggregate.setter
    def aggregate(self, value: Callable) -> None:
        """Setter for aggregate to maintain backward compatibility."""
        self.aggregation_fn = value

    @cached_property
    def metric_name(self) -> str:
        return self.name

    @cached_property
    def aggregation(self) -> Callable[..., Any] | None:
        from lm_eval.api.registry import get_aggregation

        if self.aggregation_fn is None:
            try:
                return get_aggregation(self.name)
            except (KeyError, ImportError):
                return None
        return self.aggregation_fn

    @cached_property
    def _higher_is_better(self) -> bool | None:
        from lm_eval.api.registry import is_higher_better

        if self.higher_is_better is None:
            try:
                return is_higher_better(self.name)
            except (KeyError, ImportError):
                return None
        return self.higher_is_better

    @cached_property
    def repeat_aggregation(self) -> Callable[..., Any] | None:
        """Resolve repeat aggregation function from registry if needed."""
        from lm_eval.api.registry import get_repeat_aggregation

        if self.repeat_aggregation_fn is None:
            # Default to "first" for backward compatibility
            try:
                return get_repeat_aggregation("first")
            except (KeyError, ImportError):
                return None
        elif isinstance(self.repeat_aggregation_fn, str):
            # Lookup in registry
            try:
                return get_repeat_aggregation(self.repeat_aggregation_fn)
            except (KeyError, ImportError):
                return None
        else:
            # Already a callable
            return self.repeat_aggregation_fn

    def compute_metric(self, *args, **kwargs) -> Any:
        """Calculates the metric using the provided function and arguments."""
        if self.fn is None:
            raise ValueError(f"Metric function for {self.name} is not defined.")
        return self.fn(*args, **{**(self.kwargs or {}), **kwargs})

    def compute_aggregation(self, *args, **kwargs) -> Any:
        """Computes the aggregation of the metric values."""
        if self.aggregation_fn is None:
            raise ValueError(f"Aggregation function for {self.name} is not defined.")
        return self.aggregation_fn(*args, **kwargs)

    def compute_repeat_aggregation(self, scores: list[float], **kwargs) -> float:
        """Computes the aggregation across repeat generations."""
        repeat_agg_fn = self.repeat_aggregation
        if repeat_agg_fn is None:
            # Fallback to first if not defined
            return scores[0] if scores else 0.0
        return repeat_agg_fn(scores, **kwargs)
