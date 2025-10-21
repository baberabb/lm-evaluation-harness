"""
Template system for task configuration in lm-evaluation-harness.

This module provides a flexible template system for defining how tasks should format
their prompts, particularly for MCQ (Multiple Choice Question) and Cloze (fill-in-the-blank)
style evaluations. The template system allows easy conversion between different formats
while maintaining consistent evaluation logic.

Key Features:
- MCQ templates with customizable choice formatting (A/B/C/D, 1/2/3/4, etc.)
- Cloze templates for fill-in-the-blank style questions
- Easy conversion between template types
- Support for different prompt structures (MMLU, GPQA, etc.)
- Support for callable doc_to_* fields
- Generic choice formatting that works with arbitrary choice lists
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union, Callable
from abc import ABC, abstractmethod
from jinja2 import Template as Jinja2Template, Environment, BaseLoader


def process_field(doc: dict, field_spec: Union[str, Callable, None], default: Any = None) -> Any:
    """
    Process a field specification to extract value from a document.

    Args:
        doc: Document dictionary
        field_spec: Field specification - can be:
            - None: return default
            - str: field name or Jinja2 template
            - Callable: function that takes doc and returns value
        default: Default value if field_spec is None

    Returns:
        Extracted value
    """
    if field_spec is None:
        return default
    elif callable(field_spec):
        return field_spec(doc)
    elif isinstance(field_spec, str):
        # Check if it's a Jinja2 template (contains {{ }})
        if "{{" in field_spec and "}}" in field_spec:
            # Check if it's a simple single-expression template like "{{choices.text}}"
            # vs a complex template like "{{subject}}: {{question}}"
            import re
            matches = re.findall(r'\{\{(.+?)\}\}', field_spec)

            # If it's ONLY a single Jinja2 expression (no literal text), use direct extraction
            # This preserves types (e.g., lists remain lists)
            if len(matches) == 1 and field_spec.strip() == f"{{{{{matches[0]}}}}}":
                expr = matches[0].strip()

                # Evaluate the expression in the context of doc
                # This allows us to get the actual value, not a string representation
                try:
                    # Use a safe evaluation approach
                    # Split by '.' to navigate nested dicts
                    parts = expr.split('.')
                    value = doc
                    for part in parts:
                        # Handle list indexing like choices[0]
                        if '[' in part:
                            key = part[:part.index('[')]
                            index_str = part[part.index('[')+1:part.index(']')]
                            value = value[key]
                            try:
                                index = int(index_str)
                                value = value[index]
                            except ValueError:
                                # It's a string index
                                value = value[index_str]
                        else:
                            value = value[part]
                    return value
                except (KeyError, IndexError, TypeError):
                    # Fall back to Jinja2 rendering if manual parsing fails
                    env = Environment(loader=BaseLoader())
                    template = env.from_string(field_spec)
                    return template.render(doc)
            else:
                # Complex template with multiple expressions or literal text
                # Use Jinja2 rendering (returns string)
                env = Environment(loader=BaseLoader())
                template = env.from_string(field_spec)
                return template.render(doc)
        else:
            # It's a field name
            return doc.get(field_spec, default)
    else:
        return field_spec


@dataclass
class TemplateConfig(ABC):
    """
    Base class for all template configurations.

    Templates define how to format prompts, choices, and answers for different
    task types. They handle the conversion between raw data and formatted strings
    that will be sent to the model.
    """

    # The prompt prefix (e.g., "The following are multiple choice questions...")
    prefix: str = ""

    # The prompt suffix (e.g., "Answer:")
    suffix: str = "Answer:"

    # Delimiter between question and choices
    question_choice_delimiter: str = "\n"

    # Delimiter between individual choices
    choice_delimiter: str = "\n"

    @abstractmethod
    def format_prompt(self, question: str, choices: Optional[List[str]] = None, **kwargs) -> str:
        """
        Format a complete prompt from question and choices.

        Args:
            question: The question text
            choices: List of choice strings (if applicable)
            **kwargs: Additional template-specific parameters

        Returns:
            Formatted prompt string
        """
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert template config to dictionary for YAML export.

        Returns:
            Dictionary representation of the template
        """
        pass

    def _should_show_choices(self) -> bool:
        """
        Check if this template shows choices in the prompt.

        Different template types use different attribute names.
        """
        # MCQTemplateConfig uses 'show_choices_in_prompt'
        if hasattr(self, 'show_choices_in_prompt'):
            return self.show_choices_in_prompt
        # ClozeTemplateConfig uses 'show_choices'
        elif hasattr(self, 'show_choices'):
            return self.show_choices
        # Default to True
        return True

    def wrap_doc_to_text(
        self,
        original_doc_to_text: Union[str, Callable, None],
        original_doc_to_choice: Union[str, Callable, List, None] = None
    ) -> Callable:
        """
        Wrap existing doc_to_text to add template formatting.

        This is the key method for the wrapper API. It takes the user's
        doc_to_text and doc_to_choice specifications and wraps them to
        add template formatting.

        Args:
            original_doc_to_text: User's doc_to_text (Jinja2, callable, or field name)
            original_doc_to_choice: User's doc_to_choice (Jinja2, callable, list, or field name)

        Returns:
            New callable that extracts values using originals and formats with template

        Example:
            # User specifies:
            doc_to_text = "{{question}}"
            doc_to_choice = "{{choices.text}}"
            template = mcq::mmlu

            # Template wraps them:
            wrapped = template.wrap_doc_to_text(doc_to_text, doc_to_choice)

            # Result formats as MMLU style with A/B/C/D labels
        """
        def wrapped_doc_to_text(doc: dict) -> str:
            # Extract question using original doc_to_text
            question = process_field(doc, original_doc_to_text, "")

            # Extract choices using original doc_to_choice (if needed for prompt)
            if self._should_show_choices() and original_doc_to_choice is not None:
                choices = process_field(doc, original_doc_to_choice, [])
            else:
                choices = None

            # Format according to template
            return self.format_prompt(question, choices)

        return wrapped_doc_to_text

    def wrap_doc_to_choice(
        self,
        original_doc_to_choice: Union[str, Callable, List, None]
    ) -> Callable:
        """
        Wrap existing doc_to_choice to return template choice labels.

        For MCQ templates, this returns the choice labels (A, B, C, D)
        based on the number of choices extracted by the original doc_to_choice.

        Args:
            original_doc_to_choice: User's doc_to_choice specification

        Returns:
            New callable that returns appropriate choice labels

        Example:
            # User specifies:
            doc_to_choice = "{{choices.text}}"  # Returns ["Paris", "London", "Berlin"]

            # Template wraps it:
            wrapped = template.wrap_doc_to_choice(doc_to_choice)

            # Result returns:
            wrapped(doc) # ["A", "B", "C"] (matching number of choices)
        """
        def wrapped_doc_to_choice(doc: dict) -> List[str]:
            # Extract original choices to determine count
            choices = process_field(doc, original_doc_to_choice, [])

            # Return appropriate number of labels
            if isinstance(choices, list):
                num_choices = len(choices)
            else:
                num_choices = len(self.choice_labels)

            return self.choice_labels[:num_choices]

        return wrapped_doc_to_choice


@dataclass
class MCQTemplateConfig(TemplateConfig):
    """
    Template for Multiple Choice Question (MCQ) tasks.

    MCQ templates format questions with labeled choices (e.g., A/B/C/D).
    They support various formatting styles:
    - MMLU style: "A. choice1\nB. choice2\n..."
    - GPQA style: "(A) choice1 (B) choice2 ..."
    - Numbered: "1. choice1\n2. choice2\n..."

    The template applies labels to choices from the document dynamically.

    Example usage:
        template = MCQTemplateConfig(
            choice_labels=["A", "B", "C", "D"],
            choice_format="{label}. {choice}",
            choices_source="choices",  # or callable
            suffix="Answer:"
        )

        # Generate doc_to_text and doc_to_choice callables
        doc_to_text = template.get_doc_to_text()
        doc_to_choice = template.get_doc_to_choice()

        # Use with a document
        doc = {"question": "What is 2+2?", "choices": ["3", "4", "5", "6"]}
        prompt = doc_to_text(doc)  # Formats with A/B/C/D labels
        labels = doc_to_choice(doc)  # Returns ["A", "B", "C", "D"]
    """

    # Labels for choices (e.g., ["A", "B", "C", "D"] or ["1", "2", "3", "4"])
    choice_labels: List[str] = field(default_factory=lambda: ["A", "B", "C", "D"])

    # Format string for each choice. Use {label} for the choice label and {choice} for the text
    # Examples:
    #   "{label}. {choice}" -> "A. first choice"
    #   "({label}) {choice}" -> "(A) first choice"
    #   "{label}) {choice}" -> "A) first choice"
    choice_format: str = "{label}. {choice}"

    # Whether to show all choices in the prompt (True) or use continuation (False)
    show_choices_in_prompt: bool = True

    def format_prompt(self, question: str, choices: Optional[List[str]] = None, **kwargs) -> str:
        """
        Format an MCQ prompt with question and choices.

        Args:
            question: The question text
            choices: List of choice strings
            **kwargs: Additional parameters (ignored)

        Returns:
            Formatted prompt string
        """
        parts = []

        # Add prefix if present
        if self.prefix:
            parts.append(self.prefix)

        # Add question
        parts.append(question.strip())

        # Add choices if provided and should be shown
        if choices and self.show_choices_in_prompt:
            formatted_choices = []
            for label, choice in zip(self.choice_labels, choices):
                formatted_choice = self.choice_format.format(label=label, choice=choice)
                formatted_choices.append(formatted_choice)

            choices_text = self.choice_delimiter.join(formatted_choices)
            parts.append(choices_text)

        # Add suffix
        if self.suffix:
            parts.append(self.suffix)

        return self.question_choice_delimiter.join(parts)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert MCQ template to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "template_type": "mcq",
            "prefix": self.prefix,
            "suffix": self.suffix,
            "question_choice_delimiter": self.question_choice_delimiter,
            "choice_delimiter": self.choice_delimiter,
            "choice_labels": self.choice_labels,
            "choice_format": self.choice_format,
            "show_choices_in_prompt": self.show_choices_in_prompt,
        }

    def to_cloze(self, blank_marker: str = "______") -> 'ClozeTemplateConfig':
        """
        Convert MCQ template to Cloze template.

        This conversion transforms a multiple choice question into a fill-in-the-blank
        format. The choices are shown as options to fill in the blank.

        Args:
            blank_marker: The marker to use for the blank (default: "______")

        Returns:
            ClozeTemplateConfig instance
        """
        return ClozeTemplateConfig(
            prefix=self.prefix,
            suffix="",  # Cloze typically doesn't need suffix
            blank_marker=blank_marker,
            show_choices=True,  # Show choices as options
            choice_labels=self.choice_labels,
            choice_format=self.choice_format,
            choice_delimiter=self.choice_delimiter,
        )


@dataclass
class ClozeTemplateConfig(TemplateConfig):
    """
    Template for Cloze (fill-in-the-blank) tasks.

    Cloze templates format questions as fill-in-the-blank prompts.
    The blank can be represented in various ways:
    - "______" (underscores)
    - "[MASK]" (token)
    - "___" (shorter underscores)

    Choices can optionally be shown as hints.

    Example usage:
        template = ClozeTemplateConfig(
            blank_marker="______",
            show_choices=True,
            choice_labels=["A", "B", "C", "D"],
            choices_source="choices"
        )

        doc_to_text = template.get_doc_to_text()
        doc_to_choice = template.get_doc_to_choice()
    """

    # The marker used to represent the blank
    blank_marker: str = "______"

    # Whether to show choices as hints
    show_choices: bool = True

    # Labels for choices (if shown)
    choice_labels: Optional[List[str]] = None

    # Format string for each choice (if shown)
    choice_format: str = "{label}. {choice}"

    # Position of blank relative to question: "end" or "inline"
    # "end": "What is the capital? ______"
    # "inline": Blank is embedded in the question text
    blank_position: str = "end"

    # Delimiter before choices (if shown)
    choices_prefix: str = "\nOptions: "

    def format_prompt(self, question: str, choices: Optional[List[str]] = None, **kwargs) -> str:
        """
        Format a cloze prompt with question and optional choices.

        Args:
            question: The question text (may contain blank marker)
            choices: List of choice strings (optional)
            **kwargs: Additional parameters (ignored)

        Returns:
            Formatted prompt string
        """
        parts = []

        # Add prefix if present
        if self.prefix:
            parts.append(self.prefix)

        # Add question with blank
        if self.blank_position == "end" and self.blank_marker not in question:
            question_with_blank = f"{question.strip()} {self.blank_marker}"
        else:
            question_with_blank = question.strip()

        parts.append(question_with_blank)

        # Add choices if provided and should be shown
        if choices and self.show_choices and self.choice_labels:
            formatted_choices = []
            for label, choice in zip(self.choice_labels, choices):
                formatted_choice = self.choice_format.format(label=label, choice=choice)
                formatted_choices.append(formatted_choice)

            choices_text = self.choices_prefix + self.choice_delimiter.join(formatted_choices)
            parts.append(choices_text)

        # Add suffix
        if self.suffix:
            parts.append(self.suffix)

        return self.question_choice_delimiter.join(parts)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Cloze template to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "template_type": "cloze",
            "prefix": self.prefix,
            "suffix": self.suffix,
            "question_choice_delimiter": self.question_choice_delimiter,
            "choice_delimiter": self.choice_delimiter,
            "blank_marker": self.blank_marker,
            "show_choices": self.show_choices,
            "choice_labels": self.choice_labels,
            "choice_format": self.choice_format,
            "blank_position": self.blank_position,
            "choices_prefix": self.choices_prefix,
        }

    def to_mcq(self, suffix: str = "Answer:") -> MCQTemplateConfig:
        """
        Convert Cloze template to MCQ template.

        This conversion transforms a fill-in-the-blank question into a
        multiple choice format with labeled options.

        Args:
            suffix: The suffix to use for MCQ (default: "Answer:")

        Returns:
            MCQTemplateConfig instance
        """
        return MCQTemplateConfig(
            prefix=self.prefix,
            suffix=suffix,
            question_choice_delimiter=self.question_choice_delimiter,
            choice_delimiter=self.choice_delimiter,
            choice_labels=self.choice_labels or ["A", "B", "C", "D"],
            choice_format=self.choice_format,
            show_choices_in_prompt=True,
        )


class TemplateFactory:
    """
    Factory for creating and converting between template types.

    This class provides utilities for:
    - Creating templates from dictionaries/YAML
    - Converting between template types
    - Applying templates to task configurations
    """

    @staticmethod
    def from_dict(config: Dict[str, Any]) -> TemplateConfig:
        """
        Create a template from a dictionary configuration.

        Supports template_type with :: syntax for predefined styles:
        - "mcq::mmlu" → MMLU-style MCQ
        - "mcq::gpqa" → GPQA-style MCQ
        - "mcq::numbered" → Numbered MCQ
        - "cloze" → Cloze with options
        - "mcq" → Default MMLU-style MCQ

        Args:
            config: Dictionary with template configuration

        Returns:
            TemplateConfig instance (MCQTemplateConfig or ClozeTemplateConfig)

        Raises:
            ValueError: If template_type is unknown
        """
        template_type = config.get("template_type", "mcq")

        # Support template_type: mcq::mmlu syntax
        if "::" in template_type:
            type_part, style_part = template_type.split("::", 1)

            if type_part == "mcq":
                if style_part == "mmlu":
                    return TemplateFactory.create_mmlu_style()
                elif style_part == "gpqa":
                    return TemplateFactory.create_gpqa_style()
                elif style_part == "numbered":
                    num_choices = config.get("num_choices", 4)
                    return TemplateFactory.create_numbered_style(num_choices)
                else:
                    raise ValueError(f"Unknown MCQ style: {style_part}")
            elif type_part == "cloze":
                if style_part == "with_options":
                    return TemplateFactory.create_cloze_with_options()
                elif style_part == "pure":
                    return TemplateFactory.create_pure_cloze()
                else:
                    raise ValueError(f"Unknown cloze style: {style_part}")
            else:
                raise ValueError(f"Unknown template type: {type_part}")

        # Remove template_type from config before passing to constructor
        config = {k: v for k, v in config.items() if k != "template_type"}

        if template_type == "mcq":
            return MCQTemplateConfig(**config)
        elif template_type == "cloze":
            return ClozeTemplateConfig(**config)
        else:
            raise ValueError(f"Unknown template type: {template_type}")

    @staticmethod
    def create_mmlu_style() -> MCQTemplateConfig:
        """
        Create an MMLU-style MCQ template.

        Format:
            Question text
            A. choice1
            B. choice2
            C. choice3
            D. choice4
            Answer:

        Returns:
            MCQTemplateConfig for MMLU-style prompts
        """
        return MCQTemplateConfig(
            choice_labels=["A", "B", "C", "D"],
            choice_format="{label}. {choice}",
            suffix="Answer:",
            question_choice_delimiter="\n",
            choice_delimiter="\n",
        )

    @staticmethod
    def create_gpqa_style() -> MCQTemplateConfig:
        """
        Create a GPQA-style MCQ template.

        Format:
            Question text
            (A) choice1 (B) choice2 (C) choice3 (D) choice4
            Answer:

        Returns:
            MCQTemplateConfig for GPQA-style prompts
        """
        return MCQTemplateConfig(
            choice_labels=["A", "B", "C", "D"],
            choice_format="({label}) {choice}",
            suffix="Answer:",
            question_choice_delimiter="\n",
            choice_delimiter=" ",
        )

    @staticmethod
    def create_numbered_style(num_choices: int = 4) -> MCQTemplateConfig:
        """
        Create a numbered MCQ template.

        Format:
            Question text
            1. choice1
            2. choice2
            3. choice3
            4. choice4
            Answer:

        Args:
            num_choices: Number of choices (default: 4)

        Returns:
            MCQTemplateConfig for numbered prompts
        """
        return MCQTemplateConfig(
            choice_labels=[str(i+1) for i in range(num_choices)],
            choice_format="{label}. {choice}",
            suffix="Answer:",
            question_choice_delimiter="\n",
            choice_delimiter="\n",
        )

    @staticmethod
    def create_cloze_with_options() -> ClozeTemplateConfig:
        """
        Create a cloze template with choice options shown.

        Format:
            Question text ______
            Options: A. choice1 B. choice2 C. choice3 D. choice4

        Returns:
            ClozeTemplateConfig with options
        """
        return ClozeTemplateConfig(
            blank_marker="______",
            show_choices=True,
            choice_labels=["A", "B", "C", "D"],
            choice_format="{label}. {choice}",
            blank_position="end",
            choices_prefix="\nOptions: ",
            choice_delimiter=" ",
        )

    @staticmethod
    def create_pure_cloze() -> ClozeTemplateConfig:
        """
        Create a pure cloze template without showing choices.

        Format:
            Question text ______

        Returns:
            ClozeTemplateConfig without choices
        """
        return ClozeTemplateConfig(
            blank_marker="______",
            show_choices=False,
            choice_labels=None,
            blank_position="end",
        )

    @staticmethod
    def convert_template(template: TemplateConfig, target_type: str, **kwargs) -> TemplateConfig:
        """
        Convert a template to a different type.

        Args:
            template: Source template
            target_type: Target template type ("mcq" or "cloze")
            **kwargs: Additional parameters for the conversion

        Returns:
            Converted template

        Raises:
            ValueError: If conversion is not supported
        """
        if target_type == "mcq":
            if isinstance(template, ClozeTemplateConfig):
                return template.to_mcq(**kwargs)
            elif isinstance(template, MCQTemplateConfig):
                return template
            else:
                raise ValueError(f"Cannot convert {type(template)} to MCQ")

        elif target_type == "cloze":
            if isinstance(template, MCQTemplateConfig):
                return template.to_cloze(**kwargs)
            elif isinstance(template, ClozeTemplateConfig):
                return template
            else:
                raise ValueError(f"Cannot convert {type(template)} to Cloze")

        else:
            raise ValueError(f"Unknown target type: {target_type}")


# Convenience functions for common templates
def mmlu_template() -> MCQTemplateConfig:
    """Create MMLU-style template."""
    return TemplateFactory.create_mmlu_style()


def gpqa_template() -> MCQTemplateConfig:
    """Create GPQA-style template."""
    return TemplateFactory.create_gpqa_style()


def numbered_template(num_choices: int = 4) -> MCQTemplateConfig:
    """Create numbered template."""
    return TemplateFactory.create_numbered_style(num_choices)


def cloze_template(show_choices: bool = True) -> ClozeTemplateConfig:
    """Create cloze template."""
    if show_choices:
        return TemplateFactory.create_cloze_with_options()
    else:
        return TemplateFactory.create_pure_cloze()
