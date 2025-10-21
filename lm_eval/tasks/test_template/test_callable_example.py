"""
Example showing how to use templates with callable doc_to_* fields.

This demonstrates:
1. Using callables for question_source and choices_source
2. Custom processing of document fields
3. Jinja2 templates as sources
4. Generic choice formatting
"""


# Example 1: Custom callable for extracting choices
def get_shuffled_choices(doc):
    """
    Custom function to extract and process choices.

    This could do any custom processing like:
    - Shuffling choices
    - Filtering choices
    - Transforming choice format
    """
    import random
    choices = doc.get("choices", [])
    # Example: could shuffle here if needed
    # shuffled = choices.copy()
    # random.shuffle(shuffled)
    # return shuffled
    return choices


# Example 2: Custom callable for extracting question
def get_formatted_question(doc):
    """
    Custom function to extract and format the question.

    This could do any custom processing like:
    - Adding context
    - Formatting markdown
    - Stripping whitespace
    """
    question = doc.get("question", "")
    # Add custom formatting
    return f"Question: {question.strip()}"


# Example 3: Using template with callables
def example_with_callables():
    """Demonstrate using templates with callable sources."""
    from lm_eval.api.template import MCQTemplateConfig

    template = MCQTemplateConfig(
        choice_labels=["A", "B", "C", "D"],
        choice_format="{label}. {choice}",
        question_source=get_formatted_question,  # Custom callable
        choices_source=get_shuffled_choices,      # Custom callable
        suffix="Answer:"
    )

    # Get callables for task config
    doc_to_text = template.get_doc_to_text()
    doc_to_choice = template.get_doc_to_choice()

    # Test with sample document
    doc = {
        "question": "What is the capital of France?",
        "choices": ["London", "Paris", "Berlin", "Madrid"],
        "answer": 1
    }

    print("Example 1: Using Callables")
    print("-" * 70)
    print("Prompt:")
    print(doc_to_text(doc))
    print("\nChoice labels:")
    print(doc_to_choice(doc))
    print()


# Example 4: Using Jinja2 templates as sources
def example_with_jinja2():
    """Demonstrate using Jinja2 templates as sources."""
    from lm_eval.api.template import MCQTemplateConfig

    template = MCQTemplateConfig(
        choice_labels=["A", "B", "C", "D"],
        choice_format="{label}) {choice}",
        # Jinja2 template for question
        question_source="{{subject}}: {{question.strip()}}",
        choices_source="choices",  # Simple field name
        suffix="Your answer:"
    )

    doc_to_text = template.get_doc_to_text()
    doc_to_choice = template.get_doc_to_choice()

    doc = {
        "subject": "Geography",
        "question": "What is the capital of France?",
        "choices": ["London", "Paris", "Berlin", "Madrid"],
        "answer": 1
    }

    print("Example 2: Using Jinja2 Templates")
    print("-" * 70)
    print("Prompt:")
    print(doc_to_text(doc))
    print("\nChoice labels:")
    print(doc_to_choice(doc))
    print()


# Example 5: Generic choice formatting with arbitrary lists
def example_with_dynamic_choices():
    """Demonstrate generic choice formatting with varying number of choices."""
    from lm_eval.api.template import MCQTemplateConfig

    # Template with many labels (will use only as many as needed)
    template = MCQTemplateConfig(
        choice_labels=["A", "B", "C", "D", "E", "F", "G", "H"],
        choice_format="{label}. {choice}",
        question_source="question",
        choices_source="choices",
    )

    doc_to_text = template.get_doc_to_text()
    doc_to_choice = template.get_doc_to_choice()

    # Test with different numbers of choices
    docs = [
        {
            "question": "Pick the primary color:",
            "choices": ["Red", "Blue", "Yellow"],
            "answer": 0
        },
        {
            "question": "Pick the largest number:",
            "choices": ["10", "20", "30", "40", "50", "60"],
            "answer": 5
        }
    ]

    print("Example 3: Dynamic Choice Formatting")
    print("-" * 70)
    for i, doc in enumerate(docs, 1):
        print(f"Document {i}:")
        print(doc_to_text(doc))
        print(f"Labels: {doc_to_choice(doc)}")
        print()


# Example 6: Converting between MCQ and Cloze with callables
def example_conversion_with_callables():
    """Demonstrate converting templates while preserving callables."""
    from lm_eval.api.template import MCQTemplateConfig

    # Create MCQ template with custom sources
    mcq = MCQTemplateConfig(
        choice_labels=["A", "B", "C", "D"],
        choice_format="{label}. {choice}",
        question_source=get_formatted_question,  # Custom callable preserved
        choices_source="choices",
    )

    # Convert to cloze - callables are preserved!
    cloze = mcq.to_cloze()

    doc = {
        "question": "The capital of France is",
        "choices": ["London", "Paris", "Berlin", "Madrid"],
        "answer": 1
    }

    print("Example 4: Conversion Preserves Callables")
    print("-" * 70)
    print("MCQ Format:")
    print(mcq.get_doc_to_text()(doc))
    print("\nCloze Format:")
    print(cloze.get_doc_to_text()(doc))
    print()


def main():
    """Run all examples."""
    print("=" * 70)
    print("Template System Examples with Callables")
    print("=" * 70)
    print()

    example_with_callables()
    example_with_jinja2()
    example_with_dynamic_choices()
    example_conversion_with_callables()

    print("=" * 70)
    print("All examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
