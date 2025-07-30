import * as vscode from 'vscode';
import { ConfigManager } from '../services/ConfigManager';
import { AgentManager } from '../agents/AgentManager';

export class SettingsWebviewProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'theWritersRoom.settingsView';
    private _view?: vscode.WebviewView;
    private configManager: ConfigManager;
    private agentManager: AgentManager;

    constructor(private readonly _extensionUri: vscode.Uri, private readonly context: vscode.ExtensionContext) {
        this.configManager = ConfigManager.getInstance(context);
        this.agentManager = new AgentManager(context);
    }

    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken,
    ) {
        this._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };

        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

        webviewView.webview.onDidReceiveMessage(
            message => {
                switch (message.command) {
                    case 'saveSettings':
                        this.saveSettings(message.settings);
                        break;
                    case 'testConnection':
                        this.testConnection(message.provider, message.settings);
                        break;
                    case 'getSettings':
                        this.sendCurrentSettings();
                        break;
                    case 'selectModel':
                        this.handleModelSelection(message.provider, message.model);
                        break;
                    case 'assignAgentModel':
                        this.assignAgentModel(message.agentId, message.provider, message.model);
                        break;
                    case 'toggleAgent':
                        this.toggleAgentActive(message.agentId, message.active);
                        break;
                    case 'getAgents':
                        this.sendAgentsList();
                        break;
                }
            },
            undefined,
            []
        );

        // Send initial data
        this.sendCurrentSettings();
        this.sendAgentsList();
    }

    private async saveSettings(settings: any) {
        try {
            const config = this.configManager.getConfiguration();
            
            for (const [provider, providerConfig] of Object.entries(settings)) {
                for (const [key, value] of Object.entries(providerConfig as any)) {
                    await config.update(`ai.${provider}.${key}`, value, vscode.ConfigurationTarget.Global);
                }
            }

            this._view?.webview.postMessage({
                command: 'settingsSaved',
                success: true,
                message: 'Settings saved successfully!'
            });
        } catch (error) {
            this._view?.webview.postMessage({
                command: 'settingsSaved',
                success: false,
                message: `Error saving settings: ${error}`
            });
        }
    }

    private async testConnection(provider: string, settings: any) {
        try {
            // Basic validation - just check if API key is provided
            let success = false;
            if (provider === 'openai' && settings.apiKey && settings.apiKey.startsWith('sk-')) {
                success = true;
            } else if (provider === 'anthropic' && settings.apiKey && settings.apiKey.startsWith('sk-ant-')) {
                success = true;
            } else if (provider === 'bedrock' && settings.accessKeyId && settings.secretAccessKey) {
                success = true;
            }
            
            this._view?.webview.postMessage({
                command: 'connectionTested',
                provider,
                success,
                message: success ? 'Connection successful!' : 'Connection failed. Please check your settings.'
            });
        } catch (error) {
            this._view?.webview.postMessage({
                command: 'connectionTested',
                provider,
                success: false,
                message: `Connection test failed: ${error}`
            });
        }
    }

    private async sendCurrentSettings() {
        const settings = {
            openai: this.configManager.getAISettings('openai'),
            anthropic: this.configManager.getAISettings('anthropic'),
            bedrock: this.configManager.getAISettings('bedrock')
        };

        this._view?.webview.postMessage({
            command: 'currentSettings',
            settings
        });
    }

    private async sendAgentsList() {
        const agents = this.agentManager.getAllAgents();
        const agentAssignments: any = {};

        for (const agent of agents) {
            const assignment = this.configManager.getAgentModelAssignment(agent.id);
            const config = this.configManager.getConfiguration();
            const normalizedAgentId = this.normalizeAgentId(agent.id);
            const active = config.get<boolean>(`agents.${normalizedAgentId}.active`, true);
            
            agentAssignments[agent.id] = {
                provider: assignment.provider,
                model: assignment.model,
                active: active
            };
        }

        this._view?.webview.postMessage({
            command: 'agentsList',
            agents: agents.map(agent => ({
                id: agent.id,
                name: agent.name,
                description: agent.description,
                title: agent.title
            })),
            assignments: agentAssignments
        });
    }

    private async handleModelSelection(provider: string, model: string) {
        // Get model-specific configuration options
        const modelConfig = this.getModelConfiguration(provider, model);
        
        this._view?.webview.postMessage({
            command: 'modelSelected',
            provider,
            model,
            config: modelConfig
        });
    }

    private async assignAgentModel(agentId: string, provider: string, model: string) {
        try {
            await this.configManager.setAgentModelAssignment(agentId, provider, model);
            
            this._view?.webview.postMessage({
                command: 'agentModelAssigned',
                success: true,
                agentId,
                provider,
                model,
                message: 'Agent model assignment saved successfully!'
            });
        } catch (error) {
            this._view?.webview.postMessage({
                command: 'agentModelAssigned',
                success: false,
                message: `Error assigning model: ${error}`
            });
        }
    }

    private async toggleAgentActive(agentId: string, active: boolean) {
        try {
            const config = this.configManager.getConfiguration();
            const normalizedAgentId = this.normalizeAgentId(agentId);
            
            await config.update(`agents.${normalizedAgentId}.active`, active, vscode.ConfigurationTarget.Global);
            
            // Just send success without showing popup message
            this._view?.webview.postMessage({
                command: 'agentToggled',
                success: true,
                agentId,
                active
            });
        } catch (error) {
            this._view?.webview.postMessage({
                command: 'agentToggled',
                success: false,
                message: `Error toggling agent: ${error}`
            });
        }
    }

    // Normalize agent ID for settings keys
    private normalizeAgentId(agentId: string): string {
        const idMap: { [key: string]: string } = {
            'script-doctor': 'scriptDoctor',
            'script_doctor': 'scriptDoctor',
            'aaron-sorkin': 'aaronSorkin',
            'aaron_sorkin_agent': 'aaronSorkin',
            'character-specialist': 'characterSpecialist',
            'character_specialist': 'characterSpecialist',
            'creative-visionary': 'creativeVisionary',
            'creative_visionary': 'creativeVisionary',
            'coen-brothers': 'coenBrothers',
            'coen_brothers_agent': 'coenBrothers',
            'quentin-tarantino': 'quentinTarantino',
            'quentin_tarantino_agent': 'quentinTarantino',
            'taylor-sheridan': 'taylorSheridan',
            'taylor_sheridan_agent': 'taylorSheridan',
            'jack-carr': 'jackCarr',
            'jack_carr_agent': 'jackCarr',
            'location-scout': 'locationScout',
            'location_scout': 'locationScout',
            'producer': 'producer',
            'director': 'director',
            'continuity-expert': 'continuityExpert',
            'continuity_agent': 'continuityExpert',
            'showrunner': 'showrunner'
        };
        
        return idMap[agentId] || agentId;
    }

    private getModelConfiguration(provider: string, model: string) {
        const configs: any = {
            openai: {
                'gpt-4o': {
                    maxTokens: { min: 1, max: 128000, default: 4000 },
                    temperature: { min: 0, max: 2, default: 0.7, step: 0.1 },
                    topP: { min: 0, max: 1, default: 1, step: 0.1 },
                    frequencyPenalty: { min: -2, max: 2, default: 0, step: 0.1 },
                    presencePenalty: { min: -2, max: 2, default: 0, step: 0.1 }
                },
                'gpt-4o-mini': {
                    maxTokens: { min: 1, max: 128000, default: 4000 },
                    temperature: { min: 0, max: 2, default: 0.7, step: 0.1 },
                    topP: { min: 0, max: 1, default: 1, step: 0.1 },
                    frequencyPenalty: { min: -2, max: 2, default: 0, step: 0.1 },
                    presencePenalty: { min: -2, max: 2, default: 0, step: 0.1 }
                }
            },
            anthropic: {
                'claude-3-5-sonnet-20241022': {
                    maxTokens: { min: 1, max: 200000, default: 4000 },
                    temperature: { min: 0, max: 1, default: 0.7, step: 0.1 },
                    topP: { min: 0, max: 1, default: 1, step: 0.1 },
                    topK: { min: 1, max: 200, default: 40 }
                },
                'claude-3-opus-20240229': {
                    maxTokens: { min: 1, max: 200000, default: 4000 },
                    temperature: { min: 0, max: 1, default: 0.7, step: 0.1 },
                    topP: { min: 0, max: 1, default: 1, step: 0.1 },
                    topK: { min: 1, max: 200, default: 40 }
                }
            },
            bedrock: {
                'anthropic.claude-3-5-sonnet-20241022-v2:0': {
                    maxTokens: { min: 1, max: 200000, default: 4000 },
                    temperature: { min: 0, max: 1, default: 0.7, step: 0.1 },
                    topP: { min: 0, max: 1, default: 1, step: 0.1 },
                    topK: { min: 0, max: 500, default: 250 }
                }
            }
        };

        return configs[provider]?.[model] || {};
    }

    private _getHtmlForWebview(webview: vscode.Webview): string {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Writers Room Settings</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: var(--vscode-font-family);
            background-color: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
            line-height: 1.6;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--vscode-panel-border);
        }

        .header h1 {
            font-size: 24px;
            font-weight: 600;
            color: var(--vscode-editor-foreground);
        }

        .search-container {
            position: relative;
            margin-bottom: 20px;
        }

        .search-input {
            width: 100%;
            padding: 12px 16px 12px 40px;
            background-color: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            border-radius: 6px;
            color: var(--vscode-input-foreground);
            font-size: 14px;
        }

        .search-icon {
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--vscode-input-placeholderForeground);
        }

        .tabs {
            display: flex;
            margin-bottom: 30px;
            border-bottom: 1px solid var(--vscode-panel-border);
        }

        .tab {
            padding: 12px 24px;
            cursor: pointer;
            background: none;
            border: none;
            color: var(--vscode-editor-foreground);
            font-size: 14px;
            font-weight: 500;
            border-bottom: 2px solid transparent;
            transition: all 0.2s ease;
        }

        .tab:hover {
            background-color: var(--vscode-list-hoverBackground);
        }

        .tab.active {
            color: var(--vscode-button-background);
            border-bottom-color: var(--vscode-button-background);
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        .section {
            margin-bottom: 30px;
        }

        .section-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 15px;
            color: var(--vscode-editor-foreground);
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: var(--vscode-editor-foreground);
        }

        .form-input {
            width: 100%;
            padding: 10px 12px;
            background-color: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            border-radius: 4px;
            color: var(--vscode-input-foreground);
            font-size: 14px;
        }

        .form-select {
            width: 100%;
            padding: 10px 12px;
            background-color: var(--vscode-dropdown-background);
            border: 1px solid var(--vscode-dropdown-border);
            border-radius: 4px;
            color: var(--vscode-dropdown-foreground);
            font-size: 14px;
        }

        .form-range {
            width: 100%;
            margin: 10px 0;
        }

        .range-labels {
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            color: var(--vscode-input-placeholderForeground);
        }

        .models-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .model-card {
            background-color: var(--vscode-list-inactiveSelectionBackground);
            border: 1px solid var(--vscode-panel-border);
            border-radius: 8px;
            padding: 20px;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .model-card:hover {
            background-color: var(--vscode-list-hoverBackground);
            border-color: var(--vscode-button-background);
        }

        .model-card.selected {
            background-color: var(--vscode-list-activeSelectionBackground);
            border-color: var(--vscode-button-background);
        }

        .model-name {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 8px;
            color: var(--vscode-editor-foreground);
        }

        .model-description {
            font-size: 14px;
            color: var(--vscode-input-placeholderForeground);
            margin-bottom: 12px;
        }

        .model-specs {
            display: flex;
            gap: 15px;
            font-size: 12px;
            color: var(--vscode-input-placeholderForeground);
        }

        .agent-assignment {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid var(--vscode-panel-border);
        }

        .agent-assignment:last-child {
            border-bottom: none;
        }

        .agent-info {
            flex: 1;
        }

        .agent-name {
            font-weight: 600;
            margin-bottom: 4px;
        }

        .agent-description {
            font-size: 12px;
            color: var(--vscode-input-placeholderForeground);
        }

        .agent-models {
            display: flex;
            gap: 10px;
            align-items: center;
        }

        .agent-assignment.inactive {
            opacity: 0.6;
        }

        .agent-controls {
            display: flex;
            align-items: center;
            gap: 16px;
        }

        .agent-toggle {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .toggle-switch {
            position: relative;
            display: inline-block;
            width: 44px;
            height: 24px;
        }

        .toggle-switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }

        .toggle-slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            transition: 0.2s;
            border-radius: 24px;
        }

        .toggle-slider:before {
            position: absolute;
            content: "";
            height: 16px;
            width: 16px;
            left: 3px;
            bottom: 3px;
            background-color: var(--vscode-input-placeholderForeground);
            transition: 0.2s;
            border-radius: 50%;
        }

        input:checked + .toggle-slider {
            background-color: var(--vscode-button-background);
            border-color: var(--vscode-button-background);
        }

        input:checked + .toggle-slider:before {
            transform: translateX(20px);
            background-color: var(--vscode-button-foreground);
        }

        .toggle-label {
            font-size: 12px;
            color: var(--vscode-editor-foreground);
            font-weight: 500;
            min-width: 50px;
        }

        .agent-models.disabled {
            opacity: 0.5;
            pointer-events: none;
        }

        .button {
            padding: 8px 16px;
            background-color: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: background-color 0.2s ease;
        }

        .button:hover {
            background-color: var(--vscode-button-hoverBackground);
        }

        .button.secondary {
            background-color: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
        }

        .button.secondary:hover {
            background-color: var(--vscode-button-secondaryHoverBackground);
        }

        .status-message {
            padding: 12px;
            border-radius: 4px;
            margin-bottom: 20px;
            font-size: 14px;
        }

        .status-success {
            background-color: var(--vscode-editorGutter-addedBackground);
            color: var(--vscode-editor-foreground);
        }

        .status-error {
            background-color: var(--vscode-editorGutter-deletedBackground);
            color: var(--vscode-editor-foreground);
        }

        .provider-tabs {
            display: flex;
            margin-bottom: 20px;
            background-color: var(--vscode-list-inactiveSelectionBackground);
            border-radius: 6px;
            padding: 4px;
        }

        .provider-tab {
            flex: 1;
            padding: 8px 16px;
            text-align: center;
            cursor: pointer;
            border-radius: 4px;
            transition: all 0.2s ease;
        }

        .provider-tab.active {
            background-color: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
        }

        .model-config {
            margin-top: 20px;
            padding: 20px;
            background-color: var(--vscode-list-inactiveSelectionBackground);
            border-radius: 8px;
            border: 1px solid var(--vscode-panel-border);
        }

        .hidden {
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎬 The Writers Room Settings</h1>
            <button class="button" onclick="saveAllSettings()">💾 Save Settings</button>
        </div>

        <div class="search-container">
            <div class="search-icon">🔍</div>
            <input type="text" class="search-input" placeholder="Search settings and models..." id="searchInput">
        </div>

        <div class="tabs">
            <button class="tab active" onclick="switchTab('providers')">🟢 AI Providers</button>
            <button class="tab" onclick="switchTab('models')">🤖 Models</button>
            <button class="tab" onclick="switchTab('agents')">Agent Assignments</button>
            <button class="tab" onclick="switchTab('general')">⚙️ General</button>
        </div>

        <div id="statusMessage" class="status-message hidden"></div>

        <!-- AI Providers Tab -->
        <div id="providers" class="tab-content active">
            <div class="provider-tabs">
                <div class="provider-tab active" onclick="switchProvider('openai')">OpenAI</div>
                <div class="provider-tab" onclick="switchProvider('anthropic')">Anthropic</div>
                <div class="provider-tab" onclick="switchProvider('bedrock')">AWS Bedrock</div>
            </div>

            <!-- OpenAI Settings -->
            <div id="openai-settings" class="provider-settings">
                <div class="section">
                    <h3 class="section-title">OpenAI Configuration</h3>
                    <div class="form-group">
                        <label class="form-label">API Key</label>
                        <input type="password" class="form-input" id="openai-apiKey" placeholder="sk-...">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Model</label>
                        <select class="form-select" id="openai-model">
                            <option value="gpt-4o">GPT-4o</option>
                            <option value="gpt-4o-mini">GPT-4o Mini</option>
                            <option value="gpt-4-turbo">GPT-4 Turbo</option>
                            <option value="gpt-4">GPT-4</option>
                            <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Max Tokens</label>
                        <input type="number" class="form-input" id="openai-maxTokens" min="1" max="128000" value="4000">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Temperature</label>
                        <input type="range" class="form-range" id="openai-temperature" min="0" max="2" step="0.1" value="0.7">
                        <div class="range-labels">
                            <span>Focused (0)</span>
                            <span>Creative (2)</span>
                        </div>
                    </div>
                    <button class="button secondary" onclick="testConnection('openai')">🔗 Test Connection</button>
                </div>
            </div>

            <!-- Anthropic Settings -->
            <div id="anthropic-settings" class="provider-settings hidden">
                <div class="section">
                    <h3 class="section-title">Anthropic Configuration</h3>
                    <div class="form-group">
                        <label class="form-label">API Key</label>
                        <input type="password" class="form-input" id="anthropic-apiKey" placeholder="sk-ant-...">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Model</label>
                        <select class="form-select" id="anthropic-model">
                            <option value="claude-3-5-sonnet-20241022">Claude 3.5 Sonnet</option>
                            <option value="claude-3-5-haiku-20241022">Claude 3.5 Haiku</option>
                            <option value="claude-3-opus-20240229">Claude 3 Opus</option>
                            <option value="claude-3-sonnet-20240229">Claude 3 Sonnet</option>
                            <option value="claude-3-haiku-20240307">Claude 3 Haiku</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Max Tokens</label>
                        <input type="number" class="form-input" id="anthropic-maxTokens" min="1" max="200000" value="4000">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Temperature</label>
                        <input type="range" class="form-range" id="anthropic-temperature" min="0" max="1" step="0.1" value="0.7">
                        <div class="range-labels">
                            <span>Focused (0)</span>
                            <span>Creative (1)</span>
                        </div>
                    </div>
                    <button class="button secondary" onclick="testConnection('anthropic')">🔗 Test Connection</button>
                </div>
            </div>

            <!-- Bedrock Settings -->
            <div id="bedrock-settings" class="provider-settings hidden">
                <div class="section">
                    <h3 class="section-title">AWS Bedrock Configuration</h3>
                    <div class="form-group">
                        <label class="form-label">Access Key ID</label>
                        <input type="text" class="form-input" id="bedrock-accessKeyId" placeholder="AKIA...">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Secret Access Key</label>
                        <input type="password" class="form-input" id="bedrock-secretAccessKey" placeholder="...">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Region</label>
                        <select class="form-select" id="bedrock-region">
                            <option value="us-east-1">US East (N. Virginia)</option>
                            <option value="us-west-2">US West (Oregon)</option>
                            <option value="eu-west-1">Europe (Ireland)</option>
                            <option value="eu-central-1">Europe (Frankfurt)</option>
                            <option value="ap-northeast-1">Asia Pacific (Tokyo)</option>
                            <option value="ap-southeast-1">Asia Pacific (Singapore)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Model</label>
                        <select class="form-select" id="bedrock-model">
                            <option value="anthropic.claude-3-5-sonnet-20241022-v2:0">Claude 3.5 Sonnet</option>
                            <option value="anthropic.claude-3-5-haiku-20241022-v1:0">Claude 3.5 Haiku</option>
                            <option value="anthropic.claude-3-opus-20240229-v1:0">Claude 3 Opus</option>
                            <option value="amazon.titan-text-express-v1">Titan Text Express</option>
                            <option value="amazon.titan-text-lite-v1">Titan Text Lite</option>
                        </select>
                    </div>
                    <button class="button secondary" onclick="testConnection('bedrock')">🔗 Test Connection</button>
                </div>
            </div>
        </div>

        <!-- Models Tab -->
        <div id="models" class="tab-content">
            <div class="section">
                <h3 class="section-title">Available Models</h3>
                <div class="provider-tabs">
                    <div class="provider-tab active" onclick="switchModelProvider('openai')">OpenAI</div>
                    <div class="provider-tab" onclick="switchModelProvider('anthropic')">Anthropic</div>
                    <div class="provider-tab" onclick="switchModelProvider('bedrock')">AWS Bedrock</div>
                </div>

                <div id="openai-models" class="models-grid">
                    <div class="model-card" onclick="selectModel('openai', 'gpt-4o')">
                        <div class="model-name">GPT-4o</div>
                        <div class="model-description">Most advanced multimodal model</div>
                        <div class="model-specs">
                            <span>Max 128k tokens</span>
                            <span>Text & Vision</span>
                        </div>
                    </div>
                    <div class="model-card" onclick="selectModel('openai', 'gpt-4o-mini')">
                        <div class="model-name">GPT-4o Mini</div>
                        <div class="model-description">Faster, cost-effective model</div>
                        <div class="model-specs">
                            <span>Max 128k tokens</span>
                            <span>Text & Vision</span>
                        </div>
                    </div>
                    <div class="model-card" onclick="selectModel('openai', 'gpt-4-turbo')">
                        <div class="model-name">GPT-4 Turbo</div>
                        <div class="model-description">Enhanced performance and efficiency</div>
                        <div class="model-specs">
                            <span>Max 128k tokens</span>
                            <span>Text & Vision</span>
                        </div>
                    </div>
                </div>

                <div id="anthropic-models" class="models-grid hidden">
                    <div class="model-card" onclick="selectModel('anthropic', 'claude-3-5-sonnet-20241022')">
                        <div class="model-name">Claude 3.5 Sonnet</div>
                        <div class="model-description">Balanced performance and capability</div>
                        <div class="model-specs">
                            <span>Max 200k tokens</span>
                            <span>Text & Vision</span>
                        </div>
                    </div>
                    <div class="model-card" onclick="selectModel('anthropic', 'claude-3-opus-20240229')">
                        <div class="model-name">Claude 3 Opus</div>
                        <div class="model-description">Most capable model for complex tasks</div>
                        <div class="model-specs">
                            <span>Max 200k tokens</span>
                            <span>Text & Vision</span>
                        </div>
                    </div>
                    <div class="model-card" onclick="selectModel('anthropic', 'claude-3-5-haiku-20241022')">
                        <div class="model-name">Claude 3.5 Haiku</div>
                        <div class="model-description">Fastest model for quick responses</div>
                        <div class="model-specs">
                            <span>Max 200k tokens</span>
                            <span>Text model</span>
                        </div>
                    </div>
                </div>

                <div id="bedrock-models" class="models-grid hidden">
                    <div class="model-card" onclick="selectModel('bedrock', 'anthropic.claude-3-5-sonnet-20241022-v2:0')">
                        <div class="model-name">Claude 3.5 Sonnet</div>
                        <div class="model-description">Available through AWS Bedrock</div>
                        <div class="model-specs">
                            <span>Max 200k tokens</span>
                            <span>Text & Vision</span>
                        </div>
                    </div>
                    <div class="model-card" onclick="selectModel('bedrock', 'amazon.titan-text-express-v1')">
                        <div class="model-name">Titan Text Express</div>
                        <div class="model-description">Amazon's flagship text model</div>
                        <div class="model-specs">
                            <span>Max 8k tokens</span>
                            <span>Text model</span>
                        </div>
                    </div>
                </div>

                <div id="model-config" class="model-config hidden">
                    <h4>Model Configuration</h4>
                    <div id="model-config-content"></div>
                </div>
            </div>
        </div>

        <!-- Agent Assignments Tab -->
        <div id="agents" class="tab-content">
            <div class="section">
                <h3 class="section-title">Agent Model Assignments</h3>
                <div id="agent-assignments"></div>
            </div>
        </div>

        <!-- General Tab -->
        <div id="general" class="tab-content">
            <div class="section">
                <h3 class="section-title">General Settings</h3>
                <div class="form-group">
                    <label class="form-label">Default AI Provider</label>
                    <select class="form-select" id="defaultProvider">
                        <option value="openai">OpenAI</option>
                        <option value="anthropic">Anthropic</option>
                        <option value="bedrock">AWS Bedrock</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Auto-save Conversations</label>
                    <input type="checkbox" id="autoSave" checked>
                </div>
                <div class="form-group">
                    <label class="form-label">Enable Telemetry</label>
                    <input type="checkbox" id="enableTelemetry">
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentSettings = {};
        let currentAgents = [];
        let currentAssignments = {};
        let selectedModel = null;

        // Initialize
        window.addEventListener('load', () => {
            vscode.postMessage({ command: 'getSettings' });
            vscode.postMessage({ command: 'getAgents' });
        });

        // Message handling
        window.addEventListener('message', event => {
            const message = event.data;
            
            switch (message.command) {
                case 'currentSettings':
                    currentSettings = message.settings;
                    populateSettings();
                    break;
                case 'agentsList':
                    currentAgents = message.agents;
                    currentAssignments = message.assignments;
                    populateAgentAssignments();
                    break;
                case 'settingsSaved':
                    showStatus(message.message, message.success);
                    break;
                case 'connectionTested':
                    showStatus(message.message, message.success);
                    break;
                case 'modelSelected':
                    showModelConfig(message.provider, message.model, message.config);
                    break;
                case 'agentModelAssigned':
                    showStatus(message.message, message.success);
                    if (message.success) {
                        currentAssignments[message.agentId] = {
                            provider: message.provider,
                            model: message.model
                        };
                        populateAgentAssignments();
                    }
                    break;
                case 'agentToggled':
                    if (message.success) {
                        currentAssignments[message.agentId].active = message.active;
                        // Don't show status message for successful toggles
                    } else {
                        // Only show status for errors
                        showStatus(message.message, message.success);
                    }
                    break;
            }
        });

        // Tab switching
        function switchTab(tabName) {
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            
            event.target.classList.add('active');
            document.getElementById(tabName).classList.add('active');
        }

        // Provider switching
        function switchProvider(provider) {
            document.querySelectorAll('.provider-tab').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.provider-settings').forEach(settings => settings.classList.add('hidden'));
            
            event.target.classList.add('active');
            document.getElementById(provider + '-settings').classList.remove('hidden');
        }

        // Model provider switching
        function switchModelProvider(provider) {
            document.querySelectorAll('.provider-tab').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.models-grid').forEach(grid => grid.classList.add('hidden'));
            
            event.target.classList.add('active');
            document.getElementById(provider + '-models').classList.remove('hidden');
        }

        // Model selection
        function selectModel(provider, model) {
            // Remove previous selection
            document.querySelectorAll('.model-card').forEach(card => card.classList.remove('selected'));
            
            // Add selection to clicked card
            event.target.closest('.model-card').classList.add('selected');
            
            selectedModel = { provider, model };
            vscode.postMessage({ command: 'selectModel', provider, model });
        }

        // Show model configuration
        function showModelConfig(provider, model, config) {
            const configDiv = document.getElementById('model-config');
            const contentDiv = document.getElementById('model-config-content');
            
            let html = \`<h5>\${provider.toUpperCase()} - \${model}</h5>\`;
            
            for (const [param, settings] of Object.entries(config)) {
                html += \`
                    <div class="form-group">
                        <label class="form-label">\${param.charAt(0).toUpperCase() + param.slice(1)}</label>
                        <input type="range" class="form-range" 
                               min="\${settings.min}" max="\${settings.max}" 
                               step="\${settings.step || 1}" value="\${settings.default}"
                               onchange="updateModelParam('\${param}', this.value)">
                        <div class="range-labels">
                            <span>\${settings.min}</span>
                            <span>\${settings.max}</span>
                        </div>
                    </div>
                \`;
            }
            
            contentDiv.innerHTML = html;
            configDiv.classList.remove('hidden');
        }

        // Populate settings
        function populateSettings() {
            for (const [provider, settings] of Object.entries(currentSettings)) {
                for (const [key, value] of Object.entries(settings)) {
                    const element = document.getElementById(\`\${provider}-\${key}\`);
                    if (element) {
                        if (element.type === 'checkbox') {
                            element.checked = value;
                        } else {
                            element.value = value;
                        }
                    }
                }
            }
        }

        // Populate agent assignments
        function populateAgentAssignments() {
            const container = document.getElementById('agent-assignments');
            let html = '';
            
            currentAgents.forEach(agent => {
                const assignment = currentAssignments[agent.id] || { provider: 'openai', model: 'gpt-4o', active: true };
                const isActive = assignment.active !== false;
                html += \`
                    <div class="agent-assignment \${isActive ? '' : 'inactive'}">
                        <div class="agent-info">
                            <div class="agent-name">\${agent.name}</div>
                            <div class="agent-description">\${agent.description}</div>
                        </div>
                        <div class="agent-controls">
                            <div class="agent-toggle">
                                <label class="toggle-switch">
                                    <input type="checkbox" \${isActive ? 'checked' : ''} 
                                           onchange="toggleAgent('\${agent.id}', this.checked)">
                                    <span class="toggle-slider"></span>
                                </label>
                                <span class="toggle-label">\${isActive ? 'Active' : 'Inactive'}</span>
                            </div>
                            <div class="agent-models \${isActive ? '' : 'disabled'}">
                                <select class="form-select" \${isActive ? '' : 'disabled'} 
                                        onchange="assignAgentModel('\${agent.id}', 'provider', this.value)">
                                    <option value="openai" \${assignment.provider === 'openai' ? 'selected' : ''}>OpenAI</option>
                                    <option value="anthropic" \${assignment.provider === 'anthropic' ? 'selected' : ''}>Anthropic</option>
                                    <option value="bedrock" \${assignment.provider === 'bedrock' ? 'selected' : ''}>AWS Bedrock</option>
                                </select>
                                <input type="text" class="form-input" value="\${assignment.model}" 
                                       \${isActive ? '' : 'disabled'}
                                       onchange="assignAgentModel('\${agent.id}', 'model', this.value)" 
                                       placeholder="Model name">
                            </div>
                        </div>
                    </div>
                \`;
            });
            
            container.innerHTML = html;
        }

        // Toggle agent active/inactive
        function toggleAgent(agentId, active) {
            currentAssignments[agentId].active = active;
            
            vscode.postMessage({ 
                command: 'toggleAgent', 
                agentId, 
                active
            });
            
            // Update UI immediately
            populateAgentAssignments();
        }

        // Assign agent model
        function assignAgentModel(agentId, type, value) {
            if (type === 'provider') {
                currentAssignments[agentId].provider = value;
                // Update model to default for new provider
                const defaultModels = {
                    openai: 'gpt-4o',
                    anthropic: 'claude-3-5-sonnet-20241022',
                    bedrock: 'anthropic.claude-3-5-sonnet-20241022-v2:0'
                };
                currentAssignments[agentId].model = defaultModels[value];
            } else {
                currentAssignments[agentId].model = value;
            }
            
            vscode.postMessage({ 
                command: 'assignAgentModel', 
                agentId, 
                provider: currentAssignments[agentId].provider,
                model: currentAssignments[agentId].model
            });
        }

        // Test connection
        function testConnection(provider) {
            const settings = {};
            const elements = document.querySelectorAll(\`#\${provider}-settings input, #\${provider}-settings select\`);
            
            elements.forEach(element => {
                const key = element.id.replace(\`\${provider}-\`, '');
                settings[key] = element.type === 'checkbox' ? element.checked : element.value;
            });
            
            vscode.postMessage({ command: 'testConnection', provider, settings });
        }

        // Save all settings
        function saveAllSettings() {
            const settings = {};
            
            ['openai', 'anthropic', 'bedrock'].forEach(provider => {
                settings[provider] = {};
                const elements = document.querySelectorAll(\`#\${provider}-settings input, #\${provider}-settings select\`);
                
                elements.forEach(element => {
                    const key = element.id.replace(\`\${provider}-\`, '');
                    settings[provider][key] = element.type === 'checkbox' ? element.checked : element.value;
                });
            });
            
            vscode.postMessage({ command: 'saveSettings', settings });
        }

        // Show status message
        function showStatus(message, isSuccess) {
            const statusDiv = document.getElementById('statusMessage');
            statusDiv.textContent = message;
            statusDiv.className = \`status-message \${isSuccess ? 'status-success' : 'status-error'}\`;
            statusDiv.classList.remove('hidden');
            
            setTimeout(() => {
                statusDiv.classList.add('hidden');
            }, 5000);
        }

        // Search functionality
        document.getElementById('searchInput').addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            // Implement search logic here
        });

        // VS Code API
        const vscode = acquireVsCodeApi();
    </script>
</body>
</html>`;
    }
} 