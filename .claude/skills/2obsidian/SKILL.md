---
name: 2obsidian
description: Record technical knowledge from conversations into Obsidian markdown files. When user invokes /2obsidian <topic>, extract key commands, parameters, and notes from the conversation, then append them to the markdown file at <OBSIDIAN_LYS_DIR>/<topic>.md without affecting existing content.
license: MIT
---

# 2obsidian - Obsidian Technical Knowledge Recorder

## Configuration
- <OBSIDIAN_LYS_DIR>: `/Users/liyansheng/data/Obsidian-lys`

## Overview

This skill automatically records technical information from your conversation with Claude into Obsidian markdown files. It extracts successful commands, parameters, important notes, and best practices, creating a searchable technical manual.

## Quick Start

### Usage

```
/2obsidian <topic>
```

**Example:**
```
/2obsidian v2raya
```

### What Happens

1. Claude asks for the topic name (if not provided)
2. Creates/opens markdown file: `<OBSIDIAN_LYS_DIR>/<topic>.md`
3. Extracts key information from the conversation:
   - Successful commands with explanations
   - Configuration parameters
   - Important notes and warnings
   - Best practices
4. Appends to the file (preserving existing content)
5. Displays what was recorded



### Environment Variable

Set the Obsidian directory path:

```bash
export OBSIDIAN_LYS_DIR=/Users/liyansheng/data/Obsidian-lys
```

**Default:** If not set, uses: `/Users/liyansheng/Downloads/skilltest`

### File Structure

For topic "v2raya", the file will be:
```
<OBSIDIAN_LYS_DIR>/v2raya.md
```

## Markdown Format

### New File Template

```markdown
# <topic> 技术手册

> 创建时间：YYYY-MM-DD
> 最后更新：YYYY-MM-DD

## 简介
[Brief description of the tool/technology]

---

## 安装与配置

### <Section Title>

**中文说明**
```bash
command_here
```

---

## 服务管理

### <Section Title>

**中文说明**
```bash
command_here
```

---

## 关键信息

### <Subsection>
- **Key**: Value
- **Key**: Value

---

## 注意事项

⚠️ **重要提示**
1. Important note 1
2. Important note 2

---

## 相关链接

- [Link text](URL)
```

### Appending to Existing Files

When appending to existing files:
1. Read the existing file first
2. Identify the most relevant section
3. Append new information under appropriate headings
4. Update the "最后更新" timestamp
5. Do NOT modify existing content

## Content Extraction Rules

When recording technical information:

### ✅ DO Record

- **Successful commands** with Chinese explanations
- **Configuration parameters** and their effects
- **File paths** and **directory structures**
- **Service names** and **port numbers**
- **Error messages** and **solutions**
- **Warnings** and **security considerations**
- **Version information** and **system requirements**
- **Working examples** from the conversation

### ❌ DON'T Record

- Failed commands (unless explaining what NOT to do)
- Repetitive information
- Generic information not specific to the topic
- Commands that weren't executed or verified
- Unrelated side discussions

### Format Guidelines

1. **Commands should include Chinese explanations:**
   ```bash
   # 安装 sshpass 工具（macOS）
   brew install hudochenkov/sshpass/sshpass
   ```

2. **Group related information:**
   - Put installation commands together
   - Group configuration steps
   - Keep service management commands in one section

3. **Use appropriate hierarchy:**
   - `##` for major sections (安装与配置, 服务管理, etc.)
   - `###` for subsections
   - `-` for lists

4. **Highlight important warnings:**
   ```
   ⚠️ **重要提示**
   1. First warning
   2. Second warning
   ```

## Examples

### Example 1: SSH File Transfer

**Input:** User asks about transferring files to remote Linux server

**Recorded:**
```markdown
### SSH 文件传输（macOS → Linux）

**安装 sshpass 工具**
```bash
brew install hudochenkov/sshpass/sshpass
```

**使用 SFTP 批处理传输文件**
```bash
sshpass -p '密码' sftp -oBatchMode=no -b - 用户@主机 <<EOF
lcd /本地/目录
put 文件名
EOF
```

**实际示例**
```bash
sshpass -p 'lys7268Z' sftp -oBatchMode=no -b - liyansheng@192.168.1.13 <<EOF
lcd /Users/liyansheng/Downloads
put installer_archlinux_x64_2.2.7.5.pkg.tar.zst
EOF
```
```

### Example 2: Service Management

**Input:** User installs and starts v2rayA service

**Recorded:**
```markdown
### 启动和启用服务

```bash
# 启用服务（开机自启）
sudo systemctl enable v2raya

# 启动服务
sudo systemctl start v2raya

# 查看服务状态
sudo systemctl status v2raya --no-pager
```

### 其他服务命令

```bash
# 停止服务
sudo systemctl stop v2raya

# 重启服务
sudo systemctl restart v2raya

# 查看服务日志
sudo journalctl -u v2raya -f
```
```

### Example 3: Important Warnings

**Recorded:**
```markdown
## 注意事项

⚠️ **重要提示**
1. **非交互式 sudo 密码输入**：使用 `echo '密码' | sudo -S 命令` 的方式
2. **Ubuntu 不支持 pacman**：Arch Linux 包需手动解压安装
3. **sshpass 安全性**：密码在命令行中可见，不建议在生产环境使用
4. **服务端口**：确保防火墙允许 2017 端口访问
```

## Implementation Guide for Claude

When user invokes `/2obsidian <topic>`:

1. **Get topic name** (from parameter or ask user)
2. **Read conversation history** to extract:
   - All successful bash commands and their outputs
   - Configuration files and parameters
   - Important notes and warnings
   - File paths and directory structures
   - Version information
3. **Check if file exists:**
   - If NO: Create with template
   - If YES: Read existing content
4. **Organize information:**
   - Group by category (installation, configuration, management, etc.)
   - Add Chinese explanations for commands
   - Highlight warnings
5. **Write to file:**
   - Append to appropriate sections
   - Update timestamp
   - Preserve existing content
6. **Display recorded items** in a formatted list

## Troubleshooting

### File not created
- Check `OBSIDIAN_LYS_DIR` environment variable
- Verify directory permissions: `ls -la $OBSIDIAN_LYS_DIR`
- Ensure directory exists or is creatable

### Content not appended correctly
- Claude will read the file first before appending
- Check that existing content is preserved
- Verify markdown formatting is correct

## Related Skills

- **pdf**: For PDF manipulation and documentation
- **xlsx**: For Excel file operations
