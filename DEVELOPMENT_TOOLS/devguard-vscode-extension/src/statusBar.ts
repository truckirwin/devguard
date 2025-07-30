import * as vscode from 'vscode';
import { BackupManager } from './backupManager';

export class StatusBarManager implements vscode.Disposable {
    private statusBarItem: vscode.StatusBarItem;
    private lastBackupTime: Date | undefined;
    private updateInterval: any;

    constructor(private backupManager: BackupManager) {
        this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
        this.statusBarItem.command = 'devguard.showStatus';
    }

    public initialize(): void {
        this.updateStatus();
        this.statusBarItem.show();
        
        // Update status every 30 seconds
        this.updateInterval = setInterval(() => {
            this.updateStatus();
        }, 30000);
    }

    public updateStatus(): void {
        const config = vscode.workspace.getConfiguration('devguard');
        const enabled = config.get('enabled', true);
        
        if (!enabled) {
            this.statusBarItem.text = '🛡️ DevGuard (Disabled)';
            this.statusBarItem.tooltip = 'DevGuard protection is disabled. Click to enable.';
            this.statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
            this.statusBarItem.command = 'devguard.toggleEnabled';
            return;
        }

        // Get workspace info
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            this.statusBarItem.text = '🛡️ DevGuard (No Workspace)';
            this.statusBarItem.tooltip = 'DevGuard requires a workspace to provide protection';
            this.statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
            this.statusBarItem.command = 'devguard.showStatus';
            return;
        }

        // Normal status
        this.statusBarItem.text = '🛡️ DevGuard';
        this.statusBarItem.tooltip = this.getStatusTooltip();
        this.statusBarItem.backgroundColor = undefined;
        this.statusBarItem.command = 'devguard.showStatus';
    }

    private getStatusTooltip(): string {
        const config = vscode.workspace.getConfiguration('devguard');
        const phrases = config.get('completionPhrases', []) as string[];
        const backupLocation = this.backupManager.getBackupLocationPath();
        
        let tooltip = `DevGuard Protection Active\n`;
        tooltip += `Backup Location: ${backupLocation}\n`;
        tooltip += `Monitoring ${phrases.length} completion phrases\n`;
        tooltip += `Auto-commit: ${config.get('autoCommitEnabled', true) ? 'Enabled' : 'Disabled'}\n`;
        tooltip += `Push to remote: ${config.get('pushToRemote', true) ? 'Enabled' : 'Disabled'}\n`;
        
        if (this.lastBackupTime) {
            const timeDiff = Date.now() - this.lastBackupTime.getTime();
            const minutes = Math.floor(timeDiff / 60000);
            const hours = Math.floor(minutes / 60);
            
            if (hours > 0) {
                tooltip += `Last backup: ${hours}h ${minutes % 60}m ago`;
            } else if (minutes > 0) {
                tooltip += `Last backup: ${minutes}m ago`;
            } else {
                tooltip += `Last backup: Just now`;
            }
        } else {
            tooltip += `No backups yet`;
        }

        tooltip += `\n\nClick for backup status details`;
        return tooltip;
    }

    public async showDetailedStatus(): Promise<void> {
        const config = vscode.workspace.getConfiguration('devguard');
        const enabled = config.get('enabled', true);
        
        if (!enabled) {
            const action = await vscode.window.showInformationMessage(
                '🛡️ DevGuard protection is currently disabled',
                'Enable Protection',
                'Open Settings'
            );
            
            if (action === 'Enable Protection') {
                await vscode.commands.executeCommand('devguard.toggleEnabled');
            } else if (action === 'Open Settings') {
                vscode.commands.executeCommand('workbench.action.openSettings', 'devguard');
            }
            return;
        }

        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            vscode.window.showInformationMessage('🛡️ DevGuard requires a workspace to provide protection');
            return;
        }

        try {
            const stats = await this.backupManager.getBackupStats();
            const backupLocation = this.backupManager.getBackupLocationPath();
            
            const totalSizeMB = (stats.totalSize / (1024 * 1024)).toFixed(2);
            
            let message = `🛡️ DevGuard Backup Status\n\n`;
            message += `📁 Backup Location: ${backupLocation}\n`;
            message += `📦 Total Backups: ${stats.totalBackups}\n`;
            message += `💾 Total Size: ${totalSizeMB} MB\n`;
            
            if (stats.oldestBackup) {
                message += `🕐 Oldest: ${stats.oldestBackup.toLocaleDateString()}\n`;
            }
            if (stats.newestBackup) {
                message += `🕐 Newest: ${stats.newestBackup.toLocaleDateString()}\n`;
            }
            
            message += `\n⚙️ Configuration:\n`;
            message += `• Auto-commit: ${config.get('autoCommitEnabled', true) ? '✅' : '❌'}\n`;
            message += `• Push to remote: ${config.get('pushToRemote', true) ? '✅' : '❌'}\n`;
            message += `• Retention: ${config.get('backupRetentionDays', 5)} days\n`;
            message += `• Phrases: ${(config.get('completionPhrases', []) as string[]).length} monitored\n`;

            const action = await vscode.window.showInformationMessage(
                message,
                'Open Backup Folder',
                'Quick Save',
                'Smart Save',
                'Settings'
            );

            switch (action) {
                case 'Open Backup Folder':
                    this.backupManager.openBackupLocation();
                    break;
                case 'Quick Save':
                    await vscode.commands.executeCommand('devguard.quickSave');
                    break;
                case 'Smart Save':
                    await vscode.commands.executeCommand('devguard.smartSave');
                    break;
                case 'Settings':
                    vscode.commands.executeCommand('workbench.action.openSettings', 'devguard');
                    break;
            }

        } catch (error) {
            vscode.window.showErrorMessage(`Failed to get backup status: ${error}`);
        }
    }

    public notifyBackupCompleted(): void {
        this.lastBackupTime = new Date();
        this.updateStatus();
    }

    public dispose(): void {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        this.statusBarItem.dispose();
    }
} 