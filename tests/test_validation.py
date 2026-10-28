import pytest

from agentrelease import Status, evaluate


@pytest.mark.parametrize(
    "bad", [None, [], "policy", {}, {"schema_version": 1, "id": "x", "tests": []}]
)
def test_invalid_policy_root(bad, evidence):
    assert evaluate(bad, evidence).status is Status.ERROR


@pytest.mark.parametrize("bad", [None, [], "evidence", {}])
def test_invalid_evidence_root(policy, bad):
    assert evaluate(policy, bad).status is Status.ERROR


@pytest.mark.parametrize("version", [True, 1.0, "1", 0, 2, None])
@pytest.mark.parametrize("target", ["policy", "evidence"])
def test_invalid_schema_version(policy, evidence, version, target):
    (policy if target == "policy" else evidence)["schema_version"] = version
    assert evaluate(policy, evidence).status is Status.ERROR


@pytest.mark.parametrize(
    "value", [True, None, "0.95", float("nan"), float("inf"), -float("inf"), [], {}]
)
@pytest.mark.parametrize("target", ["threshold", "measurement"])
def test_invalid_numbers(policy, evidence, value, target):
    if target == "threshold":
        policy["tests"][0]["metrics"][0]["threshold"] = value
    else:
        evidence["tests"][0]["metrics"]["accuracy"] = value
    assert evaluate(policy, evidence).status is Status.ERROR


@pytest.mark.parametrize("value", ["", "a b", "../path", "á", "x" * 65, 42, None, True])
def test_invalid_identifiers(policy, evidence, value):
    policy["tests"][0]["id"] = value
    assert evaluate(policy, evidence).status is Status.ERROR


@pytest.mark.parametrize("target", ["policy", "evidence", "metric"])
def test_duplicate_identifiers(policy, evidence, target):
    if target == "metric":
        metrics = policy["tests"][0]["metrics"]
        metrics.append(dict(metrics[0]))
    else:
        tests = (policy if target == "policy" else evidence)["tests"]
        tests.append(dict(tests[0]))
    report = evaluate(policy, evidence)
    assert report.status is Status.ERROR
    assert report.errors[0].code == "DUPLICATE_ID"


@pytest.mark.parametrize("target", ["test", "metric"])
def test_unknown_references(policy, evidence, target):
    if target == "test":
        evidence["tests"][0]["id"] = "unknown"
    else:
        evidence["tests"][0]["metrics"]["unknown"] = 1
    report = evaluate(policy, evidence)
    assert report.status is Status.ERROR
    assert report.errors[0].code == "UNKNOWN_REFERENCE"


@pytest.mark.parametrize("target", ["policy", "evidence", "test", "metric"])
def test_unknown_fields(policy, evidence, target):
    locations = {
        "policy": policy,
        "evidence": evidence,
        "test": evidence["tests"][0],
        "metric": policy["tests"][0]["metrics"][0],
    }
    locations[target]["unexpected"] = True
    assert evaluate(policy, evidence).status is Status.ERROR


@pytest.mark.parametrize("operator", ["eval", "=", [], None, True])
def test_invalid_operator(policy, evidence, operator):
    policy["tests"][0]["metrics"][0]["operator"] = operator
    assert evaluate(policy, evidence).status is Status.ERROR


@pytest.mark.parametrize("status", ["PASS", "success", [], None, True])
def test_invalid_test_status(policy, evidence, status):
    evidence["tests"][0]["status"] = status
    assert evaluate(policy, evidence).status is Status.ERROR


def test_skipped_test_with_measurements_is_error(policy, evidence):
    evidence["tests"][0]["status"] = "skipped"
    assert evaluate(policy, evidence).status is Status.ERROR


@pytest.mark.parametrize(
    "target", ["policy_tests", "policy_metrics", "evidence_tests", "evidence_metrics"]
)
def test_invalid_collection_types(policy, evidence, target):
    if target == "policy_tests":
        policy["tests"] = {}
    elif target == "policy_metrics":
        policy["tests"][0]["metrics"] = {}
    elif target == "evidence_tests":
        evidence["tests"] = {}
    else:
        evidence["tests"][0]["metrics"] = []
    assert evaluate(policy, evidence).status is Status.ERROR


def test_nonstring_mapping_key(policy, evidence):
    policy[1] = "bad"
    assert evaluate(policy, evidence).status is Status.ERROR
