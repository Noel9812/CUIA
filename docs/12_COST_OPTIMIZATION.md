# 12. Cost Optimization

Running Large Language Models (like AWS Bedrock) is expensive and slow. CUIA is architected specifically to minimize token usage and LLM invocations.

## Architectural Principle: Determinism First

The core philosophy of CUIA's cost optimization is: **Do not send every question to the LLM.**

## 1. Zero-Model Intent Classification
- Over 90% of user queries can be routed to the correct tool without invoking an LLM.
- The `intent_classifier.py` uses a fast, deterministic weighted keyword algorithm.
- If a user asks "What is Team Alpha's utilization?", the system scores the keywords "utilization", detects the `analytics` intent, and routes it immediately. Cost: $0.
- **LLM Fallback:** Only if the keyword scores are ambiguous (e.g., a tie) does the system make a tiny, 0-temperature LLM call to classify the intent.

## 2. Zero-Model Entity Extraction
- Extracting teams, engineers, or sprints from a query ("Team Alpha", "Sprint 42") is done using exact/fuzzy string matching against the loaded dataset in `entity_extractor.py`. Cost: $0.

## 3. Conversational Deflection
- Conversational queries like "Hello", "Who are you?", or malicious queries ("Ignore instructions") are detected deterministically and routed to an `END` state with a hardcoded response. Cost: $0.

## 4. Extreme Context Minimization
- The most expensive part of RAG (Retrieval-Augmented Generation) is the context window.
- If a user asks about "Team Alpha", sending the entire organization's dataset to the LLM wastes tokens.
- The `ContextBuilder` dynamically filters the pre-computed analytics. It isolates only Team Alpha's data, strips out unnecessary JSON keys, and removes whitespace (`json.dumps(data, separators=(",", ":"))`). 
- This reduces the prompt payload from potentially 50,000 tokens down to ~300 tokens.

## Total Cost Profile
For a standard query:
1. Intent Classification: 0 tokens
2. Entity Extraction: 0 tokens
3. Context Building: 0 tokens
4. Explanation Generation: ~400 input tokens, ~100 output tokens.

By pushing all heavy lifting to standard Python execution, CUIA achieves enterprise-grade analytics at a fraction of the cost of a naive Agentic system.
