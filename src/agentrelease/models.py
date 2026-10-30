"""Immutable evaluation results."""

import json
from dataclasses import asdict, dataclass
from enum import StrEnum

VERSION = "0.1.0"
SCOPE = (
    "This report describes only the supplied evidence and policy criteria. "
    "It is not a certification of general agent safety or reliability."
)


class Status(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    INCONCLUSIVE = "INCONCLUSIVE"
    ERROR = "ERROR"

    @property
    def exit_code(self) -> int:
        return {self.PASS: 0, self.FAIL: 1, self.INCONCLUSIVE: 2, self.ERROR: 3}[self]


@dataclass(frozen=True)
class Check:
    test_id: str
    kind: str
    status: Status
    reason: str
    metric: str | None = None
    observed: int | float | str | None = None
    operator: str | None = None
    threshold: int | float | None = None


@dataclass(frozen=True)
class Issue:
    code: str
    message: str


@dataclass(frozen=True)
class Report:
    status: Status
    policy_id: str | None = None
    checks: tuple[Check, ...] = ()
    errors: tuple[Issue, ...] = ()
    policy_sha256: str | None = None
    evidence_sha256: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "evaluator_version": VERSION,
            "policy_id": self.policy_id,
            "status": self.status.value,
            "scope": SCOPE,
            "input_sha256": {"policy": self.policy_sha256, "evidence": self.evidence_sha256},
            "checks": [{**asdict(c), "status": c.status.value} for c in self.checks],
            "errors": [asdict(e) for e in self.errors],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, indent=2, allow_nan=False) + "\n"

    def to_text(self) -> str:
        lines = [f"AgentRelease: {self.status.value}", f"Policy: {self.policy_id or 'unavailable'}"]
        lines.append(f"Evaluator version: {VERSION}")
        if self.policy_sha256 is not None:
            lines.append(f"Policy SHA-256: {self.policy_sha256}")
        if self.evidence_sha256 is not None:
            lines.append(f"Evidence SHA-256: {self.evidence_sha256}")
        for check in self.checks:
            label = check.test_id + (f" / {check.metric}" if check.metric else "")
            detail = ""
            if check.operator is not None:
                detail = (
                    f" (observed={check.observed!r}, required {check.operator} {check.threshold!r})"
                )
            lines.append(f"[{check.status.value}] {label}: {check.reason}{detail}")
        lines.extend(f"[ERROR] {error.code}: {error.message}" for error in self.errors)
        lines.extend(["", SCOPE])
        return "\n".join(lines) + "\n"


def error_report(code: str, message: str) -> Report:
    return Report(Status.ERROR, errors=(Issue(code, message),))
