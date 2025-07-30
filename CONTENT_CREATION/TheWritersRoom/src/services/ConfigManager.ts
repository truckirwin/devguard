import * as vscode from 'vscode';

export class ConfigManager {
    private static instance: ConfigManager;
    private context: vscode.ExtensionContext;

    private constructor(context: vscode.ExtensionContext) {
        this.context = context;
    }

    public static getInstance(context?: vscode.ExtensionContext): ConfigManager {
        if (!ConfigManager.instance && context) {
            ConfigManager.instance = new ConfigManager(context);
        }
        return ConfigManager.instance;
    }

    public getConfiguration(): vscode.WorkspaceConfiguration {
        return vscode.workspace.getConfiguration('theWritersRoom');
    }

    public async configureAPIKeys(): Promise<void> {
        const config = this.getConfiguration();
        const currentProvider = config.get<string>('aiProvider', 'openai');

        const providerOptions = [
            { label: 'OpenAI (GPT-4, GPT-3.5)', value: 'openai' },
            { label: 'Anthropic (Claude)', value: 'anthropic' },
            { label: 'AWS Bedrock', value: 'aws-bedrock' }
        ];

        const selectedProvider = await vscode.window.showQuickPick(providerOptions, {
            placeHolder: 'Select your AI provider',
            title: 'Configure AI Provider'
        });

        if (!selectedProvider) {
            return;
        }

        await config.update('aiProvider', selectedProvider.value, vscode.ConfigurationTarget.Global);

        switch (selectedProvider.value) {
            case 'openai':
                await this.configureOpenAI();
                break;
            case 'anthropic':
                await this.configureAnthropic();
                break;
            case 'aws-bedrock':
                await this.configureAWSBedrock();
                break;
        }

        vscode.window.showInformationMessage(`✅ AI provider configured: ${selectedProvider.label}`);
    }

    private async configureOpenAI(): Promise<void> {
        const config = this.getConfiguration();
        
        const apiKey = await vscode.window.showInputBox({
            prompt: 'Enter your OpenAI API key',
            placeHolder: 'sk-...',
            password: true,
            value: config.get<string>('ai.openai.apiKey', ''),
            validateInput: (value) => {
                if (!value) {
                    return 'API key is required';
                }
                if (!value.startsWith('sk-')) {
                    return 'OpenAI API key should start with "sk-"';
                }
                return null;
            }
        });

        if (apiKey) {
            await config.update('ai.openai.apiKey', apiKey, vscode.ConfigurationTarget.Global);
            
            // Show additional settings option
            const showAdvanced = await vscode.window.showInformationMessage(
                'API key saved! Would you like to configure advanced settings?',
                'Yes', 'No'
            );
            
            if (showAdvanced === 'Yes') {
                await this.openSettings();
            }
        }
    }

    private async configureAnthropic(): Promise<void> {
        const config = this.getConfiguration();
        
        const apiKey = await vscode.window.showInputBox({
            prompt: 'Enter your Anthropic API key',
            placeHolder: 'sk-ant-...',
            password: true,
            value: config.get<string>('ai.anthropic.apiKey', ''),
            validateInput: (value) => {
                if (!value) {
                    return 'API key is required';
                }
                if (!value.startsWith('sk-ant-')) {
                    return 'Anthropic API key should start with "sk-ant-"';
                }
                return null;
            }
        });

        if (apiKey) {
            await config.update('ai.anthropic.apiKey', apiKey, vscode.ConfigurationTarget.Global);
            
            // Show additional settings option
            const showAdvanced = await vscode.window.showInformationMessage(
                'API key saved! Would you like to configure advanced settings?',
                'Yes', 'No'
            );
            
            if (showAdvanced === 'Yes') {
                await this.openSettings();
            }
        }
    }

    private async configureAWSBedrock(): Promise<void> {
        const config = this.getConfiguration();
        
        const accessKeyId = await vscode.window.showInputBox({
            prompt: 'Enter your AWS Access Key ID',
            placeHolder: 'AKIA...',
            password: true,
            value: config.get<string>('ai.bedrock.accessKeyId', ''),
            validateInput: (value) => {
                if (!value) {
                    return 'AWS Access Key ID is required';
                }
                return null;
            }
        });

        if (!accessKeyId) {
            return;
        }

        const secretAccessKey = await vscode.window.showInputBox({
            prompt: 'Enter your AWS Secret Access Key',
            password: true,
            value: config.get<string>('ai.bedrock.secretAccessKey', ''),
            validateInput: (value) => {
                if (!value) {
                    return 'AWS Secret Access Key is required';
                }
                return null;
            }
        });

        if (!secretAccessKey) {
            return;
        }

        const region = await vscode.window.showQuickPick([
            { label: 'US East (N. Virginia)', value: 'us-east-1' },
            { label: 'US West (Oregon)', value: 'us-west-2' },
            { label: 'Europe (Ireland)', value: 'eu-west-1' },
            { label: 'Asia Pacific (Singapore)', value: 'ap-southeast-1' }
        ], {
            placeHolder: 'Select AWS region',
            title: 'AWS Region'
        });

        if (region) {
            await Promise.all([
                config.update('ai.bedrock.accessKeyId', accessKeyId, vscode.ConfigurationTarget.Global),
                config.update('ai.bedrock.secretAccessKey', secretAccessKey, vscode.ConfigurationTarget.Global),
                config.update('ai.bedrock.region', region.value, vscode.ConfigurationTarget.Global)
            ]);
            
            // Show additional settings option
            const showAdvanced = await vscode.window.showInformationMessage(
                'AWS credentials saved! Would you like to configure advanced settings?',
                'Yes', 'No'
            );
            
            if (showAdvanced === 'Yes') {
                await this.openSettings();
            }
        }
    }

    public async openSettings(): Promise<void> {
        await vscode.commands.executeCommand('workbench.action.openSettings', 'theWritersRoom');
    }

    public getAPIKeyStatus(): { [key: string]: boolean } {
        const config = this.getConfiguration();
        
        return {
            openai: !!config.get<string>('ai.openai.apiKey'),
            anthropic: !!config.get<string>('ai.anthropic.apiKey'),
            awsBedrock: !!(config.get<string>('ai.bedrock.accessKeyId') && config.get<string>('ai.bedrock.secretAccessKey'))
        };
    }

    // New method to get AI-specific settings
    public getAISettings(provider: 'openai' | 'anthropic' | 'bedrock') {
        const config = this.getConfiguration();
        
        switch (provider) {
            case 'openai':
                return {
                    apiKey: config.get<string>('ai.openai.apiKey', ''),
                    model: config.get<string>('ai.openai.model', 'gpt-4o'),
                    maxTokens: config.get<number>('ai.openai.maxTokens', 4000),
                    temperature: config.get<number>('ai.openai.temperature', 0.7),
                    topP: config.get<number>('ai.openai.topP', 1),
                    frequencyPenalty: config.get<number>('ai.openai.frequencyPenalty', 0),
                    presencePenalty: config.get<number>('ai.openai.presencePenalty', 0)
                };
            case 'anthropic':
                return {
                    apiKey: config.get<string>('ai.anthropic.apiKey', ''),
                    model: config.get<string>('ai.anthropic.model', 'claude-3-5-sonnet-20241022'),
                    maxTokens: config.get<number>('ai.anthropic.maxTokens', 4000),
                    temperature: config.get<number>('ai.anthropic.temperature', 0.7),
                    topP: config.get<number>('ai.anthropic.topP', 1),
                    topK: config.get<number>('ai.anthropic.topK', 40)
                };
            case 'bedrock':
                return {
                    accessKeyId: config.get<string>('ai.bedrock.accessKeyId', ''),
                    secretAccessKey: config.get<string>('ai.bedrock.secretAccessKey', ''),
                    region: config.get<string>('ai.bedrock.region', 'us-east-1'),
                    model: config.get<string>('ai.bedrock.model', 'anthropic.claude-3-5-sonnet-20241022-v2:0'),
                    maxTokens: config.get<number>('ai.bedrock.maxTokens', 4000),
                    temperature: config.get<number>('ai.bedrock.temperature', 0.7),
                    topP: config.get<number>('ai.bedrock.topP', 1),
                    topK: config.get<number>('ai.bedrock.topK', 250)
                };
            default:
                return {};
        }
    }

    // Get agent-specific model assignment
    public getAgentModelAssignment(agentId: string): { provider: string; model: string } {
        const config = this.getConfiguration();
        const normalizedAgentId = this.normalizeAgentId(agentId);
        
        const provider = config.get<string>(`agents.${normalizedAgentId}.provider`, 'openai');
        const model = config.get<string>(`agents.${normalizedAgentId}.model`, this.getDefaultModelForProvider(provider));
        
        return { provider, model };
    }

    // Get AI settings for a specific agent
    public getAgentAISettings(agentId: string) {
        const { provider, model } = this.getAgentModelAssignment(agentId);
        const baseSettings = this.getAISettings(provider as 'openai' | 'anthropic' | 'bedrock');
        
        // Override the model with agent-specific assignment
        return {
            ...baseSettings,
            model,
            provider
        };
    }

    // Set agent-specific model assignment
    public async setAgentModelAssignment(agentId: string, provider: string, model: string): Promise<void> {
        const config = this.getConfiguration();
        const normalizedAgentId = this.normalizeAgentId(agentId);
        
        await Promise.all([
            config.update(`agents.${normalizedAgentId}.provider`, provider, vscode.ConfigurationTarget.Global),
            config.update(`agents.${normalizedAgentId}.model`, model, vscode.ConfigurationTarget.Global)
        ]);
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

    // Get default model for provider
    private getDefaultModelForProvider(provider: string): string {
        const defaults: { [key: string]: string } = {
            'openai': 'gpt-4o',
            'anthropic': 'claude-3-5-sonnet-20241022',
            'bedrock': 'anthropic.claude-3-5-sonnet-20241022-v2:0'
        };
        
        return defaults[provider] || 'gpt-4o';
    }

    // Quick setup for agent model assignments
    public async configureAgentModels(): Promise<void> {
        const agents = [
            { id: 'script-doctor', name: '🎬 Script Doctor', defaultProvider: 'openai' },
            { id: 'aaron-sorkin', name: '✍️ Aaron Sorkin', defaultProvider: 'anthropic' },
            { id: 'character-specialist', name: '👥 Character Specialist', defaultProvider: 'anthropic' },
            { id: 'creative-visionary', name: '🎨 Creative Visionary', defaultProvider: 'openai' },
            { id: 'location-scout', name: '🗺️ Location Scout', defaultProvider: 'bedrock' },
            { id: 'producer', name: '💼 Producer', defaultProvider: 'openai' },
            { id: 'director', name: '🎬 Director', defaultProvider: 'anthropic' },
            { id: 'continuity-expert', name: '📋 Continuity Expert', defaultProvider: 'openai' },
            { id: 'showrunner', name: '👑 Showrunner', defaultProvider: 'anthropic' }
        ];

        const selectedAgent = await vscode.window.showQuickPick(
            agents.map(agent => ({
                label: agent.name,
                description: `Currently: ${this.getAgentModelAssignment(agent.id).provider}`,
                value: agent.id
            })),
            {
                placeHolder: 'Select agent to configure',
                title: 'Configure Agent Model Assignment'
            }
        );

        if (!selectedAgent) return;

        const providers = [
            { label: 'OpenAI (GPT-4, GPT-3.5)', value: 'openai' },
            { label: 'Anthropic (Claude)', value: 'anthropic' },
            { label: 'AWS Bedrock', value: 'bedrock' }
        ];

        const selectedProvider = await vscode.window.showQuickPick(providers, {
            placeHolder: 'Select AI provider',
            title: `Configure ${selectedAgent.label}`
        });

        if (!selectedProvider) return;

        const models = this.getModelsForProvider(selectedProvider.value);
        const selectedModel = await vscode.window.showQuickPick(models, {
            placeHolder: 'Select model',
            title: `Select model for ${selectedAgent.label}`
        });

        if (!selectedModel) return;

        await this.setAgentModelAssignment(selectedAgent.value, selectedProvider.value, selectedModel.value);
        
        vscode.window.showInformationMessage(
            `✅ ${selectedAgent.label} configured: ${selectedProvider.label} - ${selectedModel.label}`
        );
    }

    // Get available models for a provider
    private getModelsForProvider(provider: string): Array<{ label: string; value: string }> {
        switch (provider) {
            case 'openai':
                return [
                    { label: 'GPT-4o (Latest)', value: 'gpt-4o' },
                    { label: 'GPT-4o Mini', value: 'gpt-4o-mini' },
                    { label: 'GPT-4 Turbo', value: 'gpt-4-turbo' },
                    { label: 'GPT-4', value: 'gpt-4' },
                    { label: 'GPT-3.5 Turbo', value: 'gpt-3.5-turbo' }
                ];
            case 'anthropic':
                return [
                    { label: 'Claude 3.5 Sonnet (Latest)', value: 'claude-3-5-sonnet-20241022' },
                    { label: 'Claude 3.5 Haiku', value: 'claude-3-5-haiku-20241022' },
                    { label: 'Claude 3 Opus', value: 'claude-3-opus-20240229' },
                    { label: 'Claude 3 Sonnet', value: 'claude-3-sonnet-20240229' },
                    { label: 'Claude 3 Haiku', value: 'claude-3-haiku-20240307' }
                ];
            case 'bedrock':
                return [
                    { label: 'Claude 3.5 Sonnet (Bedrock)', value: 'anthropic.claude-3-5-sonnet-20241022-v2:0' },
                    { label: 'Claude 3.5 Haiku (Bedrock)', value: 'anthropic.claude-3-5-haiku-20241022-v1:0' },
                    { label: 'Claude 3 Opus (Bedrock)', value: 'anthropic.claude-3-opus-20240229-v1:0' },
                    { label: 'Amazon Titan Express', value: 'amazon.titan-text-express-v1' },
                    { label: 'Amazon Titan Lite', value: 'amazon.titan-text-lite-v1' },
                    { label: 'Cohere Command', value: 'cohere.command-text-v14' },
                    { label: 'Meta Llama 2 70B', value: 'meta.llama2-70b-chat-v1' }
                ];
            default:
                return [];
        }
    }

    public async selectAgent(): Promise<string | undefined> {
        const config = this.getConfiguration();
        const currentAgent = config.get<string>('defaultAgent', 'script-doctor');

        const agentOptions = [
            { label: '🎬 Script Doctor', description: 'Structure & pacing expert', value: 'script-doctor' },
            { label: '✍️ Aaron Sorkin', description: 'Sharp dialogue & character development', value: 'aaron-sorkin' },
            { label: '👥 Character Specialist', description: 'Deep character development', value: 'character-specialist' },
            { label: '🎨 Creative Visionary', description: 'Story & vision focused', value: 'creative-visionary' },
            { label: '🎭 Coen Brothers', description: 'Dark comedy & unique style', value: 'coen-brothers' },
            { label: '🎪 Quentin Tarantino', description: 'Bold dialogue & storytelling', value: 'quentin-tarantino' },
            { label: '🏔️ Taylor Sheridan', description: 'Character-driven stories', value: 'taylor-sheridan' },
            { label: '⚔️ Jack Carr', description: 'Military & thriller expertise', value: 'jack-carr' }
        ];

        const selectedAgent = await vscode.window.showQuickPick(agentOptions, {
            placeHolder: `Current: ${currentAgent} - Select a writing agent`,
            title: 'Choose Your AI Writing Agent'
        });

        if (selectedAgent) {
            await config.update('defaultAgent', selectedAgent.value, vscode.ConfigurationTarget.Global);
            return selectedAgent.value;
        }

        return undefined;
    }
} 