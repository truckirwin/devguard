import * as vscode from 'vscode';
import { VoiceControlManager } from './services/VoiceControlManager';
import { SpeechService } from './services/SpeechService';
import { CommandService } from './services/CommandService';
import { ConfigurationService } from './services/ConfigurationService';
import { VoiceControlPanel } from './ui/VoiceControlPanel';

let voiceControlManager: VoiceControlManager;
let speechService: SpeechService;
let commandService: CommandService;
let configurationService: ConfigurationService;
let voiceControlPanel: VoiceControlPanel;

export async function activate(context: vscode.ExtensionContext) {
    console.log('Cursor Voice Control extension is now active!');

    // Initialize services
    configurationService = new ConfigurationService();
    speechService = new SpeechService(configurationService);
    commandService = new CommandService();
    voiceControlManager = new VoiceControlManager(speechService, commandService, configurationService);
    voiceControlPanel = VoiceControlPanel.create(context.extensionUri);

    // Register commands
    registerCommands(context);

    // Setup status bar
    setupStatusBar(context);

    // Initialize voice control if auto-start is enabled
    const autoStart = vscode.workspace.getConfiguration('cursorVoice').get<boolean>('autoStart', false);
    if (autoStart) {
        await voiceControlManager.initialize();
    }

    // Show welcome message on first install
    showWelcomeMessage(context);
}

function registerCommands(context: vscode.ExtensionContext) {
    const commands = [
        vscode.commands.registerCommand('cursorVoice.startVoiceAgent', async () => {
            try {
                await voiceControlManager.startVoiceAgent();
                vscode.window.showInformationMessage('Voice Agent started. Say "Hey Cursor" to begin.');
            } catch (error) {
                vscode.window.showErrorMessage(`Failed to start Voice Agent: ${error}`);
            }
        }),

        vscode.commands.registerCommand('cursorVoice.toggleDictation', async () => {
            try {
                await voiceControlManager.toggleDictation();
            } catch (error) {
                vscode.window.showErrorMessage(`Failed to toggle dictation: ${error}`);
            }
        }),

        vscode.commands.registerCommand('cursorVoice.openControlPanel', async () => {
            voiceControlPanel.show();
        }),

        vscode.commands.registerCommand('cursorVoice.configureAPI', async () => {
            await configureAPIKeys();
        }),

        vscode.commands.registerCommand('cursorVoice.executeVoiceCommand', async () => {
            try {
                await voiceControlManager.executeVoiceCommand();
            } catch (error) {
                vscode.window.showErrorMessage(`Failed to execute voice command: ${error}`);
            }
        }),

        vscode.commands.registerCommand('cursorVoice.startContinuousListening', async () => {
            try {
                await voiceControlManager.startContinuousListening();
                vscode.window.showInformationMessage('Continuous listening enabled. Press Alt+Space to toggle.');
            } catch (error) {
                vscode.window.showErrorMessage(`Failed to start continuous listening: ${error}`);
            }
        }),

        vscode.commands.registerCommand('cursorVoice.stopListening', async () => {
            voiceControlManager.stopListening();
            vscode.window.showInformationMessage('Voice listening stopped.');
        }),

        vscode.commands.registerCommand('cursorVoice.testMicrophone', async () => {
            try {
                const result = await speechService.testMicrophone();
                if (result.success) {
                    vscode.window.showInformationMessage(`Microphone test successful: ${result.message}`);
                } else {
                    vscode.window.showWarningMessage(`Microphone test failed: ${result.message}`);
                }
            } catch (error) {
                vscode.window.showErrorMessage(`Microphone test error: ${error}`);
            }
        })
    ];

    commands.forEach(command => context.subscriptions.push(command));
}

function setupStatusBar(context: vscode.ExtensionContext) {
    const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.command = 'cursorVoice.openControlPanel';
    statusBarItem.text = '$(mic) Voice';
    statusBarItem.tooltip = 'Cursor Voice Control - Click to open control panel';
    statusBarItem.show();

    context.subscriptions.push(statusBarItem);

    // Update status bar based on voice control state
    voiceControlManager.onStateChange((state) => {
        switch (state) {
            case 'listening':
                statusBarItem.text = '$(mic-filled) Listening';
                statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.activeBackground');
                break;
            case 'processing':
                statusBarItem.text = '$(sync~spin) Processing';
                statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
                break;
            case 'idle':
                statusBarItem.text = '$(mic) Voice';
                statusBarItem.backgroundColor = undefined;
                break;
            case 'error':
                statusBarItem.text = '$(error) Voice Error';
                statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
                break;
        }
    });
}

async function configureAPIKeys() {
    const quickPick = vscode.window.createQuickPick();
    quickPick.items = [
        { label: 'Deepgram API Key', description: 'Configure speech recognition service' },
        { label: 'OpenAI API Key', description: 'Configure AI assistance service' }
    ];
    quickPick.placeholder = 'Select API key to configure';

    quickPick.onDidChangeSelection(async (selection) => {
        if (selection[0]) {
            const selected = selection[0].label;
            const configKey = selected === 'Deepgram API Key' ? 'deepgramApiKey' : 'openaiApiKey';
            const serviceName = selected === 'Deepgram API Key' ? 'Deepgram' : 'OpenAI';
            
            const apiKey = await vscode.window.showInputBox({
                prompt: `Enter your ${serviceName} API key`,
                password: true,
                ignoreFocusOut: true,
                validateInput: (value) => {
                    if (!value || value.trim().length === 0) {
                        return 'API key cannot be empty';
                    }
                    return null;
                }
            });

            if (apiKey) {
                await vscode.workspace.getConfiguration('cursorVoice').update(configKey, apiKey, vscode.ConfigurationTarget.Global);
                vscode.window.showInformationMessage(`${serviceName} API key configured successfully!`);
            }
        }
        quickPick.hide();
    });

    quickPick.onDidHide(() => quickPick.dispose());
    quickPick.show();
}

function showWelcomeMessage(context: vscode.ExtensionContext) {
    const hasShownWelcome = context.globalState.get<boolean>('hasShownWelcome', false);
    
    if (!hasShownWelcome) {
        vscode.window.showInformationMessage(
            'Welcome to Cursor Voice Control! Configure your API keys to get started.',
            'Configure APIs',
            'Show Guide'
        ).then(selection => {
            if (selection === 'Configure APIs') {
                vscode.commands.executeCommand('cursorVoice.configureAPI');
            } else if (selection === 'Show Guide') {
                vscode.commands.executeCommand('cursorVoice.openControlPanel');
            }
        });
        
        context.globalState.update('hasShownWelcome', true);
    }
}

export function deactivate() {
    if (voiceControlManager) {
        voiceControlManager.dispose();
    }
    if (speechService) {
        speechService.dispose();
    }
} 