import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

export class VoiceControlPanel {
    public static currentPanel: VoiceControlPanel | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private _disposables: vscode.Disposable[] = [];

    public static createOrShow(extensionUri: vscode.Uri) {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;

        if (VoiceControlPanel.currentPanel) {
            VoiceControlPanel.currentPanel._panel.reveal(column);
            return;
        }

        const panel = vscode.window.createWebviewPanel(
            'cursorVoiceControl',
            'Cursor Voice Control',
            column || vscode.ViewColumn.One,
            {
                enableScripts: true,
                localResourceRoots: [vscode.Uri.joinPath(extensionUri, 'media')]
            }
        );

        VoiceControlPanel.currentPanel = new VoiceControlPanel(panel, extensionUri);
    }

    private constructor(panel: vscode.WebviewPanel, private readonly _extensionUri: vscode.Uri) {
        this._panel = panel;
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
        this._panel.webview.html = this._getHtmlForWebview();
        this._setWebviewMessageListener();
    }

    public static create(extensionUri: vscode.Uri): VoiceControlPanel {
        // For compatibility with the main extension
        return new VoiceControlPanel(null as any, extensionUri);
    }

    public show() {
        VoiceControlPanel.createOrShow(this._extensionUri);
    }

    public dispose() {
        VoiceControlPanel.currentPanel = undefined;
        if (this._panel) {
            this._panel.dispose();
        }
        while (this._disposables.length) {
            const x = this._disposables.pop();
            if (x) {
                x.dispose();
            }
        }
    }

    private _setWebviewMessageListener() {
        if (!this._panel) return;

        this._panel.webview.onDidReceiveMessage(
            (message: any) => {
                switch (message.command) {
                    case 'startVoiceAgent':
                        vscode.commands.executeCommand('cursorVoice.startVoiceAgent');
                        break;
                    case 'toggleDictation':
                        vscode.commands.executeCommand('cursorVoice.toggleDictation');
                        break;
                    case 'stopListening':
                        vscode.commands.executeCommand('cursorVoice.stopListening');
                        break;
                    case 'testMicrophone':
                        vscode.commands.executeCommand('cursorVoice.testMicrophone');
                        break;
                    case 'configureAPI':
                        vscode.commands.executeCommand('cursorVoice.configureAPI');
                        break;
                    case 'updateSetting':
                        this._updateSetting(message.setting, message.value);
                        break;
                    case 'getConfiguration':
                        this._sendConfiguration();
                        break;
                }
            },
            null,
            this._disposables
        );
    }

    private async _updateSetting(setting: string, value: any) {
        try {
            await vscode.workspace.getConfiguration('cursorVoice').update(setting, value, vscode.ConfigurationTarget.Global);
            vscode.window.showInformationMessage(`Updated ${setting}`);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to update setting: ${error}`);
        }
    }

    private _sendConfiguration() {
        if (!this._panel) return;

        const config = vscode.workspace.getConfiguration('cursorVoice');
        this._panel.webview.postMessage({
            command: 'configurationUpdate',
            configuration: {
                deepgramConfigured: !!config.get('deepgramApiKey'),
                openaiConfigured: !!config.get('openaiApiKey'),
                language: config.get('language', 'en-US'),
                sensitivity: config.get('sensitivity', 0.7),
                continuousListening: config.get('continuousListening', false),
                enableCodeContext: config.get('enableCodeContext', true),
                enableAIAssistance: config.get('enableAIAssistance', true),
                microphoneDevice: config.get('microphoneDevice', 'default')
            }
        });
    }

    private _getHtmlForWebview(): string {
        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Cursor Voice Control</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                    padding: 20px;
                    background-color: var(--vscode-editor-background);
                    color: var(--vscode-editor-foreground);
                    margin: 0;
                }
                .container {
                    max-width: 600px;
                    margin: 0 auto;
                }
                .section {
                    background-color: var(--vscode-editor-background);
                    border: 1px solid var(--vscode-panel-border);
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 20px;
                }
                .section h2 {
                    margin-top: 0;
                    color: var(--vscode-foreground);
                    border-bottom: 1px solid var(--vscode-panel-border);
                    padding-bottom: 10px;
                }
                .status-indicator {
                    display: inline-block;
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    margin-right: 8px;
                }
                .status-active { background-color: #4CAF50; }
                .status-inactive { background-color: #f44336; }
                .status-warning { background-color: #ff9800; }
                
                .btn {
                    background-color: var(--vscode-button-background);
                    color: var(--vscode-button-foreground);
                    border: none;
                    padding: 10px 20px;
                    border-radius: 4px;
                    cursor: pointer;
                    margin: 5px;
                    font-size: 14px;
                }
                .btn:hover {
                    background-color: var(--vscode-button-hoverBackground);
                }
                .btn-primary {
                    background-color: var(--vscode-button-background);
                }
                .btn-secondary {
                    background-color: var(--vscode-button-secondaryBackground);
                    color: var(--vscode-button-secondaryForeground);
                }
                
                .setting-row {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 15px;
                }
                .setting-label {
                    font-weight: 500;
                }
                .setting-control {
                    background-color: var(--vscode-input-background);
                    color: var(--vscode-input-foreground);
                    border: 1px solid var(--vscode-input-border);
                    padding: 5px 10px;
                    border-radius: 4px;
                    min-width: 150px;
                }
                
                .voice-commands {
                    background-color: var(--vscode-editor-background);
                    padding: 15px;
                    border-radius: 4px;
                    margin-top: 10px;
                }
                .command-list {
                    column-count: 2;
                    column-gap: 20px;
                }
                .command-item {
                    break-inside: avoid;
                    margin-bottom: 8px;
                    font-family: monospace;
                    font-size: 12px;
                }
                
                .quick-actions {
                    text-align: center;
                    margin-bottom: 20px;
                }
                .status-display {
                    text-align: center;
                    padding: 15px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    font-weight: 500;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="status-display" id="statusDisplay">
                    <span class="status-indicator status-inactive" id="statusIndicator"></span>
                    <span id="statusText">Voice Control Ready</span>
                </div>

                <div class="quick-actions">
                    <button class="btn btn-primary" onclick="startVoiceAgent()">
                        🎤 Start Voice Agent
                    </button>
                    <button class="btn btn-secondary" onclick="toggleDictation()">
                        ✏️ Toggle Dictation
                    </button>
                    <button class="btn btn-secondary" onclick="stopListening()">
                        ⏹️ Stop Listening
                    </button>
                </div>

                <div class="section">
                    <h2>🔧 Configuration</h2>
                    <div class="setting-row">
                        <span class="setting-label">Deepgram API:</span>
                        <span id="deepgramStatus">Not Configured</span>
                    </div>
                    <div class="setting-row">
                        <span class="setting-label">OpenAI API:</span>
                        <span id="openaiStatus">Not Configured</span>
                    </div>
                    <div class="setting-row">
                        <span class="setting-label">Language:</span>
                        <select class="setting-control" id="languageSelect" onchange="updateSetting('language', this.value)">
                            <option value="en-US">English (US)</option>
                            <option value="en-GB">English (UK)</option>
                            <option value="es-ES">Spanish</option>
                            <option value="fr-FR">French</option>
                            <option value="de-DE">German</option>
                            <option value="it-IT">Italian</option>
                            <option value="pt-BR">Portuguese (Brazil)</option>
                            <option value="zh-CN">Chinese (Simplified)</option>
                            <option value="ja-JP">Japanese</option>
                        </select>
                    </div>
                    <div class="setting-row">
                        <span class="setting-label">Sensitivity:</span>
                        <input type="range" class="setting-control" id="sensitivitySlider" 
                               min="0.1" max="1.0" step="0.1" value="0.7"
                               onchange="updateSetting('sensitivity', parseFloat(this.value))">
                        <span id="sensitivityValue">0.7</span>
                    </div>
                    <div class="setting-row">
                        <span class="setting-label">Continuous Listening:</span>
                        <input type="checkbox" id="continuousCheckbox" 
                               onchange="updateSetting('continuousListening', this.checked)">
                    </div>
                    <div class="setting-row">
                        <span class="setting-label">AI Assistance:</span>
                        <input type="checkbox" id="aiAssistanceCheckbox" 
                               onchange="updateSetting('enableAIAssistance', this.checked)">
                    </div>
                    <button class="btn btn-primary" onclick="configureAPI()">
                        Configure API Keys
                    </button>
                    <button class="btn btn-secondary" onclick="testMicrophone()">
                        Test Microphone
                    </button>
                </div>

                <div class="section">
                    <h2>🎙️ Voice Commands</h2>
                    <div class="voice-commands">
                        <div class="command-list">
                            <div class="command-item">"open file" - Open file dialog</div>
                            <div class="command-item">"save file" - Save current file</div>
                            <div class="command-item">"new file" - Create new file</div>
                            <div class="command-item">"close file" - Close current file</div>
                            <div class="command-item">"go to line [number]" - Navigate to line</div>
                            <div class="command-item">"find [text]" - Search in file</div>
                            <div class="command-item">"replace" - Find and replace</div>
                            <div class="command-item">"toggle sidebar" - Show/hide sidebar</div>
                            <div class="command-item">"open terminal" - Open terminal</div>
                            <div class="command-item">"run code" - Execute current file</div>
                            <div class="command-item">"format code" - Format document</div>
                            <div class="command-item">"comment" - Toggle line comment</div>
                            <div class="command-item">"copy line" - Duplicate line</div>
                            <div class="command-item">"delete line" - Delete current line</div>
                            <div class="command-item">"select all" - Select all text</div>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h2>⌨️ Keyboard Shortcuts</h2>
                    <div class="voice-commands">
                        <div class="command-item">Cmd/Ctrl + Shift + V - Start Voice Agent</div>
                        <div class="command-item">Cmd/Ctrl + Shift + D - Toggle Dictation</div>
                        <div class="command-item">Cmd/Ctrl + Alt + V - Execute Voice Command</div>
                        <div class="command-item">Alt + Space - Toggle Continuous Listening</div>
                    </div>
                </div>
            </div>

            <script>
                const vscode = acquireVsCodeApi();

                function startVoiceAgent() {
                    vscode.postMessage({ command: 'startVoiceAgent' });
                }

                function toggleDictation() {
                    vscode.postMessage({ command: 'toggleDictation' });
                }

                function stopListening() {
                    vscode.postMessage({ command: 'stopListening' });
                }

                function testMicrophone() {
                    vscode.postMessage({ command: 'testMicrophone' });
                }

                function configureAPI() {
                    vscode.postMessage({ command: 'configureAPI' });
                }

                function updateSetting(setting, value) {
                    vscode.postMessage({ 
                        command: 'updateSetting', 
                        setting: setting, 
                        value: value 
                    });
                    
                    if (setting === 'sensitivity') {
                        document.getElementById('sensitivityValue').textContent = value;
                    }
                }

                // Request initial configuration
                vscode.postMessage({ command: 'getConfiguration' });

                // Listen for configuration updates
                window.addEventListener('message', event => {
                    const message = event.data;
                    
                    if (message.command === 'configurationUpdate') {
                        updateUI(message.configuration);
                    }
                });

                function updateUI(config) {
                    // Update API status
                    document.getElementById('deepgramStatus').textContent = 
                        config.deepgramConfigured ? '✅ Configured' : '❌ Not Configured';
                    document.getElementById('openaiStatus').textContent = 
                        config.openaiConfigured ? '✅ Configured' : '❌ Not Configured';
                    
                    // Update controls
                    document.getElementById('languageSelect').value = config.language;
                    document.getElementById('sensitivitySlider').value = config.sensitivity;
                    document.getElementById('sensitivityValue').textContent = config.sensitivity;
                    document.getElementById('continuousCheckbox').checked = config.continuousListening;
                    document.getElementById('aiAssistanceCheckbox').checked = config.enableAIAssistance;
                }
            </script>
        </body>
        </html>`;
    }
} 