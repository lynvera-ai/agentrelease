"""Deterministic evaluation of explicit criteria."""

import hashlib
import json
import operator
from pathlib import Path

from .loading import load_document
from .models import Check, Report, Status, error_report
from .validation import InputError, TestEvidence, TestRule, validate_evidence, validate_policy

COMPARISONS = {
    ">=": operator.ge,
    ">": operator.gt,
    "<=": operator.le,
    "<": operator.lt,
    "==": operator.eq,
    "!=": operator.ne,
}


def _fingerprint(value: object) -> str:
    content = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _checks(rule: TestRule, evidence: TestEvidence | None) -> list[Check]:
    if evidence is None:
        state, reason, observed = Status.INCONCLUSIVE, "Required test is missing.", None
    elif evidence.status == "skipped":
        state, reason, observed = Status.INCONCLUSIVE, "Required test was skipped.", "skipped"
    elif evidence.status == "failed":
        state, reason, observed = Status.FAIL, "Required test failed.", "failed"
    else:
        state, reason, observed = Status.PASS, "Required test passed.", "passed"
    checks = [Check(rule.id, "test", state, reason, observed=observed)]
    for metric in rule.metrics:
        measured = evidence.metrics.get(metric.name) if evidence is not None else None
        if evidence is None or evidence.status == "skipped":
            result, message = Status.INCONCLUSIVE, "Required test was not executed."
        elif measured is None:
            result, message = Status.INCONCLUSIVE, "Required measurement is missing."
        elif COMPARISONS[metric.operator](measured, metric.threshold):
            result, message = Status.PASS, "Measurement meets the threshold."
        else:
            result, message = Status.FAIL, "Measurement violates the threshold."
        checks.append(
            Check(
                rule.id,
                "metric",
                result,
                message,
                metric.name,
                measured,
                metric.operator,
                metric.threshold,
            )
        )
    return checks


def evaluate(policy: object, evidence: object) -> Report:
    """Evaluate dictionaries; invalid inputs return ERROR without partial checks."""
    try:
        policy_id, rules = validate_policy(policy)
        observations = validate_evidence(evidence, rules)
        checks = tuple(
            check for rule in rules for check in _checks(rule, observations.get(rule.id))
        )
        states = {check.status for check in checks}
        status = next(s for s in (Status.FAIL, Status.INCONCLUSIVE, Status.PASS) if s in states)
        return Report(
            status,
            policy_id,
            checks,
            policy_sha256=_fingerprint(policy),
            evidence_sha256=_fingerprint(evidence),
        )
    except InputError as exc:
        return error_report(exc.code, str(exc))
    except (ValueError, TypeError, OverflowError, RecursionError):
        return error_report("INVALID_INPUT", "Inputs cannot be represented as valid JSON data.")
    except Exception:
        return error_report("EVALUATION_ERROR", "Evaluation could not be completed.")


def evaluate_files(policy_path: str | Path, evidence_path: str | Path) -> Report:
    """Evaluate safe YAML policy and strict JSON evidence files."""
    try:
        policy = load_document(policy_path, "policy")
        evidence = load_document(evidence_path, "evidence")
    except InputError as exc:
        return error_report(exc.code, str(exc))
    except (ValueError, TypeError):
        return error_report("INVALID_INPUT", "Input paths must identify readable files.")
    return evaluate(policy, evidence)
