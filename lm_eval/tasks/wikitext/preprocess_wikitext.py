import datasets
import transformers


tokenizer = transformers.AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")


def split_list(lst, n):
    return [lst[i : i + n] for i in range(0, len(lst), n)]


def process_docs(ds):
    tokens = split_list(
        tokenizer("\n\n".join(ds["text"]), add_special_tokens=False).input_ids, 2047
    )
    text = tokenizer.batch_decode(tokens)
    return datasets.Dataset.from_dict({"text": text})


# def wikitext_detokenizer(doc):
#     string = doc["page"]
#     # contractions
#     string = string.replace("s '", "s'")
#     string = re.sub(r"/' [0-9]/", r"/'[0-9]/", string)
#     # number separators
#     string = string.replace(" @-@ ", "-")
#     string = string.replace(" @,@ ", ",")
#     string = string.replace(" @.@ ", ".")
#     # punctuation
#     string = string.replace(" : ", ": ")
#     string = string.replace(" ; ", "; ")
#     string = string.replace(" . ", ". ")
#     string = string.replace(" ! ", "! ")
#     string = string.replace(" ? ", "? ")
#     string = string.replace(" , ", ", ")
#     # double brackets
#     string = re.sub(r"\(\s*([^\)]*?)\s*\)", r"(\1)", string)
#     string = re.sub(r"\[\s*([^\]]*?)\s*\]", r"[\1]", string)
#     string = re.sub(r"{\s*([^}]*?)\s*}", r"{\1}", string)
#     string = re.sub(r"\"\s*([^\"]*?)\s*\"", r'"\1"', string)
#     string = re.sub(r"'\s*([^']*?)\s*'", r"'\1'", string)
#     # miscellaneous
#     string = string.replace("= = = =", "====")
#     string = string.replace("= = =", "===")
#     string = string.replace("= =", "==")
#     string = string.replace(" " + chr(176) + " ", chr(176))
#     string = string.replace(" \n", "\n")
#     string = string.replace("\n ", "\n")
#     string = string.replace(" N ", " 1 ")
#     string = string.replace(" 's", "'s")
#
#     return string


def process_results(doc, results):
    (loglikelihood,) = results
    # IMPORTANT: wikitext counts number of words in *original doc before detokenization*
    _words = len(tokenizer(doc["text"]).input_ids)
    _bytes = len(doc["text"].encode("utf-8"))
    return {
        "word_perplexity": (loglikelihood, _words),
        "byte_perplexity": (loglikelihood, _bytes),
        "bits_per_byte": (loglikelihood, _bytes),
    }
