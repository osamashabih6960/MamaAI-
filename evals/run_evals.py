import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from router import handle

TEST_CASES_PATH = Path("evals/test_cases.json")
RESULTS_PATH = Path("evals/eval_results.json")
FAILURES_PATH = Path("evals/failures.md")


def run_single(case: dict) -> dict:
    result = handle(case["input"])

    checks = {}

    # Check 1: success flag
    if "expect_success" in case:
        checks["success"] = result.get("success") == case["expect_success"]

    # Check 2: expected fields present
    if "expect_fields" in case:
        for field in case["expect_fields"]:
            val = result.get(field)
            checks[f"field_{field}"] = val is not None and val != [] and val != ""

    # Check 3: defer_to_doctor flag
    if "expect_defer_to_doctor" in case:
        checks["defer_to_doctor"] = result.get("defer_to_doctor") == case["expect_defer_to_doctor"]

    # Check 4: escalation flag
    if "expect_escalation_flag" in case:
        checks["escalation_flag"] = result.get("escalation_flag") == case["expect_escalation_flag"]

    # Check 5: confidence ceiling
    if "expect_confidence_below" in case:
        conf = result.get("confidence", 1.0)
        checks["confidence_ceiling"] = conf < case["expect_confidence_below"]

    # Check 6: decision value
    if "expect_decision" in case:
        checks["decision"] = result.get("decision") == case["expect_decision"]

    passed = all(checks.values())
    return {
        "id": case["id"],
        "type": case["type"],
        "input": case["input"],
        "notes": case.get("notes", ""),
        "passed": passed,
        "checks": checks,
        "result": result,
    }


def write_failures_md(results: list[dict]):
    failures = [r for r in results if not r["passed"]]
    with open(FAILURES_PATH, "w") as f:
        f.write("# MamaAI Eval Failures\n\n")
        f.write(f"Total failures: {len(failures)} / {len(results)}\n\n")
        if not failures:
            f.write("All tests passed!\n")
            return
        for r in failures:
            f.write(f"## {r['id']} ({r['type']})\n")
            f.write(f"**Input:** {r['input']}\n\n")
            f.write(f"**Notes:** {r['notes']}\n\n")
            f.write("**Failed checks:**\n")
            for check, ok in r["checks"].items():
                if not ok:
                    f.write(f"- `{check}` FAILED\n")
            f.write(f"\n**Actual result:** `{json.dumps(r['result'], ensure_ascii=False, indent=2)}`\n\n---\n\n")


def main():
    with open(TEST_CASES_PATH) as f:
        cases = json.load(f)

    results = []
    passed = 0

    for case in cases:
        print(f"Running {case['id']} ({case['type']})... ", end="")
        r = run_single(case)
        status = "PASS" if r["passed"] else "FAIL"
        print(status)
        if r["passed"]:
            passed += 1
        results.append(r)

    print(f"\nResult: {passed}/{len(cases)} passed")

    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Results saved to {RESULTS_PATH}")

    write_failures_md(results)
    print(f"Failure log saved to {FAILURES_PATH}")


if __name__ == "__main__":
    main()
    
    