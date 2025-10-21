# Template System - Developer Documentation

## Overview

This document describes the template system changes made to lm-evaluation-harness. It is intended for contributors who need to understand how the task configuration pipeline has changed and how the new template system works.

## Table of Contents

1. [Quick Summary](#quick-summary)
2. [What Changed](#what-changed)
3. [Task Configuration Pipeline](#task-configuration-pipeline)
4. [Template System Architecture](#template-system-architecture)
5. [Implementation Details](#implementation-details)
6. [Usage Examples](#usage-examples)
7. [Migration Guide](#migration-guide)
8. [Testing](#testing)

---

## Quick Summary

**What was added:**
- New template system for standardized prompt formatting
- Support for easy MCQ ↔ Cloze conversion
- Wrapper-based architecture where templates wrap user's `doc_to_*` fields

**What changed:**
- TaskConfig now processes `template` field in `__post_init__`
- TaskConfig wraps `doc_to_text` and `doc_to_choice` when template is specified
- New `lm_eval/api/template.py` module with template classes

**Backward compatibility:**
- ✅ All existing tasks without templates work unchanged
- ✅ No changes to runtime evaluation logic
- ✅ No breaking API changes

---

## What Changed

### Files Added

**`lm_eval/api/template.py`** (new file, ~650 lines)
- Core template system implementation
- Template classes: `MCQTemplateConfig`, `ClozeTemplateConfig`
- `TemplateFactory` for creating templates
- `process_field()` helper for extracting values from documents

**`WRAPPER_API.md`** (new file)
- User-facing documentation for template system
- API reference and examples

**`TEMPLATE_SYSTEM_CHANGES.md`** (this file)
- Developer documentation
- Implementation details for contributors

**`test_template_wrapper_standalone.py`** (new file)
- Comprehensive test suite for template system
- 6 tests covering all major functionality

### Files Modified

**`lm_eval/api/task.py`**
- Modified `TaskConfig.__post_init__()` to process templates
- Added template wrapping logic (lines 144-183)
- Added import: `from lm_eval.api.template import TemplateConfig, TemplateFactory`
- Added fields: `template`, `template_config`

**Changes to TaskConfig:**
```python
@dataclass
class TaskConfig(dict):
    # ... existing fields ...

    # NEW: Template configuration
    template: Optional[Union[str, dict]] = None
    template_config: Optional[TemplateConfig] = None

    def __post_init__(self) -> None:
        # ... existing logic ...

        # NEW: Process template configuration
        if self.template is not None:
            # Create template config
            if isinstance(self.template, str):
                if self.template == "mcq":
                    self.template_config = TemplateFactory.create_mmlu_style()
                # ...
            elif isinstance(self.template, dict):
                self.template_config = TemplateFactory.from_dict(self.template)

            # Wrap existing doc_to_text and doc_to_choice
            original_doc_to_text = self.doc_to_text
            original_doc_to_choice = self.doc_to_choice

            if original_doc_to_text is not None:
                self.doc_to_text = self.template_config.wrap_doc_to_text(
                    original_doc_to_text,
                    original_doc_to_choice
                )

            if original_doc_to_choice is not None:
                self.doc_to_choice = self.template_config.wrap_doc_to_choice(
                    original_doc_to_choice
                )
```

---

## Task Configuration Pipeline

### Before (Without Templates)

```
┌─────────────┐
│  YAML File  │
└──────┬──────┘
       │
       │ Load & Parse
       ▼
┌─────────────────────────────────────────────┐
│            TaskConfig                        │
│                                             │
│  - doc_to_text: "{{question}}\nA. ..."     │  ← User manually formats
│  - doc_to_choice: ["A", "B", "C", "D"]    │  ← User manually specifies
│  - doc_to_target: "answer"                 │
└──────┬──────────────────────────────────────┘
       │
       │ Pass to ConfigurableTask
       ▼
┌─────────────────────────────────────────────┐
│        ConfigurableTask                      │
│                                             │
│  - Processes doc_to_text at runtime        │
│  - Calls doc_to_text(doc) for each doc    │
│  - Returns formatted prompt                 │
└─────────────────────────────────────────────┘
```

### After (With Templates)

```
┌─────────────────────────────────────────────┐
│              YAML File                       │
│                                             │
│  doc_to_text: "{{question}}"               │  ← User specifies data extraction
│  doc_to_choice: "{{choices.text}}"         │  ← User specifies data extraction
│  template:                                  │  ← User specifies formatting
│    template_type: mcq::mmlu                │
└──────┬──────────────────────────────────────┘
       │
       │ Load & Parse
       ▼
┌─────────────────────────────────────────────┐
│      TaskConfig.__post_init__()             │
│                                             │
│  1. Create template from template field    │
│     template_config = TemplateFactory      │
│                      .from_dict(...)       │
│                                             │
│  2. Store originals                         │
│     original_doc_to_text = self.doc_to_text│
│     original_doc_to_choice = ...           │
│                                             │
│  3. Wrap with template                      │
│     self.doc_to_text =                     │
│       template_config.wrap_doc_to_text(    │
│         original_doc_to_text,              │
│         original_doc_to_choice             │
│       )                                     │
│                                             │
│     self.doc_to_choice =                   │
│       template_config.wrap_doc_to_choice(  │
│         original_doc_to_choice             │
│       )                                     │
└──────┬──────────────────────────────────────┘
       │
       │ TaskConfig now has wrapped callables
       ▼
┌─────────────────────────────────────────────┐
│            TaskConfig                        │
│                                             │
│  doc_to_text: <wrapped callable>           │  ← Extracts + formats
│    def wrapped(doc):                        │
│      q = extract("{{question}}", doc)      │
│      c = extract("{{choices.text}}", doc)  │
│      return format_mmlu(q, c)              │
│                                             │
│  doc_to_choice: <wrapped callable>         │  ← Returns labels
│    def wrapped(doc):                        │
│      choices = extract("{{choices}}", doc) │
│      return ["A", "B", "C", ...][:len(c)] │
└──────┬──────────────────────────────────────┘
       │
       │ Pass to ConfigurableTask
       │ (no changes needed)
       ▼
┌─────────────────────────────────────────────┐
│        ConfigurableTask                      │
│                                             │
│  - Processes doc_to_text at runtime        │  ← Same as before!
│  - Calls doc_to_text(doc) for each doc    │  ← Same as before!
│  - Returns formatted prompt                 │  ← Same as before!
│                                             │
│  NO CHANGES TO ConfigurableTask            │
└─────────────────────────────────────────────┘
```

**Key Insight:** The template system works entirely at config time (in `TaskConfig.__post_init__`). By the time `ConfigurableTask` receives the config, `doc_to_text` and `doc_to_choice` are already wrapped callables. No runtime changes needed!

---

## Template System Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    lm_eval/api/template.py                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────────┐    ┌──────────────┐
│TemplateConfig│    │MCQTemplateConfig │    │ClozeTemplate │
│  (Abstract)  │    │                  │    │   Config     │
├──────────────┤    ├──────────────────┤    ├──────────────┤
│              │    │ choice_labels    │    │ blank_marker │
│ Common:      │    │ choice_format    │    │ show_choices │
│ - prefix     │    │ suffix           │    │ ...          │
│ - suffix     │    │ ...              │    │              │
│ - delimiters │    │                  │    │              │
│              │    │ Methods:         │    │ Methods:     │
│ Methods:     │    │ - format_prompt()│    │ - format_... │
│ - wrap_...   │    │ - to_cloze()     │    │ - to_mcq()   │
│ - _should... │    │ - to_dict()      │    │ - to_dict()  │
└──────────────┘    └──────────────────┘    └──────────────┘
                              │
                              │
                              ▼
                    ┌──────────────────┐
                    │ TemplateFactory  │
                    ├──────────────────┤
                    │ from_dict()      │
                    │ create_mmlu_...()│
                    │ create_gpqa_...()│
                    │ convert_...()    │
                    └──────────────────┘
```

### Class Hierarchy

**`TemplateConfig` (Abstract Base Class)**
```python
@dataclass
class TemplateConfig(ABC):
    prefix: str = ""
    suffix: str = "Answer:"
    question_choice_delimiter: str = "\n"
    choice_delimiter: str = "\n"

    @abstractmethod
    def format_prompt(self, question, choices) -> str:
        """Format a prompt from question and choices."""
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        pass

    def wrap_doc_to_text(self, original_doc_to_text, original_doc_to_choice):
        """Wrap user's doc_to_text with template formatting."""
        def wrapped(doc):
            question = process_field(doc, original_doc_to_text, "")
            choices = process_field(doc, original_doc_to_choice, [])
            return self.format_prompt(question, choices)
        return wrapped

    def wrap_doc_to_choice(self, original_doc_to_choice):
        """Wrap user's doc_to_choice to return template labels."""
        def wrapped(doc):
            choices = process_field(doc, original_doc_to_choice, [])
            num_choices = len(choices) if isinstance(choices, list) else len(self.choice_labels)
            return self.choice_labels[:num_choices]
        return wrapped
```

**`MCQTemplateConfig` (Multiple Choice Questions)**
```python
@dataclass
class MCQTemplateConfig(TemplateConfig):
    choice_labels: List[str] = ["A", "B", "C", "D"]
    choice_format: str = "{label}. {choice}"
    show_choices_in_prompt: bool = True

    def format_prompt(self, question, choices):
        parts = [self.prefix, question]
        if choices and self.show_choices_in_prompt:
            formatted = [
                self.choice_format.format(label=l, choice=c)
                for l, c in zip(self.choice_labels, choices)
            ]
            parts.append(self.choice_delimiter.join(formatted))
        parts.append(self.suffix)
        return self.question_choice_delimiter.join(parts)

    def to_cloze(self):
        """Convert to cloze template."""
        return ClozeTemplateConfig(...)
```

**`ClozeTemplateConfig` (Fill-in-the-blank)**
```python
@dataclass
class ClozeTemplateConfig(TemplateConfig):
    blank_marker: str = "______"
    show_choices: bool = True
    choice_labels: Optional[List[str]] = None
    blank_position: str = "end"
    choices_prefix: str = "\nOptions: "

    def format_prompt(self, question, choices):
        parts = [self.prefix]
        question_with_blank = f"{question} {self.blank_marker}"
        parts.append(question_with_blank)
        if choices and self.show_choices:
            # Format choices as options
            ...
        return self.question_choice_delimiter.join(parts)

    def to_mcq(self):
        """Convert to MCQ template."""
        return MCQTemplateConfig(...)
```

---

## Implementation Details

### 1. process_field() Function

**Purpose:** Extract a value from a document given a field specification.

**Supports:**
- Simple field names: `"question"` → `doc["question"]`
- Jinja2 single expressions: `"{{question}}"` → `doc["question"]` (preserves type)
- Jinja2 complex templates: `"{{a}}: {{b}}"` → `"value_a: value_b"` (returns string)
- Nested access: `"{{choices.text}}"` → `doc["choices"]["text"]`
- Callables: `lambda doc: doc["question"]`

**Implementation:**
```python
def process_field(doc: dict, field_spec: Union[str, Callable, None], default: Any = None):
    if field_spec is None:
        return default
    elif callable(field_spec):
        return field_spec(doc)
    elif isinstance(field_spec, str):
        if "{{" in field_spec and "}}" in field_spec:
            # Check if single expression (preserves type) vs complex (returns string)
            matches = re.findall(r'\{\{(.+?)\}\}', field_spec)

            if len(matches) == 1 and field_spec.strip() == f"{{{{{matches[0]}}}}}":
                # Single expression - use direct extraction (preserves type)
                expr = matches[0].strip()
                # Navigate: "choices.text" → doc["choices"]["text"]
                parts = expr.split('.')
                value = doc
                for part in parts:
                    value = value[part]  # (simplified - actual code handles indexing)
                return value
            else:
                # Complex template - use Jinja2 (returns string)
                env = Environment(loader=BaseLoader())
                template = env.from_string(field_spec)
                return template.render(doc)
        else:
            # Simple field name
            return doc.get(field_spec, default)
    else:
        return field_spec
```

**Why this matters:**
- `"{{choices}}"` returns a list (not string representation)
- Allows templates to iterate over actual choice values
- Complex templates like `"{{subject}}: {{question}}"` still work

### 2. Template Wrapping

**wrap_doc_to_text():**
```python
def wrap_doc_to_text(self, original_doc_to_text, original_doc_to_choice):
    def wrapped_doc_to_text(doc: dict) -> str:
        # 1. Extract question using user's spec
        question = process_field(doc, original_doc_to_text, "")

        # 2. Extract choices using user's spec (if needed)
        if self._should_show_choices() and original_doc_to_choice is not None:
            choices = process_field(doc, original_doc_to_choice, [])
        else:
            choices = None

        # 3. Format according to template
        return self.format_prompt(question, choices)

    return wrapped_doc_to_text
```

**wrap_doc_to_choice():**
```python
def wrap_doc_to_choice(self, original_doc_to_choice):
    def wrapped_doc_to_choice(doc: dict) -> List[str]:
        # 1. Extract choices to determine count
        choices = process_field(doc, original_doc_to_choice, [])

        # 2. Return appropriate number of labels
        num_choices = len(choices) if isinstance(choices, list) else len(self.choice_labels)
        return self.choice_labels[:num_choices]

    return wrapped_doc_to_choice
```

### 3. Template Factory

**Supports `template_type::style` syntax:**
```python
@staticmethod
def from_dict(config: Dict[str, Any]) -> TemplateConfig:
    template_type = config.get("template_type", "mcq")

    # Support :: syntax
    if "::" in template_type:
        type_part, style_part = template_type.split("::", 1)

        if type_part == "mcq":
            if style_part == "mmlu":
                return TemplateFactory.create_mmlu_style()
            elif style_part == "gpqa":
                return TemplateFactory.create_gpqa_style()
            # ...

    # Regular dict-based construction
    if template_type == "mcq":
        return MCQTemplateConfig(**config)
    # ...
```

**Predefined templates:**
- `create_mmlu_style()` → MMLU-style MCQ
- `create_gpqa_style()` → GPQA-style MCQ
- `create_numbered_style()` → Numbered MCQ
- `create_cloze_with_options()` → Cloze with options
- `create_pure_cloze()` → Pure cloze

### 4. TaskConfig Integration

**In `TaskConfig.__post_init__()`:**
```python
# Process template configuration
if self.template is not None:
    # 1. Create template config from template field
    if isinstance(self.template, str):
        if self.template == "mcq":
            self.template_config = TemplateFactory.create_mmlu_style()
        elif self.template == "cloze":
            self.template_config = TemplateFactory.create_cloze_with_options()
    elif isinstance(self.template, dict):
        self.template_config = TemplateFactory.from_dict(self.template)

    # 2. Store originals
    original_doc_to_text = self.doc_to_text
    original_doc_to_choice = self.doc_to_choice

    # 3. Wrap with template
    if original_doc_to_text is not None:
        self.doc_to_text = self.template_config.wrap_doc_to_text(
            original_doc_to_text,
            original_doc_to_choice
        )

    if original_doc_to_choice is not None:
        self.doc_to_choice = self.template_config.wrap_doc_to_choice(
            original_doc_to_choice
        )
```

---

## Usage Examples

### Example 1: Basic MMLU-Style MCQ

**YAML:**
```yaml
task: arc_easy
doc_to_text: "{{question}}"
doc_to_choice: "{{choices.text}}"
doc_to_target: "{{choices.label.index(answerKey)}}"
template:
  template_type: mcq::mmlu
output_type: multiple_choice
```

**What happens:**
1. TaskConfig loads YAML
2. `__post_init__` creates MMLU template
3. Wraps `doc_to_text` and `doc_to_choice`
4. ConfigurableTask uses wrapped callables

**Runtime:**
```python
doc = {
    "question": "What is the capital of France?",
    "choices": {
        "text": ["London", "Paris", "Berlin", "Madrid"],
        "label": ["A", "B", "C", "D"]
    },
    "answerKey": "B"
}

# doc_to_text(doc) returns:
"""
What is the capital of France?
A. London
B. Paris
C. Berlin
D. Madrid
Answer:
"""

# doc_to_choice(doc) returns:
["A", "B", "C", "D"]

# doc_to_target(doc) returns:
1  # index of "B" in labels
```

### Example 2: Custom Template

**YAML:**
```yaml
task: custom_mcq
doc_to_text: "{{question}}"
doc_to_choice: "{{options}}"
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

### Example 3: MCQ to Cloze Conversion

**MCQ YAML:**
```yaml
task: task_mcq
doc_to_text: "{{question}}"
doc_to_choice: "{{choices}}"
template:
  template_type: mcq::mmlu
```

**Cloze YAML (same data extraction, different format):**
```yaml
task: task_cloze
doc_to_text: "{{question}}"
doc_to_choice: "{{choices}}"
template:
  template_type: cloze
```

**Programmatic conversion:**
```python
# Load MCQ template
mcq_template = TemplateFactory.from_dict({"template_type": "mcq::mmlu"})

# Convert to cloze
cloze_template = mcq_template.to_cloze()

# Use in config
config = TaskConfig(
    doc_to_text="{{question}}",
    doc_to_choice="{{choices}}",
    template=cloze_template.to_dict()
)
```

### Example 4: With Callables (Python)

```python
def extract_question(doc):
    """Custom question extractor."""
    return f"Q: {doc['question'].upper()}"

def extract_choices(doc):
    """Custom choice extractor."""
    return [c.strip() for c in doc['choices']]

config = TaskConfig(
    task="custom_task",
    doc_to_text=extract_question,  # Callable
    doc_to_choice=extract_choices,  # Callable
    template={"template_type": "mcq::mmlu"}
)
```

---

## Migration Guide

### For Task Creators

**Old way (manual formatting):**
```yaml
task: my_task
doc_to_text: "{{question.strip()}}\nA. {{choices[0]}}\nB. {{choices[1]}}\nC. {{choices[2]}}\nD. {{choices[3]}}\nAnswer:"
doc_to_choice: ["A", "B", "C", "D"]
doc_to_target: answer
```

**New way (with template):**
```yaml
task: my_task
doc_to_text: "{{question}}"
doc_to_choice: "{{choices}}"
doc_to_target: answer
template:
  template_type: mcq::mmlu
```

**Benefits:**
- Cleaner YAML
- Easy format conversion (just change template_type)
- Consistent formatting
- Handles variable choice counts automatically

### For Contributors

**If you're adding a new task:**
1. Use templates when possible
2. Specify data extraction in `doc_to_text` and `doc_to_choice`
3. Use `template` for formatting

**If you're modifying existing tasks:**
- Templates are optional - no need to convert everything
- Test both with and without templates
- Ensure backward compatibility

**If you're modifying ConfigurableTask:**
- No changes needed! Templates work at config time
- `doc_to_text` and `doc_to_choice` are already wrapped callables
- Runtime behavior unchanged

---

## Testing

### Test Files

**`test_template_wrapper_standalone.py`**
- 6 comprehensive tests
- Tests all major functionality
- Runs without full package installation

**Run tests:**
```bash
python test_template_wrapper_standalone.py
```

**Tests:**
1. ✅ Basic wrapper API (Jinja2 extraction + MMLU formatting)
2. ✅ `mcq::mmlu` syntax
3. ✅ `mcq::gpqa` syntax
4. ✅ Variable choice count (generic formatting)
5. ✅ Cloze template
6. ✅ Complex Jinja2 templates

### Manual Testing

**Test template creation:**
```python
from lm_eval.api.template import TemplateFactory

# Create from dict
template = TemplateFactory.from_dict({"template_type": "mcq::mmlu"})
print(template.choice_labels)  # ["A", "B", "C", "D"]

# Test wrapping
doc = {"question": "Test?", "choices": ["A", "B", "C"]}
wrapped = template.wrap_doc_to_text("{{question}}", "{{choices}}")
print(wrapped(doc))  # Should show formatted prompt
```

**Test TaskConfig integration:**
```python
from lm_eval.api.task import TaskConfig

config = TaskConfig(
    task="test",
    doc_to_text="{{question}}",
    doc_to_choice="{{choices}}",
    template={"template_type": "mcq::mmlu"}
)

doc = {"question": "Test?", "choices": ["A", "B", "C"]}
print(config.doc_to_text(doc))  # Should show MMLU-formatted prompt
print(config.doc_to_choice(doc))  # Should return ["A", "B", "C"]
```

---

## Common Questions

### Q: Do I have to use templates?

**A:** No! Templates are completely optional. All existing tasks without templates work unchanged.

### Q: Can I mix templates with manual formatting?

**A:** Yes. If you specify both `template` and `doc_to_text`, the template wraps your `doc_to_text`. If you want to skip wrapping for `doc_to_text` but use template for `doc_to_choice`, set `template` but keep your custom `doc_to_text`.

### Q: Do templates work with custom Python tasks?

**A:** Yes! You can pass callables as `doc_to_text` and `doc_to_choice`, and templates will wrap them.

### Q: Can I create my own template types?

**A:** Yes! Extend `TemplateConfig` and implement the required methods. See `MCQTemplateConfig` for an example.

### Q: How do templates handle variable numbers of choices?

**A:** Templates automatically adapt. If a document has 3 choices, the template uses 3 labels (A, B, C). If it has 5 choices but the template only defines 4 labels, it uses 4.

### Q: What if I need to debug template wrapping?

**A:** Add logging in `TaskConfig.__post_init__()` or check `config.template_config` to see the template that was created.

---

## Architecture Decisions

### Why Wrapper-Based?

**Alternatives considered:**
1. ❌ Replace `doc_to_text` entirely → Breaks when users have custom extraction
2. ❌ Add new fields `doc_to_question`, `doc_to_choices` → Breaking change
3. ✅ Wrap existing fields → Clean, backward compatible, separation of concerns

**Benefits of wrapping:**
- Users control data extraction
- Templates control formatting
- No breaking changes
- Easy to debug (can inspect originals)

### Why `template_type::style` Syntax?

**Alternatives:**
- `template_type: "mcq"`, `template_style: "mmlu"` → Too verbose
- `template: "mmlu"` → Not clear it's MCQ vs Cloze
- ✅ `template_type: "mcq::mmlu"` → Clear hierarchy, concise

### Why process_field() Preserves Types?

**Problem:** Jinja2 always returns strings. `"{{choices}}"` → `"['A', 'B', 'C']"` (string)

**Solution:** Detect single-expression templates and use direct extraction.

**Benefit:** Templates can iterate over actual lists, not string representations.

---

## Summary for Contributors

**Key Takeaways:**

1. **Templates wrap, not replace** - User's `doc_to_*` fields are wrapped with formatting
2. **Config-time processing** - All template logic happens in `TaskConfig.__post_init__`
3. **No runtime changes** - `ConfigurableTask` sees wrapped callables, works as before
4. **Backward compatible** - Tasks without templates work unchanged
5. **Easy conversion** - Change `template_type` to convert between formats

**When working on tasks:**
- Use templates for consistent formatting
- Specify data extraction in `doc_to_text` / `doc_to_choice`
- Use `template` for formatting

**When working on core:**
- Template logic is in `lm_eval/api/template.py`
- Integration is in `TaskConfig.__post_init__()`
- No changes needed to `ConfigurableTask`

**Testing:**
- Run `test_template_wrapper_standalone.py`
- Test with and without templates
- Check backward compatibility

---

## References

- **Implementation:** `lm_eval/api/template.py`
- **Integration:** `lm_eval/api/task.py` (lines 144-183)
- **User Docs:** `WRAPPER_API.md`
- **Tests:** `test_template_wrapper_standalone.py`
- **Example:** `lm_eval/tasks/arc/arc_easy.yaml`

---

## Changelog

**Initial Implementation (commits f2caf55, bab9ad2, 96bfe37):**
- Added template system with MCQ and Cloze templates
- Implemented wrapper-based architecture
- Added `template_type::style` syntax support
- Integrated with TaskConfig
- Created comprehensive test suite
- Full backward compatibility maintained
