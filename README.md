# PaperBot

A discord bot support my research. Includes RAG, Paper collection and summarize.

## 1. Structure

### 1.1 Workflow

```mermaid
graph TD
    A[Discord Commands/ Interactions] --> B[Cogs]
    B --> C[Service]
    C --> D[DB, External Repos]
    
```
