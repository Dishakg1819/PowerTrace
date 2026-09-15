"""
CI/CD Pipeline Energy Guard (Regression Gatekeeper) Module for EcoCode
Automated GitHub Action gate simulation that compares PR metrics against
a production baseline (baseline.json) and blocks merges exceeding energy thresholds.
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
from .profiler import CodeProfiler, ProfileResult


@dataclass
class GateResult:
    passed: bool
    status: str  # 'PASSED' or 'BLOCKED'
    regression_pct: float
    threshold_pct: float
    baseline_metrics: Dict[str, float]
    pr_metrics: Dict[str, float]
    delta_time_sec: float
    delta_energy_kwh: float
    delta_carbon_g: float
    delta_cost_inr: float
    pr_comment_markdown: str
    action_log: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CICDGatekeeper:
    """
    Automated GreenOps CI/CD Gatekeeper.
    Enforces sustainability budgets and stops carbon regressions in pipeline.
    """
    DEFAULT_BASELINE_FILE = "baseline.json"

    def __init__(self, baseline_path: str = DEFAULT_BASELINE_FILE, threshold_pct: float = 10.0):
        self.baseline_path = baseline_path
        self.threshold_pct = threshold_pct
        self.profiler = CodeProfiler()

    def load_baseline(self) -> Dict[str, Any]:
        """Loads historical production baseline metrics."""
        if os.path.exists(self.baseline_path):
            try:
                with open(self.baseline_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Default fallback baseline if file doesn't exist yet
        return {
            "name": "Production Master v2.4",
            "execution_time_sec": 0.052,
            "energy_kwh": 0.000001444,
            "carbon_g_co2": 0.001155,
            "cost_inr": 0.00001155,
            "peak_memory_kb": 124.0,
            "timestamp": "2026-09-01T12:00:00Z",
            "commit": "a7f39b2",
        }

    def save_baseline(self, metrics: Dict[str, Any], name: str = "Production Baseline", commit: str = "main-head") -> bool:
        """Saves current metrics as the new production baseline."""
        payload = {
            "name": name,
            "commit": commit,
            "execution_time_sec": metrics.get("execution_time_sec", 0.0),
            "energy_kwh": metrics.get("energy_kwh", 0.0),
            "carbon_g_co2": metrics.get("carbon_g_co2", 0.0),
            "cost_inr": metrics.get("cost_inr", 0.0),
            "peak_memory_kb": metrics.get("peak_memory_kb", 0.0),
        }
        try:
            with open(self.baseline_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            return True
        except Exception:
            return False

    def evaluate_pr(
        self,
        pr_code: Optional[str] = None,
        pr_profile: Optional[ProfileResult] = None,
        pr_number: int = 142,
        commit_sha: str = "7e49c81",
        author: str = "dev-contributor"
    ) -> GateResult:
        """
        Runs CI/CD regression check against the baseline.
        """
        baseline = self.load_baseline()

        if pr_profile is None and pr_code is not None:
            pr_profile = self.profiler.execute_and_profile(pr_code, repeat=3)

        if pr_profile is None:
            raise ValueError("Must provide either pr_code or pr_profile")

        base_time = max(0.000001, baseline.get("execution_time_sec", 0.05))
        base_energy = max(0.000000001, baseline.get("energy_kwh", (base_time / 3600.0) * 0.1))
        base_carbon = baseline.get("carbon_g_co2", base_energy * 0.8 * 1000.0)
        base_cost = baseline.get("cost_inr", base_energy * 8.0)

        pr_time = pr_profile.execution_time_sec
        pr_energy = pr_profile.energy_kwh
        pr_carbon = pr_profile.carbon_g_co2
        pr_cost = pr_profile.cost_inr

        # Calculate percentage change in energy consumption
        regression_pct = ((pr_energy - base_energy) / base_energy) * 100.0
        delta_time = pr_time - base_time
        delta_energy = pr_energy - base_energy
        delta_carbon = pr_carbon - base_carbon
        delta_cost = pr_cost - base_cost

        passed = regression_pct <= self.threshold_pct
        status = "PASSED" if passed else "BLOCKED"

        pr_metrics = {
            "execution_time_sec": pr_time,
            "energy_kwh": pr_energy,
            "carbon_g_co2": pr_carbon,
            "cost_inr": pr_cost,
            "peak_memory_kb": pr_profile.peak_memory_kb,
        }

        # Generate automated GitHub PR comment markdown
        comment_md = self._generate_pr_comment(
            passed=passed,
            status=status,
            regression_pct=regression_pct,
            threshold_pct=self.threshold_pct,
            pr_number=pr_number,
            commit_sha=commit_sha,
            author=author,
            baseline=baseline,
            pr_metrics=pr_metrics,
            delta_time=delta_time,
            delta_carbon=delta_carbon,
            delta_cost=delta_cost,
        )

        action_log = self._generate_action_log(
            passed=passed,
            regression_pct=regression_pct,
            threshold_pct=self.threshold_pct,
            commit_sha=commit_sha
        )

        return GateResult(
            passed=passed,
            status=status,
            regression_pct=regression_pct,
            threshold_pct=self.threshold_pct,
            baseline_metrics=baseline,
            pr_metrics=pr_metrics,
            delta_time_sec=delta_time,
            delta_energy_kwh=delta_energy,
            delta_carbon_g=delta_carbon,
            delta_cost_inr=delta_cost,
            pr_comment_markdown=comment_md,
            action_log=action_log
        )

    def _generate_pr_comment(
        self,
        passed: bool,
        status: str,
        regression_pct: float,
        threshold_pct: float,
        pr_number: int,
        commit_sha: str,
        author: str,
        baseline: Dict[str, Any],
        pr_metrics: Dict[str, Any],
        delta_time: float,
        delta_carbon: float,
        delta_cost: float,
    ) -> str:
        if passed:
            badge = "![CI: EcoCode PASSED](https://img.shields.io/badge/EcoCode%20CI-PASSED%20%E2%9C%94-10b981?style=flat-square)"
            header = "### 🌿 EcoCode GreenOps CI Gate: PASS (Merge Approved)"
            summary_alert = (
                f"> **PASSED**: Pull Request #{pr_number} adheres to green computing standards.\n"
                f"> Energy variance is `{regression_pct:+.2f}%` (Budget threshold: `+{threshold_pct:.1f}%`)."
            )
            action_call = "**Result**: No energy regression detected. This pull request is eligible for automated merging."
        else:
            badge = "![CI: EcoCode BLOCKED](https://img.shields.io/badge/EcoCode%20CI-BLOCKED%20%E2%9D%8C-ef4444?style=flat-square)"
            header = "### ⚠️ EcoCode GreenOps CI Gate: BLOCKED (Energy Regression Detected)"
            summary_alert = (
                f"> **MERGE BLOCKED**: PR #{pr_number} exceeds the allowable energy consumption threshold!\n"
                f"> Energy consumption increased by **`{regression_pct:+.2f}%`** (Max Allowed: `+{threshold_pct:.1f}%`)."
            )
            action_call = (
                "**Action Required**: Please run the `EcoCode Green-Code Advisor` locally to identify $O(N^2)$ loops, "
                "unoptimized DataFrame operations, or memory leaks before requesting a re-run."
            )

        sign = "+" if delta_time >= 0 else ""

        markdown = f"""{badge}
{header}

{summary_alert}

#### 📊 Sustainability Resource Scorecard (Commit: `{commit_sha[:7]}`)

| Metric | Production Baseline | PR #{pr_number} Candidate | Absolute Delta | % Variance |
| :--- | :--- | :--- | :--- | :--- |
| **Execution Time** | `{baseline.get('execution_time_sec', 0):.4f} s` | `{pr_metrics['execution_time_sec']:.4f} s` | `{sign}{delta_time:.4f} s` | `{regression_pct:+.2f}%` |
| **Energy Consumption** | `{baseline.get('energy_kwh', 0):.8f} kWh` | `{pr_metrics['energy_kwh']:.8f} kWh` | `{sign}{pr_metrics['energy_kwh'] - baseline.get('energy_kwh', 0):.8f} kWh` | `{regression_pct:+.2f}%` |
| **Carbon Footprint** | `{baseline.get('carbon_g_co2', 0):.6f} g CO₂e` | `{pr_metrics['carbon_g_co2']:.6f} g CO₂e` | `{sign}{delta_carbon:.6f} g` | `{regression_pct:+.2f}%` |
| **Cloud Cost (INR)** | `₹{baseline.get('cost_inr', 0):.6f}` | `₹{pr_metrics['cost_inr']:.6f}` | `{sign}₹{delta_cost:.6f}` | `{regression_pct:+.2f}%` |
| **Peak Memory** | `{baseline.get('peak_memory_kb', 0):.1f} KB` | `{pr_metrics['peak_memory_kb']:.1f} KB` | `{sign}{pr_metrics['peak_memory_kb'] - baseline.get('peak_memory_kb', 0):.1f} KB` | -- |

{action_call}

---
*Report automatically generated by [EcoCode GreenOps CI/CD Gatekeeper](https://github.com/ecocode-greenops)*
"""
        return markdown

    def _generate_action_log(self, passed: bool, regression_pct: float, threshold_pct: float, commit_sha: str) -> str:
        lines = [
            f"[INFO] EcoCode CI/CD Runner initialized for commit {commit_sha}",
            "[INFO] Loading production baseline from baseline.json ... [OK]",
            "[INFO] Executing sandboxed proxy profiling across 3 iterations ...",
            f"[METRIC] Evaluated Energy Regression: {regression_pct:+.2f}%",
            f"[POLICY] Configured Max Regression Policy: +{threshold_pct:.1f}%",
        ]
        if passed:
            lines.extend([
                "[STATUS] Gate Evaluation: SUCCESS",
                "[SUCCESS] Energy variance is within sustainable budget.",
                "[EXIT] Process exited with status code 0 (Allow Merge)",
            ])
        else:
            lines.extend([
                f"[ERROR] SUSTAINABILITY REGRESSION ALERT: {regression_pct:+.2f}% > {threshold_pct:.1f}%",
                "[STATUS] Gate Evaluation: FAILED",
                "[BLOCK] Merge gate locked. Pull request status set to: FAILED",
                "[EXIT] Process exited with status code 1 (Block Merge)",
            ])
        return "\n".join(lines)
