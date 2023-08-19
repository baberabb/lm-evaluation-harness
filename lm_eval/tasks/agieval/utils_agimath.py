from lm_eval.logger import eval_logger


# Based on Hendrycks math dataset.
# taken from https://github.com/microsoft/AGIEval/blob/main/src/dataset_loader.py
def doc_to_text_math_fewshot(doc: dict) -> str:
    """
    'Here are the answers for the problems in the exam.\n
    <Problem 1.>    <Question>\n
    The answer is therefore <answer>\n
    ...
    <Problem n.>   <Question>

    original adds \n at the end. I removed it.
    """

    _fewshot = [
        "Here are the answers for the problems in the exam.\n",
        "Problem 1.    Find the domain of the expression $\\frac{\\sqrt{x-2}}{\\sqrt{5-x}}$.\nThe answer is therefore [2,5)\n",
        "Problem 2.    If $\\det \\mathbf{A} = 5,$ then find $\\det (\\mathbf{A^3}).$\nThe answer is therefore 125\n",
        "Problem 3.    Terrell usually lifts two 20-pound weights 12 times. If he uses two 15-pound weights instead, how many times must Terrell lift them in order to lift the same total weight?\nThe answer is therefore 16\n",
        "Problem 4.    If the system of equations  \\begin{align*}\n3x+y&=a,\\\\\n2x+5y&=2a,\n\\end{align*} has a solution $(x,y)$ when $x=2$, compute $a$.\nThe answer is therefore \\frac{26}{3}\n",
    ]
    _fewshot = "".join(_fewshot)
    question_input = "Problem {}.   ".format(5) + doc["question"]
    return _fewshot + question_input


# taken from https://github.com/microsoft/AGIEval/blob/main/src/post_process.py


def remove_few_shot_prefix(string: str):
    prefix = "The answer is therefore"
    if string.startswith(prefix):
        string = string[len(prefix) :].strip()
    elif prefix in string:
        index = string.rfind(prefix)
        if index >= 0:
            string = string[index + len(prefix) :].strip()
    return string


def parse_math_answer(raw_string: str) -> str:
    raw_string = remove_few_shot_prefix(raw_string)
    return raw_string


def process_results_math(doc, results):
    completions = results[0]
    processed_answer = parse_math_answer(completions)
    eval_logger.info(f"Result: {completions}")
    eval_logger.info(f"Parsed: {processed_answer}")
    if doc["answer"] == processed_answer:
        return {"acc": 1}
    else:
        return {"acc": 0}


# def parse_math_answer(raw_string):
#     if setting_name == "few-shot-CoT":
#         raw_string = extract_last_line(raw_string)
#     if setting_name == "few-shot-CoT" or setting_name == "few-shot":
#         raw_string = remove_few_shot_prefix(raw_string)
#         return raw_string
