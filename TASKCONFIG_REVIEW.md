# TaskConfig Review and Analysis

**Status**: ⚠️ **CRITICAL** - TaskConfig is imported but does not exist!
**Impact**: The code will fail to run

---

## Problem Statement

The codebase imports `TaskConfig` from `lm_eval.config.task`:

```python
from lm_eval.config.task import TaskConfig
from lm_eval.config.utils import process_field
```

However, **neither `lm_eval/config/` directory nor these files exist**. This is likely an incomplete refactoring from a previous branch.

---

## Current Usage Analysis

By analyzing how `self.config` is used throughout `task.py`, I've identified what TaskConfig needs to provide:

### Required Attributes

```python
# Core identification
config.output_type: str  # "generate_until", "loglikelihood", etc.
config.task: str  # Task name
config.dataset_path: str | None
config.dataset_name: str | None

# Dataset configuration
config.test_split: str | None
config.validation_split: str | None
config.training_split: str | None
config.fewshot_split: str | None
config.dataset_kwargs: dict[str, Any]
config.metadata: dict[str, Any]
config.custom_dataset: Callable | None

# Document processing
config.doc_to_text: Callable | str | None
config.doc_to_choice: Callable | str | list | None
config.doc_to_target: Callable | str | None
config.doc_to_image: Callable | str | None
config.doc_to_audio: Callable | str | None
config.process_docs: Callable | None
config.process_results: Callable | None

# Few-shot configuration
config.num_fewshot: int | None
config._fewshot_cfg: FewshotConfig  # Has init_sampler() and rnd attribute
config.fewshot_delimiter: str
config.description: str | None

# Generation configuration (for GenerateTask)
config.generation_kwargs: dict[str, Any]
config.gen_prefix: str | None
config.target_delimiter: str

# Templates
config.template: Template | None  # Has format_prompt(), format_choices(), format_target()

# Metrics and filtering
config._metric_list: list[MetricConfig]
config.metric_list: list[MetricConfig]  # Alias or different?

# Repeat/sampling configuration
config.repeats: int
config.repeat_cfg: RepeatConfig  # Has reducer attribute

# Unconditional context (for mutual information)
config.unconditional_context: str
```

### Required Methods

```python
config.get_filters() -> list[FilterEnsemble]
TaskConfig.from_arbitrary_dict(dict) -> TaskConfig
```

---

## Issues with Current Pattern

### 1. **Broken Imports** ❌

**Problem**: Code imports non-existent modules.

```python
from lm_eval.config.task import TaskConfig  # Does not exist!
from lm_eval.config.utils import process_field  # Does not exist!
```

**Impact**: Code cannot run at all.

**Solution**: Create the config module structure.

### 2. **Unclear Attribute Hierarchy** ⚠️

**Problem**: Inconsistent naming suggests unclear design:

```python
config._metric_list  # Private? Internal use only?
config.metric_list   # Public? User-facing?
config._fewshot_cfg  # Why private?
```

**Questions**:
- What's the difference between `_metric_list` and `metric_list`?
- Why is `_fewshot_cfg` private but extensively used?
- Should users access these directly or through methods?

**Impact**: Confusing API, unclear contracts.

### 3. **Too Many Responsibilities** ⚠️

**Problem**: TaskConfig handles too many concerns:

1. Dataset loading (dataset_path, dataset_kwargs)
2. Document processing (doc_to_text, doc_to_target)
3. Few-shot sampling (num_fewshot, _fewshot_cfg)
4. Metrics configuration (_metric_list)
5. Filtering (get_filters())
6. Generation parameters (generation_kwargs)
7. Templates (template)
8. Repeats/sampling (repeats, repeat_cfg)

**Impact**:
- Hard to understand what TaskConfig is responsible for
- Difficult to test individual pieces
- Unclear which attributes are required vs optional
- Hard to document comprehensively

**Comparison to Industry Practice**:
- Django models: Separate Model, Manager, QuerySet
- FastAPI: Separate Settings, Dependencies, State
- Kubernetes: Separate Pod spec, Container spec, Volume spec

### 4. **Unclear Initialization Contract** ⚠️

**Problem**: Multiple ways to create TaskConfig:

```python
# From dict
config = TaskConfig(**config_dict)

# From arbitrary dict (what's the difference?)
config = TaskConfig.from_arbitrary_dict(self.CONFIG)

# Conditionally
self.config = (
    TaskConfig.from_arbitrary_dict(self.CONFIG)
    if self.CONFIG
    else (config if isinstance(config, TaskConfig) else TaskConfig(**config))
)
```

**Questions**:
- What's the difference between `__init__(**dict)` and `from_arbitrary_dict(dict)`?
- Why the complex conditional in Task.__init__?
- How does YAML → dict → TaskConfig conversion work?

**Impact**: Difficult to create TaskConfig correctly.

### 5. **Nested Configuration Objects** ⚠️

**Problem**: Config contains other config objects:

```python
config._fewshot_cfg: FewshotConfig
config.repeat_cfg: RepeatConfig
# Likely also:
# config.filter_list: list[FilterConfig]
# config._metric_list: list[MetricConfig]
```

**Questions**:
- How deep does the nesting go?
- Are these configs mutable?
- How are they validated together?
- What if there are conflicts between levels?

**Impact**: Complex object graph, hard to validate.

### 6. **Missing Validation** ❌

**Problem**: No apparent validation of configuration:

- Is `output_type` one of the valid types?
- If `output_type="generate_until"`, is `generation_kwargs` required?
- If `num_fewshot > 0`, is `_fewshot_cfg` required?
- Are filter names unique?
- Do metric names match registered metrics?

**Impact**: Errors surface late (at runtime) instead of early (at config load).

### 7. **No Type Hints on Config Class** ⚠️

**Problem**: Without seeing TaskConfig definition, we don't know:
- Which attributes are required vs optional
- What types each attribute should be
- What default values are used

**Impact**: Poor IDE support, runtime type errors.

---

## Proposed Design: TaskConfig Structure

### Option A: Monolithic Dataclass (Simpler)

```python
from dataclasses import dataclass, field
from typing import Any, Callable

@dataclass
class TaskConfig:
    """Configuration for a single task.

    Required fields:
        task: Task identifier/name
        output_type: Type of task (generate_until, loglikelihood, etc.)

    Most other fields have sensible defaults.
    """
    # Required
    task: str
    output_type: str  # Validated against Task._registry

    # Dataset
    dataset_path: str | None = None
    dataset_name: str | None = None
    test_split: str | None = None
    validation_split: str | None = None
    training_split: str | None = None
    fewshot_split: str | None = None
    dataset_kwargs: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    custom_dataset: Callable | None = None

    # Document processing
    doc_to_text: Callable | str | None = None
    doc_to_choice: Callable | str | list | None = None
    doc_to_target: Callable | str | None = None
    doc_to_image: Callable | str | None = None
    doc_to_audio: Callable | str | None = None
    process_docs: Callable | None = None
    process_results: Callable | None = None

    # Few-shot
    num_fewshot: int | None = None
    fewshot_delimiter: str = "\n\n"
    description: str | None = None

    # Generation (for generate_until tasks)
    generation_kwargs: dict[str, Any] = field(default_factory=dict)
    gen_prefix: str | None = None
    target_delimiter: str = " "

    # Templates
    template: Any | None = None  # Template object

    # Metrics
    metric_list: list[Any] = field(default_factory=list)  # List of MetricConfig

    # Filtering
    filter_list: list[Any] = field(default_factory=list)  # List of FilterConfig

    # Repeats
    repeats: int = 1
    reducer: str = "first"  # min, max, mean, median, first

    # Mutual information
    unconditional_context: str = ""

    # Internal (constructed from above)
    _fewshot_cfg: Any = field(init=False, repr=False)
    _metric_list: list[Any] = field(init=False, repr=False)
    _filter_list: list[Any] = field(init=False, repr=False)

    def __post_init__(self):
        """Validate and construct derived fields."""
        # Validate output_type
        from lm_eval.api.task import Task
        if self.output_type not in Task._registry:
            raise ValueError(
                f"Invalid output_type '{self.output_type}'. "
                f"Valid types: {sorted(Task._registry.keys())}"
            )

        # Construct fewshot config
        self._fewshot_cfg = self._build_fewshot_config()

        # Construct metric configs
        self._metric_list = self._build_metric_configs()

        # Construct filter configs
        self._filter_list = self._build_filter_configs()

    @classmethod
    def from_arbitrary_dict(cls, data: dict[str, Any]) -> "TaskConfig":
        """Create TaskConfig from arbitrary dictionary (e.g., from YAML).

        Handles:
        - Missing optional fields (uses defaults)
        - Extra fields (ignores them with warning)
        - Type conversion (str → Callable via utils.get_function)
        """
        # Extract known fields
        known_fields = {f.name for f in fields(cls) if f.init}
        config_data = {}
        extra_fields = {}

        for key, value in data.items():
            if key in known_fields:
                config_data[key] = value
            else:
                extra_fields[key] = value

        if extra_fields:
            logger.warning(
                f"Ignoring unknown fields in config: {list(extra_fields.keys())}"
            )

        return cls(**config_data)

    def get_filters(self) -> list[Any]:
        """Return constructed filter ensembles."""
        return self._filter_list

    def to_dict(self) -> dict[str, Any]:
        """Convert back to dictionary (for serialization)."""
        # Exclude private fields
        return {
            k: v for k, v in asdict(self).items()
            if not k.startswith('_')
        }
```

**Pros**:
- Simple, flat structure
- All fields visible in one place
- Easy to document
- Dataclass provides __init__, __repr__, etc. for free

**Cons**:
- Very long class (50+ attributes)
- No logical grouping
- Hard to extend with new feature areas

### Option B: Hierarchical Configs (More Organized)

```python
from dataclasses import dataclass, field

@dataclass
class DatasetConfig:
    """Configuration for dataset loading."""
    path: str | None = None
    name: str | None = None
    test_split: str | None = None
    validation_split: str | None = None
    training_split: str | None = None
    fewshot_split: str | None = None
    kwargs: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    custom_dataset: Callable | None = None
    process_docs: Callable | None = None

@dataclass
class DocProcessingConfig:
    """Configuration for document-to-text conversion."""
    doc_to_text: Callable | str | None = None
    doc_to_choice: Callable | str | list | None = None
    doc_to_target: Callable | str | None = None
    doc_to_image: Callable | str | None = None
    doc_to_audio: Callable | str | None = None

@dataclass
class FewshotConfig:
    """Configuration for few-shot prompting."""
    num_fewshot: int | None = None
    split: str | None = None  # Which split to sample from
    delimiter: str = "\n\n"
    description: str | None = None
    sampler: str = "random"  # random, first_n, balanced
    seed: int | None = None

@dataclass
class GenerationConfig:
    """Configuration for generation tasks."""
    kwargs: dict[str, Any] = field(default_factory=dict)
    prefix: str | None = None
    target_delimiter: str = " "

@dataclass
class RepeatConfig:
    """Configuration for repeated sampling."""
    repeats: int = 1
    reducer: str = "first"  # min, max, mean, median, first

@dataclass
class TaskConfig:
    """Main task configuration.

    Composes several sub-configurations for different aspects of the task.
    """
    # Required
    task: str
    output_type: str

    # Sub-configurations
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    doc_processing: DocProcessingConfig = field(default_factory=DocProcessingConfig)
    fewshot: FewshotConfig = field(default_factory=FewshotConfig)
    generation: GenerationConfig = field(default_factory=GenerationConfig)
    repeat: RepeatConfig = field(default_factory=RepeatConfig)

    # Top-level configs
    metric_list: list[MetricConfig] = field(default_factory=list)
    filter_list: list[FilterConfig] = field(default_factory=list)
    template: Any | None = None
    process_results: Callable | None = None

    # Mutual information
    unconditional_context: str = ""

    def __post_init__(self):
        """Validate configuration."""
        self._validate_output_type()
        self._validate_required_fields()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TaskConfig":
        """Create TaskConfig from nested dictionary.

        Handles:
        - Nested configs (dataset.path, fewshot.num_fewshot)
        - Flat configs for backward compatibility (dataset_path → dataset.path)
        - Type conversion
        """
        # Extract sub-configs
        dataset_data = data.get('dataset', {})
        # Also check for flat keys for backward compat
        if 'dataset_path' in data:
            dataset_data['path'] = data['dataset_path']
        if 'dataset_name' in data:
            dataset_data['name'] = data['dataset_name']
        # ... etc

        return cls(
            task=data['task'],
            output_type=data['output_type'],
            dataset=DatasetConfig(**dataset_data),
            fewshot=FewshotConfig(**data.get('fewshot', {})),
            # ... etc
        )
```

**Pros**:
- Logical grouping (dataset stuff together, fewshot stuff together)
- Each sub-config can be validated independently
- Easier to extend (add new sub-configs)
- Clearer which fields relate to which features

**Cons**:
- More complex object graph
- Nested access: `config.dataset.path` vs `config.dataset_path`
- Backward compatibility requires mapping
- More classes to maintain

### Option C: Hybrid (Recommended)

```python
@dataclass
class TaskConfig:
    """Configuration for a single task.

    This is a flat dataclass for simplicity, but logically groups
    related fields in the documentation and property accessors.
    """
    # === REQUIRED ===
    task: str
    output_type: str

    # === DATASET ===
    dataset_path: str | None = None
    dataset_name: str | None = None
    test_split: str | None = None
    validation_split: str | None = None
    training_split: str | None = None
    fewshot_split: str | None = None
    dataset_kwargs: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    custom_dataset: Callable | None = None
    process_docs: Callable | None = None

    # === DOCUMENT PROCESSING ===
    doc_to_text: Callable | str | None = None
    doc_to_choice: Callable | str | list | None = None
    doc_to_target: Callable | str | None = None
    doc_to_image: Callable | str | None = None
    doc_to_audio: Callable | str | None = None
    process_results: Callable | None = None

    # === FEW-SHOT ===
    num_fewshot: int | None = None
    fewshot_delimiter: str = "\n\n"
    fewshot_sampler: str = "random"
    fewshot_seed: int | None = None
    description: str | None = None

    # === GENERATION (generate_until tasks only) ===
    generation_kwargs: dict[str, Any] = field(default_factory=dict)
    gen_prefix: str | None = None
    target_delimiter: str = " "

    # === METRICS ===
    metric_list: list[MetricConfig] = field(default_factory=list)

    # === FILTERING ===
    filter_list: list[FilterConfig] = field(default_factory=list)

    # === TEMPLATES ===
    template: Any | None = None

    # === REPEATS ===
    repeats: int = 1
    repeat_reducer: str = "first"  # min, max, mean, median, first

    # === MUTUAL INFORMATION ===
    unconditional_context: str = ""

    # === PRIVATE (constructed in __post_init__) ===
    _fewshot_cfg: Any = field(init=False, repr=False, default=None)
    _metric_list: list[MetricConfig] = field(init=False, repr=False, default_factory=list)
    _filter_ensembles: list[FilterEnsemble] = field(init=False, repr=False, default_factory=list)

    def __post_init__(self):
        """Validate and construct derived fields."""
        self._validate()
        self._build_fewshot_cfg()
        self._build_metric_list()
        self._build_filter_ensembles()

    def _validate(self):
        """Validate configuration consistency."""
        from lm_eval.api.task import Task

        # Validate output_type
        if self.output_type not in Task._registry:
            raise ValueError(
                f"Invalid output_type='{self.output_type}'. "
                f"Valid: {sorted(Task._registry.keys())}"
            )

        # Validate dataset
        if not self.dataset_path and not self.custom_dataset:
            raise ValueError("Must specify dataset_path or custom_dataset")

        # Validate splits
        if not self.test_split and not self.validation_split:
            raise ValueError("Must specify test_split or validation_split")

        # Validate generation config for generate_until
        if self.output_type == "generate_until":
            if not self.generation_kwargs:
                logger.warning(
                    f"Task '{self.task}' is generate_until but has empty generation_kwargs"
                )

        # Validate fewshot
        if self.num_fewshot and self.num_fewshot > 0:
            if not self.fewshot_split and not self.training_split:
                logger.warning(
                    f"Task '{self.task}' has num_fewshot={self.num_fewshot} "
                    f"but no fewshot_split or training_split specified"
                )

        # Validate repeat_reducer
        valid_reducers = ["min", "max", "mean", "median", "first"]
        if self.repeat_reducer not in valid_reducers:
            raise ValueError(
                f"Invalid repeat_reducer='{self.repeat_reducer}'. "
                f"Valid: {valid_reducers}"
            )

    @classmethod
    def from_arbitrary_dict(cls, data: dict[str, Any]) -> "TaskConfig":
        """Create TaskConfig from dictionary (e.g., from YAML).

        Handles:
        - Missing optional fields (uses defaults)
        - Extra unknown fields (logs warning, ignores)
        - String function references (converts via utils)
        """
        from dataclasses import fields
        import logging

        logger = logging.getLogger(__name__)

        # Separate known from unknown fields
        known_field_names = {f.name for f in fields(cls) if f.init}
        known_data = {}
        unknown_data = {}

        for key, value in data.items():
            if key in known_field_names:
                known_data[key] = value
            else:
                unknown_data[key] = value

        # Warn about unknown fields
        if unknown_data:
            logger.warning(
                f"TaskConfig for '{data.get('task', '?')}' has unknown fields: "
                f"{sorted(unknown_data.keys())}. These will be ignored."
            )

        # Convert string references to functions
        known_data = cls._convert_string_refs(known_data)

        return cls(**known_data)

    @staticmethod
    def _convert_string_refs(data: dict[str, Any]) -> dict[str, Any]:
        """Convert string function references to actual functions."""
        # Fields that can be string references to functions
        function_fields = [
            'doc_to_text', 'doc_to_choice', 'doc_to_target',
            'doc_to_image', 'doc_to_audio',
            'process_docs', 'process_results', 'custom_dataset'
        ]

        for field in function_fields:
            if field in data and isinstance(data[field], str):
                if data[field].startswith('!function'):
                    # YAML function reference
                    data[field] = utils.get_function(data[field])

        return data

    def get_filters(self) -> list[FilterEnsemble]:
        """Get constructed filter ensembles."""
        return self._filter_ensembles

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary (excludes private fields)."""
        from dataclasses import asdict
        return {
            k: v for k, v in asdict(self).items()
            if not k.startswith('_')
        }
```

**Why Hybrid is Best**:
- ✅ Flat structure (simple access, `config.dataset_path`)
- ✅ Logical grouping via comments and documentation
- ✅ All validation in one place
- ✅ Backward compatible
- ✅ Easy to see all fields at once
- ✅ Property accessors can provide grouping if needed later

---

## Recommendations

### Immediate Actions (Critical)

1. **Create the config module** ✅ HIGH PRIORITY
   ```bash
   mkdir -p lm_eval/config
   touch lm_eval/config/__init__.py
   touch lm_eval/config/task.py
   touch lm_eval/config/utils.py
   touch lm_eval/config/metric.py
   touch lm_eval/config/filter.py
   touch lm_eval/config/fewshot.py
   ```

2. **Implement TaskConfig** using Option C (Hybrid)
   - Single dataclass with logical grouping
   - Comprehensive validation in `__post_init__`
   - Clear `from_arbitrary_dict()` for YAML loading

3. **Implement supporting config classes**:
   - `MetricConfig` - wraps metric name, function, kwargs, aggregation
   - `FilterConfig` - wraps filter name, filter functions
   - `FewshotConfig` - wraps fewshot sampling configuration

4. **Implement `process_field()` utility**
   - Handles field resolution from docs
   - Converts string refs to functions
   - Template variable substitution

### Short-term Improvements

5. **Add comprehensive validation**
   - Validate output_type against registry
   - Validate required fields based on output_type
   - Validate metric names against registered metrics
   - Validate filter compatibility

6. **Improve documentation**
   - Docstring for each field explaining when it's used
   - Examples showing common configurations
   - Migration guide from old config format (if applicable)

7. **Add type hints everywhere**
   - Use typing.Literal for enums (output_type, repeat_reducer)
   - Use NewType for semantic types
   - Add TypedDict for structured dicts (generation_kwargs)

### Long-term Refactoring

8. **Consider splitting by task type**
   - `GenerateTaskConfig` extends `TaskConfig` with generation-specific fields
   - `MCTaskConfig` extends `TaskConfig` with MC-specific fields
   - Enforces that only relevant fields are present

9. **Add config versioning**
   - Support multiple config versions for backward compat
   - Automatic migration from old to new formats
   - Clear deprecation warnings

10. **Add config validation CLI**
    - `lm-eval validate-task-config task.yaml`
    - Checks for common errors
    - Suggests fixes

---

## Example Implementation

See next section for a complete, working implementation of TaskConfig following the Hybrid approach.

---

## Comparison: Before vs After

### Before (Current - Broken)

```python
# DOES NOT WORK - imports don't exist
from lm_eval.config.task import TaskConfig

# Unclear how to create
config = TaskConfig(???)

# No validation
config.output_type = "invalid"  # No error until runtime

# No documentation of fields
config.mystery_field  # Is this required? What type? What does it do?
```

### After (Proposed)

```python
from lm_eval.config.task import TaskConfig

# Clear creation from dict
config = TaskConfig.from_arbitrary_dict({
    "task": "mmlu",
    "output_type": "loglikelihood",
    "dataset_path": "cais/mmlu",
    "test_split": "test",
    "metric_list": [{"metric": "acc"}],
})

# Immediate validation
# ValueError: Invalid output_type='invalid'. Valid: [...]

# Clear documentation
config.num_fewshot  # int | None - Number of few-shot examples
config.dataset_path  # str | None - Path to dataset on HF
```

---

## Next Steps

1. Implement the config module structure
2. Create TaskConfig using the Hybrid design
3. Create supporting config classes (MetricConfig, FilterConfig, etc.)
4. Add comprehensive tests
5. Update documentation
6. Consider adding schema validation (pydantic, marshmallow, etc.)
