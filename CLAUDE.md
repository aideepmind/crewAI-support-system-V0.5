YOU ARE OPERATING IN STRICT PROJECT GOVERNANCE MODE.

====================================
GLOBAL NON-NEGOTIABLE RULES
====================================
## Verification
- 回答所有问题前输入: [老李，你又在挑战我：]
- 文字前后分别加两个有颜色的图标

--------------------
## LOGGING (MANDATORY)
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
=====================================

## FILE TRACEABILITY (MANDATORY)
Whenever you create or modify a program file, you MUST update:
.claude/artifacts/code_index.md

Each entry must include:
- File path
- Purpose
- Role / responsibility
- Created or modified date
- Related task

## OUTPUT KEYWORD RULE ("tomd")
If the user instruction contains the keyword "tomd":
- Output MUST be written to a Markdown file
- Place it under /docs or /outputs
- Do NOT print full content in chat
- Record output path in the log
- 文件创建后，在消息中提供可以点击的文件链接，让用户可以直接点击在当前环境中打开

## Update req.md and design.md RULE ("toreq")
If the user instruction contains the keyword "toreq":
- 如果涉及软件需求变化，同步到req.md
- 如果涉及软件设计变化，同步到design.md
- 同时确保需求和设计也要同步
- req.md创建或更新后，在消息中提供可以点击的文件链接，让用户可以直接点击在当前环境中打开
- design.md创建或更新后，在消息中提供可以点击的文件链接，让用户可以直接点击在当前环境中打开

## CONTENT CLASSIFICATION
Classify each task into ONE category:
- code          → src/
- test          → tests/
- documentation → docs/
- design        → design/
- analysis      → outputs/

## COMPLETION CRITERIA
A task is COMPLETE only if:
- Logs are written
- code_index.md is updated (if applicable)
- Outputs are correctly classified

====================================
END OF GOVERNANCE RULES
====================================