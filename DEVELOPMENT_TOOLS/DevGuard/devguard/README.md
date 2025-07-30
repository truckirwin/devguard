# 🛡️ DevGuard - Developer's Backup Guardian

**Never lose your development work again!** DevGuard is a comprehensive backup and recovery system designed for developers who want bulletproof protection without the complexity.

## 🚀 Features

- ✅ **Smart Daily Backups**: One zip per day with incremental diffs
- ✅ **Intelligent Git Integration**: Automatic commits and pushes
- ✅ **Crash Recovery Tools**: Complete restoration from any backup
- ✅ **AI-Powered Auto-Save**: Detects completion phrases and auto-saves
- ✅ **Rolling Retention**: Keeps 5 days of backups automatically
- ✅ **External Storage**: Backups stored outside project directory
- ✅ **Zero Configuration**: Works out of the box
- ✅ **Universal**: Works with any programming language/framework

## 📦 Quick Installation

```bash
# Copy DevGuard to your project
cp -r devguard /path/to/your/project/
cd /path/to/your/project
chmod +x devguard/*.sh

# Initialize DevGuard
./devguard/install.sh
```

## ⚡ Quick Start

```bash
# Save your work instantly
./quick-save.sh

# Contextual backup with description  
./smart-save.sh "Completed user authentication feature"

# End-of-day comprehensive backup
./daily-backup.sh

# Recover from crash (if needed)
./recover.sh
```

## 🎯 How It Works

### Daily Backup Flow
```
First save of day → Creates: DAILY_ProjectName_20241206.zip
Later saves → Adds: DIFF_timestamp.txt to same zip
Git operations → Always: commit + push to remote
```

### Auto-Save Triggers
DevGuard automatically saves when you say:
- "Good, that works"
- "Perfect, that's done" 
- "This section is complete"
- "That fixes it"

## 📋 Commands

| Command | Purpose |
|---------|---------|
| `./quick-save.sh` | Quick backup (auto-triggered) |
| `./smart-save.sh "context"` | Contextual backup with description |
| `./daily-backup.sh` | End-of-day comprehensive backup |
| `./recover.sh` | Interactive recovery tool |
| `./devguard/help.sh` | Get help and troubleshooting |

## 📁 Package Contents

- `install.sh` - One-time setup script
- `smart-save.sh` - Intelligent backup with context
- `quick-save.sh` - Quick backup wrapper  
- `daily-backup.sh` - End-of-day backup
- `recover.sh` - Recovery tool
- `help.sh` - Help and troubleshooting
- `docs/` - Complete documentation

## 🔄 Recovery Process

1. **After Crash**: `./recover.sh`
2. **Choose Option**: Extract latest backup
3. **Follow Guide**: Built-in recovery instructions
4. **Resume Work**: `./quick-save.sh` to restart protection

## 🧠 Intelligence Features

- **Smart Deduplication**: Avoids unnecessary backups
- **Context Awareness**: Meaningful commit messages
- **Automatic Cleanup**: Maintains optimal storage
- **Incremental Diffs**: Tracks all daily changes
- **External Redundancy**: Multiple backup locations

## 🚨 Emergency Recovery

**Computer crashed? Project corrupted?**

```bash
cd /path/to/parent/directory
./devguard/recover.sh
# Follow interactive prompts
# Your work is fully recoverable!
```

## 📄 License

MIT License - Use freely in personal and commercial projects

---

**DevGuard**: Because your code is too valuable to lose. 🛡️
