# DevGuard VSCode Extension - Technical Design

## 🎯 **Core Requirements**
- Monitor **user phrases** (not AI responses) for completion detection
- **Hot keys** for manual backup triggers
- **Centralized backup location** for all projects
- **GitHub integration** using existing git workflows
- **True VSCode extension** (no per-project installation)
- **Marketplace ready** for distribution

## 🏗️ **Extension Architecture**

### **1. Extension Manifest (package.json)**
```json
{
  "name": "devguard-backup",
  "displayName": "DevGuard - Intelligent Code Backup",
  "description": "Bulletproof backup protection with AI-powered auto-save detection",
  "version": "1.0.0",
  "engines": { "vscode": "^1.74.0" },
  "categories": ["Other", "SCM Providers"],
  "activationEvents": ["onStartupFinished"],
  "main": "./out/extension.js",
  "contributes": {
    "commands": [
      {
        "command": "devguard.quickSave",
        "title": "DevGuard: Quick Save",
        "icon": "$(save)"
      },
      {
        "command": "devguard.smartSave",
        "title": "DevGuard: Smart Save with Message"
      },
      {
        "command": "devguard.dailyBackup",
        "title": "DevGuard: Daily Backup"
      },
      {
        "command": "devguard.openBackupLocation",
        "title": "DevGuard: Open Backup Location"
      },
      {
        "command": "devguard.showStatus",
        "title": "DevGuard: Show Backup Status"
      }
    ],
    "keybindings": [
      {
        "command": "devguard.quickSave",
        "key": "ctrl+shift+s",
        "mac": "cmd+shift+s"
      },
      {
        "command": "devguard.smartSave",
        "key": "ctrl+shift+alt+s",
        "mac": "cmd+shift+alt+s"
      }
    ],
    "configuration": {
      "title": "DevGuard",
      "properties": {
        "devguard.enabled": {
          "type": "boolean",
          "default": true,
          "description": "Enable DevGuard backup protection"
        },
        "devguard.backupLocation": {
          "type": "string",
          "default": "~/DevGuard-Backups",
          "description": "Centralized backup location for all projects"
        },
        "devguard.completionPhrases": {
          "type": "array",
          "default": [
            "that works",
            "perfect",
            "great that works",
            "good that works", 
            "looks good",
            "working now",
            "fixed",
            "done",
            "completed",
            "finished"
          ],
          "description": "Phrases that trigger automatic backup"
        },
        "devguard.autoCommitEnabled": {
          "type": "boolean", 
          "default": true,
          "description": "Automatically commit changes to git"
        },
        "devguard.pushToRemote": {
          "type": "boolean",
          "default": true, 
          "description": "Push commits to remote repository"
        },
        "devguard.backupRetentionDays": {
          "type": "number",
          "default": 5,
          "description": "Number of days to retain backups"
        }
      }
    }
  }
}
```

### **2. Main Extension File (extension.ts)**
```typescript
import * as vscode from 'vscode';
import { PhraseDetector } from './phraseDetector';
import { BackupManager } from './backupManager';
import { StatusBarManager } from './statusBar';

export function activate(context: vscode.ExtensionContext) {
    console.log('🛡️ DevGuard extension activated');

    const backupManager = new BackupManager(context);
    const phraseDetector = new PhraseDetector(backupManager);
    const statusBar = new StatusBarManager(backupManager);

    // Register commands
    const quickSave = vscode.commands.registerCommand('devguard.quickSave', () => {
        backupManager.performQuickSave();
    });

    const smartSave = vscode.commands.registerCommand('devguard.smartSave', async () => {
        const message = await vscode.window.showInputBox({
            prompt: 'Enter backup message',
            placeHolder: 'Describe what was accomplished...'
        });
        if (message) {
            backupManager.performSmartSave(message);
        }
    });

    const dailyBackup = vscode.commands.registerCommand('devguard.dailyBackup', () => {
        backupManager.performDailyBackup();
    });

    const openBackupLocation = vscode.commands.registerCommand('devguard.openBackupLocation', () => {
        backupManager.openBackupLocation();
    });

    // Initialize phrase detection
    phraseDetector.start();
    statusBar.initialize();

    context.subscriptions.push(
        quickSave,
        smartSave, 
        dailyBackup,
        openBackupLocation,
        phraseDetector,
        statusBar
    );
}

export function deactivate() {
    console.log('🛡️ DevGuard extension deactivated');
}
```

### **3. Phrase Detection (phraseDetector.ts)**
```typescript
import * as vscode from 'vscode';
import { BackupManager } from './backupManager';

export class PhraseDetector implements vscode.Disposable {
    private disposables: vscode.Disposable[] = [];
    private lastTextBuffer: string = '';
    private detectionTimeout: NodeJS.Timeout | undefined;

    constructor(private backupManager: BackupManager) {}

    public start() {
        // Monitor text changes in active editor
        const onDidChangeText = vscode.workspace.onDidChangeTextDocument((event) => {
            if (event.document === vscode.window.activeTextEditor?.document) {
                this.analyzeTextChange(event);
            }
        });

        // Monitor when user stops typing (debounced phrase detection)
        const onDidChangeSelection = vscode.window.onDidChangeTextEditorSelection(() => {
            this.scheduleAnalysis();
        });

        this.disposables.push(onDidChangeText, onDidChangeSelection);
    }

    private analyzeTextChange(event: vscode.TextDocumentChangeEvent) {
        // Build up text buffer from recent changes
        for (const change of event.contentChanges) {
            this.lastTextBuffer += change.text;
        }

        // Keep buffer reasonable size (last 500 characters)
        if (this.lastTextBuffer.length > 500) {
            this.lastTextBuffer = this.lastTextBuffer.slice(-500);
        }

        this.scheduleAnalysis();
    }

    private scheduleAnalysis() {
        // Clear existing timeout
        if (this.detectionTimeout) {
            clearTimeout(this.detectionTimeout);
        }

        // Schedule analysis after user stops typing (2 seconds)
        this.detectionTimeout = setTimeout(() => {
            this.detectCompletionPhrases();
        }, 2000);
    }

    private detectCompletionPhrases() {
        const config = vscode.workspace.getConfiguration('devguard');
        const phrases: string[] = config.get('completionPhrases', []);
        
        const recentText = this.lastTextBuffer.toLowerCase();
        
        for (const phrase of phrases) {
            if (recentText.includes(phrase.toLowerCase())) {
                this.triggerAutoSave(phrase);
                break;
            }
        }

        // Clear buffer after analysis
        this.lastTextBuffer = '';
    }

    private async triggerAutoSave(detectedPhrase: string) {
        const config = vscode.workspace.getConfiguration('devguard');
        if (!config.get('enabled', true)) return;

        // Show notification
        vscode.window.showInformationMessage(
            `🛡️ DevGuard detected completion: "${detectedPhrase}" - Auto-saving...`,
            { modal: false }
        );

        // Perform backup
        await this.backupManager.performSmartSave(`Auto-save triggered by: "${detectedPhrase}"`);
    }

    dispose() {
        this.disposables.forEach(d => d.dispose());
        if (this.detectionTimeout) {
            clearTimeout(this.detectionTimeout);
        }
    }
}
```

### **4. Backup Manager (backupManager.ts)**
```typescript
import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export class BackupManager {
    private backupLocation: string;

    constructor(private context: vscode.ExtensionContext) {
        this.backupLocation = this.getBackupLocation();
        this.ensureBackupDirectory();
    }

    private getBackupLocation(): string {
        const config = vscode.workspace.getConfiguration('devguard');
        const location = config.get('backupLocation', '~/DevGuard-Backups');
        
        // Expand home directory
        return location.replace('~', require('os').homedir());
    }

    private async ensureBackupDirectory() {
        try {
            await fs.promises.mkdir(this.backupLocation, { recursive: true });
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to create backup directory: ${error}`);
        }
    }

    public async performQuickSave(): Promise<void> {
        return this.performBackup('Quick save session', false);
    }

    public async performSmartSave(message: string): Promise<void> {
        return this.performBackup(message, true);
    }

    public async performDailyBackup(): Promise<void> {
        return this.performBackup('Daily backup', true, true);
    }

    private async performBackup(message: string, isDetailed: boolean = false, isDaily: boolean = false): Promise<void> {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            vscode.window.showWarningMessage('No workspace folder open for backup');
            return;
        }

        try {
            const projectPath = workspaceFolder.uri.fsPath;
            const projectName = path.basename(projectPath);
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            
            // 1. Save all open files
            await vscode.workspace.saveAll();

            // 2. Git operations (if enabled)
            const config = vscode.workspace.getConfiguration('devguard');
            if (config.get('autoCommitEnabled', true)) {
                await this.performGitOperations(projectPath, message);
            }

            // 3. Create external backup
            if (isDetailed || isDaily) {
                await this.createExternalBackup(projectPath, projectName, timestamp, message);
            }

            // 4. Update status
            vscode.window.showInformationMessage(`🛡️ DevGuard: Backup completed for ${projectName}`);

        } catch (error) {
            vscode.window.showErrorMessage(`DevGuard backup failed: ${error}`);
        }
    }

    private async performGitOperations(projectPath: string, message: string): Promise<void> {
        const config = vscode.workspace.getConfiguration('devguard');
        
        try {
            // Check if git repository
            await execAsync('git rev-parse --is-inside-work-tree', { cwd: projectPath });

            // Add all changes
            await execAsync('git add .', { cwd: projectPath });

            // Check if there are changes to commit
            const { stdout } = await execAsync('git status --porcelain', { cwd: projectPath });
            if (stdout.trim()) {
                // Commit changes
                const commitMessage = `DevGuard save: ${message} - ${new Date().toISOString()}`;
                await execAsync(`git commit -m "${commitMessage}"`, { cwd: projectPath });

                // Push to remote (if enabled)
                if (config.get('pushToRemote', true)) {
                    await execAsync('git push', { cwd: projectPath });
                }
            }
        } catch (error) {
            // Silent fail for git operations (project might not be a git repo)
            console.log('Git operations failed:', error);
        }
    }

    private async createExternalBackup(projectPath: string, projectName: string, timestamp: string, message: string): Promise<void> {
        const backupFileName = `${projectName}-${timestamp}.zip`;
        const backupFilePath = path.join(this.backupLocation, backupFileName);

        // Create backup using zip
        const excludePatterns = [
            'node_modules',
            '.git',
            'venv',
            '__pycache__',
            '*.log',
            'build',
            'dist',
            '.next',
            'coverage'
        ].map(pattern => `--exclude="${pattern}"`).join(' ');

        await execAsync(`zip -r "${backupFilePath}" . ${excludePatterns}`, { cwd: projectPath });

        // Create info file
        const infoFilePath = path.join(this.backupLocation, `${projectName}-${timestamp}-info.txt`);
        const info = `DevGuard Backup Info
Project: ${projectName}
Timestamp: ${new Date().toISOString()}
Message: ${message}
Source: ${projectPath}
Backup File: ${backupFileName}
`;
        await fs.promises.writeFile(infoFilePath, info);

        // Clean old backups
        await this.cleanOldBackups(projectName);
    }

    private async cleanOldBackups(projectName: string): Promise<void> {
        const config = vscode.workspace.getConfiguration('devguard');
        const retentionDays = config.get('backupRetentionDays', 5);
        const cutoffTime = Date.now() - (retentionDays * 24 * 60 * 60 * 1000);

        try {
            const files = await fs.promises.readdir(this.backupLocation);
            for (const file of files) {
                if (file.startsWith(projectName)) {
                    const filePath = path.join(this.backupLocation, file);
                    const stats = await fs.promises.stat(filePath);
                    
                    if (stats.mtime.getTime() < cutoffTime) {
                        await fs.promises.unlink(filePath);
                    }
                }
            }
        } catch (error) {
            console.log('Failed to clean old backups:', error);
        }
    }

    public openBackupLocation(): void {
        vscode.env.openExternal(vscode.Uri.file(this.backupLocation));
    }
}
```

### **5. Status Bar Integration (statusBar.ts)**
```typescript
import * as vscode from 'vscode';
import { BackupManager } from './backupManager';

export class StatusBarManager implements vscode.Disposable {
    private statusBarItem: vscode.StatusBarItem;

    constructor(private backupManager: BackupManager) {
        this.statusBarItem = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Right, 
            100
        );
    }

    public initialize() {
        this.statusBarItem.text = '🛡️ DevGuard';
        this.statusBarItem.tooltip = 'DevGuard Backup Protection - Click for options';
        this.statusBarItem.command = 'devguard.showStatus';
        this.statusBarItem.show();

        // Register status command
        vscode.commands.registerCommand('devguard.showStatus', () => {
            this.showStatusMenu();
        });
    }

    private async showStatusMenu() {
        const options = [
            { label: '🚀 Quick Save', detail: 'Perform immediate backup' },
            { label: '💾 Smart Save', detail: 'Backup with custom message' },
            { label: '📅 Daily Backup', detail: 'Complete daily backup' },
            { label: '📁 Open Backup Location', detail: 'View backup files' },
            { label: '⚙️ Settings', detail: 'Configure DevGuard' }
        ];

        const selected = await vscode.window.showQuickPick(options, {
            placeHolder: 'DevGuard - Choose backup action'
        });

        switch (selected?.label) {
            case '🚀 Quick Save':
                vscode.commands.executeCommand('devguard.quickSave');
                break;
            case '💾 Smart Save':
                vscode.commands.executeCommand('devguard.smartSave');
                break;
            case '📅 Daily Backup':
                vscode.commands.executeCommand('devguard.dailyBackup');
                break;
            case '📁 Open Backup Location':
                vscode.commands.executeCommand('devguard.openBackupLocation');
                break;
            case '⚙️ Settings':
                vscode.commands.executeCommand('workbench.action.openSettings', 'devguard');
                break;
        }
    }

    dispose() {
        this.statusBarItem.dispose();
    }
}
```

## 🎯 **Key Benefits**

1. **Universal Protection**: Works across all projects without setup
2. **Intelligent Detection**: Monitors your typing patterns for completion phrases
3. **Centralized Management**: All backups in one location
4. **Native Integration**: Seamless VSCode experience
5. **Configurable**: Extensive settings for customization
6. **Marketplace Ready**: Professional extension structure

## 🚀 **Installation & Usage**

1. Install from VSCode Marketplace
2. Configure backup location in settings
3. Customize completion phrases
4. Start coding - DevGuard automatically protects your work!

**Hot Keys:**
- `Ctrl+Shift+S` (Cmd+Shift+S on Mac): Quick Save
- `Ctrl+Shift+Alt+S` (Cmd+Shift+Alt+S on Mac): Smart Save with Message

This extension provides bulletproof backup protection with zero project setup required! 