"""Label reviews with an LLM using the codebook (prompts/codebook.md).

The shipped labels (data/labelled_reviews.csv, column `codes`) were produced by an LLM (Claude)
reading the reviews in batches of ~100 against the same codebook and prompt. This script lets
anyone re-run the labelling with Gemini, e.g. to scale to all 26k reviews or to check the
labels with a second model.

    pip install google-genai pandas
    export GEMINI_API_KEY=...
    python src/classify_llm.py data/sample_to_label.csv data/labels_gemini.csv
"""
import os
import re
import sys
import time

import pandas as pd
from google import genai

CODEBOOK = open(os.path.join(os.path.dirname(__file__), "..", "prompts", "codebook.md")).read()
VALID_NEG, VALID_POS = set("QWLXPRABSUMO"), set("qfpscagktou")

PROMPT = """You label Indian quick-commerce app reviews. Use ONLY the codebook below.
Return one line per review in the form  <id>:<codes>  and nothing else.
- Use upper-case codes for 1-2 star reviews, lower-case codes for 4-5 star reviews.
- List every code that applies. Put the code for the MAIN reason for the rating first.
- Hinglish and Hindi reviews are in scope; label them like English ones.
- If nothing fits or the text is unintelligible, use O (or o).

{codebook}

Reviews:
{reviews}"""


def label_batch(client, batch: pd.DataFrame, model="gemini-2.5-flash") -> dict:
    lines = "\n".join(f"{r.sid}|{r.score}|{str(r.text)[:450]}" for r in batch.itertuples())
    resp = client.models.generate_content(model=model, contents=PROMPT.format(codebook=CODEBOOK, reviews=lines))
    out = {}
    for line in resp.text.splitlines():
        m = re.match(r"\s*(\d+)\s*:\s*([A-Za-z]+)", line)
        if m:
            sid, codes = int(m.group(1)), m.group(2)
            valid = VALID_NEG if codes[0].isupper() else VALID_POS
            codes = "".join(c for c in codes if c in valid)
            if codes:
                out[sid] = codes
    return out


def main(inp, outp, batch_size=100):
    df = pd.read_csv(inp)
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    labels = {}
    for i in range(0, len(df), batch_size):
        labels.update(label_batch(client, df.iloc[i:i + batch_size]))
        print(f"{min(i + batch_size, len(df))}/{len(df)} labelled")
        time.sleep(1)
    df["codes"] = df.sid.map(labels)
    df["primary_code"] = df.codes.str[0]
    df.to_csv(outp, index=False)
    print("missing labels:", df.codes.isna().sum())


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
