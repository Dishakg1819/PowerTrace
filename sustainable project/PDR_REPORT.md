# 📋 Product Development Report (PDR)
## Project Title: EcoCode — Software Energy Profiler, Algorithm Scoreboard & GreenOps CI/CD Gatekeeper
**Problem Statement**: PS 5.3 — Software Energy Profiler & Green-Code Advisor  
**Target Domain**: Green Computing, Sustainable Software Engineering, Cloud Optimization, DevOps CI/CD Automation

---

## 1. Executive Summary
Modern software engineering focuses extensively on runtime performance and feature delivery, largely overlooking the physical energy consumption and carbon footprint of code execution. **EcoCode** is an integrated software sustainability platform designed to measure, quantify, and automatically optimize software resource footprints. By utilizing a hardware-agnostic proxy profiler, a rule-based Green-Code static advisor, an A/B algorithm performance scoreboard, and an automated CI/CD regression guard, EcoCode empowers developers to visualize and slash energy waste instantly.

---

## 2. Problem Statement & Background
- **The Problem**: Computers consume electricity to execute programs. Inefficient coding patterns (such as $O(N^2)$ nested loops, unoptimized data frame lookups, and unclosed connection handles) cause processors to work harder and longer than necessary, driving up data center power grids, cloud computing infrastructure bills, and carbon dioxide ($\mathrm{CO}_2$) emissions.
- **The Gap**: Traditional profilers require low-level kernel hooks, root permissions, or expensive hardware modules (e.g., Intel RAPL). Developers lack an intuitive, developer-friendly tool that bridges raw code execution with tangible environmental impact ($\text{kWh}$, $\text{kgCO}_2\text{e}$, $\text{₹}$) and stops energy regressions proactively before reaching production.

---

## 3. Core Product Features & Innovation

### A. Hardware-Agnostic Proxy Profiler
- **Functionality**: Measures code execution time ($T$ in seconds) via isolated script execution and maps it mathematically to a simulated cloud server CPU workload profile (~100 Watts / 0.1 kW load).
- **Quantification Formulas**:
  $$\text{Energy (kWh)} = \left(\frac{T}{3600}\right) \times 0.1\text{ kW}$$
  $$\text{Carbon Footprint (kgCO}_2\text{e)} = \text{Energy (kWh)} \times \text{Grid Intensity Factor (0.8)}$$
  $$\text{Financial Cost (₹)} = \text{Energy (kWh)} \times \text{Commercial Rate (₹8/kWh)}$$

### B. Proactive Green-Code Advisor (Static Heuristics)
- **Functionality**: Scans Python source code using regular expressions and AST analysis to flag code smells and resource-heavy anti-patterns.
- **Checks & Remediation**:
  - Detects nested loops ($O(N^2)$ time complexity) and recommends vectorization or hash maps.
  - Identifies unoptimized data parsing anti-patterns (e.g., Pandas `.iterrows()`) and suggests `.apply()` or vectorization.
  - Flags missing context managers (`open()` without `with`) to prevent idle connection leaks.
  - Flags repeated string concatenation (`+=`) inside loops and suggests `str.join()`.
  - Flags linear lookups inside loops (`item in list`) and suggests `set()` lookups.

### C. Live A/B Algorithm Scoreboard & Charts
- **Functionality**: Allows users to run side-by-side performance comparisons of two distinct code approaches addressing the same business problem (e.g., Linear Search vs. Direct Hash Lookups).
- **Impact Visualizer**: Renders an interactive bar chart and exact percentage delta metrics to prove live how optimized code drastically reduces power consumption.

### D. AI Green Consultant Chatbot
- **Functionality**: Integrates an interactive contextual AI assistant trained on green-coding standards. It answers developer queries regarding memory footprint reduction, algorithmic optimization, and cloud cost control based on recent profile runs.
- **Architecture**: Domain expert heuristics engine + optional Google Gemini 2.5 Flash API connection.

### E. CI/CD Pipeline Energy Guard (Regression Gatekeeper)
- **Functionality**: Acts as an automated GitHub Action simulation. It compares a pull request's energy metrics against a saved production baseline (`baseline.json`).
- **Automated Logic**: If a code change increases energy consumption by more than 10%, the pipeline automatically fails, blocks the merge, and generates a detailed PR comment with suggested fixes.

---

## 4. Proposed Architecture & Workflow

```
[User Code Input (Text Area / PR Hook)] 
       │
       ├──> [Static Regex / AST Parser] ───> [Green-Code Advisor Tips & Score]
       │
       ├──> [Execution Time Profiler] ─────> [Math Proxy Engine (kWh, kgCO2e, ₹)]
       │
       └──> [CI/CD Baseline Comparer] ─────> [PASS / FAIL Gate & PR Block]
```

- **Input Layer**: Interactive Streamlit web interface supporting live text inputs, script uploads, benchmark presets, and module navigation.
- **Analysis & Simulation Engine**: Core Python backend executing dynamic sandboxed evaluation (`exec()`), timing metrics, and metric modeling.
- **Output & Enforcement Interface**: Real-time metrics dashboard, visual comparison bar charts, AI consultation chat panels, and pipeline build failure states.

---

## 5. Hackathon Sprint Impact & Feasibility
- **Rapid MVP Delivery**: Built completely within a rapid sprint window using native Python modules (`time`, `re`, `sys`, `io`, `tracemalloc`, `ast`) and Streamlit, eliminating heavy dependencies or complex installations.
- **Judge Appeal**: Combines technical accuracy with intuitive visualization. The inclusion of the CI/CD Pipeline Guard and A/B Scoreboard demonstrates clear enterprise readiness and real-world commercial viability.
