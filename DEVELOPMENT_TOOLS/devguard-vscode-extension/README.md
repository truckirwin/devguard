# 🛡️ DevGuard - Intelligent Code Backup

**Bulletproof backup protection with AI-powered auto-save detection for VSCode**

DevGuard is the ultimate safety net for developers, providing intelligent backup protection that automatically detects when you've completed meaningful work and creates comprehensive backups without interrupting your flow.

## ✨ Features

### 🤖 AI-Powered Auto-Save Detection
- **Smart Phrase Recognition**: Automatically detects completion phrases like "that works", "perfect", "done"
- **Non-Intrusive**: Monitors your typing without interfering with your workflow
- **Customizable Triggers**: Configure your own completion phrases

### 📦 Multi-Layer Backup Protection
- **Git Integration**: Automatic commits with descriptive messages
- **External Archives**: ZIP backups to centralized location
- **Remote Push**: Optional automatic push to remote repositories
- **Smart Retention**: Configurable backup cleanup

### ⚡ Instant Manual Backup
- **Quick Save** (`Ctrl+Shift+S`): Instant git commit
- **Smart Save** (`Ctrl+Shift+Alt+S`): Detailed backup with custom message
- **Daily Backup**: Comprehensive project archive

### 🎯 Universal Project Support
- **Centralized Storage**: `~/DevGuard-Backups` for all projects
- **Language Agnostic**: Works with any codebase
- **Zero Configuration**: Works out of the box

## 🚀 Quick Start

1. **Install DevGuard** from the VSCode marketplace
2. **Open any project** - DevGuard activates automatically
3. **Start coding** - Protection is immediate
4. **Type completion phrases** - Watch DevGuard auto-save your progress

That's it! Your code is now protected.

## 📋 Commands

| Command | Shortcut | Description |
|---------|----------|-------------|
| DevGuard: Quick Save | `Ctrl+Shift+S` | Instant git commit |
| DevGuard: Smart Save | `Ctrl+Shift+Alt+S` | Detailed backup with message |
| DevGuard: Daily Backup | - | Full project archive |
| DevGuard: Show Status | - | View backup statistics |
| DevGuard: Toggle Protection | - | Enable/disable DevGuard |
| DevGuard: Open Backup Location | - | Open backup folder |

## ⚙️ Configuration

### Completion Phrases
Configure which phrases trigger automatic backups:

```json
{
  "devguard.completionPhrases": [
    "that works",
    "perfect",
    "great that works", 
    "looks good",
    "working now",
    "fixed",
    "done",
    "completed"
  ]
}
```

### Backup Settings
```json
{
  "devguard.backupLocation": "~/DevGuard-Backups",
  "devguard.backupRetentionDays": 5,
  "devguard.autoCommitEnabled": true,
  "devguard.pushToRemote": true
}
```

### Detection Tuning
```json
{
  "devguard.phraseDetectionDelay": 2000,
  "devguard.showNotifications": true
}
```

## 🛡️ Status Bar Integration

The DevGuard shield (`🛡️`) in your status bar shows:
- **Green**: Protection active and monitoring
- **Yellow**: Disabled or no workspace
- **Tooltip**: Hover for backup statistics

Click the shield for detailed backup status and quick actions.

## 📁 Backup Structure

```
~/DevGuard-Backups/
├── ProjectName-2025-06-08.zip
├── ProjectName-2025-06-08-info.txt
├── ProjectName-2025-06-07.zip
└── ...
```

Each backup includes:
- Complete project archive (excluding configured patterns)
- Metadata file with backup details
- Git commit in original repository
- Optional remote push

## 🎛️ Advanced Configuration

### Exclude Patterns
Control what gets backed up:
```json
{
  "devguard.excludePatterns": [
    "node_modules",
    ".git", 
    "venv",
    "*.log",
    "build",
    "dist"
  ]
}
```

### Git Integration
```json
{
  "devguard.autoCommitEnabled": true,  // Auto-commit changes
  "devguard.pushToRemote": true        // Push to remote repo
}
```

## 🔧 Development

### Building from Source
```bash
git clone https://github.com/devguard/vscode-extension
cd vscode-extension
npm install
npm run compile
```

### Testing
```bash
npm run lint
npm run test
```

### Packaging
```bash
npm run package
```

## 📊 Backup Statistics

DevGuard tracks comprehensive backup metrics:
- Total number of backups
- Storage usage
- Backup frequency
- Git commit history
- Remote push status

## 🛟 Recovery

### Quick Recovery
1. Click DevGuard shield in status bar
2. Select "Open Backup Folder"
3. Locate desired backup zip file
4. Extract to new location

### Git Recovery
All saves create git commits, so you can also:
```bash
git log --oneline | grep "DevGuard save"
git checkout <commit-hash>
```

## 🌟 Why DevGuard?

### For Individual Developers
- **Never lose work** from crashes, power outages, or mistakes
- **Peace of mind** with automated protection
- **Zero overhead** - works silently in background
- **Smart detection** learns your completion patterns

### For Teams
- **Consistent backup practices** across all developers
- **Centralized backup location** for easy management
- **Git workflow integration** maintains clean history
- **Configurable policies** adapt to team standards

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/devguard/vscode-extension/issues)
- **Discussions**: [GitHub Discussions](https://github.com/devguard/vscode-extension/discussions)
- **Email**: support@devguard.dev

---

**🛡️ DevGuard: Because your code deserves protection.** 