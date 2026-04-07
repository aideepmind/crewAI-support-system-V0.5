YOU ARE OPERATING IN STRICT PROJECT GOVERNANCE MODE.

====================================
GLOBAL NON-NEGOTIABLE RULES
====================================

1. LOGGING (MANDATORY)
For every user interaction and every action you take, you MUST append
a log entry to:
.claude/logs/session-<current-session>.log

Each log entry MUST include:
- Timestamp
- User input (verbatim)
- AI interpretation / plan
- Actions taken
- Files affected (created / modified / deleted)
- Output location (if any)
- Classification

------------------------------------

2. FILE TRACEABILITY (MANDATORY)
Whenever you create or modify a program file, you MUST update:
.claude/artifacts/code_index.md

Each entry must include:
- File path
- Purpose
- Role / responsibility
- Created or modified date
- Related task

------------------------------------

3. OUTPUT KEYWORD RULE ("tomd")
If the user instruction contains the keyword "tomd":
- Output MUST be written to a Markdown file
- Place it under /docs or /outputs
- Do NOT print full content in chat
- Record output path in the log

------------------------------------

4. CONTENT CLASSIFICATION
Classify each task into ONE category:
- code          → src/
- test          → tests/
- documentation → docs/
- design        → design/
- analysis      → outputs/

------------------------------------

5. EXECUTION BOUNDARIES
- Work ONLY inside this project directory
- No network access unless explicitly instructed
- No shell execution unless explicitly instructed

------------------------------------

6. COMPLETION CRITERIA
A task is COMPLETE only if:
- Logs are written
- code_index.md is updated (if applicable)
- Outputs are correctly classified

====================================
END OF GOVERNANCE RULES
====================================
