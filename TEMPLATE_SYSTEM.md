# Template System Implementation

## Overview

This document describes the new template system implemented for lm-evaluation-harness. The template system makes it **easy to convert between MCQ (Multiple Choice Question) and Cloze (fill-in-the-blank) formats** while maintaining consistency and reducing code duplication.

## Key Features

✅ **Easy Format Conversion**: Convert between MCQ and Cloze with a single method call
✅ **Backward Compatible**: Existing tasks without templates continue to work
✅ **Flexible Customization**: Support for different formatting styles (MMLU, GPQA, numbered, etc.)
✅ **Type-Safe**: Dataclass-based configuration with clear types
✅ **No Runtime Overhead**: Templates processed at config time, not during evaluation

## Architecture

### Components

1. **`lm_eval/api/template.py`** - Core template system
   - `TemplateConfig` - Abstract base class for templates
   - `MCQTemplateConfig` - Multiple choice question templates
   - `ClozeTemplateConfig` - Fill-in-the-blank templates
   - `TemplateFactory` - Factory for creating and converting templates

2. **`lm_eval/api/task.py`** - Integration with TaskConfig
   - Added `template` field to TaskConfig
   - Added `template_config` field to hold the processed template
   - Modified `__post_init__` to process templates

3. **`lm_eval/tasks/test_template/`** - Example templates and utilities
   - Example YAML configs for different template types
   - Conversion utility script
   - Comprehensive README

## Usage

### Basic MCQ Template

```yaml
task: my_task
template: mcq  # Uses default MMLU-style
doc_to_target: answer
output_type: multiple_choice
```

**Generated prompt:**
```
Question text
A. choice1
B. choice2
C. choice3
D. choice4
Answer:
```

### Basic Cloze Template

```yaml
task: my_task
template: cloze  # Uses default cloze style
doc_to_target: answer
output_type: multiple_choice
```

**Generated prompt:**
```
Question text ______
Options: A. choice1 B. choice2 C. choice3 D. choice4
```

### Converting Between Formats

#### In YAML

Simply change the `template` field:

```yaml
# MCQ version
template: mcq

# Cloze version
template: cloze
```

#### Programmatically

```python
from lm_eval.api.template import mmlu_template

# Create MCQ template
mcq = mmlu_template()

# Convert to cloze - EASY!
cloze = mcq.to_cloze()

# Convert back to MCQ
mcq_again = cloze.to_mcq()
```

#### Using the Conversion Utility

```bash
# Convert YAML config from MCQ to Cloze
python lm_eval/tasks/test_template/convert_template.py \
  -i task_mcq.yaml \
  -f cloze \
  -o task_cloze.yaml

# Run interactive demo
python lm_eval/tasks/test_template/convert_template.py --demo
```

## Template Types

### MCQ Template

**Configuration:**
```yaml
template:
  template_type: mcq
  choice_labels: ["A", "B", "C", "D"]
  choice_format: "{label}. {choice}"
  suffix: "Answer:"
  choice_delimiter: "\n"
  question_choice_delimiter: "\n"
```

**Options:**
- `choice_labels`: Labels for choices (default: ["A", "B", "C", "D"])
- `choice_format`: Format string with {label} and {choice} placeholders
- `suffix`: Text after choices (default: "Answer:")
- `choice_delimiter`: Separator between choices (default: "\n")
- `question_choice_delimiter`: Separator between question and choices

**Predefined Styles:**
- MMLU: `TemplateFactory.create_mmlu_style()`
- GPQA: `TemplateFactory.create_gpqa_style()`
- Numbered: `TemplateFactory.create_numbered_style(num_choices=4)`

### Cloze Template

**Configuration:**
```yaml
template:
  template_type: cloze
  blank_marker: "______"
  show_choices: true
  choice_labels: ["A", "B", "C", "D"]
  choice_format: "{label}. {choice}"
  choices_prefix: "\nOptions: "
  blank_position: end
```

**Options:**
- `blank_marker`: Marker for the blank (default: "______")
- `show_choices`: Whether to show choices (default: true)
- `choice_labels`: Labels if showing choices
- `choice_format`: Format for choices
- `choices_prefix`: Text before choices (default: "\nOptions: ")
- `blank_position`: "end" or "inline"

**Predefined Styles:**
- With options: `TemplateFactory.create_cloze_with_options()`
- Pure cloze: `TemplateFactory.create_pure_cloze()`

## Implementation Details

### How Templates Work

1. **Config Time Processing**:
   ```python
   # User specifies template in YAML
   template: mcq

   # TaskConfig.__post_init__ processes it:
   self.template_config = TemplateFactory.create_mmlu_style()
   self.doc_to_text = self.template_config.get_doc_to_text()
   self.doc_to_choice = self.template_config.get_doc_to_choice()
   ```

2. **Runtime Execution**:
   - ConfigurableTask uses `doc_to_text` and `doc_to_choice` normally
   - No changes needed to existing runtime code
   - No performance overhead

### Conversion Methods

Each template class has conversion methods:

**MCQTemplateConfig:**
```python
def to_cloze(self, blank_marker: str = "______") -> ClozeTemplateConfig:
    """Convert MCQ to Cloze format."""
    return ClozeTemplateConfig(
        prefix=self.prefix,
        suffix="",
        blank_marker=blank_marker,
        show_choices=True,
        choice_labels=self.choice_labels,
        choice_format=self.choice_format,
        choice_delimiter=self.choice_delimiter,
    )
```

**ClozeTemplateConfig:**
```python
def to_mcq(self, suffix: str = "Answer:") -> MCQTemplateConfig:
    """Convert Cloze to MCQ format."""
    return MCQTemplateConfig(
        prefix=self.prefix,
        suffix=suffix,
        choice_labels=self.choice_labels or ["A", "B", "C", "D"],
        choice_format=self.choice_format,
        # ... other fields
    )
```

## Examples

### Example 1: Converting MMLU to Cloze

**Original MMLU config:**
```yaml
doc_to_text: "{{question.strip()}}\nA. {{choices[0]}}\nB. {{choices[1]}}\nC. {{choices[2]}}\nD. {{choices[3]}}\nAnswer:"
doc_to_choice: ["A", "B", "C", "D"]
```

**New MCQ template:**
```yaml
template: mcq
```

**Converted to Cloze:**
```yaml
template: cloze
```

### Example 2: Custom GPQA-style

```yaml
template:
  template_type: mcq
  choice_labels: ["A", "B", "C", "D"]
  choice_format: "({label}) {choice}"
  choice_delimiter: " "  # Inline choices
  suffix: "Answer:"
```

**Output:**
```
Question text
(A) choice1 (B) choice2 (C) choice3 (D) choice4
Answer:
```

### Example 3: Numbered Choices

```yaml
template:
  template_type: mcq
  choice_labels: ["1", "2", "3", "4"]
  choice_format: "{label}. {choice}"
```

**Output:**
```
Question text
1. choice1
2. choice2
3. choice3
4. choice4
Answer:
```

## Testing

### Run Integration Tests

```bash
python test_template_integration.py
```

### Run Conversion Demo

```bash
python lm_eval/tasks/test_template/convert_template.py --demo
```

### Test YAML Conversion

```bash
python lm_eval/tasks/test_template/convert_template.py \
  -i lm_eval/tasks/test_template/test_mcq.yaml \
  -f cloze
```

## Files Created

```
lm_eval/
├── api/
│   ├── template.py                          # Core template system (NEW)
│   └── task.py                              # Modified to support templates
└── tasks/
    └── test_template/                       # Example templates (NEW)
        ├── README.md                        # Detailed documentation
        ├── convert_template.py              # Conversion utility
        ├── test_mcq.yaml                    # Basic MCQ example
        ├── test_mcq_custom.yaml             # Custom MCQ (GPQA style)
        ├── test_cloze.yaml                  # Basic Cloze example
        ├── test_cloze_custom.yaml           # Custom Cloze
        └── test_numbered.yaml               # Numbered MCQ

test_template_integration.py                 # Integration tests (NEW)
TEMPLATE_SYSTEM.md                          # This file (NEW)
```

## API Reference

### TemplateConfig (Abstract Base)

```python
@dataclass
class TemplateConfig(ABC):
    prefix: str = ""
    suffix: str = "Answer:"
    question_choice_delimiter: str = "\n"
    choice_delimiter: str = "\n"

    @abstractmethod
    def format_prompt(self, question, choices=None, **kwargs) -> str:
        """Format a complete prompt."""

    @abstractmethod
    def get_doc_to_text(self) -> Union[str, Callable]:
        """Get doc_to_text for TaskConfig."""

    @abstractmethod
    def get_doc_to_choice(self) -> Union[List[str], Dict, None]:
        """Get doc_to_choice for TaskConfig."""
```

### MCQTemplateConfig

```python
@dataclass
class MCQTemplateConfig(TemplateConfig):
    choice_labels: List[str] = ["A", "B", "C", "D"]
    choice_format: str = "{label}. {choice}"
    use_choice_labels: bool = True
    show_choices_in_prompt: bool = True

    def to_cloze(self, blank_marker="______") -> ClozeTemplateConfig:
        """Convert to cloze format."""
```

### ClozeTemplateConfig

```python
@dataclass
class ClozeTemplateConfig(TemplateConfig):
    blank_marker: str = "______"
    show_choices: bool = True
    choice_labels: Optional[List[str]] = None
    choice_format: str = "{label}. {choice}"
    blank_position: str = "end"
    choices_prefix: str = "\nOptions: "

    def to_mcq(self, suffix="Answer:") -> MCQTemplateConfig:
        """Convert to MCQ format."""
```

### TemplateFactory

```python
class TemplateFactory:
    @staticmethod
    def from_dict(config: Dict[str, Any]) -> TemplateConfig:
        """Create template from dict."""

    @staticmethod
    def create_mmlu_style() -> MCQTemplateConfig:
        """Create MMLU-style MCQ template."""

    @staticmethod
    def create_gpqa_style() -> MCQTemplateConfig:
        """Create GPQA-style MCQ template."""

    @staticmethod
    def create_numbered_style(num_choices=4) -> MCQTemplateConfig:
        """Create numbered MCQ template."""

    @staticmethod
    def create_cloze_with_options() -> ClozeTemplateConfig:
        """Create cloze template with options."""

    @staticmethod
    def create_pure_cloze() -> ClozeTemplateConfig:
        """Create pure cloze template."""

    @staticmethod
    def convert_template(template, target_type, **kwargs) -> TemplateConfig:
        """Convert between template types."""
```

## Benefits

1. **DRY Principle**: No need to duplicate formatting logic across tasks
2. **Consistency**: All MCQ tasks use the same formatting
3. **Flexibility**: Easy to experiment with different prompt formats
4. **Maintainability**: Change formatting in one place
5. **Clarity**: YAML configs are cleaner and more readable
6. **Experimentation**: Quick to test MCQ vs Cloze performance

## Future Enhancements

Potential future additions:

- **Generation Template**: For open-ended generation tasks
- **Ranking Template**: For ranking multiple options
- **Classification Template**: For multi-label classification
- **Automatic Metric Selection**: Choose metrics based on template type
- **Template Validation**: Validate template configs at load time
- **Template Presets**: More predefined styles (Chain-of-Thought, etc.)

## Backward Compatibility

✅ All existing tasks without `template` field continue to work
✅ Manual `doc_to_text` and `doc_to_choice` take precedence over templates
✅ No changes required to existing task implementations
✅ No changes to runtime evaluation logic

## Summary

The template system makes it **trivial to convert between MCQ and Cloze formats**. Instead of manually rewriting `doc_to_text` and `doc_to_choice` for each format, you can:

1. **In YAML**: Change `template: mcq` to `template: cloze`
2. **In Python**: Call `mcq_template.to_cloze()` or `cloze_template.to_mcq()`
3. **With CLI**: Run the conversion utility script

This enables rapid experimentation with different prompt formats while maintaining clean, consistent code.
