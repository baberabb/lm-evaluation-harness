"""
Scorer classes for computing metrics from filtered model outputs.

The Scorer architecture separates the concerns of filtering (transforming outputs)
from scoring (computing metrics). This makes the codebase more modular, testable,
and extensible.

Key classes:
- Scorer: Abstract base class defining the scorer interface
- ProcessResultsScorer: For custom process_results functions (backwards compatibility)
- GenerationScorer: For generate_until tasks (text generation)
- LoglikelihoodScorer: For loglikelihood/multiple-choice tasks
- ScorerFactory: Creates the appropriate scorer based on task configuration
"""

from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, Callable, Generic, TypeVar

from lm_eval.api.instance import Instance
from lm_eval.config.metric import MetricConfig
from lm_eval.config.task import TaskConfig
from lm_eval.types import GenResult, MCResult, Results

# Type variable for different result types
ResultT = TypeVar("ResultT", bound="Results")


class Scorer(ABC, Generic[ResultT]):
    """
    A Scorer computes metric scores from filtered model outputs.

    Responsibilities:
    1. Convert filtered outputs into Result objects (MCResult/GenResult)
    2. Apply metrics to compute scores
    3. Handle repeat/aggregation logic at the sample level
    4. Track which filter produced the outputs

    The Scorer is type-aware, ensuring that the right kind of Result object
    is created for each task type (generation vs. multiple-choice).
    """

    def __init__(self, task_config: TaskConfig):
        """
        Initialize scorer with task configuration.

        Args:
            task_config: Configuration object containing task settings, metrics, filters
        """
        self.config = task_config

    @abstractmethod
    def score_instances(
        self, instances: list[Instance], filter_name: str
    ) -> ResultT | dict[str, Any]:
        """
        Score a group of instances (typically same doc_id) using a specific filter.

        This is the main scoring method that subclasses must implement.
        It should:
        1. Extract filtered outputs from instances
        2. Create appropriate Result object
        3. Apply metrics to compute scores
        4. Return scored result

        Args:
            instances: List of Instance objects for the same document
            filter_name: Name of the filter whose outputs to use

        Returns:
            Result object with computed scores, or dict of scores for ProcessResultsScorer
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement score_instances"
        )

    def get_metrics(self, filter_name: str) -> list[MetricConfig]:
        """
        Get the metrics to compute for a given filter.

        The default implementation looks up the filter by name in the task config
        and returns its metric list. If not found, falls back to task-level metrics.

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
    process_results method. It maintains backwards compatibility with existing
    task configurations that override process_results.

    The ProcessResultsScorer doesn't know what metrics it will produce ahead of time,
    as that's determined by the custom process_results function.
    """

    def __init__(self, task_config: TaskConfig, process_results_fn: Callable):
        """
        Initialize with custom process_results function.

        Args:
            task_config: Task configuration
            process_results_fn: Custom function that takes (doc, results) and returns scores
        """
        super().__init__(task_config)
        self.process_results_fn = process_results_fn

    def score_instances(
        self, instances: list[Instance], filter_name: str
    ) -> dict[str, Any]:
        """
        Delegate to custom process_results function.

        Args:
            instances: List of instances for the same doc
            filter_name: Name of the filter to use

        Returns:
            Dictionary of metric_name -> score from custom function
        """
        # Extract doc from instances (all instances share the same doc)
        doc = instances[0].doc

        # Create a Result object to extract filtered results
        result = Results.create(instances, filter_name)

        # Call custom process_results with doc and filtered results
        scores = self.process_results_fn(
            doc,
            [result.results],
        )

        # Return scores or empty dict if None
        return scores or {}

    def get_metrics(self, filter_name: str) -> list[MetricConfig]:
        """
        For custom process_results, we don't know the metrics ahead of time.

        Returns:
            Empty list (metrics determined dynamically by process_results)
        """
        return []


class GenerationScorer(Scorer[GenResult]):
    """
    Scorer for generation tasks (generate_until).

    Handles:
    - String outputs (generated text)
    - Reference-based metrics (BLEU, ROUGE, exact match, etc.)
    - Multiple generations per sample (e.g., from temperature sampling)
    - Repeat reduction if configured

    The GenerationScorer creates GenResult objects that contain the generated
    text and applies text-based metrics to compute scores.
    """

    def score_instances(
        self, instances: list[Instance], filter_name: str
    ) -> GenResult:
        """
        Score generation instances for a single document.

        Args:
            instances: List of instances for the same doc
            filter_name: Name of the filter to use

        Returns:
            GenResult with computed scores
        """
        # Create GenResult from instances with filtered outputs
        gen_result = GenResult.from_instances(instances, filter_name)
        gen_result.repeats = self.config.repeat_cfg.repeats

        # Get metrics for this filter
        metrics = self.get_metrics(filter_name)

        # Compute metrics
        gen_result.scores = self._compute_metrics(gen_result, metrics)

        return gen_result

    def _compute_metrics(
        self, gen_result: GenResult, metrics: list[MetricConfig]
    ) -> dict[str, list[float]]:
        """
        Compute all metrics for a GenResult.

        For each generation in the result, applies each metric function
        to compute a score. Handles both simple metrics that return a single
        value and complex metrics that return dictionaries.

        Args:
            gen_result: GenResult containing generations and target
            metrics: List of metrics to compute

        Returns:
            Dictionary mapping metric_name -> list of scores (one per generation)
        """
        scores = defaultdict(list)
        gold = gen_result.target

        # Compute metric for each generation
        for generation in gen_result.results:
            for metric in metrics:
                if metric.fn is None:
                    continue

                try:
                    # Standard interface: references and predictions as lists
                    score = metric.fn(
                        references=[gold] if not isinstance(gold, list) else gold,
                        predictions=[generation],
                        **metric.kwargs,
                    )
                except TypeError:
                    # Handle metrics with different interfaces (legacy)
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
    - Multiple choices per sample

    The LoglikelihoodScorer creates MCResult objects that contain log probabilities
    for each choice and applies choice-based metrics to compute scores.
    """

    def score_instances(
        self, instances: list[Instance], filter_name: str
    ) -> MCResult:
        """
        Score multiple-choice instances for a single document.

        Args:
            instances: List of instances for the same doc
            filter_name: Name of the filter to use

        Returns:
            MCResult with computed scores
        """
        # Create MCResult from instances
        # Note: MCResult doesn't currently use filter_name as it works with
        # log probabilities directly, but we include it for consistency
        mc_result = MCResult.from_instances(instances)

        # Get metrics for this filter
        metrics = self.get_metrics(filter_name)

        # Compute metrics
        mc_result.scores = self._compute_metrics(mc_result, metrics)

        return mc_result

    def _compute_metrics(
        self, mc_result: MCResult, metrics: list[MetricConfig]
    ) -> dict[str, float]:
        """
        Compute all metrics for an MCResult.

        Multiple-choice metrics typically take the entire MCResult as input
        (containing log probabilities, target index, etc.) and return a single
        score per sample.

        Args:
            mc_result: MCResult containing log probs and target
            metrics: List of metrics to compute

        Returns:
            Dictionary mapping metric_name -> score
        """
        scores = {}

        for metric in metrics:
            if metric.fn is None:
                continue

            # MC metrics take the entire MCResult as input
            score = metric.fn(mc_result)

            # Handle metrics that return dicts (multiple metrics at once)
            if isinstance(score, dict):
                scores.update(score)
            else:
                scores[metric.name] = score

        return scores


class ScorerFactory:
    """
    Factory for creating the appropriate Scorer based on task configuration.

    The factory implements a decision tree:
    1. If process_results is defined → ProcessResultsScorer
    2. Elif output_type is generate_until → GenerationScorer
    3. Elif output_type is loglikelihood/multiple_choice → LoglikelihoodScorer
    4. Else → raise error

    This ensures that each task gets the right kind of scorer automatically.
    """

    @staticmethod
    def create_scorer(task_config: TaskConfig) -> Scorer:
        """
        Create appropriate scorer for task configuration.

        Args:
            task_config: Task configuration object

        Returns:
            Scorer instance appropriate for the task type

        Raises:
            ValueError: If output_type is not recognized
            NotImplementedError: If output_type doesn't have a scorer yet
        """
        # Check for custom process_results first (highest priority)
        if callable(task_config.process_results):
            return ProcessResultsScorer(task_config, task_config.process_results)

        # Create type-specific scorer based on output_type
        output_type = task_config.output_type

        if output_type == "generate_until":
            return GenerationScorer(task_config)
        elif output_type in ("loglikelihood", "multiple_choice"):
            return LoglikelihoodScorer(task_config)
        elif output_type == "loglikelihood_rolling":
            # TODO: Implement PerplexityScorer
            raise NotImplementedError(
                f"Scorer for {output_type} not yet implemented. "
                "Please implement PerplexityScorer for loglikelihood_rolling tasks."
            )
        else:
            raise ValueError(
                f"Unknown output_type: {output_type}. "
                f"Expected one of: generate_until, loglikelihood, multiple_choice, loglikelihood_rolling"
            )


# Example custom scorers (for documentation/extension purposes)
class RewardModelScorer(GenerationScorer):
    """
    Example custom scorer that uses a reward model to score generations.

    This demonstrates how to extend the base GenerationScorer with additional
    scoring logic. You can override _compute_metrics to add custom metrics
    while still computing standard metrics.

    Usage:
        scorer = RewardModelScorer(task_config, reward_model_path="path/to/model")
    """

    def __init__(self, task_config: TaskConfig, reward_model_path: str):
        """
        Initialize with reward model.

        Args:
            task_config: Task configuration
            reward_model_path: Path to reward model weights
        """
        super().__init__(task_config)
        self.reward_model_path = reward_model_path
        # In practice, you would load the model here:
        # self.reward_model = load_reward_model(reward_model_path)

    def _compute_metrics(
        self, gen_result: GenResult, metrics: list[MetricConfig]
    ) -> dict[str, list[float]]:
        """
        Compute metrics including reward model scores.

        Args:
            gen_result: GenResult with generations
            metrics: Standard metrics to compute

        Returns:
            Scores including both standard metrics and reward model scores
        """
        # First compute standard metrics
        scores = super()._compute_metrics(gen_result, metrics)

        # Add reward model scores
        reward_scores = []
        for generation in gen_result.results:
            # In practice, call reward model:
            # score = self.reward_model.score(generation)
            score = 0.0  # Placeholder
            reward_scores.append(score)

        scores["reward_model"] = reward_scores

        return scores
