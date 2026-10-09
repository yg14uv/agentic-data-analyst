# Agentic Data Analyst



An end-to-end agentic AI application that allows users to ask business data questions in natural language and receive grounded answers generated from a real SQL database.



The system uses LLM tool calling, metadata retrieval, vector search, SQL execution, retry/self-correction, session memory, and LLM-based evaluation to build a more reliable data analysis agent.



---


## Architecture

![Agentic Data Analyst Architecture](docs/architecture.png)

## Overview



Instead of asking users to write SQL manually, this application allows questions such as:



```text

How much money did we make in Canada?

