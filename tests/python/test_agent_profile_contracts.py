from __future__ import annotations

import pytest
from pydantic import ValidationError

from asset_allocation_contracts.agent_profile import (
    AgentAppliedConfigChange,
    AgentBehaviorTraits,
    AgentEvidencePolicy,
    AgentProfileConfig,
    AgentProfilePreset,
    AgentRegimePreference,
    AgentStrategyBinding,
    AgentStrategyResolutionPreview,
)
from asset_allocation_contracts.strategy import ConfigIdentity, ConfigReference, StrategyConfig


def test_agent_profile_preset_validates_deterministic_v1_scope() -> None:
    preset = AgentProfilePreset.model_validate(
        {
            "identity": {
                "name": "balanced-alpha-researcher",
                "version": 1,
                "status": "active",
                "intendedUse": "research",
            },
            "config": {
                "role": "alpha_research",
                "maxWorkflowScope": "paper_preview",
                "traits": {
                    "riskAppetite": 0.55,
                    "lossAversion": 0.45,
                    "patience": 0.6,
                    "conviction": 0.7,
                    "concentrationTolerance": 0.35,
                    "turnoverTolerance": 0.4,
                    "recencyBias": 0.5,
                    "contrarianBias": -0.1,
                },
                "worldviewWeights": [
                    {"worldview": "quality", "weight": 3},
                    {"worldview": "momentum", "weight": 2},
                ],
                "regimePreference": {
                    "preferredRegimes": ["trending_up", "low_volatility"],
                    "blockedRegimes": ["liquidity_stress"],
                },
                "evidencePolicy": {
                    "minimumConfidence": 0.7,
                    "minimumIndependentSignals": 2,
                    "requireRankingSupport": True,
                    "requireRegimeSupport": True,
                    "requireLiquiditySupport": True,
                },
            },
        }
    )

    assert preset.identity == ConfigIdentity(
        name="balanced-alpha-researcher",
        version=1,
        status="active",
        intendedUse="research",
    )
    assert preset.config.maxWorkflowScope == "paper_preview"
    assert [item.worldview for item in preset.config.worldviewWeights] == ["quality", "momentum"]


def test_agent_profile_rejects_duplicate_worldview_weights() -> None:
    with pytest.raises(ValidationError, match="worldviewWeights must be unique"):
        AgentProfileConfig.model_validate(
            {
                "role": "portfolio_manager",
                "worldviewWeights": [
                    {"worldview": "quality", "weight": 1},
                    {"worldview": "quality", "weight": 2},
                ],
            }
        )


def test_agent_profile_rejects_vague_or_unbounded_traits() -> None:
    with pytest.raises(ValidationError):
        AgentBehaviorTraits.model_validate({"riskAppetite": 1.1})

    with pytest.raises(ValidationError):
        AgentEvidencePolicy.model_validate({"minimumIndependentSignals": 0})


def test_agent_regime_preferences_are_deduped_and_non_overlapping() -> None:
    preference = AgentRegimePreference.model_validate(
        {
            "preferredRegimes": ["trending_up", "trending_up", "low_volatility"],
            "blockedRegimes": ["liquidity_stress", "liquidity_stress"],
        }
    )

    assert preference.preferredRegimes == ["trending_up", "low_volatility"]
    assert preference.blockedRegimes == ["liquidity_stress"]

    with pytest.raises(ValidationError, match="both prefer and block"):
        AgentRegimePreference.model_validate(
            {
                "preferredRegimes": ["high_volatility"],
                "blockedRegimes": ["high_volatility"],
            }
        )


def test_agent_strategy_binding_requires_exact_refs_and_valid_clamps() -> None:
    binding = AgentStrategyBinding.model_validate(
        {
            "agentProfileRef": {"name": "balanced-alpha-researcher", "version": 1},
            "baseStrategyRef": {"name": "core-quality-momentum", "version": 4},
            "rankingRefsByWorldview": {
                "quality": {"name": "quality_momentum", "version": 2},
                "momentum": {"name": "price_momentum", "version": 3},
            },
            "riskPolicyRefsByBand": {
                "balanced": {"name": "balanced_long_only", "version": 1},
            },
            "rebalancePolicyRefsByBand": {
                "medium": {"name": "monthly_last_trading_day", "version": 1},
            },
            "exitPolicyRefsByBand": {
                "balanced": {"name": "rank_decay_exit", "version": 1},
            },
            "minTopN": 10,
            "maxTopN": 40,
            "minHoldingPeriod": 5,
            "maxHoldingPeriod": 63,
            "maxPositionSizePct": 8,
            "blockedRegimes": ["liquidity_stress"],
        }
    )

    assert binding.agentProfileRef == ConfigReference(name="balanced-alpha-researcher", version=1)
    assert binding.baseStrategyRef == ConfigReference(name="core-quality-momentum", version=4)
    assert binding.rankingRefsByWorldview["quality"] == ConfigReference(
        name="quality_momentum",
        version=2,
    )

    with pytest.raises(ValidationError, match="minTopN cannot exceed maxTopN"):
        AgentStrategyBinding.model_validate(
            {
                "agentProfileRef": {"name": "p", "version": 1},
                "baseStrategyRef": {"name": "s", "version": 1},
                "minTopN": 50,
                "maxTopN": 25,
            }
        )


def test_agent_strategy_resolution_preview_carries_hashes_and_structured_changes() -> None:
    preview = AgentStrategyResolutionPreview.model_validate(
        {
            "agentProfileRef": {"name": "balanced-alpha-researcher", "version": 1},
            "baseStrategyRef": {"name": "core-quality-momentum", "version": 4},
            "resolvedStrategy": StrategyConfig(
                universeConfigName="us-large-liquid",
                rankingSchemaName="quality_momentum",
                rankingSchemaVersion=2,
            ).model_dump(mode="json"),
            "appliedChanges": [
                {
                    "path": "rankingSchemaName",
                    "previousValue": "base-ranking",
                    "newValue": "quality_momentum",
                    "reasonCode": "dominant_worldview",
                    "reason": "quality carried the largest normalized worldview weight",
                    "clampStatus": "not_clamped",
                },
                AgentAppliedConfigChange(
                    path="topN",
                    previousValue=50,
                    newValue=40,
                    reasonCode="binding_max_top_n",
                    clampStatus="clamped",
                ).model_dump(mode="json"),
            ],
            "warnings": ["Saved refs should be used for durable backtests."],
            "agentProfileSnapshotHash": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "baseStrategySnapshotHash": "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "bindingHash": "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
            "resolvedStrategyHash": "sha256:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",
            "validationStatus": "warning",
        }
    )

    assert preview.resolvedStrategy.rankingSchemaName == "quality_momentum"
    assert preview.appliedChanges[1].clampStatus == "clamped"
    assert preview.validationStatus == "warning"
