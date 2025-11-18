"""
Example implementation of the Scorer architecture.

This shows how the Scorer pattern would work in practice with the lm-evaluation-harness.
"""

from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Callable, Generic, TypeVar

from lm_eval.api.instance import Instance
from lm_eval.config.task import TaskConfig, FilterConfig
from lm_eval.config.metric import MetricConfig
from lm_eval.types import GenResult, MCResult, Results

# Type variables for different result types
ResultT = TypeVar('ResultT', bound='Results')


class Scorer(ABC, Generic[ResultT]):
    """
    A Scorer computes metric scores from filtered model outputs.

    Key responsibilities:
    1. Convert filtered outputs into Result objects (MCResult/GenResult)
    2. Apply metrics to compute scores
    3. Handle repeat/aggregation logic at the sample level
    4. Track which filter produced the outputs
    """

    def __init__(self, task_config: TaskConfig):
        self.config = task_config

    @abstractmethod
    def score_instances(
        self,
        instances: list[Instance],
        filter_name: str
    ) -> ResultT:
        """
        Score a group of instances (typically same doc_id) using a specific filter.

        Args:
            instances: List of Instance objects for the same document
            filter_name: Name of the filter whose outputs to use

        Returns:
            Result object with computed scores
        """
        raise NotImplementedError

    def get_metrics(self, filter_name: str) -> list[MetricConfig]:
        """
        Get the metrics to compute for a given filter.

        Args:
            filter_name: Name of the filter

        Returns:
            List of MetricConfig objects to apply
        """
        # Find the FilterConfig for this filter_name
        for filter_config in self.config.get_filters():
            if filter_config.name == filter_name:
                return filter_config.metric_list

        # Fallback to task-level metrics
        return self.config._metric_list


class ProcessResultsScorer(Scorer):
    """
    Scorer that delegates to custom process_results function.

    This handles the legacy/custom scoring path where tasks define their own
    process_results method. It maintains backwards compatibility.
    """

    def __init__(self, task_config: TaskConfig, process_results_fn: Callable):
        super().__init__(task_config)
        self.process_results_fn = process_results_fn

    def score_instances(
        self,
        instances: list[Instance],
        filter_name: str
    ) -> dict[str, Any]:
        """Delegate to custom process_results function."""
        # Create a Result object to extract doc and filtered results
        result = Results.create(instances, filter_name)

        # Call custom process_results
        scores = self.process_results_fn(
            result.doc,
            [result.results]
        )

        return scores or {}

    def get_metrics(self, filter_name: str) -> list[MetricConfig]:
        """
        For custom process_results, we don't know the metrics ahead of time.
        Return empty list and use mean aggregation as default.
        """
        return []


class GenerationScorer(Scorer[GenResult]):
    """
    Scorer for generation tasks (generate_until).

    Handles:
    - String outputs (generated text)
    - Reference-based metrics (BLEU, ROUGE, exact match, etc.)
    - Repeat reduction if configured
    """

    def score_instances(
        self,
        instances: list[Instance],
        filter_name: str
    ) -> GenResult:
        """Score generation instances."""
        # Create GenResult from instances
        gen_result = GenResult.from_instances(instances, filter_name)
        gen_result.repeats = self.config.repeat_cfg.repeats

        # Get metrics for this filter
        metrics = self.get_metrics(filter_name)

        # Compute metrics
        gen_result.scores = self._compute_metrics(gen_result, metrics)

        return gen_result

    def _compute_metrics(
        self,
        gen_result: GenResult,
        metrics: list[MetricConfig]
    ) -> dict[str, list[float]]:
        """Compute all metrics for a GenResult."""
        scores = defaultdict(list)
        gold = gen_result.target

        # Compute metric for each generation
        for generation in gen_result.results:
            for metric in metrics:
                if metric.fn is None:
                    continue

                try:
                    score = metric.fn(
                        references=[gold] if not isinstance(gold, list) else gold,
                        predictions=[generation],
                        **metric.kwargs,
                    )
                except TypeError:
                    # Handle metrics with different interfaces
                    score = metric.fn([gold, generation])

                # Handle metrics that return dicts (multiple metrics at once)
                if isinstance(score, dict):
                    for k, v in score.items():
                        scores[k].append(v)
                else:
                    scores[metric.name].append(score)

        return dict(scores)


class LoglikelihoodScorer(Scorer[MCResult]):
    """
    Scorer for loglikelihood/multiple-choice tasks.

    Handles:
    - Loglikelihood outputs (log probabilities)
    - Choice-based metrics (accuracy, Brier score, etc.)
    - Mutual information if configured
    """

    def score_instances(
        self,
        instances: list[Instance],
        filter_name: str
    ) -> MCResult:
        """Score multiple-choice instances."""
        # Create MCResult from instances
        mc_result = MCResult.from_instances(instances)

        # Get metrics for this filter
        metrics = self.get_metrics(filter_name)

        # Compute metrics
        mc_result.scores = self._compute_metrics(mc_result, metrics)

        return mc_result

    def _compute_metrics(
        self,
        mc_result: MCResult,
        metrics: list[MetricConfig]
    ) -> dict[str, float]:
        """Compute all metrics for an MCResult."""
        scores = {}

        for metric in metrics:
            if metric.fn is None:
                continue

            # MC metrics take the entire MCResult as input
            score = metric.fn(mc_result)

            # Handle metrics that return dicts
            if isinstance(score, dict):
                scores.update(score)
            else:
                scores[metric.name] = score

        return scores


class ScorerFactory:
    """
    Factory for creating the appropriate Scorer based on task configuration.

    Decision tree:
    1. If process_results is defined → ProcessResultsScorer
    2. Elif output_type is generate_until → GenerationScorer
    3. Elif output_type is loglikelihood → LoglikelihoodScorer
    4. Else → raise error
    """

    @staticmethod
    def create_scorer(task_config: TaskConfig) -> Scorer:
        """Create appropriate scorer for task configuration."""

        # Check for custom process_results first
        if callable(task_config.process_results):
            return ProcessResultsScorer(task_config, task_config.process_results)

        # Create type-specific scorer
        output_type = task_config.output_type

        if output_type == "generate_until":
            return GenerationScorer(task_config)
        elif output_type in ("loglikelihood", "multiple_choice"):
            return LoglikelihoodScorer(task_config)
        elif output_type == "loglikelihood_rolling":
            # Could add PerplexityScorer here
            raise NotImplementedError(f"Scorer for {output_type} not yet implemented")
        else:
            raise ValueError(f"Unknown output_type: {output_type}")


# Example: How this would be used in Task class
class Task(ABC):
    """Base task class with Scorer integration."""

    def __init__(self, config: TaskConfig):
        self.config = config
        self._instances: list[Instance] = []
        self._filters: list[FilterConfig] = config.get_filters()
        self._sample_scores: dict[tuple[str, str], list] = defaultdict(list)

        # Create scorer during initialization
        self._scorer: Scorer = ScorerFactory.create_scorer(config)

    def process_instances(self, instances: list[Instance] | None = None):
        """
        Process instances to compute metrics.

        This is now a simple orchestration method that:
        1. Groups instances by doc_id
        2. For each filter, delegates scoring to the Scorer
        3. Collects results
        """
        _instances = self.sort_instances(instances or self._instances)
        if not _instances:
            return {}

        results = defaultdict(list)

        # Iterate over filters
        for filter_config in self._filters:
            filter_name = filter_config.name

            # Score each document's instances
            for doc_instances in _instances.values():
                # Delegate to scorer
                scored_result = self._scorer.score_instances(
                    doc_instances,
                    filter_name
                )

                # Collect scores
                if isinstance(scored_result, dict):
                    # ProcessResultsScorer returns dict directly
                    for metric, value in scored_result.items():
                        results[(metric, filter_name)].append(value)
                else:
                    # Type-specific scorers return Result objects
                    for metric, score in scored_result.scores.items():
                        results[(metric, filter_name)].append(score)

        self._sample_scores = results
        return results


# Example: Custom scorer extension
class RewardModelScorer(GenerationScorer):
    """
    Custom scorer that uses a reward model to score generations.

    This shows how easy it is to extend the base scorers.
    """

    def __init__(self, task_config: TaskConfig, reward_model_path: str):
        super().__init__(task_config)
        # Load your reward model here
        # self.reward_model = load_reward_model(reward_model_path)

    def _compute_metrics(
        self,
        gen_result: GenResult,
        metrics: list[MetricConfig]
    ) -> dict[str, list[float]]:
        """Compute metrics including reward model scores."""
        # First compute standard metrics
        scores = super()._compute_metrics(gen_result, metrics)

        # Add reward model scores
        reward_scores = []
        for generation in gen_result.results:
            # Example: score = self.reward_model.score(generation)
            # For now, just placeholder
            score = 0.0  # Replace with actual reward model call
            reward_scores.append(score)

        scores['reward_model'] = reward_scores

        return scores


# Example: LLM-as-Judge scorer
class LLMJudgeScorer(GenerationScorer):
    """
    Scorer that uses an LLM to judge generation quality.

    Useful for complex criteria that are hard to capture with traditional metrics.
    """

    def __init__(self, task_config: TaskConfig, judge_model_name: str):
        super().__init__(task_config)
        self.judge_model_name = judge_model_name
        # self.judge_lm = get_model(judge_model_name)

    def _compute_metrics(
        self,
        gen_result: GenResult,
        metrics: list[MetricConfig]
    ) -> dict[str, list[float]]:
        """Compute metrics including LLM judge scores."""
        # First compute standard metrics
        scores = super()._compute_metrics(gen_result, metrics)

        # Add LLM judge scores
        judge_scores = []
        for generation in gen_result.results:
            # Create prompt for judge
            prompt = self._create_judge_prompt(generation, gen_result.target)

            # Get score from judge LLM
            # score = self.judge_lm.evaluate(prompt)
            score = 0.0  # Placeholder
            judge_scores.append(score)

        scores['llm_judge'] = judge_scores

        return scores

    def _create_judge_prompt(self, generation: str, reference: str) -> str:
        """Create a prompt for the judge LLM."""
        return f"""Rate the quality of the following generation on a scale of 0-10.

Reference answer: {reference}
Generated answer: {generation}

Rating (0-10):"""


if __name__ == "__main__":
    print("Scorer architecture example loaded successfully!")
    print("\nKey components:")
    print("- Scorer (base class)")
    print("- ProcessResultsScorer (for custom process_results)")
    print("- GenerationScorer (for generate_until tasks)")
    print("- LoglikelihoodScorer (for loglikelihood/MC tasks)")
    print("- ScorerFactory (creates appropriate scorer)")
    print("\nExtension examples:")
    print("- RewardModelScorer")
    print("- LLMJudgeScorer")
