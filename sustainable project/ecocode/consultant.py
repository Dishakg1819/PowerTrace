"""
GreenConsultant: AI Chatbot backend for EcoCode powered by Google Gemini 
with built-in offline GreenOps fallback heuristics and domain-boundary enforcement.
"""

import os
from typing import Optional

SYSTEM_PROMPT = """You are EcoCode GreenConsultant, an elite AI advisor specialized strictly in Sustainable Software Engineering, Green Computing, and Cloud Resource Optimization (EcoCode PS 5.3).

YOUR MANDATE:
1. ONLY answer questions related to green coding, software energy profiling, carbon accounting, algorithmic time-complexity (Big-O), memory management, and GreenOps CI/CD pipelines.
2. NEVER give lavish, broad, or general chatbot responses (e.g., writing poetry, discussing movies, or general programming unrelated to software energy efficiency).
3. BOUNDARY ENFORCEMENT: If a user asks something outside the scope of green computing or this platform, you MUST politely decline and offer a direct alternative related to EcoCode features.
4. Provide crisp, actionable, and mathematically grounded advice. Include refactored code snippets where applicable."""

KNOWLEDGE_BASE = [
    {
        "keywords": ["nested", "loop", "o(n^2)", "complexity", "quadratic", "slow"],
        "topic": "Algorithmic Complexity & Loop Optimization",
        "answer": (
            "### 🌿 Optimizing Nested Loops (O(N²) ➔ O(N))\n\n"
            "**The Problem**: Nested loops force the CPU to execute $N \\times M$ iterations. On modern server cores, this spikes power draw from an idle ~15W to 120W+ peak TDP.\n\n"
            "**Key Remediation Strategies**:\n"
            "1. **Hash Maps / Sets**: Replace the inner linear search with a Python `set` or `dict` for instantaneous $O(1)$ membership checks.\n"
            "2. **Vectorization**: In numerical pipelines, replace Python loops with NumPy or Polars SIMD vector instructions.\n"
            "3. **Early Exit**: If you must loop, use `break` immediately once conditions are satisfied to cut unnecessary cycles."
        )
    },
    {
        "keywords": ["pandas", "iterrows", "itertuples", "dataframe", "dataframe loop"],
        "topic": "Pandas & DataFrame Efficiency",
        "answer": (
            "### 🌿 Pandas Traversal: Slashing DataFrame Carbon\n\n"
            "**The Problem**: `.iterrows()` creates a Python Series object on every row step. For 100k rows, that's 100k allocations!\n\n"
            "**Energy Hierarchy (Slowest ➔ Greenest)**:\n"
            "- ❌ `.iterrows()`: ~100x slower, maximum CPU burn.\n"
            "- ⚠️ `.apply(func)`: Faster, but still loops under the hood.\n"
            "- 🌿 `.itertuples()`: ~10x faster than iterrows (yields namedtuples).\n"
            "- ⚡ **Vectorized column ops (`df['A'] * df['B']`)**: 100x–500x faster, running in compiled C/BLAS with minimal energy."
        )
    },
    {
        "keywords": ["memory", "ram", "leak", "tracemalloc", "footprint", "allocation"],
        "topic": "Memory Footprint Reduction",
        "answer": (
            "### 🌿 Memory Optimization & Carbon Impact\n\n"
            "**How Memory Affects Energy**: RAM requires constant refresh cycles (~3W per 8GB stick). High allocations trigger Python's Garbage Collector (GC), pausing execution and driving up CPU utilization.\n\n"
            "**Green Practices**:\n"
            "1. **Use Generators**: Replace `[x for x in data]` with `(x for x in data)` for lazy evaluation.\n"
            "2. **`__slots__`**: On class instances, defining `__slots__` eliminates `__dict__` overhead, saving up to 40% RAM.\n"
            "3. **Memory Views & Buffers**: Use `memoryview()` or `bytearray` when processing binary streams to avoid deep copies."
        )
    },
    {
        "keywords": ["ci/cd", "gate", "github action", "pipeline", "regression", "baseline"],
        "topic": "GreenOps CI/CD Gatekeeping",
        "answer": (
            "### 🌿 GreenOps CI/CD Integration\n\n"
            "**Why Pipeline Gates Matter**: 80% of software carbon is baked in during feature addition. Without automated gates, energy regressions silently reach production clusters.\n\n"
            "**Recommended Thresholds**:\n"
            "- **Max Allowed Regression**: `+5%` to `+10%` on core microservices.\n"
            "- **Automated PR Bot**: Post transparent metric diffs (Execution Time, kWh, ₹) on every Pull Request.\n"
            "- **Nightly Baselines**: Refresh `baseline.json` on tagged production releases."
        )
    },
    {
        "keywords": ["cloud", "aws", "gcp", "azure", "serverless", "cost", "inr", "region"],
        "topic": "Cloud Sustainability & Carbon-Aware Computing",
        "answer": (
            "### 🌿 Carbon-Aware Cloud Architecture\n\n"
            "1. **Grid Carbon Intensity**: Schedule heavy batch jobs in data center regions powered by renewable energy (e.g., Sweden, Oregon, or Finland vs fossil-heavy regions).\n"
            "2. **Scale to Zero**: Use Serverless or auto-scaled node pools to eliminate idle watt draw.\n"
            "3. **Right-Sizing**: Downgrade instances with < 20% average CPU utilization to reduce idle energy overhead."
        )
    }
]

# Strict whitelist of domain terms for boundary enforcement in offline mode
DOMAIN_KEYWORDS = [
    "green", "code", "python", "energy", "carbon", "cpu", "memory", "ram", "loop", 
    "pandas", "dataframe", "ci/cd", "pipeline", "optimization", "optimizer", "profiler", 
    "algorithm", "big-o", "time", "cost", "cloud", "server", "watt", "kwh", "gatekeeper",
    "baseline", "regression", "performance", "speed", "refactor", "software", "computing", "json", "docker", "container"
]

class GreenConsultant:
    """
    Intelligent GreenOps Chatbot Consultant.
    Provides answers using built-in knowledge retrieval and optional Gemini API integration,
    enforcing strict project scoping and domain boundaries.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        self.gemini_client = None

        if self.api_key and self.api_key.strip():
            try:
                # Attempting connection via modern Google GenAI library
                from google import genai
                self.gemini_client = genai.Client(api_key=self.api_key.strip())
            except Exception:
                try:
                    # Fallback configuration for legacy google-generativeai package if installed
                    import google.generativeai as legacy_genai
                    legacy_genai.configure(api_key=self.api_key.strip())
                    self.legacy_model = legacy_genai.GenerativeModel('gemini-1.5-flash')
                except Exception:
                    self.gemini_client = None

    def ask(self, user_query: str, context: Optional[str] = None) -> str:
        """
        Processes a user question about green software engineering with strict domain boundaries.
        """
        query_lower = user_query.lower()

        # Check if query is within domain keywords
        is_in_domain = any(kw in query_lower for kw in DOMAIN_KEYWORDS)
        
        # Check matching knowledge base items
        matched_answers = []
        for item in KNOWLEDGE_BASE:
            score = sum(1 for kw in item["keywords"] if kw in query_lower)
            if score > 0:
                matched_answers.append((score, item["answer"]))

        # Boundary enforcement for offline mode if query is completely unrelated
        if not self.gemini_client and not getattr(self, 'legacy_model', None) and not is_in_domain and not matched_answers:
            return (
                "⚠️ **Out-of-Scope Query Detected**\n\n"
                f"I am **EcoBot**, strictly dedicated to **EcoCode (PS 5.3)** software energy profiling, "
                "carbon accounting, and GreenOps optimization. I cannot assist with queries outside this domain.\n\n"
                "**Suggested Alternatives:**\n"
                "* Ask me: *'How do nested loops impact CPU energy and thermal TDP?'*\n"
                "* Ask me: *'Why is Pandas .iterrows() bad for carbon footprint and how do I fix it?'*\n"
                "* Ask me: *'How does the CI/CD Gatekeeper prevent energy regressions?'*\n"
                "* Switch to the **Green-Code Advisor** tab to inspect your Python code for anti-patterns."
            )

        # If Gemini client (modern) is available
        if self.gemini_client:
            try:
                prompt = user_query
                if context:
                    prompt = f"Recent Profiling Context:\n{context}\n\nUser Question:\n{user_query}"

                response = self.gemini_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config={"system_instruction": SYSTEM_PROMPT}
                )
                if response and response.text:
                    return response.text
            except Exception:
                pass

        # If legacy model client is available
        if getattr(self, 'legacy_model', None):
            try:
                full_prompt = f"{SYSTEM_PROMPT}\n\nUser Question: {user_query}"
                response = self.legacy_model.generate_content(full_prompt)
                if response and response.text:
                    return response.text
            except Exception:
                pass

        # Built-in Domain Knowledge Retrieval Fallback
        if matched_answers:
            matched_answers.sort(key=lambda x: x[0], reverse=True)
            return matched_answers[0][1]

        # General EcoCode response if in-domain but no specific KB match
        return (
            f"### 🌿 EcoCode GreenOps Advisor Insight\n\n"
            f"Regarding your query on **\"{user_query}\"**:\n\n"
            f"- **Core Principle**: Software energy consumption is directly proportional to CPU cycle duration and memory bus transactions.\n"
            f"- **Formula Reference**:\n"
            f"  - $\\text{{Energy (kWh)}} = (T / 3600) \\times 0.1\\text{{ kW}}$\n"
            f"  - $\\text{{Carbon (kgCO}}_2\\text{{e)}} = \\text{{Energy}} \\times 0.8$\n"
            f"- **Quick Tip**: Run your code through the **Container Profiler** or the **Green-Code Advisor** tab to detect $O(N^2)$ loops, `.iterrows()` anti-patterns, or unclosed file handles!"
        )