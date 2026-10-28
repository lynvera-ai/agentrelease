import copy
import json

import pytest

from agentrelease import Status, evaluate
from agentrelease.models import SCOPE


def test_all_required_criteria_pass(policy, evidence):
    report = evaluate(policy, evidence)
    assert report.status is Status.PASS
    assert len(report.checks) == 3
    assert all(check.status is Status.PASS for check in report.checks)
    assert report.policy_id == "synthetic-release"
    assert report.errors == ()


def test_failed_required_test(policy, evidence):
    evidence["tests"][1]["status"] = "failed"
    report = evaluate(policy, evidence)
    assert report.status is Status.FAIL
    assert report.checks[0].reason == "Required test failed."


def test_missing_required_test(policy, evidence):
    evidence["tests"].pop()
    report = evaluate(policy, evidence)
    assert report.status is Status.INCONCLUSIVE
    assert report.checks[0].reason == "Required test is missing."


def test_skipped_required_test(policy, evidence):
    evidence["tests"][0] = {"id": "quality", "status": "skipped"}
    report = evaluate(policy, evidence)
    assert report.status is Status.INCONCLUSIVE
    assert [c.status for c in report.checks] == [
        Status.PASS,
        Status.INCONCLUSIVE,
        Status.INCONCLUSIVE,
    ]
    assert report.checks[1].reason == "Required test was skipped."


def test_threshold_violation(policy, evidence):
    evidence["tests"][0]["metrics"]["accuracy"] = 0.89
    report = evaluate(policy, evidence)
    assert report.status is Status.FAIL
    assert report.checks[2].observed == 0.89
    assert report.checks[2].threshold == 0.9


def test_missing_measurement(policy, evidence):
    evidence["tests"][0].pop("metrics")
    report = evaluate(policy, evidence)
    assert report.status is Status.INCONCLUSIVE
    assert report.checks[2].reason == "Required measurement is missing."


def test_empty_evidence_is_inconclusive(policy):
    report = evaluate(policy, {"schema_version": 1, "tests": []})
    assert report.status is Status.INCONCLUSIVE
    assert all(c.status is Status.INCONCLUSIVE for c in report.checks)


def test_failure_has_priority_over_incomplete_evidence(policy, evidence):
    evidence["tests"].pop()
    evidence["tests"][0]["status"] = "failed"
    evidence["tests"][0].pop("metrics")
    report = evaluate(policy, evidence)
    assert report.status is Status.FAIL
    assert {c.status for c in report.checks} == {Status.FAIL, Status.INCONCLUSIVE}


def test_invalid_input_has_priority_over_failure(policy, evidence):
    evidence["tests"][0]["status"] = "failed"
    evidence["tests"].append({"id": "unknown", "status": "passed"})
    report = evaluate(policy, evidence)
    assert report.status is Status.ERROR
    assert report.checks == ()
    assert report.errors[0].code == "UNKNOWN_REFERENCE"


@pytest.mark.parametrize(
    ("operator", "threshold", "observed", "status"),
    [
        (">=", 1, 1, Status.PASS),
        (">=", 1, 0, Status.FAIL),
        (">", 1, 2, Status.PASS),
        (">", 1, 1, Status.FAIL),
        ("<=", -1, -1, Status.PASS),
        ("<=", -1, 0, Status.FAIL),
        ("<", 1, 0, Status.PASS),
        ("<", 1, 1, Status.FAIL),
        ("==", 0, 0, Status.PASS),
        ("==", 0, 1, Status.FAIL),
        ("!=", 0, 1, Status.PASS),
        ("!=", 0, 0, Status.FAIL),
    ],
)
def test_numeric_comparisons(policy, evidence, operator, threshold, observed, status):
    rule = policy["tests"][0]["metrics"][0]
    rule.update(operator=operator, threshold=threshold)
    evidence["tests"][0]["metrics"]["accuracy"] = observed
    assert evaluate(policy, evidence).status is status


def test_failed_test_metrics_still_evaluated(policy, evidence):
    evidence["tests"][0]["status"] = "failed"
    report = evaluate(policy, evidence)
    assert report.status is Status.FAIL
    assert report.checks[-1].status is Status.PASS


def test_deterministic_and_does_not_mutate_inputs(policy, evidence):
    before = copy.deepcopy((policy, evidence))
    report = evaluate(policy, evidence)
    assert report == evaluate(policy, evidence)
    assert report.to_json() == evaluate(policy, evidence).to_json()
    assert (policy, evidence) == before
    assert [c.test_id for c in report.checks] == ["boundary", "quality", "quality"]
    assert len(report.policy_sha256) == len(report.evidence_sha256) == 64
    assert json.loads(report.to_json()) == report.to_dict()
    assert SCOPE in report.to_text()


def test_mapping_key_order_does_not_affect_fingerprints(policy, evidence):
    reordered = {key: policy[key] for key in reversed(policy)}
    assert evaluate(policy, evidence).to_json() == evaluate(reordered, evidence).to_json()


def test_fingerprint_changes_with_evidence(policy, evidence):
    first = evaluate(policy, evidence)
    evidence["tests"][0]["metrics"]["accuracy"] = 0.96
    second = evaluate(policy, evidence)
    assert first.status is second.status is Status.PASS
    assert first.evidence_sha256 != second.evidence_sha256


def test_report_is_immutable_and_serialization_is_detached(policy, evidence):
    from dataclasses import FrozenInstanceError

    report = evaluate(policy, evidence)
    with pytest.raises(FrozenInstanceError):
        report.status = Status.FAIL
    data = report.to_dict()
    data["checks"][0]["reason"] = "changed"
    assert report.checks[0].reason == "Required test passed."


def test_unexpected_evaluation_error_never_passes(policy, evidence, monkeypatch):
    from agentrelease import engine

    def broken_comparison(observed, threshold):
        raise RuntimeError("synthetic evaluation failure")

    monkeypatch.setitem(engine.COMPARISONS, ">=", broken_comparison)
    report = evaluate(policy, evidence)
    assert report.status is Status.ERROR
    assert report.errors[0].code == "EVALUATION_ERROR"
    assert report.checks == ()
