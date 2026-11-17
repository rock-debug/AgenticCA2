# 2-Minute Video Walkthrough Script & Presentation Guide
## CSE476: Agentic AI and Intelligent Automation — Task 2 Project
**Project:** Group 16 — Automated Academic Research Assistant Team (Group of 3 Configuration)  
**Architecture:** Pipeline with RAG and a Critic Architecture  
**Target Duration:** ~2 Minutes (120 Seconds / ~260–280 words at natural speaking pace)

---

## ⏱️ Video Timeline & Screen Breakdown

```
[0:00 - 0:20] 🎙️ Introduction, Problem Statement & Framework
[0:20 - 0:50] 🧩 Architecture & 6-Agent Roster (Tools + Critic + Contradiction)
[0:50 - 1:30] 💻 Live UI Demonstration (Pipeline Stepper, Citations & Critic Test Mode)
[1:30 - 2:00] 🛡️ Contradiction Dossier, Append-Only Run Log, Pytest & Conclusion
```

---

### [0:00 – 0:20] Hook, Introduction & The Problem
**📺 Screen:** Open the browser at `http://127.0.0.1:5000/academic-team` showing the title banner and the 6-agent visual pipeline cards.

> **Voiceover:**  
> *"Hello everyone. Today I'm presenting our CSE476 Task 2 project for **Group 16: The Automated Academic Research Assistant Team**, built using **Microsoft Semantic Kernel** in Python.  
> Standard monolithic language models suffer from catastrophic context dilution and hallucinations when reviewing academic literature. To solve this, we designed a **Pipeline with RAG and a Critic Architecture** that decomposes research questions, grounds retrieval in an academic corpus, and enforces strict adversarial claim verification before publication."*

---

### [0:20 – 0:50] Architecture & 6 Specialized Agents
**📺 Screen:** Mouse hover across the 6 pipeline cards (`Query Agent` &rarr; `Retrieval Agent` &rarr; `Summary Agent` &rarr; `Fact-Check Agent (Critic)` &rarr; `Contradiction Agent` &rarr; `Writer Agent`).

> **Voiceover:**  
> *"Our system coordinates six modular agents, each calling at least two real plain Python tools decorated with `@kernel_function`:  
> 1. The **Query Agent** breaks complex inquiries into targeted search sub-queries and expands domain lexicon.  
> 2. The **Retrieval Agent** executes TF-IDF and semantic RAG across our paper corpus, tagging passages as `[P1]`, `[P2]`.  
> 3. The **Summary Agent** clusters evidence into thematic findings.  
> 4. The **Fact-Check Agent** acts as our **Critic Gate**, auditing proposition entailment and token overlap to reject hallucinations.  
> 5. As our **Group of 3 extension**, the **Contradiction Agent** actively detects empirical disagreements between authors.  
> 6. Finally, the **Writer Agent** prunes ungrounded claims and compiles the final verified report."*

---

### [0:50 – 1:30] Live Demonstration & Critic Verification
**📺 Screen:**  
1. Select the preset question: *"Compare centralized orchestration vs decentralized blackboard architectures for autonomous agent systems."*  
2. Toggle ON the **"Critic Test Mode"** switch (to demonstrate hallucination pruning).  
3. Click **"Execute Multi-Agent Pipeline"**.  
4. Show the results tabs.

> **Voiceover:**  
> *"Let's see this in action. I'll select an inquiry comparing centralized orchestrators with decentralized blackboards, and toggle on our **Critic Test Mode**, which injects a synthetic ungrounded claim.  
> In under 20 milliseconds, the pipeline executes.  
> Here in the **Final Literature Review**, every sentence is explicitly mapped to a verified citation tag.  
> When we click into the **Critic Audit Ledger**, notice how our Fact-Check Critic immediately flagged the injected claim as `UNSUPPORTED` because it lacked grounded evidence, pruning it completely from the final text."*

---

### [1:30 – 2:00] Contradiction Analysis, Append-Only Log & Wrap-Up
**📺 Screen:**  
1. Click the **"Contradiction Dossier"** tab (showing Position A by Chen et al. vs Position B by Weber et al.).  
2. Switch briefly to VS Code showing `run_log.jsonl`, `demo.ipynb`, and `pytest tests/test_academic_agents.py` passing 100%.

> **Voiceover:**  
> *"In the **Contradiction Dossier**, rather than arbitrarily picking one side, the agent presents both perspectives side-by-side: David Chen's case for decentralized blackboards versus Alexander Weber's proof for centralized orchestrators with formal SLA guarantees.  
> Every execution is recorded in our append-only log, `run_log.jsonl`, and all three required rubric scenarios pass at 100% in Pytest.  
> This delivers a fully grounded, transparent, and defensible multi-agent system. Thank you!"*

---

## 💡 Quick Tips for Recording
- **Resolution:** Record at 1080p (Full HD) with your browser zoomed to 110% so text and citation tags are crisp.
- **Pace:** Speak at a calm, confident pace. 120 seconds gives you plenty of time if you follow the timestamps.
- **Key Viva Keywords to Emphasize:** *Pipeline with RAG and Critic Architecture*, *Microsoft Semantic Kernel*, *Adversarial Fact-Check Gate*, *Dual-Perspective Contradiction Analysis*, *Append-Only Run Log*.
