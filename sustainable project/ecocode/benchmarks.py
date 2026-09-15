"""
Pre-configured A/B Algorithm Benchmarks for EcoCode
Provides ready-to-run side-by-side code pairs demonstrating dramatic energy reductions.
"""

from typing import Dict, Any

BENCHMARK_SUITES: Dict[str, Dict[str, Any]] = {
    "lookup_challenge": {
        "title": "🔍 Lookup Challenge: Linear Search vs Hash Set O(1)",
        "description": "Searches for 5,000 items in a dataset of 20,000 records. Demonstrates the extreme carbon cost of O(N) linear scanning versus O(1) hash lookups.",
        "baseline_label": "Baseline: Linear List Scan O(N)",
        "optimized_label": "Optimized: Hash Set Lookup O(1)",
        "code_a": """# ❌ Baseline: Linear Search (O(N) search on list)
data_pool = list(range(20000))
queries = list(range(1000, 6000))

matches = []
for q in queries:
    if q in data_pool:  # O(N) linear scan on list every time
        matches.append(q)

print(f"Total matches found: {len(matches)}")
""",
        "code_b": """# ✅ Optimized: Hash Set Lookup (O(1) search)
data_pool = set(range(20000))  # O(1) membership test
queries = list(range(1000, 6000))

# Instant O(1) lookups
matches = [q for q in queries if q in data_pool]

print(f"Total matches found: {len(matches)}")
""",
    },
    "matrix_nested_loop": {
        "title": "🧮 Nested Loops vs List Comprehension / Vector Math",
        "description": "Performs element-wise pair distance computation across coordinate lists. Highlights exponential O(N²) thermal drain vs optimized vector comprehension.",
        "baseline_label": "Baseline: O(N²) Nested Loops",
        "optimized_label": "Optimized: Flattened Comprehension",
        "code_a": """# ❌ Baseline: Nested Loops O(N²)
coords_x = list(range(500))
coords_y = list(range(500))

pairs = []
for x in coords_x:
    for y in coords_y:
        if (x + y) % 7 == 0:
            pairs.append((x, y))

print(f"Total pairs: {len(pairs)}")
""",
        "code_b": """# ✅ Optimized: Filtered Generator Comprehension
coords_x = range(500)
coords_y = range(500)

# Memory-efficient flat comprehension
pairs = [(x, y) for x in coords_x for y in coords_y if (x + y) % 7 == 0]

print(f"Total pairs: {len(pairs)}")
""",
    },
    "string_concatenation": {
        "title": "🧵 String Builder: 's += chunk' vs ''.join()",
        "description": "Constructs a large serialized payload from 30,000 tokens. Illustrates repeated memory buffer re-allocations vs single-pass buffer join.",
        "baseline_label": "Baseline: In-Place Concatenation (+=",
        "optimized_label": "Optimized: Single-Pass ''.join()",
        "code_a": """# ❌ Baseline: String concatenation in loop
tokens = [f"token_{i}," for i in range(30000)]

result = ""
for t in tokens:
    result += t  # Re-allocates string memory buffer on every iteration

print(f"Total length: {len(result)}")
""",
        "code_b": """# ✅ Optimized: List buffer + single join
tokens = [f"token_{i}," for i in range(30000)]

# Pre-allocates single buffer
result = "".join(tokens)

print(f"Total length: {len(result)}")
""",
    },
    "dataframe_iteration": {
        "title": "📊 Data Processing: Iterative Row Scan vs Vector Math",
        "description": "Calculates tax and discount adjustments on 20,000 transaction records. Compares row-by-row iteration against list comprehension vectorization.",
        "baseline_label": "Baseline: Row-by-Row Iteration",
        "optimized_label": "Optimized: Vectorized Calculation",
        "code_a": """# ❌ Baseline: Iterative calculation simulating .iterrows()
records = [{"price": i, "tax_rate": 0.18, "discount": 0.05} for i in range(25000)]

net_totals = []
for item in records:
    # Multiple dictionary lookups and manual arithmetic
    net = (item["price"] * (1 + item["tax_rate"])) * (1 - item["discount"])
    net_totals.append(net)

print(f"Processed items: {len(net_totals)}, Sum: {sum(net_totals):.2f}")
""",
        "code_b": """# ✅ Optimized: Fast single-pass list comprehension
records = [{"price": i, "tax_rate": 0.18, "discount": 0.05} for i in range(25000)]

# Pre-calculated multiplier factor
factor = 1.18 * 0.95
net_totals = [item["price"] * factor for item in records]

print(f"Processed items: {len(net_totals)}, Sum: {sum(net_totals):.2f}")
""",
    }
}
