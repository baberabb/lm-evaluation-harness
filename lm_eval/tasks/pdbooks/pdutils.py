def doc_to_text(doc) -> str:
    """
    Passage: <passage>
    Question: <question>
    Choices:
    A. <choice1>
    B. <choice2>
    C. <choice3>
    D. <choice4>
    Answer:
    """
    SYSTEM_PROMPT = "<|im_start|>system\nYou are a helpful and meticulous librarian with experience of reading and recommending books<|im_end|>\n"
    # PROMPT = """<|im_start|>user\nThe following is a book entry along with probable matching entries in a library system. One per line. Your job is to classify if there is a match of the entry with the choices. Consider both the title and and the author when matching. If none given then only match if there is a high possibility. Err on the wrong matching side.\n\nEntry:\nWords and phrases, 1658 to date. by West publishing co.\n\nChoices:\nA. [WORDS AND PHRASES, PERMANENT EDITION by West Pub. Co. (PWH)]\nB. [WORDS AND PHRASES, PERMANENT EDITION. Vol. 11. by]\n\nAnswer:<|im_end|>\n<|im_start|>assistant\nA B<|im_end|>\n<|im_start|>user\nEntry:\n"""
    PROMPT = "<|im_start|>user\nThe following is a book entry along with probable matching entries in a library system. One per line. Your job is to classify if there is a match of the entry with the choices. Consider both the title and and the author when matching. If none given then only match if there is a high possibility. Err on the wrong matching side.\n\nEntry:\nWords and phrases, 1658 to date. by West publishing co.\n\nChoices:\nA. [WORDS AND PHRASES, PERMANENT EDITION by West Pub. Co. (PWH)]\nB. [WORDS AND PHRASES, PERMANENT EDITION. Vol. 11. by]<|im_end|>\n<|im_start|>assistant\nA B<|im_end|>\n<|im_start|>user\n"
    choices = ["a", "b", "c", "d"]
    prompt = SYSTEM_PROMPT + PROMPT
    prompt += doc["prompt_reg"]
    prompt += "\n\n"
    prompt += "Choices:\n"
    for choice, option in zip(choices, doc["prompt_ren"]):
        prompt += f"{choice.upper()}. {option}\n"
    prompt += "Answer:<|im_end|>\n<|im_start|>assistant\n"
    return prompt


def doc_to_choice(doc):
    choices = ["A", "B", "C", "D"]
    return choices[: len(doc["prompt_ren"])]
