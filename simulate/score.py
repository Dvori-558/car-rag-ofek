"""Scores simulate/answers.json with the real checks from the project:
verify_citations (rag/answer.py) and check (eval_answers.py), on the same chunks the pipeline retrieves.

  python simulate/score.py
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("HF_HUB_OFFLINE", "1")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from eval_answers import check  # noqa: E402
from eval_retrieval import build_index  # noqa: E402
from rag.answer import Answer, verify_citations  # noqa: E402
from rag.search import search  # noqa: E402


def main():
    golden = json.loads(Path("golden.json").read_text(encoding="utf-8"))
    answers = {a["id"]: a for a in json.loads(Path("simulate/answers.json").read_text(encoding="utf-8"))}
    index = build_index("headings")
    lines, passed = ["SIMULATION - answers were written by an agent, not by eval_answers.py", ""], 0
    for q in golden:
        if q["id"] not in answers:
            lines.append(f"{q['id']:>2} ✗ missing answer")
            continue
        entry = {k: v for k, v in answers[q["id"]].items() if k != "id"}
        answer = Answer.model_validate(entry)
        chunks = search(index, q["question"], "hybrid", 3, True)
        bad = verify_citations(answer, chunks)
        ok, why = check(q, answer, bad, chunks)
        passed += ok
        lines.append(f"{q['id']:>2} {'✓' if ok else '✗'} [{q['type']}] {q['question']}")
        lines.append(f"   {answer.answer}")
        for c in answer.citations:
            lines.append(f"   {'✗' if c in bad else '✓'} {c.chunk_id}: \"{c.quote}\"")
        if why:
            lines.append(f"   → {why}")
    lines.append(f"\npassed {passed}/{len(golden)} (simulation)")
    Path("simulate/results.txt").write_text("\n".join(lines), encoding="utf-8")
    print(f"passed {passed}/{len(golden)} (simulation) - details in simulate/results.txt")


if __name__ == "__main__":
    main()
