import json

import pytest
import yaml

from agentrelease import Status, evaluate, evaluate_files


@pytest.fixture
def paths(tmp_path, policy, evidence):
    policy_path, evidence_path = tmp_path / "policy.yaml", tmp_path / "evidence.json"
    policy_path.write_text(yaml.safe_dump(policy), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
    return policy_path, evidence_path


def test_files_match_dictionary_api(paths, policy, evidence):
    assert evaluate_files(*paths) == evaluate(policy, evidence)


@pytest.mark.parametrize(
    ("target", "content", "code"),
    [
        (0, "tests: [", "MALFORMED_INPUT"),
        (1, '{"tests": [}', "MALFORMED_INPUT"),
        (1, '{"schema_version":1,"tests":[],"tests":[]}', "DUPLICATE_KEY"),
        (1, '{"schema_version":1,"tests":[{"id":"quality","id":"boundary"}]}', "DUPLICATE_KEY"),
        (0, "schema_version: 1\nid: x\nid: y\ntests: []", "DUPLICATE_KEY"),
        (0, "schema_version: 1\nid: x\ntests:\n- id: a\n  id: b", "DUPLICATE_KEY"),
        (0, "!!python/object/apply:os.system ['echo forbidden']", "MALFORMED_INPUT"),
        (0, "x: &x [*x]", "INVALID_INPUT"),
        (0, "1: value", "INVALID_INPUT"),
        (0, "? [a, b]\n: value", "INVALID_INPUT"),
        (0, "---\n{}\n---\n{}", "MALFORMED_INPUT"),
        (1, '{"schema_version":1,"tests":[],"invalid":NaN}', "INVALID_INPUT"),
        (1, '{"schema_version":1,"tests":[],"invalid":Infinity}', "INVALID_INPUT"),
        (0, "", "INVALID_INPUT"),
        (1, "", "MALFORMED_INPUT"),
    ],
)
def test_bad_documents(paths, target, content, code):
    paths[target].write_text(content, encoding="utf-8")
    report = evaluate_files(*paths)
    assert report.status is Status.ERROR
    assert report.errors[0].code == code
    assert report.checks == ()


def test_unsafe_yaml_cannot_execute_commands(paths, tmp_path):
    marker = tmp_path / "executed"
    paths[0].write_text(f"!!python/object/apply:os.system ['touch {marker}']", encoding="utf-8")
    assert evaluate_files(*paths).status is Status.ERROR
    assert not marker.exists()


@pytest.mark.parametrize("target", [0, 1])
def test_invalid_encoding(paths, target):
    paths[target].write_bytes(b"\xff\xfe")
    report = evaluate_files(*paths)
    assert report.status is Status.ERROR
    assert report.errors[0].code == "INVALID_ENCODING"


@pytest.mark.parametrize("target", [0, 1])
def test_missing_file(paths, target):
    paths[target].unlink()
    assert evaluate_files(*paths).errors[0].code == "INPUT_IO"


def test_directory_as_input(paths):
    assert evaluate_files(paths[0].parent, paths[1]).errors[0].code == "INPUT_IO"


def test_file_size_limit(paths):
    paths[1].write_bytes(b" " * (5 * 1024 * 1024 + 1))
    assert evaluate_files(*paths).errors[0].code == "INPUT_TOO_LARGE"


def test_deep_json_returns_error(paths):
    paths[1].write_text("[" * 2000 + "0" + "]" * 2000, encoding="utf-8")
    assert evaluate_files(*paths).status is Status.ERROR


def test_json_exponent_overflow_is_rejected(paths):
    paths[1].write_text(
        '{"schema_version":1,"tests":[{"id":"quality","status":"passed",'
        '"metrics":{"accuracy":1e999}}]}',
        encoding="utf-8",
    )
    assert evaluate_files(*paths).status is Status.ERROR


def test_yaml_nonfinite_threshold_is_rejected(paths):
    paths[0].write_text(
        "schema_version: 1\nid: x\ntests:\n- id: quality\n  metrics:\n"
        '- name: accuracy\n  operator: ">="\n  threshold: .nan\n',
        encoding="utf-8",
    )
    assert evaluate_files(*paths).status is Status.ERROR
