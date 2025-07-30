# 🛡️ DevGuard Installation Guide

## Quick Install (Recommended)

### Option 1: Install from VSIX File
1. Open VSCode
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
3. Type "Extensions: Install from VSIX..."
4. Select the `devguard-backup-1.0.0.vsix` file
5. Restart VSCode when prompted

### Option 2: Manual Installation
1. Copy the `devguard-backup-1.0.0.vsix` file to your VSCode extensions folder:
   - **Windows**: `%USERPROFILE%\.vscode\extensions\`
   - **macOS**: `~/.vscode/extensions/`
   - **Linux**: `~/.vscode/extensions/`
2. Restart VSCode

## Development Installation

### Prerequisites
- Node.js 16+ 
- npm or yarn
- VSCode 1.74.0+

### Build from Source
```bash
git clone <repository-url>
cd devguard-vscode-extension
npm install
npm run compile
npm run package
```

### Install Development Version
```bash
code --install-extension devguard-backup-1.0.0.vsix
```

## Verification

After installation, you should see:
1. 🛡️ DevGuard icon in the status bar
2. DevGuard commands in Command Palette (`Ctrl+Shift+P`)
3. Welcome notification on first use

## Configuration

DevGuard works out of the box, but you can customize:

1. Open VSCode Settings (`Ctrl+,`)
2. Search for "devguard"
3. Configure your preferences:
   - Backup location
   - Completion phrases
   - Git integration settings
   - Notification preferences

## First Use

1. Open any project folder in VSCode
2. Start coding normally
3. Type completion phrases like "that works" or "perfect"
4. Watch DevGuard automatically create backups!

## Manual Backup

Use keyboard shortcuts:
- `Ctrl+Shift+S` (Quick Save)
- `Ctrl+Shift+Alt+S` (Smart Save with message)

## Troubleshooting

### Extension Not Loading
- Check VSCode version (requires 1.74.0+)
- Restart VSCode completely
- Check Developer Console for errors

### Backup Not Working
- Ensure workspace folder is open
- Check backup location permissions
- Verify git is installed (for git features)

### Status Bar Not Showing
- Check if status bar is visible (`View > Appearance > Status Bar`)
- Look for 🛡️ icon on the right side

## Support

- **Issues**: Report bugs or feature requests
- **Documentation**: See README.md for full documentation
- **Configuration**: All settings available in VSCode preferences

---

**🛡️ Your code is now protected by DevGuard!** 