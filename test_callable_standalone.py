#!/usr/bin/env python3
"""
Standalone test of template system with callables.
This doesn't require package installation.
"""

import sys
sys.path.insert(0, '/home/user/lm-evaluation-harness')

from lm_eval.api.template import MCQTemplateConfig, ClozeTemplateConfig


def get_custom_question(doc):
    """Custom function to format question."""
    question = doc.get("question", "")
    return f"Q: {question.strip()}"


def test_callable_sources():
    """Test template with callable sources."""
    print("Test 1: Callable sources")
    print("-" * 70)

    template = MCQTemplateConfig(
        choice_labels=["A", "B", "C", "D"],
        choice_format="{label}. {choice}",
        question_source=get_custom_question,  # Callable
        choices_source="choices",  # Field name
    )

    doc_to_text = template.get_doc_to_text()
    doc_to_choice = template.get_doc_to_choice()

    doc = {
        "question": "What is 2+2?",
        "choices": ["3", "4", "5", "6"],
        "answer": 1
    }

    prompt = doc_to_text(doc)
    labels = doc_to_choice(doc)

    print("Prompt:")
    print(prompt)
    print(f"\nLabels: {labels}")
    print()

    assert "Q: What is 2+2?" in prompt, "Custom question formatter should be used"
    assert labels == ["A", "B", "C", "D"], "Should return correct labels"
    print("✓ PASSED\n")


def test_jinja2_sources():
    """Test template with Jinja2 sources."""
    print("Test 2: Jinja2 template sources")
    print("-" * 70)

    template = MCQTemplateConfig(
        choice_labels=["A", "B", "C", "D"],
        choice_format="({label}) {choice}",
        question_source="{{subject}}: {{question}}",  # Jinja2
        choices_source="choices",
    )

    doc_to_text = template.get_doc_to_text()

    doc = {
        "subject": "Math",
        "question": "What is 2+2?",
        "choices": ["3", "4", "5", "6"],
    }

    prompt = doc_to_text(doc)

    print("Prompt:")
    print(prompt)
    print()

    assert "Math: What is 2+2?" in prompt, "Jinja2 template should be rendered"
    assert "(A) 3" in prompt, "Choices should be formatted correctly"
    print("✓ PASSED\n")


def test_dynamic_choices():
    """Test generic choice formatting with different numbers of choices."""
    print("Test 3: Dynamic choice formatting")
    print("-" * 70)

    template = MCQTemplateConfig(
        choice_labels=["A", "B", "C", "D", "E", "F"],  # More labels than needed
        choice_format="{label}. {choice}",
        question_source="question",
        choices_source="choices",
    )

    doc_to_text = template.get_doc_to_text()
    doc_to_choice = template.get_doc_to_choice()

    # Test with 3 choices
    doc1 = {
        "question": "Pick a color:",
        "choices": ["Red", "Blue", "Green"]
    }

    prompt1 = doc_to_text(doc1)
    labels1 = doc_to_choice(doc1)

    print("Document with 3 choices:")
    print(prompt1)
    print(f"Labels: {labels1}")
    print()

    assert labels1 == ["A", "B", "C"], "Should use only 3 labels"

    # Test with 5 choices
    doc2 = {
        "question": "Pick a number:",
        "choices": ["1", "2", "3", "4", "5"]
    }

    labels2 = doc_to_choice(doc2)
    print(f"Document with 5 choices - Labels: {labels2}")
    print()

    assert labels2 == ["A", "B", "C", "D", "E"], "Should use 5 labels"
    print("✓ PASSED\n")


def test_mcq_to_cloze_conversion():
    """Test converting MCQ to Cloze while preserving callables."""
    print("Test 4: MCQ to Cloze conversion with callables")
    print("-" * 70)

    mcq = MCQTemplateConfig(
        choice_labels=["A", "B", "C", "D"],
        choice_format="{label}. {choice}",
        question_source=get_custom_question,  # Callable
        choices_source="choices",
    )

    # Convert to cloze
    cloze = mcq.to_cloze()

    doc = {
        "question": "The capital of France is",
        "choices": ["London", "Paris", "Berlin", "Madrid"],
    }

    mcq_prompt = mcq.get_doc_to_text()(doc)
    cloze_prompt = cloze.get_doc_to_text()(doc)

    print("MCQ Format:")
    print(mcq_prompt)
    print("\nCloze Format:")
    print(cloze_prompt)
    print()

    assert "Q: The capital of France is" in mcq_prompt, "MCQ should use custom formatter"
    assert "Q: The capital of France is" in cloze_prompt, "Cloze should preserve custom formatter"
    assert "______" in cloze_prompt, "Cloze should have blank marker"
    assert "Options:" in cloze_prompt, "Cloze should show options"

    print("✓ PASSED\n")


def test_field_name_source():
    """Test simple field name as source."""
    print("Test 5: Simple field name sources")
    print("-" * 70)

    template = MCQTemplateConfig(
        choice_labels=["1", "2", "3", "4"],
        choice_format="{label}) {choice}",
        question_source="query",  # Different field name
        choices_source="options",  # Different field name
    )

    doc_to_text = template.get_doc_to_text()

    doc = {
        "query": "What is the answer?",
        "options": ["Yes", "No", "Maybe", "Unknown"],
    }

    prompt = doc_to_text(doc)

    print("Prompt:")
    print(prompt)
    print()

    assert "What is the answer?" in prompt, "Should extract from 'query' field"
    assert "1) Yes" in prompt, "Should format choices correctly"
    assert "2) No" in prompt
    print("✓ PASSED\n")


def main():
    """Run all tests."""
    print("=" * 70)
    print("Template System - Callable and Generic Choice Tests")
    print("=" * 70)
    print()

    tests = [
        test_callable_sources,
        test_jinja2_sources,
        test_dynamic_choices,
        test_mcq_to_cloze_conversion,
        test_field_name_source,
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
