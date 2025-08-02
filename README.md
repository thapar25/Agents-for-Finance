# Agents-for-Finance

Research Agent(s) to perform Qualitative Analysis and construct Financial Forecast Report.

## Current Implementation

### General Tool Calling Agent

`route: POST /chat`






# Possible Approaches

<details>

<summary>A brief breakdown of all possible approaches</summary>

## Single Agent [✅ Implemented as API]
- One tool to extract financial metrics from Press Releases
- Another tool to extract statements and forward outlook statements from Earning Call transcripts
    - Autonomy : Low
    - No fixed structured output


## Indexed documents + Preset Workflow [WIP]
- Preset steps in a workflow, ensemble retrieval, reflections
    - Controlled Research (higher token usage, more time, higher calls/min)
    - Presets allow well-structured sections and output parsing
    - Needs domain expertise
    - Relies on indexed data
    - Autonomy : Medium



## Multi-agent (with reflection) [WIP]
- Planner creates a detailed plan with `to-do` as a list of jsons with a boolean.
- Manager looks at the plan and assigns the worker/research agent with one task at a time (one todo), and tracks progress (chnages the bool values).
- Worker uses tools to search vector DB collections for information and drafts sections.
- Manager puts it all together and throws it to a reviewer for critiqing.
- Criticism goes to manager who can decide to directly go to worker or to planner based on the review.
- Reviewer here can be either another LLM or a human-in-the-loop.
    
    - Context Isolation
    - Read [deep agents](https://blog.langchain.com/deep-agents/) implementation inspired by [article](https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html)
    - Autonomy : High


## Google Search + Simple Reflection
- Single tool -> Google Search
    - Uses search results as ground truth (less complex RAG)
    - Always upto date
    - Faster
    - Wider range of responses
    - Autonomy : High

</details>

## Steps to setup vector DB:

### First Run (To Restore the Snapshot):
```bash
docker-compose up --build
```
Qdrant will start, see the --storage-snapshot flag, load your snapshot file, and save the data into the qdrant_data volume. Wait for all services to be up and running.

### Subsequent Runs (Normal Operation):
Stop the containers: docker-compose down.
Edit your docker-compose.yml and comment out or delete the command line from the qdrant service.

```dockerfile
# In your docker-compose.yml
qdrant:
  image: qdrant/qdrant
  ports:
    - "6333:6333"
  # command: ["./qdrant", "--storage-snapshot", "/qdrant/snapshots/snapshot-file-name.snapshot"] # <-- COMMENT THIS OUT
  volumes:
    - ./snapshots:/qdrant/snapshots
    - qdrant_data:/qdrant/storage
  environment:
    - QDRANT__HTTP__HOST=0.0.0.0
```
From now on, start your services normally.
```bash
docker-compose up
```
Qdrant will now start much faster because it will load its data directly from the persistent qdrant_data volume where your snapshot data already exists.