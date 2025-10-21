#!/usr/bin/env python3
"""
Standalone test of the wrapper-based template API.
Tests the pattern from arc_easy.yaml without requiring full package.
"""

import sys
sys.path.insert(0, '/home/user/lm-evaluation-harness')

from lm_eval.api.template import TemplateFactory, process_field


def test_wrapper_api_basic():
    """Test basic wrapper API."""
    print("Test 1: Basic Wrapper API")
    print("-" * 70)

    # Create template
    template = TemplateFactory.from_dict({"template_type": "mcq::mmlu"})

    # User's doc_to_text and doc_to_choice
    doc_to_text_spec = "{{question}}"
    doc_to_choice_spec = "{{choices.text}}"

    # Wrap them
    wrapped_doc_to_text = template.wrap_doc_to_text(doc_to_text_spec, doc_to_choice_spec)
    wrapped_doc_to_choice = template.wrap_doc_to_choice(doc_to_choice_spec)

    # Test document
    doc = {
        "question": "What is the capital of France?",
        "choices": {
            "text": ["London", "Paris", "Berlin", "Madrid"],
            "label": ["A", "B", "C", "D"]
        }
    }

    # Generate prompt and labels
    prompt = wrapped_doc_to_text(doc)
    labels = wrapped_doc_to_choice(doc)

    print("Generated Prompt:")
    print(prompt)
    print()
    print(f"Labels: {labels}")
    print()

    assert "What is the capital of France?" in prompt
    assert "A. London" in prompt
    assert "B. Paris" in prompt
    assert "C. Berlin" in prompt
    assert "D. Madrid" in prompt
    assert "Answer:" in prompt
    assert labels == ["A", "B", "C", "D"]

    print("✓ PASSED\n")


def test_mcq_mmlu_syntax():
    """Test mcq::mmlu syntax."""
    print("Test 2: mcq::mmlu Syntax")
    print("-" * 70)

    template = TemplateFactory.from_dict({"template_type": "mcq::mmlu"})

    print(f"Template type: {type(template).__name__}")
    print(f"Choice labels: {template.choice_labels}")
    print(f"Choice format: {template.choice_format}")
    print(f"Suffix: {template.suffix}")
    print()

    assert template.choice_labels == ["A", "B", "C", "D"]
    assert template.choice_format == "{label}. {choice}"
    assert template.suffix == "Answer:"

    print("✓ PASSED\n")


def test_mcq_gpqa_syntax():
    """Test mcq::gpqa syntax."""
    print("Test 3: mcq::gpqa Syntax")
    print("-" * 70)

    template = TemplateFactory.from_dict({"template_type": "mcq::gpqa"})

    doc_to_text_spec = "question"  # Simple field name
    doc_to_choice_spec = "choices"

    wrapped_doc_to_text = template.wrap_doc_to_text(doc_to_text_spec, doc_to_choice_spec)

    doc = {
        "question": "Which is correct?",
        "choices": ["A", "B", "C", "D"]
    }

    prompt = wrapped_doc_to_text(doc)

    print("GPQA-style Prompt:")
    print(prompt)
    print()

    assert "(A) A" in prompt
    assert "(B) B" in prompt
    assert template.choice_format == "({label}) {choice}"
    assert template.choice_delimiter == " "  # Inline choices

    print("✓ PASSED\n")


def test_variable_choice_count():
    """Test with variable number of choices."""
    print("Test 4: Variable Choice Count")
    print("-" * 70)

    template = TemplateFactory.from_dict({"template_type": "mcq::mmlu"})

    wrapped_doc_to_choice = template.wrap_doc_to_choice("choices")

    # 3 choices
    doc1 = {"choices": ["Red", "Blue", "Green"]}
    labels1 = wrapped_doc_to_choice(doc1)
    print(f"3 choices → labels: {labels1}")

    # 5 choices - Note: MMLU only has 4 labels by default
    doc2 = {"choices": ["1", "2", "3", "4", "5"]}
    labels2 = wrapped_doc_to_choice(doc2)
    print(f"5 choices → labels: {labels2}")
    print()

    assert labels1 == ["A", "B", "C"]
    assert labels2 == ["A", "B", "C", "D"]  # Only 4 labels available

    print("✓ PASSED\n")


def test_cloze_template():
    """Test cloze template."""
    print("Test 5: Cloze Template")
    print("-" * 70)

    template = TemplateFactory.create_cloze_with_options()

    wrapped_doc_to_text = template.wrap_doc_to_text("question", "choices")

    doc = {
        "question": "The capital of France is",
        "choices": ["London", "Paris", "Berlin"]
    }

    prompt = wrapped_doc_to_text(doc)

    print("Cloze Prompt:")
    print(prompt)
    print()

    assert "______" in prompt
    assert "Options:" in prompt
    assert "A. London" in prompt

    print("✓ PASSED\n")


def test_jinja2_doc_to_text():
    """Test Jinja2 template in doc_to_text."""
    print("Test 6: Jinja2 in doc_to_text")
    print("-" * 70)

    template = TemplateFactory.from_dict({"template_type": "mcq::mmlu"})

    # Jinja2 template combining multiple fields
    doc_to_text_spec = "{{subject}}: {{question}}"
    doc_to_choice_spec = "options"

    wrapped = template.wrap_doc_to_text(doc_to_text_spec, doc_to_choice_spec)

    doc = {
        "subject": "Geography",
        "question": "What is the capital?",
        "options": ["London", "Paris"]
    }

    prompt = wrapped(doc)

    print("Prompt with Jinja2:")
    print(prompt)
    print()

    assert "Geography: What is the capital?" in prompt
    assert "A. London" in prompt

    print("✓ PASSED\n")


def main():
    """Run all tests."""
    print("=" * 70)
    print("Template Wrapper API - Standalone Tests")
    print("=" * 70)
    print()

    tests = [
        test_wrapper_api_basic,
        test_mcq_mmlu_syntax,
        test_mcq_gpqa_syntax,
        test_variable_choice_count,
        test_cloze_template,
        test_jinja2_doc_to_text,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ FAILED: {e}\n")
            import traceback
            traceback.print_exc()
            failed += 1

    print("=" * 70)
    print(f"Results: {passed}/{len(tests)} tests passed")
    if failed == 0:
        print("All tests passed! ✓")
    else:
        print(f"{failed} test(s) failed ✗")
    print("=" * 70)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
