# Template System for lm-evaluation-harness

This directory demonstrates the new template system for task configuration in lm-evaluation-harness. The template system makes it easy to:

1. Define task prompts in a standardized way
2. Convert between different prompt formats (MCQ, Cloze, etc.)
3. Customize formatting without duplicating logic
4. Maintain consistency across similar tasks

## Quick Start

### Basic MCQ Template (MMLU-style)

```yaml
task: my_mcq_task
template: mcq  # Uses default MMLU-style formatting
doc_to_target: answer
```

This automatically formats prompts as:
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
task: my_cloze_task
template: cloze  # Uses default cloze formatting
doc_to_target: answer
```

This automatically formats prompts as:
```
Question text ______
Options: A. choice1 B. choice2 C. choice3 D. choice4
```

## Converting Between Formats

### Method 1: Change Template in YAML

To convert from MCQ to Cloze, simply change the template field:

```yaml
# MCQ version
template: mcq

# Cloze version
template: cloze
```

### Method 2: Programmatic Conversion

You can also convert templates programmatically:

```python
from lm_eval.api.template import TemplateFactory, mmlu_template

# Create an MCQ template
mcq = mmlu_template()

# Convert to cloze
cloze = mcq.to_cloze()

# Or vice versa
mcq_again = cloze.to_mcq()
```

## Template Types

### MCQ Template

Multiple Choice Question template with labeled choices.

**Default format (MMLU-style):**
```
Question
A. choice1
B. choice2
C. choice3
D. choice4
Answer:
```

**Configuration options:**
- `choice_labels`: List of labels (default: ["A", "B", "C", "D"])
- `choice_format`: Format string for each choice (default: "{label}. {choice}")
- `suffix`: Text after choices (default: "Answer:")
- `choice_delimiter`: Separator between choices (default: "\n")

**Examples:**

MMLU style:
```yaml
template:
  template_type: mcq
  choice_labels: ["A", "B", "C", "D"]
  choice_format: "{label}. {choice}"
  choice_delimiter: "\n"
```

GPQA style (inline):
```yaml
template:
  template_type: mcq
  choice_labels: ["A", "B", "C", "D"]
  choice_format: "({label}) {choice}"
  choice_delimiter: " "
```

Numbered:
```yaml
template:
  template_type: mcq
  choice_labels: ["1", "2", "3", "4"]
  choice_format: "{label}. {choice}"
```

### Cloze Template

Fill-in-the-blank template with optional choices.

**Default format:**
```
Question ______
Options: A. choice1 B. choice2 C. choice3 D. choice4
```

**Configuration options:**
- `blank_marker`: Marker for the blank (default: "______")
- `show_choices`: Whether to show choices (default: true)
- `choice_labels`: Labels if showing choices (default: ["A", "B", "C", "D"])
- `choice_format`: Format for choices (default: "{label}. {choice}")
- `choices_prefix`: Text before choices (default: "\nOptions: ")
- `blank_position`: "end" or "inline" (default: "end")

**Examples:**

With options:
```yaml
template:
  template_type: cloze
  blank_marker: "______"
  show_choices: true
  choice_labels: ["A", "B", "C", "D"]
```

Pure cloze (no options):
```yaml
template:
  template_type: cloze
  blank_marker: "[MASK]"
  show_choices: false
```

## Custom Templates

You can fully customize any template:

```yaml
template:
  template_type: mcq
  prefix: "Answer this question:\n"
  suffix: "\nYour answer:"
  choice_labels: ["(a)", "(b)", "(c)", "(d)"]
  choice_format: "{label} {choice}"
  question_choice_delimiter: "\n\n"
  choice_delimiter: "\n"
```

## Template Factory

The `TemplateFactory` class provides convenience methods:

```python
from lm_eval.api.template import TemplateFactory

# Create predefined templates
mmlu = TemplateFactory.create_mmlu_style()
gpqa = TemplateFactory.create_gpqa_style()
numbered = TemplateFactory.create_numbered_style(num_choices=5)
cloze = TemplateFactory.create_cloze_with_options()
pure_cloze = TemplateFactory.create_pure_cloze()

# Convert between types
cloze_version = TemplateFactory.convert_template(mmlu, "cloze")
mcq_version = TemplateFactory.convert_template(cloze, "mcq")

# Create from dict
template = TemplateFactory.from_dict({
    "template_type": "mcq",
    "choice_labels": ["A", "B", "C", "D"],
    "choice_format": "{label}. {choice}"
})
```

## Example Files

This directory contains several example configurations:

- `test_mcq.yaml` - Basic MCQ with default MMLU style
- `test_mcq_custom.yaml` - MCQ with custom GPQA-style formatting
- `test_cloze.yaml` - Basic cloze with options
- `test_cloze_custom.yaml` - Cloze with custom blank marker
- `test_numbered.yaml` - MCQ with numbered choices

## Backward Compatibility

Tasks without a `template` field continue to work exactly as before. The template system is completely optional and backward compatible.

```yaml
# Old style - still works
doc_to_text: "{{question.strip()}}\nA. {{choices[0]}}\nB. {{choices[1]}}\nC. {{choices[2]}}\nD. {{choices[3]}}\nAnswer:"
doc_to_choice: ["A", "B", "C", "D"]

# New style - equivalent
template: mcq
```

## How It Works

1. **Configuration**: You specify a `template` field in your YAML config
2. **Processing**: During `TaskConfig.__post_init__()`, the template is processed
3. **Application**: The template generates appropriate `doc_to_text` and `doc_to_choice` values
4. **Runtime**: ConfigurableTask uses these values normally (no runtime changes needed)

The key insight is that templates are processed at **config time**, not runtime. This means:
- No performance overhead during evaluation
- Easy to inspect the generated config
- Full backward compatibility

## Migration Guide

### Converting Existing Tasks to Templates

**Before:**
```yaml
doc_to_text: "{{question.strip()}}\nA. {{choices[0]}}\nB. {{choices[1]}}\nC. {{choices[2]}}\nD. {{choices[3]}}\nAnswer:"
doc_to_choice: ["A", "B", "C", "D"]
```

**After:**
```yaml
template: mcq
```

### Creating Task Variants

To create a cloze version of an existing MCQ task:

1. Copy the YAML file
2. Change `template: mcq` to `template: cloze`
3. Update the task name and description

That's it! The template system handles the rest.

## Advanced Usage

### Custom Template Classes

You can create your own template classes by extending `TemplateConfig`:

```python
from lm_eval.api.template import TemplateConfig
from dataclasses import dataclass

@dataclass
class MyCustomTemplate(TemplateConfig):
    def format_prompt(self, question, choices=None, **kwargs):
        # Your custom formatting logic
        pass

    def get_doc_to_text(self):
        # Return Jinja2 template string
        pass

    def get_doc_to_choice(self):
        # Return choice configuration
        pass
```

### Runtime Template Switching

You can programmatically switch between templates:

```python
from lm_eval.api.task import TaskConfig
from lm_eval.api.template import mmlu_template

# Load base config
config = TaskConfig(...)

# Apply MCQ template
config.template_config = mmlu_template()
config.doc_to_text = config.template_config.get_doc_to_text()
config.doc_to_choice = config.template_config.get_doc_to_choice()

# Convert to cloze
cloze_template = config.template_config.to_cloze()
config.template_config = cloze_template
config.doc_to_text = cloze_template.get_doc_to_text()
config.doc_to_choice = cloze_template.get_doc_to_choice()
```

## Benefits

1. **Consistency**: All MCQ tasks use the same formatting logic
2. **Flexibility**: Easy to customize without duplicating code
3. **Maintainability**: Change formatting in one place
4. **Experimentation**: Quick to test different prompt formats
5. **Clarity**: YAML configs are cleaner and more readable
6. **Compatibility**: Works seamlessly with existing code

## Future Extensions

The template system is designed to be extensible. Potential future additions:

- Generation template (for open-ended questions)
- Ranking template (for ranking multiple options)
- Classification template (for label classification)
- Custom metric templates (automatically select metrics based on template type)

## Questions?

See the main documentation or check the source code at `lm_eval/api/template.py`.
