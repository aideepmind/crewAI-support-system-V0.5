---
name: 4obsidian
description: Query technical knowledge from Obsidian markdown files first. When user's input ends with " 4obsidian", search for information in md files under the directory specified by <OBSIDIAN_LYS_DIR> variable. If not found, use AI's own knowledge to answer.
license: MIT
---

# 4obsidian - Obsidian Technical Knowledge Query

## Configuration
- <OBSIDIAN_LYS_DIR>: `/Users/liyansheng/data/Obsidian-lys`

## Overview

This skill enables Claude to first search your personal technical manual (stored as markdown files in Obsidian) before using its own knowledge. When your question ends with " 4obsidian", Claude will search through your existing technical documentation first, then fall back to AI knowledge if needed.

## Quick Start

### Usage

Simply add " 4obsidian" (with a leading space) at the end of your question:

```
<your question> 4obsidian
```

**Example:**
```
linux中如何启动v2raya服务 4obsidian
```

### What Happens

1. Claude detects " 4obsidian" at the end of your input
2. Reads the technical manual directory from `<OBSIDIAN_LYS_DIR>` variable
3. Searches through all .md files in that directory for relevant information
4. **If found**: Returns information from your technical manual with file reference
5. **If not found**: Uses AI's own knowledge to answer (and can optionally offer to record it)

## Configuration

### Environment Variable

Set the Obsidian technical manual directory path:

```bash
export OBSIDIAN_LYS_DIR=/Users/liyansheng/data/Obsidian-lys
```

**Format:** `<OBSIDIAN_LYS_DIR>：<directory_path>`

**Example:**
```
<OBSIDIAN_LYS_DIR>：/Users/liyansheng/data/Obsidian-lys
```

**Default:** If not set, will prompt user to provide the directory path.

### File Structure

The skill will search all `.md` files in the configured directory:

```
<OBSIDIAN_LYS_DIR>/
├── v2raya.md
├── ssh.md
├── docker.md
└── ...
```

## Search Strategy

### Phase 1: Manual Search

When " 4obsidian" is detected:

1. **Extract keywords** from the user's question
2. **Read directory** from `<OBSIDIAN_LYS_DIR>` variable
   - If not set, ask user: "请提供技术手册目录路径（格式：<OBSIDIAN_LYS_DIR>：<路径>）"
3. **List all .md files** in the directory
4. **Search each file** for relevant keywords:
   - Search in headers (##, ###)
   - Search in code blocks
   - Search in content text
5. **Rank results** by relevance:
   - Exact matches in headers (highest priority)
   - Matches in code blocks
   - Matches in regular text

### Phase 2: Response

**If information is found:**
```
📖 从技术手册找到答案：

来源文件：v2raya.md

## 服务管理

### 启动和启用服务
```bash
# 启用服务（开机自启）
sudo systemctl enable v2raya

# 启动服务
sudo systemctl start v2raya

# 查看服务状态
sudo systemctl status v2raya --no-pager
```
```

**If information is NOT found:**
```
🔍 技术手册中未找到相关信息。

以下是我根据已有知识提供的答案：

[AI's answer]

---
💡 提示：您可以将此信息记录到技术手册中以便下次查询。使用 /2obsidian <topic> 命令记录。
```

### Phase 3: Optional Recording

If information was not found and the AI provided a useful answer, offer:

```
💡 此问题未在技术手册中找到。是否要将此答案记录到技术手册？
- 使用命令：/2obsidian <topic> 记录相关知识
```

## Implementation Guide for Claude

When user input ends with " 4obsidian":

### Step 1: Detect and Validate

1. Check if user input ends with ` 4obsidian` (space + 4obsidian)
2. Remove ` 4obsidian` from the actual question
3. Extract the core question for processing

### Step 2: Get Manual Directory

1. Read `<OBSIDIAN_LYS_DIR>` variable
2. If not set:
   ```
   请提供技术手册目录路径。格式：
   <OBSIDIAN_LYS_DIR>：<完整路径>

   例如：OBSIDIAN_LYS_DIR>：/Users/liyansheng/Documents/lys/个人资料
   ```
3. Parse the path from format: `<OBSIDIAN_LYS_DIR>：<path>`

### Step 3: Search Manual Files

1. Use Glob or Bash to find all `.md` files in the directory:
   ```bash
   find <OBSIDIAN_LYS_DIR> -name "*.md" -type f
   ```
2. For each file, use Grep or Read to search for:
   - **Keywords**: Extract 2-4 key terms from the question
   - **Technical terms**: Service names, command names, file types
   - **Related concepts**: Broader terms if exact matches fail

3. Search priority:
   ```
   Headers (##, ###) > Code blocks (```) > Bold text (**text**) > Regular text
   ```

### Step 4: Evaluate Results

**If relevant information found:**
1. Read the full section(s) containing the information
2. Format with source file reference
3. Present to user with "📖 从技术手册找到答案："

**If NO relevant information found:**
1. Use AI's own knowledge to answer the question
2. Present with "🔍 技术手册中未找到相关信息。"
3. Add prompt: "💡 您可以使用 /2obsidian <topic> 将此信息记录到技术手册中。"

### Step 5: Format Response

**For found information:**
```
📖 从技术手册找到答案：

来源文件：<filename>.md

[Extracted content with proper formatting]

---
查询时间：YYYY-MM-DD HH:MM
```

**For AI-generated information:**
```
🔍 技术手册中未找到相关信息。

以下是基于AI知识库的答案：

[AI's answer]

---
💡 要将此信息保存到技术手册，请使用：/2obsidian <topic>
```

## Search Examples

### Example 1: Exact Match

**User Input:**
```
linux中如何启动v2raya服务 4obsidian
```

**Process:**
1. Keywords: "linux", "启动", "v2raya", "服务"
2. Search: Find "v2raya.md" or files containing "v2raya"
3. Found in: `v2raya.md` under section "## 服务管理"

**Response:**
```
📖 从技术手册找到答案：

来源文件：v2raya.md

## 服务管理

### 启动和启用服务

```bash
# 启用服务（开机自启）
sudo systemctl enable v2raya

# 启动服务
sudo systemctl start v2raya

# 查看服务状态
sudo systemctl status v2raya --no-pager
```
```

### Example 2: Keyword Search

**User Input:**
```
如何使用sshpass传输文件 4obsidian
```

**Process:**
1. Keywords: "sshpass", "传输", "文件"
2. Search: Find files containing "sshpass"
3. Found in: `ssh.md` under section "### SSH 文件传输"

**Response:**
```
📖 从技术手册找到答案：

来源文件：ssh.md

### SSH 文件传输（macOS → Linux）

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

### Example 3: Not Found

**User Input:**
```
如何配置docker-compose网络 4obsidian
```

**Process:**
1. Keywords: "docker-compose", "网络", "配置"
2. Search: No relevant information found in manual files
3. Use AI knowledge instead

**Response:**
```
🔍 技术手册中未找到相关信息。

以下是基于AI知识库的答案：

## Docker Compose 网络配置

### 默认网络

Docker Compose 默认会创建一个网络，所有服务都在同一网络中可以互相通信。

```yaml
version: '3'
services:
  web:
    image: nginx
  db:
    image: postgres
```

### 自定义网络

```yaml
version: '3'
services:
  web:
    image: nginx
    networks:
      - frontend
  api:
    image: myapi
    networks:
      - frontend
      - backend

networks:
  frontend:
  backend:
```

### 连接外部网络

```yaml
services:
  app:
    image: myapp
    networks:
      - my_external_network

networks:
  my_external_network:
    external: true
```

---
💡 要将此信息保存到技术手册，请使用：/2obsidian docker
```

## Troubleshooting

### Manual directory not configured

**Error:**
```
❌ 未配置技术手册目录。

请使用以下格式配置：
<OBSIDIAN_LYS_DIR>：<完整路径>

例如：<OBSIDIAN_LYS_DIR>：/Users/liyansheng/Documents/lys/个人资料
```

**Solution:**
User should provide the directory path in their next message.

### No .md files found

**Error:**
```
⚠️ 在 <OBSIDIAN_LYS_DIR> 目录中未找到任何 .md 文件。

请确认：
1. 目录路径正确：ls <directory_path>
2. 目录中包含 .md 文件
```

**Solution:**
- Verify directory path
- Check if markdown files exist
- Create manual files using /2obsidian skill

### Permission denied

**Error:**
```
❌ 无法访问技术手册目录：权限不足
```

**Solution:**
```bash
# Check directory permissions
ls -la <OBSIDIAN_LYS_DIR>

# Fix permissions if needed
chmod -R 755 <OBSIDIAN_LYS_DIR>
```

## Best Practices

### For Manual Organization

1. **Use descriptive filenames:**
   - ✅ `v2raya.md`, `ssh.md`, `docker.md`
   - ❌ `note1.md`, `temp.md`

2. **Use clear headings:**
   ```markdown
   ## 服务管理
   ### 启动和启用服务
   ```

3. **Include code examples:**
   ```markdown
   **中文说明**
   ```bash
   command_here
   ```
   ```

4. **Add warnings prominently:**
   ```markdown
   ⚠️ **重要提示**
   1. Warning 1
   2. Warning 2
   ```

### For Querying

1. **Use specific keywords:**
   - ✅ "如何启动v2raya服务 4obsidian"
   - ❌ "帮我弄一下那个东西 4obsidian"

2. **Use technical terms:**
   - ✅ "systemctl restart nginx 4obsidian"
   - ❌ "重启网站 4obsidian"

3. **Ask follow-up questions:**
   - If initial results aren't specific enough, narrow down with more details

## Related Skills

- **2obsidian**: Record technical knowledge into Obsidian markdown files (the complement to 4obsidian)
- **pdf**: For PDF manipulation and documentation
- **xlsx**: For Excel file operations

## Technical Notes

### Search Algorithm

The skill uses a multi-pass search approach:

1. **First pass**: Exact phrase matching in headers
2. **Second pass**: Keyword matching in headers
3. **Third pass**: Code block content matching
4. **Fourth pass**: Full-text content search
5. **Fifth pass**: Related concept search (stemming, synonyms)

### Performance Optimization

- **Caching**: File list is cached per session
- **Parallel search**: Multiple files searched concurrently
- **Relevance scoring**: Results ranked by:
  - Header matches: 10 points
  - Code block matches: 5 points
  - Bold text matches: 3 points
  - Regular text matches: 1 point
  - Exact phrase bonus: +5 points

### Integration with 2obsidian

These skills work together seamlessly:

1. User asks: "How to use feature X? 4obsidian"
2. 4obsidian searches manual → Not found
3. AI provides answer
4. User wants to save: "/2obsidian topic"
5. 2obsidian records the answer
6. Next time: 4obsidian will find it!

## Version History

- **v1.0** (2025-02-14): Initial release
  - Manual-first search strategy
  - Fallback to AI knowledge
  - Integration with 2obsidian skill
