"""Writes simulate/prompts.md: the exact system prompt and the exact user message that
eval_answers.py would send to Claude for each golden question (headings + hybrid + current-only, k=3).
The expected answers from golden.json are NOT written, so whoever answers cannot see them.

  python simulate/make_prompts.py
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("HF_HUB_OFFLINE", "1")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from eval_retrieval import build_index  # noqa: E402
from rag.answer import SYSTEM, build_context  # noqa: E402
from rag.search import search  # noqa: E402


def main():
    golden = json.loads(Path("golden.json").read_text(encoding="utf-8"))
    index = build_index("headings")
    out = ["# Prompts for the simulation", "", "## System prompt (the same for every question)", "",
           "```", SYSTEM, "```", ""]
    for q in golden:
        chunks = search(index, q["question"], "hybrid", 3, True)
        user = f"{build_context(chunks)}\n\nשאלה: {q['question']}"
        out += [f"## Question {q['id']}", "", "```", user, "```", ""]
    Path("simulate/prompts.md").write_text("\n".join(out), encoding="utf-8")
    print(f"wrote simulate/prompts.md ({len(golden)} questions)")


if __name__ == "__main__":
    main()
