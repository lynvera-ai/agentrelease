"""Strict validation shared by file and dictionary inputs."""

import math
import re
from dataclasses import dataclass

IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}\Z")
OPERATORS = {">=", ">", "<=", "<", "==", "!="}


class InputError(ValueError):
    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)


@dataclass(frozen=True)
class MetricRule:
    name: str
    operator: str
    threshold: int | float


@dataclass(frozen=True)
class TestRule:
    id: str
    metrics: tuple[MetricRule, ...]


@dataclass(frozen=True)
class TestEvidence:
    id: str
    status: str
    metrics: dict[str, int | float]


def fail(message: str, code: str = "INVALID_INPUT") -> None:
    raise InputError(code, message)


def fields(value: object, required: set[str], optional: set[str], path: str) -> dict:
    if type(value) is not dict:
        fail(f"{path} must be an object.")
    if any(type(key) is not str for key in value):
        fail(f"{path} must have string keys.")
    missing = required - value.keys()
    unknown = value.keys() - required - optional
    if missing:
        fail(f"{path} is missing fields: {', '.join(sorted(missing))}.")
    if unknown:
        fail(f"{path} has unknown fields: {', '.join(sorted(unknown))}.")
    return value


def identifier(value: object, path: str) -> str:
    if type(value) is not str or not IDENTIFIER.fullmatch(value):
        fail(f"{path} must be an identifier of 1 to 64 ASCII characters.")
    return value


def number(value: object, path: str) -> int | float:
    if type(value) not in (int, float) or (type(value) is float and not math.isfinite(value)):
        fail(f"{path} must be a finite number, not a boolean or string.")
    return value


def sequence(value: object, path: str) -> list:
    if type(value) is not list:
        fail(f"{path} must be a list.")
    return value


def version(value: object, path: str) -> None:
    if type(value) is not int or value != 1:
        fail(f"{path}.schema_version must be integer 1.")


def unique(value: str, seen: set[str], path: str) -> None:
    if value in seen:
        fail(f"{path} contains duplicate identifier '{value}'.", "DUPLICATE_ID")
    seen.add(value)


def validate_policy(value: object) -> tuple[str, tuple[TestRule, ...]]:
    root = fields(value, {"schema_version", "id", "tests"}, set(), "policy")
    version(root["schema_version"], "policy")
    policy_id = identifier(root["id"], "policy.id")
    tests = sequence(root["tests"], "policy.tests")
    if not tests:
        fail("policy.tests must contain at least one mandatory test.")
    seen: set[str] = set()
    rules = []
    for index, item in enumerate(tests):
        path = f"policy.tests[{index}]"
        test = fields(item, {"id"}, {"metrics"}, path)
        test_id = identifier(test["id"], f"{path}.id")
        unique(test_id, seen, "policy.tests")
        metrics = []
        metric_names: set[str] = set()
        for metric_index, item in enumerate(sequence(test.get("metrics", []), f"{path}.metrics")):
            metric_path = f"{path}.metrics[{metric_index}]"
            metric = fields(item, {"name", "operator", "threshold"}, set(), metric_path)
            name = identifier(metric["name"], f"{metric_path}.name")
            unique(name, metric_names, f"{path}.metrics")
            operator = metric["operator"]
            if type(operator) is not str or operator not in OPERATORS:
                fail(f"{metric_path}.operator must be one of: {', '.join(sorted(OPERATORS))}.")
            threshold = number(metric["threshold"], f"{metric_path}.threshold")
            metrics.append(MetricRule(name, operator, threshold))
        rules.append(TestRule(test_id, tuple(sorted(metrics, key=lambda m: m.name))))
    return policy_id, tuple(sorted(rules, key=lambda t: t.id))


def validate_evidence(value: object, rules: tuple[TestRule, ...]) -> dict[str, TestEvidence]:
    root = fields(value, {"schema_version", "tests"}, set(), "evidence")
    version(root["schema_version"], "evidence")
    tests = sequence(root["tests"], "evidence.tests")
    allowed = {rule.id: {metric.name for metric in rule.metrics} for rule in rules}
    seen: set[str] = set()
    result = {}
    for index, item in enumerate(tests):
        path = f"evidence.tests[{index}]"
        test = fields(item, {"id", "status"}, {"metrics"}, path)
        test_id = identifier(test["id"], f"{path}.id")
        unique(test_id, seen, "evidence.tests")
        if test_id not in allowed:
            fail(f"{path}.id references unknown policy test '{test_id}'.", "UNKNOWN_REFERENCE")
        status = test["status"]
        if type(status) is not str or status not in {"passed", "failed", "skipped"}:
            fail(f"{path}.status must be passed, failed or skipped.")
        metrics = test.get("metrics", {})
        if type(metrics) is not dict:
            fail(f"{path}.metrics must be an object.")
        checked = {}
        for name, measurement in metrics.items():
            identifier(name, f"{path}.metrics key")
            if name not in allowed[test_id]:
                fail(f"{path}.metrics references unknown metric '{name}'.", "UNKNOWN_REFERENCE")
            checked[name] = number(measurement, f"{path}.metrics.{name}")
        if status == "skipped" and checked:
            fail(f"{path}: a skipped test cannot contain measurements.")
        result[test_id] = TestEvidence(test_id, status, checked)
    return result
