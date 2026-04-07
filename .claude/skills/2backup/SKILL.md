---
name: 2backup
description: Backup current project code and configuration data. Creates a zip file with project files excluding dependencies, cache, and temporary files. Save the zip file to <LYS_BACKUP_DIR>.  Usage: /2backup [project_name]
license: MIT
---

# 2backup - Project Backup Skill

## Configuration
- <LYS_BACKUP_DIR>: `/Users/liyansheng/data/backup`

## Overview

This skill creates a backup of the current project directory as a zip file. It intelligently includes project code and configuration files while excluding dependencies, cache files, and temporary data.

## Quick Start

### Usage

```
/2backup [project_name]
```

**Examples:**
```
/2backup                    # Use current directory name as project name
/2backup myproject          # Specify custom project name
```

### What Happens

1. Gets project name (from parameter or uses current directory name)
2. Determines backup directory from `<LYS_BACKUP_DIR>` environment variable
3. Creates a timestamped zip file: `<project_name>_backup_YYYYMMDD_HHMMSS.zip`
4. Includes project files while excluding:
   - Dependencies (`.venv/`, `node_modules/`, `__pycache__/`, etc.)
   - Git data (`.git/`)
   - IDE configs (`.vscode/`, `.idea/`)
   - Temporary files and caches
5. Stores backup in `<LYS_BACKUP_DIR>/`
6. Displays backup location and file size

## Backup Details

### ✅ Included

- **Project code** and directory structure
- **Configuration files**: `requirements.txt`, `.env`, `uv.lock`, `pyproject.toml`, `package.json`, etc.
- **Documentation**: `README.md`, `docs/`, `tests/`
- **Config files**: `config.yaml`, `logs/`, etc.
- **All project-specific files and data**

### ❌ Excluded

- **Dependency directories**: `.venv/`, `venv/`, `env/`, `node_modules/`, `__pycache__/`, etc.
- **Git metadata**: `.git/`, `.gitignore`, `.gitattributes`
- **IDE configs**: `.vscode/`, `.idea/`, `*.iml`
- **Cache files**: `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, etc.
- **Temporary files**: `*.tmp`, `*.temp`, `*.log`, `*.bak`, `*.cache`
- **System files**: `.DS_Store`, `Thumbs.db`
- **Archive files**: `*.zip`, `*.tar.gz`, `*.rar`, `*.7z`

## Backup Format

### File Name Pattern

```
<project_name>_backup_YYYYMMDD_HHMMSS.zip
```

**Example:** `myproject_backup_20240228_150000.zip`

### Storage Location

Default: `/Users/liyansheng/data/backup/`

Can be customized via `LYS_BACKUP_DIR` environment variable.

## Implementation Guide for Claude

When user invokes `/2backup [project_name]`:

1. **Determine project name:**
   - Use provided parameter if given
   - Otherwise, use current directory name (basename of `pwd`)

2. **Verify backup directory:**
   - Get from `<LYS_BACKUP_DIR>` environment variable
   - Default: `/Users/liyansheng/data/backup`
   - Create if doesn't exist

3. **Generate backup filename:**
   - Format: `<project_name>_backup_$(date +%Y%m%d_%H%M%S).zip`
   - Full path: `<LYS_BACKUP_DIR>/<filename>`

4. **Create zip archive:**
   - Use `zip -r` command from current directory
   - Exclude patterns using `-x` flag:
     - Python: `__pycache__/*`, `*.py[cod]`, `.venv/*`, `venv/*`, `*.egg-info/*`, `.pytest_cache/*`, `.mypy_cache/*`, `.ruff_cache/*`
     - Node: `node_modules/*`, `npm-debug.log*`, `yarn-error.log*`
     - Git: `.git/*`, `.gitignore`, `.gitattributes`
     - IDE: `.vscode/*`, `.idea/*`, `*.swp`, `*.swo`, `*.iml`
     - Temp: `*.tmp`, `*.temp`, `*.log`, `*.bak`, `*.cache`
     - System: `.DS_Store`, `Thumbs.db`
     - Archives: `*.zip`, `*.tar.gz`, `*.rar`, `*.7z`

5. **Verify backup:**
   - Check if file was created
   - Get file size using `du -h`
   - Display success message with path and size

6. **Display recovery instructions:**
   ```
   恢复方法：
     unzip <backup_file> -d <target_directory>
   ```

## Example Command

```bash
cd /path/to/project
zip -r "/Users/liyansheng/data/backup/myproject_backup_20240228_150000.zip" . \
  -x "__pycache__/*" \
  -x "*.py[cod]" \
  -x ".venv/*" \
  -x "venv/*" \
  -x "node_modules/*" \
  -x ".git/*" \
  -x ".gitignore" \
  -x ".vscode/*" \
  -x ".idea/*" \
  -x "*.tmp" \
  -x "*.log" \
  -x ".DS_Store" \
  -x "*.zip"
```

## Recovery

To restore from backup:

```bash
# Extract to specific directory
unzip /Users/liyansheng/data/backup/myproject_backup_20240228_150000.zip -d /path/to/restore

# Extract to current directory
unzip /Users/liyansheng/data/backup/myproject_backup_20240228_150000.zip
```

## Troubleshooting

### Backup directory not found
- Check `LYS_BACKUP_DIR` environment variable
- Verify directory permissions: `ls -la $LYS_BACKUP_DIR`
- Directory will be created automatically if missing

### Permission denied
- Ensure write permissions on backup directory
- Check disk space: `df -h $LYS_BACKUP_DIR`

### Empty backup file
- Verify current directory contains files
- Check exclude patterns aren't too broad

## Related Skills

- **2obsidian**: Record technical knowledge to Obsidian
- **4obsidian**: Query technical knowledge from Obsidian
