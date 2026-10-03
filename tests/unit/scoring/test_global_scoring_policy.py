import pytest

from app.domain.scoring.policy import (
    GlobalScoringPolicy,
    compute_cred_global_score,
    default_global_scoring_policy,
)


def test_default_global_scoring_policy_is_versioned_and_valid():
    policy = default_global_scoring_policy()

    assert policy.policy_id == "credona.api.global-min-score.v1"
    assert policy.aggregation_method == "min"


def test_global_scoring_policy_rejects_unsupported_aggregation_method():
    policy = GlobalScoringPolicy(
        policy_id="credona.api.invalid.v1",
        aggregation_method="average",
    )

    with pytest.raises(ValueError, match="unsupported aggregation method"):
        policy.validate()


def test_cred_global_score_uses_lowest_public_score():
    assert compute_cred_global_score(0.82, 0.97) == 0.82


def test_cred_global_score_is_bounded():
    assert compute_cred_global_score(2.0, 0.5) == 0.5
    assert compute_cred_global_score(-1.0, 0.5) == 0.0


def test_cred_global_score_is_stable_for_same_inputs():
    assert compute_cred_global_score(0.77, 0.91) == compute_cred_global_score(
        0.77, 0.91
    )


def test_cred_global_score_is_monotonic_when_lowest_score_increases():
    low = compute_cred_global_score(0.4, 0.9)
    high = compute_cred_global_score(0.8, 0.9)

    assert high >= low
