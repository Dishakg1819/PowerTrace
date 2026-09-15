"""
Proactive Green-Code Advisor Module for EcoCode
Combines Python AST analysis and regex pattern matching to detect energy anti-patterns,
idle connection leaks, and inefficient computational complexity.
"""

import ast
import re
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional


@dataclass
class CodeSmell:
    rule_id: str
    category: str
    severity: str  # HIGH, MEDIUM, LOW
    line_number: int
    line_content: str
    message: str
    recommendation: str
    green_fix_example: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class GreenAdvisor:
    """
    Static Code Heuristics Engine for Energy-Efficient Software.
    Analyzes Python source code to detect high carbon-emission anti-patterns.
    """

    RULES = {
        "ECO001": {
            "title": "Nested Loop Detected (O(N²) Complexity)",
            "category": "Algorithmic Complexity",
            "severity": "HIGH",
            "message": "Nested loops multiply CPU cycle execution exponentially, leading to severe thermal throttling and battery/grid drain.",
            "recommendation": "Refactor to O(N) using Hash Maps (dict/set), lookup tables, or vectorized array operations (NumPy).",
            "example": (
                "# ❌ Inefficient O(N²):\n"
                "for a in list_a:\n"
                "    for b in list_b:\n"
                "        if a == b: match.append(a)\n\n"
                "# ✅ Green Alternative O(N):\n"
                "set_b = set(list_b)\n"
                "match = [a for a in list_a if a in set_b]"
            )
        },
        "ECO002": {
            "title": "Inefficient DataFrame Traversal (.iterrows)",
            "category": "Data Processing",
            "severity": "HIGH",
            "message": "Calling `.iterrows()` instantiates a new Pandas Series for every single row, causing huge memory allocation churn and slow CPU execution.",
            "recommendation": "Use `.itertuples()`, column vectorization (e.g. `df['A'] + df['B']`), or `.apply()`.",
            "example": (
                "# ❌ Inefficient:\n"
                "for idx, row in df.iterrows():\n"
                "    total += row['val'] * 2\n\n"
                "# ✅ Green Vectorized:\n"
                "total = (df['val'] * 2).sum()"
            )
        },
        "ECO003": {
            "title": "Unmanaged Resource Descriptor (open() without with)",
            "category": "I/O & Memory Leaks",
            "severity": "MEDIUM",
            "message": "Opening files or sockets without a context manager leaves system file descriptors open indefinitely on exceptions, leaking memory and kernel buffers.",
            "recommendation": "Always wrap file and socket operations in `with open(...) as f:` to auto-release system handles.",
            "example": (
                "# ❌ Resource Leak:\n"
                "f = open('data.csv', 'r')\n"
                "data = f.read()\n\n"
                "# ✅ Green Context Manager:\n"
                "with open('data.csv', 'r') as f:\n"
                "    data = f.read()"
            )
        },
        "ECO004": {
            "title": "String Concatenation in Loop (+=)",
            "category": "Memory Allocation",
            "severity": "MEDIUM",
            "message": "Strings are immutable in Python. Repeated `+=` inside loops creates a new memory buffer on every iteration (O(N²) memory reallocation).",
            "recommendation": "Append string parts to a list and combine once using `''.join(parts)`.",
            "example": (
                "# ❌ Repeated reallocations:\n"
                "s = ''\n"
                "for item in data:\n"
                "    s += str(item)\n\n"
                "# ✅ Green Memory Preservation:\n"
                "s = ''.join(str(item) for item in data)"
            )
        },
        "ECO005": {
            "title": "Linear Search in Loop (item in list)",
            "category": "Algorithmic Complexity",
            "severity": "MEDIUM",
            "message": "Performing `in list` inside an iteration triggers repeated linear scans O(N × M), burning excess server CPU seconds.",
            "recommendation": "Convert the lookup target to a `set()` or `dict()` before the loop for instantaneous O(1) hash lookups.",
            "example": (
                "# ❌ O(N × M) Linear Scans:\n"
                "for item in candidates:\n"
                "    if item in large_list: ...\n\n"
                "# ✅ O(1) Instant Lookup:\n"
                "target_set = set(large_list)\n"
                "for item in candidates:\n"
                "    if item in target_set: ..."
            )
        },
        "ECO006": {
            "title": "Potential Busy Waiting Loop (while True without sleep)",
            "category": "CPU Throttling",
            "severity": "HIGH",
            "message": "A `while` loop lacking a rate-limiting `sleep` or async wait pins 100% of a CPU core, keeping hardware in maximum P-state power consumption.",
            "recommendation": "Add `time.sleep(n)` or use asynchronous event-driven triggers (`threading.Event`, `asyncio.sleep`).",
            "example": (
                "# ❌ Core Pinning:\n"
                "while not ready:\n"
                "    pass\n\n"
                "# ✅ Power Conservation:\n"
                "while not ready:\n"
                "    time.sleep(0.1)"
            )
        },
        "ECO007": {
            "title": "Unoptimized Global/Attribute Lookup inside Loop",
            "category": "Interpreter Overhead",
            "severity": "LOW",
            "message": "Repeatedly resolving global methods (e.g. `math.sin`, `list.append`) inside hot loops incurs repeated bytecode dictionary lookups.",
            "recommendation": "Localize frequently called functions into local variables or use list comprehensions.",
            "example": (
                "# ❌ Bytecode Lookups:\n"
                "res = []\n"
                "for x in data:\n"
                "    res.append(math.sqrt(x))\n\n"
                "# ✅ Localized Execution:\n"
                "sqrt = math.sqrt\n"
                "res = [sqrt(x) for x in data]"
            )
        }
    }

    def analyze_code(self, code_str: str) -> List[CodeSmell]:
        """
        Scans code using regex heuristics and AST parsing to return detected smells.
        """
        smells: List[CodeSmell] = []
        lines = code_str.splitlines()

        # 1. Regex Heuristic Checks
        for idx, line in enumerate(lines, 1):
            clean_line = line.strip()

            # Rule ECO002: Inefficient Pandas .iterrows()
            if re.search(r'\.iterrows\s*\(', line):
                smells.append(CodeSmell(
                    rule_id="ECO002",
                    category=self.RULES["ECO002"]["category"],
                    severity=self.RULES["ECO002"]["severity"],
                    line_number=idx,
                    line_content=clean_line,
                    message=self.RULES["ECO002"]["message"],
                    recommendation=self.RULES["ECO002"]["recommendation"],
                    green_fix_example=self.RULES["ECO002"]["example"]
                ))

            # Rule ECO003: open() without with
            if re.search(r'=\s*open\s*\(', line) and not re.search(r'with\s+open', line):
                smells.append(CodeSmell(
                    rule_id="ECO003",
                    category=self.RULES["ECO003"]["category"],
                    severity=self.RULES["ECO003"]["severity"],
                    line_number=idx,
                    line_content=clean_line,
                    message=self.RULES["ECO003"]["message"],
                    recommendation=self.RULES["ECO003"]["recommendation"],
                    green_fix_example=self.RULES["ECO003"]["example"]
                ))

            # Rule ECO004: String concatenation in loop
            if re.search(r'\+=\s*[\'"][^\'"]*[\'"]|\+=\s*str\(|\+=\s*[a-zA-Z_]\w*', line):
                # Check if inside an indented block
                if line.startswith("    ") or line.startswith("\t"):
                    smells.append(CodeSmell(
                        rule_id="ECO004",
                        category=self.RULES["ECO004"]["category"],
                        severity=self.RULES["ECO004"]["severity"],
                        line_number=idx,
                        line_content=clean_line,
                        message=self.RULES["ECO004"]["message"],
                        recommendation=self.RULES["ECO004"]["recommendation"],
                        green_fix_example=self.RULES["ECO004"]["example"]
                    ))

        # 2. AST Structure Checks
        try:
            tree = ast.parse(code_str)
            ast_smells = self._analyze_ast(tree, lines)
            smells.extend(ast_smells)
        except SyntaxError:
            # Code may have syntax errors, regex smells still stand
            pass

        # Deduplicate smells on same line and rule_id
        seen = set()
        deduped = []
        for s in smells:
            key = (s.rule_id, s.line_number)
            if key not in seen:
                seen.add(key)
                deduped.append(s)

        deduped.sort(key=lambda x: x.line_number)
        return deduped

    def _analyze_ast(self, tree: ast.AST, lines: List[str]) -> List[CodeSmell]:
        smells: List[CodeSmell] = []

        class EcoVisitor(ast.NodeVisitor):
            def __init__(self, rules, lines_ref):
                self.rules = rules
                self.lines = lines_ref
                self.loop_depth = 0
                self.loop_vars = []

            def visit_For(self, node: ast.For):
                self.loop_depth += 1
                if self.loop_depth >= 2:
                    line_num = getattr(node, 'lineno', 1)
                    line_str = self.lines[line_num - 1].strip() if line_num <= len(self.lines) else ""
                    smells.append(CodeSmell(
                        rule_id="ECO001",
                        category=self.rules["ECO001"]["category"],
                        severity=self.rules["ECO001"]["severity"],
                        line_number=line_num,
                        line_content=line_str,
                        message=self.rules["ECO001"]["message"],
                        recommendation=self.rules["ECO001"]["recommendation"],
                        green_fix_example=self.rules["ECO001"]["example"]
                    ))
                self.generic_visit(node)
                self.loop_depth -= 1

            def visit_While(self, node: ast.While):
                self.loop_depth += 1
                if self.loop_depth >= 2:
                    line_num = getattr(node, 'lineno', 1)
                    line_str = self.lines[line_num - 1].strip() if line_num <= len(self.lines) else ""
                    smells.append(CodeSmell(
                        rule_id="ECO001",
                        category=self.rules["ECO001"]["category"],
                        severity=self.rules["ECO001"]["severity"],
                        line_number=line_num,
                        line_content=line_str,
                        message=self.rules["ECO001"]["message"],
                        recommendation=self.rules["ECO001"]["recommendation"],
                        green_fix_example=self.rules["ECO001"]["example"]
                    ))

                # Check for while True: pass without sleep
                is_while_true = False
                if isinstance(node.test, ast.Constant) and node.test.value is True:
                    is_while_true = True
                elif isinstance(node.test, ast.NameConstant) and node.test.value is True:
                    is_while_true = True

                if is_while_true:
                    # Check if body contains any sleep
                    has_sleep = any(
                        isinstance(n, ast.Call) and (
                            (isinstance(n.func, ast.Attribute) and n.func.attr == "sleep") or
                            (isinstance(n.func, ast.Name) and n.func.id == "sleep")
                        )
                        for n in ast.walk(node)
                    )
                    if not has_sleep:
                        line_num = getattr(node, 'lineno', 1)
                        line_str = self.lines[line_num - 1].strip() if line_num <= len(self.lines) else ""
                        smells.append(CodeSmell(
                            rule_id="ECO006",
                            category=self.rules["ECO006"]["category"],
                            severity=self.rules["ECO006"]["severity"],
                            line_number=line_num,
                            line_content=line_str,
                            message=self.rules["ECO006"]["message"],
                            recommendation=self.rules["ECO006"]["recommendation"],
                            green_fix_example=self.rules["ECO006"]["example"]
                        ))

                self.generic_visit(node)
                self.loop_depth -= 1

            def visit_Compare(self, node: ast.Compare):
                # Check for `x in list` within a loop
                if self.loop_depth >= 1:
                    for op in node.ops:
                        if isinstance(op, ast.In):
                            line_num = getattr(node, 'lineno', 1)
                            line_str = self.lines[line_num - 1].strip() if line_num <= len(self.lines) else ""
                            # Only flag if lookups appear to be in variable collections (not literal sets)
                            for comparator in node.comparators:
                                if isinstance(comparator, ast.Name):
                                    smells.append(CodeSmell(
                                        rule_id="ECO005",
                                        category=self.rules["ECO005"]["category"],
                                        severity=self.rules["ECO005"]["severity"],
                                        line_number=line_num,
                                        line_content=line_str,
                                        message=self.rules["ECO005"]["message"],
                                        recommendation=self.rules["ECO005"]["recommendation"],
                                        green_fix_example=self.rules["ECO005"]["example"]
                                    ))
                self.generic_visit(node)

        visitor = EcoVisitor(self.RULES, lines)
        visitor.visit(tree)
        return smells

    def compute_green_score(self, smells: List[CodeSmell], loc: int) -> Dict[str, Any]:
        """
        Computes a Green Code Score (0 - 100) and Letter Grade (A+, A, B, C, D, F)
        based on total lines of code and smell penalties.
        """
        base_score = 100
        penalties = {
            "HIGH": 20,
            "MEDIUM": 10,
            "LOW": 5
        }

        total_penalty = 0
        severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}

        for s in smells:
            total_penalty += penalties.get(s.severity, 5)
            severity_counts[s.severity] = severity_counts.get(s.severity, 0) + 1

        final_score = max(0, min(100, base_score - total_penalty))

        if final_score >= 95:
            grade = "A+"
            color = "#10b981"  # Emerald
            status = "Eco-Certified: Ultra Clean"
        elif final_score >= 85:
            grade = "A"
            color = "#34d399"
            status = "Green-Approved: Highly Optimized"
        elif final_score >= 70:
            grade = "B"
            color = "#38bdf8"  # Cyan
            status = "Moderate: Minor Efficiency Smells"
        elif final_score >= 50:
            grade = "C"
            color = "#f59e0b"  # Amber
            status = "Sub-Optimal: Energy Waste Present"
        elif final_score >= 30:
            grade = "D"
            color = "#f97316"  # Orange
            status = "Inefficient: Heavy CPU/Memory Drain"
        else:
            grade = "F"
            color = "#ef4444"  # Red
            status = "Severe Carbon Regression: Refactoring Needed"

        return {
            "score": final_score,
            "grade": grade,
            "color": color,
            "status": status,
            "total_smells": len(smells),
            "severity_counts": severity_counts,
            "lines_of_code": loc
        }
