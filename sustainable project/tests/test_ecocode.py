"""
Unit and Integration Tests for EcoCode Platform
Verifies mathematical proxy modeling, static smell heuristics, and CI/CD gatekeeper.
"""

import sys
import os

# Ensure parent directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ecocode.profiler import CodeProfiler, ProfileResult
from ecocode.advisor import GreenAdvisor, CodeSmell
from ecocode.gatekeeper import CICDGatekeeper, GateResult


def test_profiler_mathematics():
    """Verify exact formula calculations as defined in PS 5.3 PDR."""
    profiler = CodeProfiler(
        server_power_watts=100.0,
        grid_intensity_factor=0.8,
        electricity_rate_inr=8.0
    )
    # For T = 36.0 seconds:
    # Energy = (36 / 3600) * 0.1 = 0.01 * 0.1 = 0.001 kWh
    # Carbon = 0.001 * 0.8 = 0.0008 kg = 0.8 g
    # Cost = 0.001 * 8.0 = 0.008 INR
    metrics = profiler.calculate_metrics(36.0, peak_memory_kb=500.0)

    assert abs(metrics["energy_kwh"] - 0.001) < 1e-6, f"Energy mismatch: {metrics['energy_kwh']}"
    assert abs(metrics["carbon_kg_co2"] - 0.0008) < 1e-6, f"Carbon mismatch: {metrics['carbon_kg_co2']}"
    assert abs(metrics["carbon_g_co2"] - 0.8) < 1e-4, f"Carbon g mismatch: {metrics['carbon_g_co2']}"
    assert abs(metrics["cost_inr"] - 0.008) < 1e-5, f"Cost mismatch: {metrics['cost_inr']}"
    print("✔ test_profiler_mathematics passed!")


def test_profiler_execution():
    """Verify sandboxed code execution and memory tracing."""
    profiler = CodeProfiler()
    code = """
total = sum(i * 2 for i in range(10000))
print(f"Computed total: {total}")
"""
    result = profiler.execute_and_profile(code, repeat=1)
    assert result.success is True
    assert result.execution_time_sec > 0
    assert result.energy_kwh > 0
    assert "Computed total: 99990000" in result.stdout
    print("✔ test_profiler_execution passed!")


def test_advisor_heuristics():
    """Verify detection of anti-patterns and scoring."""
    advisor = GreenAdvisor()
    bad_code = """
import pandas as pd

# Smell 1: open without with
f = open("log.txt", "r")

# Smell 2: pandas iterrows
for idx, row in df.iterrows():
    val = row['a']

# Smell 3: nested loop O(N^2)
for i in range(100):
    for j in range(100):
        # Smell 4: in list inside loop
        if i in lookup_list:
            pass

# Smell 5: string += in loop
s = ""
for char in ['a', 'b', 'c']:
    s += char
"""
    smells = advisor.analyze_code(bad_code)
    rule_ids = [s.rule_id for s in smells]

    assert "ECO001" in rule_ids, "Nested loop should be detected"
    assert "ECO002" in rule_ids, "iterrows should be detected"
    assert "ECO003" in rule_ids, "open without with should be detected"
    assert "ECO004" in rule_ids, "string += in loop should be detected"
    assert "ECO005" in rule_ids, "in list check should be detected"

    score_data = advisor.compute_green_score(smells, loc=len(bad_code.splitlines()))
    assert score_data["score"] < 50, f"Score should be low for bad code: {score_data['score']}"
    print(f"✔ test_advisor_heuristics passed! Score: {score_data['score']} ({score_data['grade']})")


def test_gatekeeper_pass_and_block():
    """Verify CI/CD gatekeeper pass/fail regression decisions."""
    gatekeeper = CICDGatekeeper(threshold_pct=10.0)

    # 1. PR with same or lower energy -> MUST PASS
    pass_profile = ProfileResult(
        success=True,
        execution_time_sec=0.050,  # lower than baseline 0.052
        energy_kwh=0.000001388,
        carbon_kg_co2=0.00000111,
        carbon_g_co2=0.00111,
        cost_inr=0.0000111,
        peak_memory_kb=120.0,
        stdout="Test passed",
    )
    res_pass = gatekeeper.evaluate_pr(pr_profile=pass_profile, pr_number=101)
    assert res_pass.passed is True
    assert res_pass.status == "PASSED"
    assert "EcoCode GreenOps CI Gate: PASS" in res_pass.pr_comment_markdown

    # 2. PR with +80% energy regression -> MUST BLOCK
    block_profile = ProfileResult(
        success=True,
        execution_time_sec=0.150,  # ~3x baseline
        energy_kwh=0.000004166,
        carbon_kg_co2=0.00000333,
        carbon_g_co2=0.00333,
        cost_inr=0.0000333,
        peak_memory_kb=300.0,
        stdout="Heavy run",
    )
    res_block = gatekeeper.evaluate_pr(pr_profile=block_profile, pr_number=102)
    assert res_block.passed is False
    assert res_block.status == "BLOCKED"
    assert "EcoCode GreenOps CI Gate: BLOCKED" in res_block.pr_comment_markdown
    print("✔ test_gatekeeper_pass_and_block passed!")


if __name__ == "__main__":
    print("Running EcoCode Engine Test Suite...")
    test_profiler_mathematics()
    test_profiler_execution()
    test_advisor_heuristics()
    test_gatekeeper_pass_and_block()
    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY!")
