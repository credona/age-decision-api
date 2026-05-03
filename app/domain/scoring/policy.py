from dataclasses import dataclass

DEFAULT_GLOBAL_SCORING_POLICY_ID = "credona.api.global-min-score.v1"


@dataclass(frozen=True)
class GlobalScoringPolicy:
    policy_id: str
    aggregation_method: str

    def validate(self) -> None:
        if not self.policy_id:
            raise ValueError("policy_id is required")

        if self.aggregation_method != "min":
            raise ValueError("unsupported aggregation method")


def default_global_scoring_policy() -> GlobalScoringPolicy:
    policy = GlobalScoringPolicy(
        policy_id=DEFAULT_GLOBAL_SCORING_POLICY_ID,
        aggregation_method="min",
    )
    policy.validate()
    return policy


def compute_cred_global_score(
    cred_decision_score: float,
    cred_antispoof_score: float,
    policy: GlobalScoringPolicy | None = None,
) -> float:
    resolved_policy = policy or default_global_scoring_policy()
    resolved_policy.validate()

    decision_score = max(0.0, min(float(cred_decision_score), 1.0))
    antispoof_score = max(0.0, min(float(cred_antispoof_score), 1.0))

    return round(min(decision_score, antispoof_score), 4)
