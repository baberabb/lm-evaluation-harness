# LM Evaluation Harness: Metrics and Scoring System - Complete Analysis

## Overview

The lm-evaluation-harness uses a unified, minimal-complexity approach to metrics and scoring. This document provides a complete understanding of the architecture, from task processing through final metric calculation.

---

## 1. GenResult and MCResult Abstractions

### Location
- **File**: `/home/user/lm-evaluation-harness/lm_eval/types.py`

### GenResult (Generation Tasks)

GenResult represents results from generation tasks (generate_until output type).

**Definition**:
```python
@dataclass
class GenResult:
    """Result of a generation task, grouped by doc_id.
    
    Handles multiple generations per doc (e.g., temperature sampling, repeats).
    """
    results: Sequence[str]              # All generated texts
    target: str | list[str]             # Gold reference(s)
    instances: Sequence["GenInstance"]  # Source instances
    repeats: int = 1                    # Number of repeats/samples per doc
    filter_name: str = "default"        # Active filter
    scores: dict[Any, list[float]] = field(
        default_factory=lambda: defaultdict(list)
    )
```

**Key Methods**:

1. **from_instances()** - Creates GenResult from instances:
```python
@classmethod
def from_instances(
    cls, 
    instances: Sequence["GenInstance"], 
    filter_name: str | None = None
) -> "GenResult":
    """Create GenResult from instances for the same doc_id.
    
    - Extracts generations from filtered responses
    - Handles both single and multiple responses
    - Uses filter_name to get filtered responses from instances
    """
```

2. **to_metric_inputs()** - Converts to standard metric input format:
```python
def to_metric_inputs(self):
    return {
        "predictions": self.results,
        "references": self.target,
    }
```

**Usage Flow**:
1. Takes instances with raw generation outputs
2. Extracts filtered responses based on filter_name
3. Combines all generations and target references
4. Returns object suitable for metric computation

### MCResult (Multiple Choice Tasks)

MCResult represents results from multiple-choice tasks (loglikelihood output type).

**Definition**:
```python
@dataclass
class MCResult(Results):
    """Result of a multiple-choice task. Instances are grouped by doc_id beforehand"""
    
    lls: Sequence[float]                      # Log-likelihoods for each choice
    is_greedy: Sequence[bool]                 # Whether each LL is from greedy decoding
    target: int                               # Index of correct choice
    instances: Sequence["MCInstance"]         # Source instances
    choices: Sequence[str] = field(default_factory=list)
    char_lens: Sequence[int] = field(default_factory=list)
    byte_lens: Sequence[int] = field(default_factory=list)
    token_lens: Sequence[int] = field(default_factory=list)
    lls_mutual_info: Sequence[float] = field(default_factory=list)
    scores: dict[Any, float] = field(default_factory=dict)
```

**Key Methods**:

1. **from_instances()** - Creates MCResult from multiple-choice instances:
```python
@classmethod
def from_instances(cls, results: Sequence["MCInstance"], acc_mutual_info=False):
    """
    - Groups instances by doc_id
    - Extracts log-likelihoods for each choice
    - Handles mutual information calculation if needed
    - Computes character/byte/token lengths for normalization
    """
```

2. **to_metric_inputs()** - Returns self (metrics take MCResult directly):
```python
def to_metric_inputs(self):
    return self
```

**Key Features**:
- **Mutual Information Support**: If `acc_mutual_info=True`, computes:
  ```
  MI(choice|context) = log(P(choice|context)) - log(P(choice))
  ```
- **Normalization Metrics**: Stores character/byte/token lengths for normalization-based metrics
- **Direct Metric Input**: MC metrics take MCResult objects directly (unlike GenResult)

### Results Protocol

Both GenResult and MCResult implement the Results protocol:

```python
@runtime_checkable
class Results(Protocol[InstanceT]):
    """Class for storing results of a task."""
    
    results: Any
    target: Any
    scores: Any
    instances: Sequence[InstanceT]
    
    @classmethod
    def from_instances(
        cls: type[ResultsSelf],
        results: Sequence[InstanceT],
        filter_name: str = "default",
    ) -> ResultsSelf: ...
    
    @abstractmethod
    def to_metric_inputs(self) -> Any: ...
    
    @staticmethod
    def create(instance: Sequence[InstanceT], filter_name: str | None = None):
        """Factory method - creates appropriate result type based on request_type"""
        output_type = instance[0].request_type
        match output_type:
            case "loglikelihood":
                return MCResult.from_instances(instance)
            case _:
                return GenResult.from_instances(instance, filter_name=filter_name)
```

---

## 2. Task.process_instances - Complete Flow

### Location
- **File**: `/home/user/lm-evaluation-harness/lm_eval/api/task.py` (lines 603-653)

### Purpose
Primary unified method for processing instances to compute metrics across all task types.

### Complete Implementation

```python
def process_instances(self, instances: list[Instance] | None = None):
    """Primary method for processing instances to compute metrics.
    
    This is the unified entry point for result processing. It implements
    a consistent iteration pattern: filter → doc → metric computation.
    
    Args:
        instances: List of instances to process. If None, uses self._instances
    
    Returns:
        Dictionary mapping (metric_name, filter_name) -> list of scores
    """
    # Step 1: Sort instances by doc_id for grouped processing
    _instances = self.sort_instances(instances or self._instances)
    if not _instances:
        return {}
    
    sample_scores = defaultdict(list)
    
    # Step 2: Handle custom process_results (backward compatibility)
    if callable(self.config.process_results):
        for filter_cfg in self._filters:
            for doc_instances in _instances.values():
                # Create result object
                result = Results.create(doc_instances, filter_cfg.name)
                
                # Call legacy process_results function
                metrics = self.process_results(
                    result.doc,
                    [result.results[filter_cfg.name]],
                )
                
                # Store results
                if metrics is not None:
                    for metric_name, value in metrics.items():
                        sample_scores[(metric_name, filter_cfg.name)].append(value)
    else:
        # Step 3: Standard unified iteration pattern
        # Pattern: for each filter → for each doc → for each metric
        for filter_cfg in self._filters:
            # Use filter's metrics if specified, else fall back to global
            metrics = (
                filter_cfg.metric_list 
                if filter_cfg.metric_list 
                else self.config._metric_list
            )
            
            for doc_id, doc_instances in _instances.items():
                # Create result object (task-type specific)
                result = self._create_result(doc_instances, filter_cfg.name)
                
                # Compute each metric for this result
                for metric in metrics:
                    if metric.fn is None:
                        continue
                    
                    # Call task-specific metric computation
                    score = self._compute_metric(result, metric)
                    if score is not None:
                        sample_scores[(metric.name, filter_cfg.name)].append(score)
    
    # Step 4: Store and return results
    self._sample_scores = dict(sample_scores)
    return self._sample_scores
```

### Key Components

#### 2.1 sort_instances()
Groups instances by doc_id for batch processing:

```python
@staticmethod
def sort_instances(
    instances: list[Instance] | None = None,
) -> dict[str, list[Instance]]:
    """Sorts instances by doc_id and then by idx"""
    if not instances:
        return {}
    
    instances_by_doc_id = defaultdict(list)
    for instance in instances:
        instances_by_doc_id[instance.doc_id].append(instance)
    
    # Sort instances within each group
    for instances in instances_by_doc_id.values():
        instances.sort(key=lambda x: x.idx)
    
    return instances_by_doc_id
```

**Why grouping?**
- Multiple instances can belong to same doc (e.g., multiple generations, multiple choices)
- Need to combine them into single result object for metric computation
- Sorted by idx to maintain consistent ordering

#### 2.2 _create_result() [Abstract]
Creates task-specific result objects:

**GenerateTask implementation**:
```python
def _create_result(self, instances: list[Instance], filter_name: str):
    """Create GenResult from instances."""
    from lm_eval.types import GenResult
    
    return GenResult.from_instances(instances, filter_name=filter_name)
```

**MultipleChoiceTask implementation**:
```python
def _create_result(self, instances: list[Instance], filter_name: str):
    """Create MCResult from instances."""
    from lm_eval.types import MCResult
    
    # Check if we need mutual information
    acc_mutual_info = "acc_mutual_info" in [
        m.name for m in self.config._metric_list
    ]
    return MCResult.from_instances(instances, acc_mutual_info=acc_mutual_info)
```

#### 2.3 _compute_metric() [Abstract]
Computes a single metric from a result object:

**GenerateTask implementation**:
```python
def _compute_metric(self, gen_result: "GenResult", metric: "MetricConfig"):
    """Compute a single metric for a generation task.
    
    Returns a list of scores (one per generation) which will be reduced
    later by the Task.reduce() method if needed.
    """
    if metric.fn is None:
        return None
    
    scores = []
    gold = gen_result.target
    
    for generation in gen_result.results:
        try:
            score = metric.fn(
                references=[gold] if not isinstance(gold, list) else gold,
                predictions=[generation],
                **metric.kwargs,
            )
        except TypeError:
            # Handle metrics with different interfaces
            score = metric.fn([gold, generation])
        
        if isinstance(score, dict):
            # Multiple metrics from the same function
            # For now, just take the first value
            scores.append(list(score.values())[0])
        else:
            scores.append(score)
    
    return scores  # List of scores (one per generation)
```

**MultipleChoiceTask implementation**:
```python
def _compute_metric(self, mc_result: "MCResult", metric: "MetricConfig"):
    """Compute a single metric for a multiple-choice task.
    
    MC metrics take MCResult directly and return a single score.
    """
    if metric.fn is None:
        return None
    
    # Multiple choice metrics take the MCResult object directly
    return metric.fn(mc_result)
```

### Iteration Pattern

The unified pattern is:
```
for each filter:
    for each doc:
        create result object
        for each metric:
            compute score
            store score in sample_scores[(metric_name, filter_name)]
```

This ensures:
- Consistent processing across all task types
- Each filter processed independently with potentially different metrics
- Metrics applied uniformly to all docs
- Results organized by (metric, filter) tuple for aggregation

---

## 3. compute_aggregations - Location and Purpose

### Location
- **File**: `/home/user/lm-evaluation-harness/lm_eval/api/task.py` (lines 691-724)

### Purpose
Aggregates per-sample scores into final metrics with error estimates.

### Implementation

```python
def compute_aggregations(
    self,
    scores: dict[tuple[str, str], list[GenResult] | list[MCResult]],
    bootstrap_iters=100,
):
    """Aggregate per-sample scores into final metrics.
    
    Args:
        scores: Dictionary mapping (metric_name, filter_name) -> list of scores
        bootstrap_iters: Number of bootstrap iterations for stderr
    
    Returns:
        Dictionary of aggregated metrics and their standard errors
    """
    from lm_eval.api.metrics import mean, stderr_for_metric
    
    agg_metrics = {}
    for (metric, filter_key), items in scores.items():
        # Step 1: Reduce repeated samples if needed
        items = self.reduce(items, metric)
        
        # Step 2: Get aggregation function for this metric
        try:
            agg_fn = self.aggregation()[metric]
        except KeyError:
            # Fallback for arbitrary metrics from process_results
            agg_fn = mean
        
        # Step 3: Compute aggregated metric
        metric_key = f"{metric},{filter_key}"
        agg_metrics[metric_key] = agg_fn(items)
        
        # Step 4: Store sample count
        self.sample_len = len(items)
        
        # Step 5: Compute standard error if requested
        if isinstance(bootstrap_iters, int):
            # Special handling for MT metrics
            stderr_fn = stderr_for_metric(
                metric=agg_fn,
                bootstrap_iters=min(bootstrap_iters, 100)
                if metric in ["bleu", "chrf", "ter"]
                else bootstrap_iters,
            )
            agg_metrics[f"{metric}_stderr,{filter_key}"] = (
                stderr_fn(items) if (stderr_fn and len(items) > 1) else "N/A"
            )
        else:
            raise ValueError(
                f"Received bootstrap_iters '{bootstrap_iters}' but expected an integer. "
                "Set to 0 to turn off stderr calculations."
            )
    
    return agg_metrics
```

### Key Steps

#### 3.1 Reduction (reduce method)
Handles multiple samples per doc (from repeats/temperature sampling):

```python
def reduce(
    self, 
    items: Sequence[float] | Sequence[list[float]], 
    metric: str
) -> list[float]:
    """Reduce a list of numbers to a single number."""
    if isinstance(items[0], float | int):
        # Already single values
        return items
    
    if self.config.repeats > 1:
        # Multiple samples per doc - apply reducer function
        return [self.config.repeat_cfg.reducer(x) for x in items]
    else:
        # Multiple generations but single sample - take first
        return [x[0] for x in items]
```

**Common reducers**:
- `min`: Take minimum score (conservative)
- `max`: Take maximum score (optimistic)
- `mean`: Average multiple samples

#### 3.2 Aggregation Functions
Built-in aggregations from `/home/user/lm-evaluation-harness/lm_eval/api/metrics.py`:

**Simple aggregations**:
```python
@register_aggregation("mean")
def mean(arr):
    return sum(arr) / len(arr)

@register_aggregation("nanmean")
def nanmean(arr):
    if len(arr) == 0 or all(np.isnan(arr)):
        return np.nan
    return np.nanmean(arr)

@register_aggregation("median")
def median(arr):
    return arr[len(arr) // 2]
```

**Specialized aggregations**:
```python
@register_aggregation("perplexity")
def perplexity(items):
    return math.exp(-mean(items))

@register_aggregation("weighted_perplexity")
def weighted_perplexity(items):
    return math.exp(-weighted_mean(items))

@register_aggregation("f1")
def f1_score(items):
    from sklearn.metrics import f1_score
    unzipped_list = list(zip(*items))
    golds = unzipped_list[0]
    preds = unzipped_list[1]
    fscore = f1_score(golds, preds)
    return np.max(fscore)
```

#### 3.3 Standard Error Computation
Bootstrap-based error estimation:

```python
def stderr_for_metric(
    metric: Callable[[Sequence[T]], float], 
    bootstrap_iters: int
) -> Optional[Callable[[Sequence[T]], float]]:
    """Return a function that estimates the standard error of `metric(xs)`.
    
    - If metric in pre-approved bootstrappable list: use bootstrap
    - If metric has closed-form SE: use closed-form formula
    - Otherwise: return None (no stderr)
    """
    
    if bootstrap_iters <= 0:
        return None
    
    bootstrappable = [
        median, matthews_corrcoef, f1_score,
        perplexity, bleu, chrf, ter, nanmean,
    ]
    
    if metric in bootstrappable:
        return lambda x: bootstrap_stderr(metric, x, iters=bootstrap_iters)
    
    stderr = {
        mean: mean_stderr,
        acc_all: acc_all_stderr
    }
    
    return stderr.get(metric, None)
```

### Output Format

```python
{
    "metric_name,filter_name": 0.85,           # Aggregated score
    "metric_name_stderr,filter_name": 0.02,    # Standard error
    "another_metric,filter": 0.72,
    "another_metric_stderr,filter": 0.03,
    ...
}
```

---

## 4. The Reduction Mechanism

### Purpose
Handles cases where multiple samples/generations exist per document.

### When Reductions Are Needed

**Scenario 1: Temperature Sampling** (config.repeats > 1)
```yaml
task: my_generation_task
generation_kwargs:
  do_sample: true
  temperature: 0.8
  num_return_sequences: 3  # 3 samples per doc
repeats: 3  # Multiple samples for uncertainty
```

Results in per-doc scores: `[[0.8, 0.75, 0.78], [0.9, 0.85, 0.92], ...]`

**Scenario 2: Multiple Choices** (MC task)
MCResult groups all choices for a doc, but metrics typically return single value per doc.

### Reduction Process

```python
def reduce(
    self, 
    items: Sequence[float] | Sequence[list[float]], 
    metric: str
) -> list[float]:
    """Convert per-sample lists into single values per sample."""
    
    # Case 1: Already reduced (simple floats)
    if isinstance(items[0], float | int):
        return items
    
    # Case 2: Multiple repeats - apply configured reducer
    if self.config.repeats > 1:
        # items = [[score1_a, score1_b, score1_c], 
        #          [score2_a, score2_b, score2_c], ...]
        # reducer could be: max, min, mean, median
        return [self.config.repeat_cfg.reducer(x) for x in items]
    
    # Case 3: Multiple generations, single sample
    # items = [[score1], [score2], ...]
    else:
        return [x[0] for x in items]
```

### Reducer Functions

Common reducers configured in TaskConfig:

```python
{
    "max": lambda scores: max(scores),           # Optimistic
    "min": lambda scores: min(scores),           # Conservative
    "mean": lambda scores: sum(scores)/len(scores),  # Average
    "median": lambda scores: sorted(scores)[len(scores)//2],  # Robust
    "first": lambda scores: scores[0],           # Deterministic
}
```

### Example Walkthrough

```
Input scores per (metric, filter):
[
  [0.8, 0.75, 0.78],   # Doc 1: 3 samples
  [0.9, 0.85, 0.92],   # Doc 2: 3 samples
  [0.7, 0.72, 0.69],   # Doc 3: 3 samples
]

With reducer = "max":
[0.80, 0.92, 0.72]

Aggregation = mean:
Final score = (0.80 + 0.92 + 0.72) / 3 = 0.8133
```

---

## 5. How Filters Work in the Scoring Pipeline

### Location
- **Filters**: `/home/user/lm-evaluation-harness/lm_eval/api/filter.py`
- **Filter Ensemble**: Applies multiple filters in sequence
- **Task Filter Application**: `/home/user/lm-evaluation-harness/lm_eval/api/task.py` (lines 469-479)

### Filter Architecture

#### 5.1 Filter Base Class

```python
class Filter(ABC):
    """
    Filter classes operate on a per-task level.
    They take all model outputs (`instance.resps` for all `task.instances`)
    across all instances of a task, and perform operations.
    """
    
    def __init__(self, **kwargs) -> None:
        """Can define custom behavior here"""
        pass
    
    @abstractmethod
    def apply(self, resps: Union[List, Iterable], docs: List[dict]) -> Iterable:
        """Defines the operation to perform on a list of instance responses.
        
        Should return the list of (filtered) response lists *in the same order*
        as they were input.
        
        Example:
            Input: [["hello world"], ["hi there"], ["goodbye"]]
            Output: [["HELLO WORLD"], ["HI THERE"], ["GOODBYE"]]  # Upper case filter
        """
        return resps
```

#### 5.2 FilterEnsemble (Filter Pipeline)

```python
@dataclass
class FilterEnsemble:
    """
    FilterEnsemble creates a pipeline applying multiple filters in sequence.
    
    Each FilterEnsemble has a unique name, allowing different filter chains
    to be applied to the same instances.
    """
    
    name: str
    filters: List[Callable[[], Filter]]
    
    def apply(self, instances: List[Instance]) -> None:
        """Apply all filters in the ensemble to instances.
        
        Execution flow:
        1. Extract responses and docs from instances
        2. Apply each filter in sequence
        3. Store filtered responses in instance.filtered_resps[self.name]
        """
        # Extract responses and docs
        resps, docs = zip(*((inst.resps, inst.doc) for inst in instances))
        resps, docs = list(resps), list(docs)
        
        # Apply filters in sequence (chaining)
        for f in self.filters:
            resps = f().apply(resps, docs)
        
        # Store results in each instance
        for inst, resp in zip(instances, resps):
            inst.filtered_resps[self.name] = resp
```

### Filter Integration in Task.process_instances()

#### Step 1: Apply Filters to Instances

```python
# In evaluator.py
task.apply_filters()  # Applies all configured FilterEnsembles
```

This calls:
```python
def apply_filters(self):
    """Iterates over FilterEnsembles and applies them to instances"""
    if hasattr(self, "_filters") and self.instances:
        for f in self._filters:
            f.ensemble.apply(self.instances)
        return self
    else:
        eval_logger.warning(
            "No filter defined or no instances, passing through instances"
        )
        return self
```

#### Step 2: Use Filtered Responses During Scoring

In `GenResult.from_instances()`:
```python
for inst in instances:
    if filter_name and filter_name in inst.filtered_resps:
        resp = inst.filtered_resps[filter_name]
        # Handle both single and multiple responses
        if isinstance(resp, list):
            generations.extend(resp)
        else:
            generations.append(resp)
    else:
        # Fallback if filter not found
        generations.append(inst.filtered_resps)
```

### Example Filter Chain

**Scenario**: Exact match metric but want case-insensitive and punctuation-stripped versions

**Configuration**:
```python
filter_list = [
    FilterEnsemble(
        name="default",
        filters=[],  # No filtering
    ),
    FilterEnsemble(
        name="exact_match_lowercase",
        filters=[
            LowercaseFilter,
            StripPunctuationFilter,
        ]
    ),
]
```

**Execution**:
```
Instance resps: ["Hello, World!", "Hi there!"]

Filter 1: Lowercase
→ ["hello, world!", "hi there!"]

Filter 2: Strip Punctuation
→ ["hello world", "hi there"]

Result stored in:
instance.filtered_resps["exact_match_lowercase"] = ["hello world", "hi there"]
```

### Filter-Specific Metrics

Each filter can have its own metric list:

```python
for filter_cfg in self._filters:
    # Use filter's metrics if specified, else fall back to global
    metrics = (
        filter_cfg.metric_list 
        if filter_cfg.metric_list 
        else self.config._metric_list
    )
    
    for doc_id, doc_instances in _instances.items():
        result = self._create_result(doc_instances, filter_cfg.name)
        
        for metric in metrics:
            score = self._compute_metric(result, metric)
```

**Example**:
```yaml
filter_list:
  - name: strict
    metric_list:
      - metric: exact_match

  - name: flexible
    metric_list:
      - metric: exact_match
      - metric: f1_score
      - metric: bert_score
```

Different filters can compute different metrics!

---

## 6. Overall Metric Calculation Flow

### Complete Pipeline

```
┌─────────────────────────────────────────────────────┐
│ 1. TASK INSTANTIATION & CONFIGURATION               │
│   - Load task from YAML/config                      │
│   - Initialize metrics, filters                     │
│   - Create Task object (GenerateTask/MCTask)        │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│ 2. BUILD REQUESTS                                   │
│   - task.build_all_requests()                       │
│   - Creates Instance objects                        │
│   - Each Instance: (request_type, doc, args, ...)   │
│   - Stored in task._instances                       │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│ 3. MODEL INFERENCE                                  │
│   - LM processes all instances                      │
│   - Populates Instance.resps with model outputs     │
│   - For generate_until: text generations            │
│   - For loglikelihood: (LL_score, is_greedy) tuples │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│ 4. FILTER APPLICATION                              │
│   - task.apply_filters()                            │
│   - For each FilterEnsemble:                        │
│     - Apply filters in sequence                     │
│     - Store in Instance.filtered_resps[filter_name] │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│ 5. PROCESS INSTANCES (Unified Scoring Loop)        │
│   - task.process_instances()                        │
│                                                     │
│   For each filter in task._filters:                │
│     For each doc_id, doc_instances in grouped:     │
│       result = _create_result(doc_instances)       │
│       # GenResult or MCResult                       │
│                                                     │
│       For each metric in filter.metric_list:       │
│         score = _compute_metric(result, metric)    │
│         sample_scores[(metric, filter)] = score    │
│                                                     │
│   Returns: sample_scores dict                      │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│ 6. AGGREGATION                                      │
│   - task.compute_aggregations(sample_scores)       │
│                                                     │
│   For each (metric, filter) in sample_scores:      │
│     1. Reduce repeated samples if needed            │
│     2. Apply aggregation function (mean/median/etc) │
│     3. Compute bootstrap stderr if requested        │
│                                                     │
│   Returns: agg_metrics dict with final scores       │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│ 7. RESULTS & GROUP AGGREGATION                      │
│   - Store task results                              │
│   - If group: compute_aggregate_metrics()           │
│   - Format final output JSON                        │
└─────────────────────────────────────────────────────┘
```

### Detailed Walkthrough: Generation Task Example

**Setup**:
```yaml
task: gsm8k
output_type: generate_until
metric_list:
  - metric: exact_match
num_fewshot: 0
repeats: 1
generation_kwargs:
  max_gen_toks: 256
  do_sample: false
filter_list:
  - name: default
    metric_list:
      - metric: exact_match
```

**Step 1-2: Build Requests**
```python
# For each doc in dataset:
Instance(
    request_type="generate_until",
    doc={"question": "2+2=?", "answer": "4"},
    arguments=("What is 2+2?\n", {"max_gen_toks": 256, ...}),
    idx=0,
    target="4",
    doc_id=0,
    repeats=1,
    task_name="gsm8k",
)
# ... more instances
```

**Step 3: Model Inference**
```python
# LM generates completions
instance.resps = ["4", "4\n", "The answer is 4"]  # Generated texts
```

**Step 4: Filters**
```python
# Default filter (no-op for this task)
instance.filtered_resps["default"] = "4"
```

**Step 5: Process Instances**

```python
# sort_instances() groups by doc_id:
{
    0: [Instance(doc_id=0, resps="4", target="4", ...)],
    1: [Instance(doc_id=1, resps="The answer is 4", target="4", ...)],
    ...
}

# For filter "default":
for metric "exact_match":
    for doc_id=0:
        # Create GenResult
        result = GenResult(
            results=["4"],
            target="4",
            repeats=1,
        )
        
        # Compute metric
        score = exact_match_fn(
            references=["4"],
            predictions=["4"],
        )
        # Returns: 1.0
        
        sample_scores[("exact_match", "default")].append(1.0)
    
    for doc_id=1:
        result = GenResult(
            results=["The answer is 4"],
            target="4",
        )
        
        score = exact_match_fn(
            references=["4"],
            predictions=["The answer is 4"],
        )
        # Returns: 0.0
        
        sample_scores[("exact_match", "default")].append(0.0)

# Result:
sample_scores = {
    ("exact_match", "default"): [1.0, 0.0, ..., 1.0]  # 8919 scores
}
```

**Step 6: Aggregation**

```python
agg_metrics = compute_aggregations(sample_scores)

# For ("exact_match", "default"):
items = [1.0, 0.0, ..., 1.0]  # 8919 values

# No reduction needed (repeats=1)
items = [1.0, 0.0, ..., 1.0]

# Apply aggregation function (mean)
score = mean(items) = sum(items) / len(items) = 0.9234

# Compute stderr
stderr = bootstrap_stderr(mean, items, iters=100)

# Result:
agg_metrics = {
    "exact_match,default": 0.9234,
    "exact_match_stderr,default": 0.0023,
}
```

**Step 7: Final Result**
```python
results["gsm8k"] = {
    "exact_match,default": 0.9234,
    "exact_match_stderr,default": 0.0023,
    "alias": "gsm8k",
}
```

### Walkthrough: Multiple Choice Task

**Setup**:
```yaml
task: mmlu_anatomy
output_type: loglikelihood
metric_list:
  - metric: acc
  - metric: acc_norm
num_fewshot: 5
```

**Step 3: Model Inference (loglikelihood)**
```python
# Model computes log-probabilities for each choice
# Instance for one question with 4 choices:

Instance(
    request_type="loglikelihood",
    arguments=[
        ("context", "A) option1"),   # (ctx, choice1)
        ("context", "B) option2"),   # (ctx, choice2)
        ("context", "C) option3"),   # (ctx, choice3)
        ("context", "D) option4"),   # (ctx, choice4)
    ],
)

# Model returns:
instance.resps = [
    (-2.1, True),   # choice A: LL=-2.1
    (-1.5, True),   # choice B: LL=-1.5
    (-0.8, True),   # choice C: LL=-0.8 (highest = argmax)
    (-3.2, True),   # choice D: LL=-3.2
]
```

**Step 5: Process Instances**

```python
# Instances grouped by doc_id:
doc_instances = [
    Instance(idx=0, target=2, resps=(-2.1, True), ...),  # Instance for choice A
    Instance(idx=1, target=2, resps=(-1.5, True), ...),  # Instance for choice B
    Instance(idx=2, target=2, resps=(-0.8, True), ...),  # Instance for choice C
    Instance(idx=3, target=2, resps=(-3.2, True), ...),  # Instance for choice D
]

# Create MCResult from all instances for this doc:
result = MCResult.from_instances(doc_instances, acc_mutual_info=False)
# Result:
# - lls: [(-2.1), (-1.5), (-0.8), (-3.2)]
# - target: 2  # Correct answer is index 2 (C)
# - choices: ["A) option1", "B) option2", "C) option3", "D) option4"]

# Compute acc metric:
score = acc_fn(result)
# Internal: argmax(lls) = 2 (index of -0.8)
# 2 == target (2)? Yes → score = 1.0

sample_scores[("acc", "default")].append(1.0)

# Compute acc_norm metric (normalized by length):
score = acc_norm_fn(result)
# Normalizes by option length before argmax
# score = 1.0 or 0.0 depending on normalized scores
```

**Step 6: Aggregation**

```python
agg_metrics = compute_aggregations(sample_scores)

# For ("acc", "default"):
items = [1.0, 0.0, 1.0, 1.0, ..., 0.0]  # One score per question

score = mean(items) = 0.8234  # Accuracy over all questions

# For ("acc_norm", "default"):
items = [1.0, 0.0, 1.0, 1.0, ..., 1.0]
score = mean(items) = 0.7891  # Normalized accuracy

agg_metrics = {
    "acc,default": 0.8234,
    "acc_stderr,default": 0.0045,
    "acc_norm,default": 0.7891,
    "acc_norm_stderr,default": 0.0051,
}
```

---

## Key Architectural Insights

### 1. **Unified vs. Task-Specific**
- **Unified**: Iteration pattern (filter → doc → metric) in base Task class
- **Task-Specific**: Result creation and metric computation delegated to subclasses
- **Benefit**: No code duplication, clear separation of concerns

### 2. **Filter-Metric Decoupling**
- Filters operate on raw responses
- Metrics operate on result objects
- Same filtered response can be used for multiple metrics
- Different filters can use different metrics

### 3. **Lazy Result Creation**
- Results created only when needed (per filter/doc combination)
- Multiple instances grouped by doc_id before creating single result
- Reduces memory overhead

### 4. **Sample vs. Aggregated Scores**
- **Sample scores**: Per-document metric values
- **Aggregated scores**: Final metric values across all documents
- **Reduction**: Handles samples per document (temperature, repeats)

### 5. **Metric Flexibility**
- Generate tasks: Metrics take (references, predictions)
- MC tasks: Metrics take MCResult object directly
- Task subclasses handle the difference via `_compute_metric()`

---

## Common Metrics

See `/home/user/lm-evaluation-harness/lm_eval/api/metrics.py` for implementations.

**Registered metrics**:
- `acc`: Accuracy (for multiple choice)
- `acc_norm`: Normalized accuracy
- `exact_match`: Exact string matching
- `bleu`: BLEU score (aggregation: corpus BLEU)
- `chrf`: Character n-gram F-score
- `ter`: Translation error rate
- `f1`: F1 score
- `mcc`: Matthews correlation coefficient
- `perplexity`: Exponential of negative mean LL
- `word_perplexity`: Perplexity normalized by words
- `byte_perplexity`: Perplexity normalized by bytes

