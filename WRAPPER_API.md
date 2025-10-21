# Template Wrapper API

## Overview

The template system uses a **wrapper-based architecture** where:
1. Users specify `doc_to_text` and `doc_to_choice` to extract data from documents
2. Templates wrap these to add formatting (MMLU style, GPQA style, etc.)
3. Templates use the `::` syntax for predefined styles (e.g., `mcq::mmlu`)

This design keeps data extraction separate from formatting, making it easy to:
- Convert between different prompt formats
- Customize formatting without changing extraction logic
- Maintain consistency across tasks

## Quick Start

###  Example: ARC-Easy Style

```yaml
task: arc_easy
dataset_path: allenai/ai2_arc
doc_to_text: "{{question}}"  # Extract question from document
doc_to_choice: "{{choices.text}}"  # Extract choices list from document
doc_to_target: "{{choices.label.index(answerKey)}}"
template:
  template_type: mcq::mmlu  # Format as MMLU style
output_type: multiple_choice
```

**What this generates:**
```
What is the capital of France?
A. London
B. Paris
C. Berlin
D. Madrid
Answer:
```

The template wraps `doc_to_text` and `doc_to_choice` to add:
- Choice labels (A, B, C, D)
- Choice formatting (label + period + choice text)
- Answer suffix

## Template Types

### MCQ Templates

Multiple Choice Question templates with labeled choices.

**Available styles:**
- `mcq::mmlu` - MMLU style (A. B. C. D. with newlines)
- `mcq::gpqa` - GPQA style ((A) (B) (C) (D) inline)
- `mcq::numbered` - Numbered (1. 2. 3. 4.)

**Example:**
```yaml
template:
  template_type: mcq::gpqa
```

**Output:**
```
Question text
(A) choice1 (B) choice2 (C) choice3 (D) choice4
Answer:
```

### Cloze Templates

Fill-in-the-blank templates.

**Available styles:**
- `cloze` or `cloze::with_options` - With choices shown
- `cloze::pure` - No choices shown

**Example:**
```yaml
template:
  template_type: cloze
```

**Output:**
```
Question text ______
Options: A. choice1 B. choice2 C. choice3 D. choice4
```

## How It Works

### 1. User Specifies Data Extraction

```yaml
doc_to_text: "{{question}}"  # How to get the question
doc_to_choice: "{{choices}}"  # How to get the choices
```

These can be:
- **Simple field names**: `"question"`, `"choices"`
- **Jinja2 templates**: `"{{question.strip()}}"`, `"{{choices.text}}"`
- **Callables** (in Python): `lambda doc: doc['question']`

### 2. Template Wraps Them

```yaml
template:
  template_type: mcq::mmlu
```

The template creates wrapper functions:
```python
def wrapped_doc_to_text(doc):
    # Extract question using user's spec
    question = extract("{{question}}", doc)  # "What is..."

    # Extract choices using user's spec
    choices = extract("{{choices}}", doc)  # ["A", "B", "C", "D"]

    # Format according to template
    return format_mmlu(question, choices)  # Adds A. B. C. D. formatting
```

### 3. Result

The wrapped functions are used by `ConfigurableTask` at runtime:
- `doc_to_text(doc)` → Formatted prompt with MMLU-style choices
- `doc_to_choice(doc)` → Choice labels ["A", "B", "C", "D"]

## doc_to_text Specifications

### Simple Field Name

```yaml
doc_to_text: "question"
```

Extracts `doc['question']`.

### Jinja2 Template - Single Expression

```yaml
doc_to_text: "{{question.strip()}}"
```

Extracts and processes `doc['question']`. **Preserves type** (list remains list).

### Jinja2 Template - Complex

```yaml
doc_to_text: "{{subject}}: {{question.strip()}}"
```

Combines multiple fields. **Returns string**.

### Nested Access

```yaml
doc_to_choice: "{{choices.text}}"
```

Extracts `doc['choices']['text']`. **Preserves type**.

### With Indexing

```yaml
doc_to_target: "{{choices.label.index(answerKey)}}"
```

Uses method calls (falls back to Jinja2 rendering).

## Generic Choice Formatting

Templates adapt to the actual number of choices in the document:

```yaml
template:
  template_type: mcq::mmlu  # Has labels A, B, C, D
```

**Document with 3 choices:**
```python
{"question": "Pick color", "choices": ["Red", "Blue", "Green"]}
```
→ Uses labels A, B, C (not D)

**Document with 5 choices:**
```python
{"question": "Pick number", "choices": ["1", "2", "3", "4", "5"]}
```
→ Uses labels A, B, C, D (template only has 4 labels)

## Conversion Between Formats

### YAML - Just Change Template

**MCQ:**
```yaml
template:
  template_type: mcq::mmlu
```

**Cloze:**
```yaml
template:
  template_type: cloze
```

Same `doc_to_text` and `doc_to_choice`, different formatting!

### Python - Programmatic Conversion

```python
from lm_eval.api.template import TemplateFactory

# Create MCQ template
mcq = TemplateFactory.from_dict({"template_type": "mcq::mmlu"})

# Convert to cloze
cloze = mcq.to_cloze()

# Get wrappers
mcq_wrapper = mcq.wrap_doc_to_text(user_doc_to_text, user_doc_to_choice)
cloze_wrapper = cloze.wrap_doc_to_text(user_doc_to_text, user_doc_to_choice)
```

## Custom Templates

You can fully customize templates:

```yaml
template:
  template_type: mcq
  choice_labels: ["(a)", "(b)", "(c)", "(d)"]
  choice_format: "{label} {choice}"
  suffix: "Select one:"
  choice_delimiter: " | "
```

**Output:**
```
Question text
(a) choice1 | (b) choice2 | (c) choice3 | (d) choice4
Select one:
```

## Advanced Examples

### With Callables (Python)

```python
def custom_question_extractor(doc):
    """Custom function to extract and format question."""
    return f"Q: {doc['question'].upper()}"

config = TaskConfig(
    task="my_task",
    doc_to_text=custom_question_extractor,  # Callable
    doc_to_choice="{{options}}",  # Jinja2
    template={"template_type": "mcq::mmlu"}
)
```

### Numbered Choices

```yaml
template:
  template_type: mcq::numbered
  num_choices: 5  # Generate labels 1-5
```

### Pure Cloze (No Choices)

```yaml
template:
  template_type: cloze::pure
```

**Output:**
```
The capital of France is ______
```

## API Reference

### Template Types

| Type | Description | Output Example |
|------|-------------|----------------|
| `mcq::mmlu` | MMLU-style MCQ | `A. choice\nB. choice` |
| `mcq::gpqa` | GPQA-style MCQ | `(A) choice (B) choice` |
| `mcq::numbered` | Numbered MCQ | `1. choice\n2. choice` |
| `cloze` | Cloze with options | `question ______\nOptions: A. B.` |
| `cloze::pure` | Pure cloze | `question ______` |

### Template Methods

**`wrap_doc_to_text(original_doc_to_text, original_doc_to_choice)`**
- Wraps user's doc_to_text to add formatting
- Returns callable that formats prompts

**`wrap_doc_to_choice(original_doc_to_choice)`**
- Wraps user's doc_to_choice to return labels
- Returns callable that returns choice labels (A, B, C, D)

**`to_cloze()` / `to_mcq()`**
- Convert between template types
- Preserves all settings

### TemplateFactory

**`from_dict(config)`**
- Create template from dictionary
- Supports `::` syntax

**`create_mmlu_style()` / `create_gpqa_style()` / etc.**
- Factory methods for common styles

## Backward Compatibility

Tasks without templates continue to work:

```yaml
# Old style - still works
doc_to_text: "{{question}}\nA. {{choices[0]}}\nB. {{choices[1]}}"
doc_to_choice: ["A", "B", "C", "D"]
```

Templates are completely optional!

## Design Philosophy

1. **Separation of Concerns**: Data extraction (user) vs formatting (template)
2. **Wrapper Pattern**: Templates wrap, not replace
3. **Type Preservation**: Jinja2 templates preserve types when possible
4. **Flexibility**: Support field names, Jinja2, callables
5. **Ease of Use**: `::` syntax for common patterns

## Migration Guide

### From Manual Formatting

**Before:**
```yaml
doc_to_text: "{{question}}\nA. {{choices[0]}}\nB. {{choices[1]}}\nC. {{choices[2]}}\nD. {{choices[3]}}\nAnswer:"
doc_to_choice: ["A", "B", "C", "D"]
```

**After:**
```yaml
doc_to_text: "{{question}}"
doc_to_choice: "{{choices}}"
template:
  template_type: mcq::mmlu
```

Benefits:
- Cleaner YAML
- Easy format conversion
- Consistent formatting across tasks
- Handles variable choice counts

## Summary

The wrapper-based template API:
✅ Keeps data extraction and formatting separate
✅ Makes format conversion trivial (change template type)
✅ Supports callables, Jinja2, and field names
✅ Preserves types (lists stay lists)
✅ Adapts to variable choice counts
✅ Is backward compatible

Perfect for the arc_easy.yaml pattern!
