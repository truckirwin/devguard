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
    const quickSave = vscode.commands.registerCommand('devguard.quickSave', async () => {
        try {
            await backupManager.performQuickSave();
            showNotification('🛡️ DevGuard: Quick save completed!');
        } catch (error) {
            vscode.window.showErrorMessage(`DevGuard Quick Save failed: ${error}`);
        }
    });

    const smartSave = vscode.commands.registerCommand('devguard.smartSave', async () => {
        try {
            const message = await vscode.window.showInputBox({
                prompt: 'Enter backup message',
                placeHolder: 'Describe what was accomplished...',
                validateInput: (value) => {
                    return value && value.trim().length > 0 ? null : 'Please enter a message';
                }
            });
            if (message) {
                await backupManager.performSmartSave(message);
                showNotification(`🛡️ DevGuard: Smart save completed - "${message}"`);
            }
        } catch (error) {
            vscode.window.showErrorMessage(`DevGuard Smart Save failed: ${error}`);
        }
    });

    const dailyBackup = vscode.commands.registerCommand('devguard.dailyBackup', async () => {
        try {
            await backupManager.performDailyBackup();
            showNotification('🛡️ DevGuard: Daily backup completed!');
        } catch (error) {
            vscode.window.showErrorMessage(`DevGuard Daily Backup failed: ${error}`);
        }
    });

    const openBackupLocation = vscode.commands.registerCommand('devguard.openBackupLocation', () => {
        backupManager.openBackupLocation();
    });

    const toggleEnabled = vscode.commands.registerCommand('devguard.toggleEnabled', async () => {
        const config = vscode.workspace.getConfiguration('devguard');
        const currentState = config.get('enabled', true);
        await config.update('enabled', !currentState, vscode.ConfigurationTarget.Global);
        
        const newState = !currentState ? 'enabled' : 'disabled';
        showNotification(`🛡️ DevGuard protection ${newState}`);
        statusBar.updateStatus();
    });

    const showStatus = vscode.commands.registerCommand('devguard.showStatus', async () => {
        await statusBar.showDetailedStatus();
    });

    // Initialize components
    phraseDetector.start();
    statusBar.initialize();

    // Subscribe to configuration changes
    const configChange = vscode.workspace.onDidChangeConfiguration((event) => {
        if (event.affectsConfiguration('devguard')) {
            statusBar.updateStatus();
            if (event.affectsConfiguration('devguard.enabled')) {
                const enabled = vscode.workspace.getConfiguration('devguard').get('enabled', true);
                if (enabled) {
                    phraseDetector.start();
                    showNotification('🛡️ DevGuard protection enabled');
                } else {
                    phraseDetector.stop();
                    showNotification('🛡️ DevGuard protection disabled');
                }
            }
        }
    });

    // Add all disposables to context
    context.subscriptions.push(
        quickSave,
        smartSave,
        dailyBackup,
        openBackupLocation,
        toggleEnabled,
        showStatus,
        configChange,
        phraseDetector,
        statusBar
    );

    // Show welcome message on first install
    const hasShownWelcome = context.globalState.get('devguard.hasShownWelcome', false);
    if (!hasShownWelcome) {
        showWelcomeMessage(context);
    }

    console.log('🛡️ DevGuard extension ready - Your code is now protected!');
}

export function deactivate() {
    console.log('🛡️ DevGuard extension deactivated');
}

function showNotification(message: string) {
    const config = vscode.workspace.getConfiguration('devguard');
    if (config.get('showNotifications', true)) {
        vscode.window.showInformationMessage(message);
    }
}

async function showWelcomeMessage(context: vscode.ExtensionContext) {
    const action = await vscode.window.showInformationMessage(
        '🛡️ Welcome to DevGuard! Your code is now protected with intelligent backup. Configure your settings?',
        'Open Settings',
        'Learn More',
        'Not Now'
    );

    switch (action) {
        case 'Open Settings':
            vscode.commands.executeCommand('workbench.action.openSettings', 'devguard');
            break;
        case 'Learn More':
            vscode.env.openExternal(vscode.Uri.parse('https://github.com/devguard/vscode-extension#readme'));
            break;
    }

    await context.globalState.update('devguard.hasShownWelcome', true);
} 