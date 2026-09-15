"""
Hardware-Agnostic Proxy Profiler Module for EcoCode
Quantifies execution duration, energy consumption (kWh), carbon emissions (kgCO2e),
and electricity cost (INR) from simulated cloud server CPU workloads.
"""

import sys
import io
import time
import tracemalloc
import traceback
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any


@dataclass
class ProfileResult:
    success: bool
    execution_time_sec: float
    energy_kwh: float
    carbon_kg_co2: float
    carbon_g_co2: float
    cost_inr: float
    peak_memory_kb: float
    stdout: str
    error: Optional[str] = None
    
    # Real-world impact equivalents
    smartphone_charges: float = 0.0
    led_bulb_hours: float = 0.0
    car_km_equivalent: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CodeProfiler:
    """
    Hardware-Agnostic Proxy Profiler.
    Maps execution time to energy, carbon, and financial metrics.
    """
    def __init__(
        self,
        server_power_watts: float = 100.0,      # Default cloud server power: 100W (0.1 kW)
        grid_intensity_factor: float = 0.8,    # kg CO2e per kWh
        electricity_rate_inr: float = 8.0,      # INR per kWh
    ):
        self.server_power_watts = server_power_watts
        self.server_power_kw = server_power_watts / 1000.0
        self.grid_intensity_factor = grid_intensity_factor
        self.electricity_rate_inr = electricity_rate_inr

    def calculate_metrics(self, execution_time_sec: float, peak_memory_kb: float = 0.0) -> Dict[str, float]:
        """
        Quantification Formulas as defined in PDR:
        - Energy (kWh) = (T / 3600) * (Power in kW)
        - Carbon Footprint (kgCO2e) = Energy (kWh) * Grid Intensity (0.8)
        - Financial Cost (₹) = Energy (kWh) * Rate (₹8/kWh)
        """
        # Energy in kWh
        energy_kwh = (execution_time_sec / 3600.0) * self.server_power_kw
        
        # Carbon in kgCO2e and grams
        carbon_kg_co2 = energy_kwh * self.grid_intensity_factor
        carbon_g_co2 = carbon_kg_co2 * 1000.0
        
        # Financial cost in INR
        cost_inr = energy_kwh * self.electricity_rate_inr
        
        # Tangible environmental equivalents:
        # 1 smartphone full charge consumes approx ~0.012 kWh (12 Wh)
        smartphone_charges = energy_kwh / 0.012 if energy_kwh > 0 else 0.0
        # 10W LED bulb 1 hour = 0.01 kWh
        led_bulb_hours = energy_kwh / 0.01 if energy_kwh > 0 else 0.0
        # Average petrol passenger car emits ~0.12 kg CO2e per km
        car_km_equivalent = carbon_kg_co2 / 0.12 if carbon_kg_co2 > 0 else 0.0

        return {
            "energy_kwh": energy_kwh,
            "carbon_kg_co2": carbon_kg_co2,
            "carbon_g_co2": carbon_g_co2,
            "cost_inr": cost_inr,
            "peak_memory_kb": peak_memory_kb,
            "smartphone_charges": smartphone_charges,
            "led_bulb_hours": led_bulb_hours,
            "car_km_equivalent": car_km_equivalent,
        }

    def execute_and_profile(self, code_str: str, repeat: int = 1) -> ProfileResult:
        """
        Executes Python code in an isolated scope, recording execution time
        and peak memory delta.
        """
        # Prepare environment
        execution_scope: Dict[str, Any] = {
            "__name__": "__main__",
            "__builtins__": __builtins__,
        }
        
        # Redirect stdout and stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        redirected_stdout = io.StringIO()
        redirected_stderr = io.StringIO()

        tracemalloc.start()
        start_time = time.perf_counter()
        error_msg = None
        success = True

        try:
            sys.stdout = redirected_stdout
            sys.stderr = redirected_stderr
            
            # Precompile to isolate syntax checks
            compiled_code = compile(code_str, "<ecocode_runner>", "exec")
            
            for _ in range(max(1, repeat)):
                exec(compiled_code, execution_scope)
                
        except Exception as ex:
            success = False
            error_msg = f"{type(ex).__name__}: {str(ex)}\n\n{traceback.format_exc()}"
        finally:
            end_time = time.perf_counter()
            _, peak_bytes = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        raw_duration = max(0.000001, (end_time - start_time) / max(1, repeat))
        peak_kb = peak_bytes / 1024.0
        stdout_content = redirected_stdout.getvalue()
        stderr_content = redirected_stderr.getvalue()
        combined_output = stdout_content
        if stderr_content:
            combined_output += f"\n[stderr]:\n{stderr_content}"

        metrics = self.calculate_metrics(raw_duration, peak_kb)

        return ProfileResult(
            success=success,
            execution_time_sec=raw_duration,
            energy_kwh=metrics["energy_kwh"],
            carbon_kg_co2=metrics["carbon_kg_co2"],
            carbon_g_co2=metrics["carbon_g_co2"],
            cost_inr=metrics["cost_inr"],
            peak_memory_kb=metrics["peak_memory_kb"],
            stdout=combined_output,
            error=error_msg,
            smartphone_charges=metrics["smartphone_charges"],
            led_bulb_hours=metrics["led_bulb_hours"],
            car_km_equivalent=metrics["car_km_equivalent"],
        )
