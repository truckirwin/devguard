import * as vscode from 'vscode';
import { BedrockRuntimeClient, InvokeModelCommand } from '@aws-sdk/client-bedrock-runtime';
import { Anthropic } from '@anthropic-ai/sdk';
import OpenAI from 'openai';
import { ConfigManager } from './ConfigManager';
import { AgentManager } from '../agents/AgentManager';

export interface AIProvider {
    name: string;
    models: string[];
}

export interface AIResponse {
    text: string;
    usage?: {
        promptTokens: number;
        completionTokens: number;
        totalTokens: number;
    };
    modelUsed: string;
    reasoning?: string;
    sessionId?: string;
}

export interface TaskRequest {
    message: string;
    agentType: string;
    documentId?: string;
    context?: any;
    userId: string;
    sessionId: string;
}

export interface SessionData {
    sessionId: string;
    userId: string;
    promptCount: number;
    maxPrompts: number;
    startTime: Date;
    modelUsage: Map<string, number>;
    costAccumulated: number;
    active: boolean;
}

export interface ModelSelection {
    primaryModel: string;
    fallbackModel: string;
    reasoning: string;
    estimatedCost: number;
    estimatedLatency: string;
    promptLimit: number;
    enhancedContext: boolean;
}

export enum TaskType {
    DIALOGUE_WRITING = 'dialogue_writing',
    CHARACTER_DEVELOPMENT = 'character_development',
    CREATIVE_BRAINSTORMING = 'creative_brainstorming',
    MULTI_AGENT_COLLABORATION = 'multi_agent_collaboration',
    STORY_STRUCTURE = 'story_structure',
    GENERAL_WRITING = 'general_writing',
    SIMPLE_TASK = 'simple_task'
}

export enum TaskComplexity {
    SIMPLE = 'simple',
    MODERATE = 'moderate',
    ADVANCED = 'advanced'
}

export interface TaskAnalysis {
    complexity: TaskComplexity;
    type: TaskType;
    urgency: string;
    estimatedTokens: number;
}

export class AIService {
    private static instance: AIService;
    private currentProvider: string = 'aws-bedrock';
    private currentModel: string = 'anthropic.claude-4-sonnet-20241022-v1:0';
    private sessions = new Map<string, SessionData>();
    private bedrockClient?: BedrockRuntimeClient;
    private anthropicClient?: Anthropic;
    private openaiClient?: OpenAI;
    private readonly PROMPT_LIMIT = 100;
    private readonly CLAUDE_4_SONNET_ID = 'anthropic.claude-4-sonnet-20241022-v1:0';
    private configManager: ConfigManager;

    private constructor() {
        this.configManager = ConfigManager.getInstance();
        this.loadConfiguration();
        this.initializeClients();
    }

    public static getInstance(): AIService {
        if (!AIService.instance) {
            AIService.instance = new AIService();
        }
        return AIService.instance;
    }

    private loadConfiguration(): void {
        const config = vscode.workspace.getConfiguration('theWritersRoom');
        this.currentProvider = config.get('aiProvider', 'aws-bedrock');
        this.currentModel = config.get('modelVersion', this.CLAUDE_4_SONNET_ID);
    }

    private initializeClients(): void {
        const config = vscode.workspace.getConfiguration('theWritersRoom');
        
        // Initialize AWS Bedrock client
        const awsAccessKeyId = config.get<string>('awsAccessKeyId');
        const awsSecretAccessKey = config.get<string>('awsSecretAccessKey');
        const awsRegion = config.get<string>('awsRegion', 'us-east-1');
        
        if (awsAccessKeyId && awsSecretAccessKey) {
            this.bedrockClient = new BedrockRuntimeClient({
                region: awsRegion,
                credentials: {
                    accessKeyId: awsAccessKeyId,
                    secretAccessKey: awsSecretAccessKey
                }
            });
        }

        // Initialize Anthropic client
        const anthropicApiKey = config.get<string>('anthropicApiKey');
        if (anthropicApiKey) {
            this.anthropicClient = new Anthropic({
                apiKey: anthropicApiKey
            });
        }

        // Initialize OpenAI client
        const openaiApiKey = config.get<string>('openaiApiKey');
        if (openaiApiKey) {
            this.openaiClient = new OpenAI({
                apiKey: openaiApiKey
            });
        }
    }

    public getAvailableProviders(): AIProvider[] {
        return [
            {
                name: 'AWS Bedrock (Recommended)',
                models: [
                    'anthropic.claude-4-sonnet-20241022-v1:0',
                    'anthropic.claude-3-sonnet-20240229-v1:0',
                    'anthropic.claude-3-haiku-20240307-v1:0',
                    'anthropic.claude-3-opus-20240229-v1:0'
                ]
            },
            {
                name: 'Anthropic',
                models: ['claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307']
            },
            {
                name: 'OpenAI',
                models: ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo']
            }
        ];
    }

    public async createSession(userId: string): Promise<SessionData> {
        const sessionId = this.generateSessionId();
        const session: SessionData = {
            sessionId,
            userId,
            promptCount: 0,
            maxPrompts: this.PROMPT_LIMIT,
            startTime: new Date(),
            modelUsage: new Map(),
            costAccumulated: 0,
            active: true
        };

        this.sessions.set(sessionId, session);
        return session;
    }

    public async processTask(task: TaskRequest): Promise<AIResponse> {
        // Get session status
        const session = this.sessions.get(task.sessionId);
        if (!session || !session.active) {
            throw new Error('Session limit reached. Please start a new session.');
        }

        // Analyze task for optimal model selection
        const taskAnalysis = await this.analyzeTask(task);
        
        // Select optimal model using hybrid logic
        const modelSelection = await this.hybridSelectModel(taskAnalysis);
        
        // Process with selected model
        let response: AIResponse;
        
        if (modelSelection.primaryModel === this.CLAUDE_4_SONNET_ID) {
            response = await this.processWithClaude4Sonnet(task, modelSelection);
        } else {
            response = await this.processWithStandardModel(task, modelSelection);
        }

        // Update session
        await this.incrementPromptCount(task.sessionId, modelSelection.primaryModel, modelSelection.estimatedCost);

        return {
            ...response,
            modelUsed: modelSelection.primaryModel,
            reasoning: modelSelection.reasoning,
            sessionId: task.sessionId
        };
    }

    private async analyzeTask(task: TaskRequest): Promise<TaskAnalysis> {
        const message = task.message.toLowerCase();
        const agentType = task.agentType;
        
        // Determine task type
        let type = TaskType.GENERAL_WRITING;
        if (message.includes('dialogue') || message.includes('conversation') || agentType.includes('sorkin')) {
            type = TaskType.DIALOGUE_WRITING;
        } else if (message.includes('character') || agentType.includes('character')) {
            type = TaskType.CHARACTER_DEVELOPMENT;
        } else if (message.includes('brainstorm') || message.includes('idea')) {
            type = TaskType.CREATIVE_BRAINSTORMING;
        } else if (message.includes('structure') || message.includes('plot')) {
            type = TaskType.STORY_STRUCTURE;
        }

        // Determine complexity
        let complexity = TaskComplexity.MODERATE;
        if (message.length < 50 || message.includes('simple') || message.includes('quick')) {
            complexity = TaskComplexity.SIMPLE;
        } else if (message.length > 200 || message.includes('complex') || message.includes('detailed')) {
            complexity = TaskComplexity.ADVANCED;
        }

        // Estimate urgency
        const urgency = message.includes('urgent') || message.includes('quickly') ? 'high' : 'normal';

        return {
            complexity,
            type,
            urgency,
            estimatedTokens: Math.min(Math.max(message.length * 4, 100), 4000)
        };
    }

    private async hybridSelectModel(analysis: TaskAnalysis): Promise<ModelSelection> {
        const { complexity, type, urgency } = analysis;
        
        // Priority 1: Dialogue writing gets Claude 4.0 Sonnet
        if (type === TaskType.DIALOGUE_WRITING || 
            type === TaskType.CHARACTER_DEVELOPMENT ||
            type === TaskType.CREATIVE_BRAINSTORMING) {
            return {
                primaryModel: this.CLAUDE_4_SONNET_ID,
                fallbackModel: 'anthropic.claude-3-sonnet-20240229-v1:0',
                reasoning: 'Claude 4.0 Sonnet for advanced dialogue and character development',
                estimatedCost: this.calculateCost(this.CLAUDE_4_SONNET_ID, analysis),
                estimatedLatency: '2-5s',
                promptLimit: this.PROMPT_LIMIT,
                enhancedContext: true
            };
        }

        // Priority 2: Complex creative tasks get Claude 4.0 Sonnet
        if (complexity === TaskComplexity.ADVANCED || 
            type === TaskType.MULTI_AGENT_COLLABORATION ||
            type === TaskType.STORY_STRUCTURE) {
            return {
                primaryModel: this.CLAUDE_4_SONNET_ID,
                fallbackModel: 'anthropic.claude-3-opus-20240229-v1:0',
                reasoning: 'Claude 4.0 Sonnet for complex creative tasks and collaboration',
                estimatedCost: this.calculateCost(this.CLAUDE_4_SONNET_ID, analysis),
                estimatedLatency: '2-5s',
                promptLimit: this.PROMPT_LIMIT,
                enhancedContext: true
            };
        }

        // Priority 3: Speed-optimized for simple, urgent tasks
        if (complexity === TaskComplexity.SIMPLE || urgency === 'high') {
            return {
                primaryModel: 'anthropic.claude-3-haiku-20240307-v1:0',
                fallbackModel: 'anthropic.claude-3-sonnet-20240229-v1:0',
                reasoning: 'Speed-optimized for simple/urgent tasks',
                estimatedCost: this.calculateCost('haiku', analysis),
                estimatedLatency: '100-300ms',
                promptLimit: this.PROMPT_LIMIT,
                enhancedContext: false
            };
        }

        // Priority 4: Balanced for moderate complexity
        return {
            primaryModel: 'anthropic.claude-3-sonnet-20240229-v1:0',
            fallbackModel: 'anthropic.claude-3-haiku-20240307-v1:0',
            reasoning: 'Balanced performance for moderate complexity',
            estimatedCost: this.calculateCost('sonnet', analysis),
            estimatedLatency: '500ms-2s',
            promptLimit: this.PROMPT_LIMIT,
            enhancedContext: true
        };
    }

    private async processWithClaude4Sonnet(task: TaskRequest, modelSelection: ModelSelection): Promise<AIResponse> {
        const prompt = this.buildDialoguePrompt(task);
        
        if (this.currentProvider === 'aws-bedrock' && this.bedrockClient) {
            return this.callClaude4SonnetBedrock(prompt, task.agentType);
        } else if (this.anthropicClient) {
            return this.callClaude4SonnetDirect(prompt, task.agentType);
        } else {
            throw new Error('Claude 4.0 Sonnet not available - please configure AWS Bedrock or Anthropic API');
        }
    }

    private async processWithStandardModel(task: TaskRequest, modelSelection: ModelSelection): Promise<AIResponse> {
        const agentContext = this.getAgentContext(task.agentType);
        const fullPrompt = `${agentContext}\n\nUser: ${task.message}`;

        switch (this.currentProvider) {
            case 'aws-bedrock':
                return this.sendBedrockMessage(fullPrompt, modelSelection.primaryModel);
            case 'anthropic':
                return this.sendAnthropicMessage(fullPrompt, modelSelection.primaryModel);
            case 'openai':
                return this.sendOpenAIMessage(fullPrompt, modelSelection.primaryModel);
            default:
                throw new Error(`Unsupported AI provider: ${this.currentProvider}`);
        }
    }

    private buildDialoguePrompt(task: TaskRequest): string {
        const agentContext = this.getAgentContext(task.agentType);
        
        return `You are an expert dialogue writer specializing in screenplay dialogue.

${agentContext}

TASK: ${task.message}

Please provide:
1. Enhanced dialogue that feels natural and character-specific
2. Emotional depth and subtext
3. Character voice consistency
4. Pacing and rhythm suggestions
5. Potential dialogue alternatives

Focus on making each character's voice distinct and authentic to their personality and background.`;
    }

    private async callClaude4SonnetBedrock(prompt: string, agentType: string): Promise<AIResponse> {
        if (!this.bedrockClient) {
            throw new Error('AWS Bedrock client not initialized');
        }

        const systemPrompt = this.getDialogueSystemPrompt(agentType);
        
        const body = JSON.stringify({
            anthropic_version: "bedrock-2023-05-31",
            max_tokens: 4000,
            system: systemPrompt,
            messages: [
                {
                    role: "user",
                    content: prompt
                }
            ],
            temperature: 0.7
        });

        const command = new InvokeModelCommand({
            modelId: this.CLAUDE_4_SONNET_ID,
            body: body,
            contentType: "application/json",
            accept: "application/json"
        });

        try {
            const response = await this.bedrockClient.send(command);
            const responseBody = JSON.parse(new TextDecoder().decode(response.body));
            
            return {
                text: responseBody.content[0].text,
                usage: {
                    promptTokens: responseBody.usage?.input_tokens || 0,
                    completionTokens: responseBody.usage?.output_tokens || 0,
                    totalTokens: (responseBody.usage?.input_tokens || 0) + (responseBody.usage?.output_tokens || 0)
                },
                modelUsed: this.CLAUDE_4_SONNET_ID
            };
        } catch (error) {
            console.error('Claude 4.0 Sonnet Bedrock error:', error);
            throw new Error(`Claude 4.0 Sonnet error: ${error}`);
        }
    }

    private async callClaude4SonnetDirect(prompt: string, agentType: string): Promise<AIResponse> {
        if (!this.anthropicClient) {
            throw new Error('Anthropic client not initialized');
        }

        const systemPrompt = this.getDialogueSystemPrompt(agentType);

        try {
            const response = await this.anthropicClient.messages.create({
                model: 'claude-3-opus-20240229', // Use opus as closest to Claude 4.0
                max_tokens: 4000,
                system: systemPrompt,
                messages: [
                    {
                        role: 'user',
                        content: prompt
                    }
                ],
                temperature: 0.7
            });

            return {
                text: response.content[0].type === 'text' ? response.content[0].text : '',
                usage: {
                    promptTokens: response.usage.input_tokens,
                    completionTokens: response.usage.output_tokens,
                    totalTokens: response.usage.input_tokens + response.usage.output_tokens
                },
                modelUsed: 'claude-3-opus-20240229'
            };
        } catch (error) {
            console.error('Anthropic API error:', error);
            throw new Error(`Anthropic API error: ${error}`);
        }
    }

    private getDialogueSystemPrompt(agentType: string): string {
        const basePrompt = `You are Claude 4.0 Sonnet, an expert in creative writing and dialogue development. 
        
Your strengths include:
- Natural, character-specific dialogue
- Emotional depth and subtext
- Understanding of human psychology
- Screenplay formatting and structure
- Character voice consistency
- Pacing and dramatic timing

For dialogue tasks, focus on:
- Making each character's voice unique and authentic
- Creating emotional resonance
- Advancing the plot through dialogue
- Maintaining character consistency
- Adding subtext and layers of meaning

Always consider the character's background, personality, and current emotional state when crafting dialogue.`;

        const agentSpecificPrompts: { [key: string]: string } = {
            'aaron-sorkin': `${basePrompt}\n\nSpecialized in Aaron Sorkin's style: rapid-fire dialogue, walk-and-talk scenes, intelligent characters who speak in perfectly crafted sentences, and dialogue that reveals character through wit and intelligence.`,
            'character-specialist': `${basePrompt}\n\nSpecialized in character development: focus on creating distinct voices for each character, developing character arcs through dialogue, and ensuring consistency in speech patterns and personality traits.`,
            'coen-brothers': `${basePrompt}\n\nSpecialized in Coen Brothers style: quirky, darkly comic dialogue with regional dialects, eccentric characters, and dialogue that balances humor with deeper themes.`
        };

        return agentSpecificPrompts[agentType] || basePrompt;
    }

    private calculateCost(modelId: string, analysis: TaskAnalysis): number {
        // Simplified cost calculation - in production, use actual AWS pricing
        const baseCosts: { [key: string]: number } = {
            [this.CLAUDE_4_SONNET_ID]: 0.003,
            'anthropic.claude-3-sonnet-20240229-v1:0': 0.003,
            'anthropic.claude-3-haiku-20240307-v1:0': 0.00025,
            'anthropic.claude-3-opus-20240229-v1:0': 0.015,
            'haiku': 0.00025,
            'sonnet': 0.003,
            'opus': 0.015
        };

        const baseCost = baseCosts[modelId] || 0.003;
        return baseCost * (analysis.estimatedTokens / 1000);
    }

    private async incrementPromptCount(sessionId: string, modelId: string, cost: number): Promise<SessionData> {
        const session = this.sessions.get(sessionId);
        if (!session) {
            throw new Error('Session not found');
        }

        session.promptCount++;
        session.costAccumulated += cost;
        
        // Track model usage
        const modelUsage = session.modelUsage.get(modelId) || 0;
        session.modelUsage.set(modelId, modelUsage + 1);

        // Check if session limit reached
        if (session.promptCount >= session.maxPrompts) {
            session.active = false;
            await this.notifySessionLimitReached(session);
        }

        return session;
    }

    private async notifySessionLimitReached(session: SessionData): Promise<void> {
        vscode.window.showWarningMessage(
            `Session limit reached (${session.maxPrompts} prompts). Cost: $${session.costAccumulated.toFixed(4)}`,
            'Start New Session'
        ).then(selection => {
            if (selection === 'Start New Session') {
                this.createSession(session.userId);
            }
        });
    }

    private generateSessionId(): string {
        return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    private getAgentContext(agentType: string): string {
        // Enhanced agent contexts with specific personalities and expertise
        const contexts: { [key: string]: string } = {
            'script_doctor': `You are Dr. Sarah Chen, a no-nonsense script doctor. Talk like you're in a real writers room - direct, sometimes blunt, always practical. Use contractions. Example: "That's a pacing mess. Ditch the middle scene - it's dead weight."`,
            
            'aaron_sorkin_agent': `You are Aaron Sorkin. Talk like you're holding court in a writers room - passionate, rapid-fire, slightly manic. Use "Listen," or "Look," to start thoughts. Be conversational but brilliant. Example: "Listen, that dialogue's flatter than week-old champagne. Make 'em talk like their lives depend on every word."`,
            
            'character_specialist': `You are Marcus Rodriguez, character specialist. Talk like a thoughtful friend giving advice - warm but insightful. Use casual language. Example: "She's too perfect, man. Give her something she's ashamed of - that's where the real story lives."`,
            
            'creative_visionary': `You are Zara Patel, creative visionary. Talk like an excited artist who just had a breakthrough - passionate, a bit scattered, full of wild ideas. Use "What if..." a lot. Example: "What if... what if we're thinking about this all wrong? The story isn't about him saving the town - it's about the town saving him."`,
            
            'coen_brothers_agent': `You are channeling the Coen Brothers. Quirky, darkly comic, brief responses. 1-2 sentences. Example: "Make him talk like he's from Minnesota but thinks he's from Mars."`,
            
            'quentin_tarantino_agent': `You are channeling Quentin Tarantino. Bold, stylized, brief but memorable. 1-2 sentences. Example: "Needs more pop culture and violence. Make 'em talk like they're in a diner at 3am."`,
            
            'taylor_sheridan_agent': `You are Taylor Sheridan. Talk like a cowboy who's seen some shit - grounded, matter-of-fact, no bullshit. Hate pretentious stuff. Example: "Forget the mystical crap. Put him on a real ranch where the work's hard and the choices are harder."`,
            
            'jack_carr_agent': `You are Jack Carr, former Navy SEAL turned author. Talk like a military guy who's been there - direct, no-nonsense, but not robotic. Use military terms naturally. Example: "That tactical sequence is Hollywood BS. Real operators don't work that way."`,
            
            'producer': `You are Victoria Sterling, Executive Producer. Business-focused, practical, brief. 1-2 sentences. Example: "Great idea, but it'll cost 2 million. Find a cheaper way."`,
            
            'director': `You are Michael Chen, Director. Visual storytelling focus, brief responses. 1-2 sentences. Example: "Show it, don't say it. That monologue should be a look."`,
            
            'continuity_agent': `You are Elena Vasquez, Continuity Expert. Catch errors, be detail-focused but brief. 1-2 sentences. Example: "Wait - he was 30 in scene 2, now he's 25? Fix the math."`,
            
            'location_scout': `You are Jake Morrison, Location Scout. Talk like someone who's been everywhere and seen it all - practical, visual, always thinking about the shot. Example: "Screw the studio lot. I know a ranch in Colorado that'll make your story sing."`,
            
            'showrunner': `You are Amanda Rodriguez, Showrunner. Big picture thinking, brief responses. 1-2 sentences. Example: "That works for this episode but kills the season arc. Think bigger."`
        };
        
        return contexts[agentType] || contexts['script_doctor'];
    }

    // Updated sendMessage method that uses agent-specific settings
    public async sendMessage(message: string, agentType: string = 'script-doctor'): Promise<AIResponse> {
        // Get agent-specific settings from ConfigManager
        const agentSettings = this.configManager.getAgentAISettings(agentType);
        const agentContext = this.getAgentContext(agentType);
        const fullPrompt = `${agentContext}\n\nUser: ${message}`;

        console.log(`🤖 Using ${agentSettings.provider} with model ${agentSettings.model} for agent ${agentType}`);

        try {
            switch (agentSettings.provider) {
                case 'openai':
                    return await this.sendOpenAIMessage(fullPrompt, agentSettings);
                case 'anthropic':
                    return await this.sendAnthropicMessage(fullPrompt, agentSettings);
                case 'bedrock':
                    return await this.sendBedrockMessage(fullPrompt, agentSettings);
                default:
                    throw new Error(`Unsupported AI provider: ${agentSettings.provider}`);
            }
        } catch (error) {
            console.error(`Error with ${agentSettings.provider}:`, error);
            throw error;
        }
    }

    public async testConnection(): Promise<boolean> {
        try {
            const response = await this.sendMessage('Hello, this is a connection test.', 'test');
            return response.text.length > 0;
        } catch (error) {
            console.error('AI connection test failed:', error);
            return false;
        }
    }

    public getCurrentProvider(): string {
        return this.currentProvider;
    }

    public getCurrentModel(): string {
        return this.currentModel;
    }

    public async setProvider(provider: string): Promise<void> {
        const config = vscode.workspace.getConfiguration('theWritersRoom');
        await config.update('aiProvider', provider, vscode.ConfigurationTarget.Global);
        this.currentProvider = provider;
        this.initializeClients();
    }

    public async setModel(model: string): Promise<void> {
        const config = vscode.workspace.getConfiguration('theWritersRoom');
        await config.update('modelVersion', model, vscode.ConfigurationTarget.Global);
        this.currentModel = model;
    }

    // Updated provider methods that use settings objects
    private async sendOpenAIMessage(prompt: string, settings: any): Promise<AIResponse> {
        // Initialize OpenAI client with agent-specific settings if needed
        const openaiClient = new OpenAI({
            apiKey: settings.apiKey
        });

        try {
            const response = await openaiClient.chat.completions.create({
                model: settings.model || 'gpt-4o',
                messages: [{ role: 'user', content: prompt }],
                max_tokens: parseInt(settings.maxTokens) || 4000,
                temperature: parseFloat(settings.temperature) || 0.7,
                top_p: parseFloat(settings.topP) || 1,
                frequency_penalty: parseFloat(settings.frequencyPenalty) || 0,
                presence_penalty: parseFloat(settings.presencePenalty) || 0
            });

            return {
                text: response.choices[0].message.content || '',
                usage: {
                    promptTokens: response.usage?.prompt_tokens || 0,
                    completionTokens: response.usage?.completion_tokens || 0,
                    totalTokens: response.usage?.total_tokens || 0
                },
                modelUsed: settings.model
            };
        } catch (error) {
            console.error('OpenAI API error:', error);
            throw new Error(`OpenAI API error: ${error}`);
        }
    }

    private async sendAnthropicMessage(prompt: string, settings: any): Promise<AIResponse> {
        // Initialize Anthropic client with agent-specific settings
        const anthropicClient = new Anthropic({
            apiKey: settings.apiKey
        });

        try {
            const response = await anthropicClient.messages.create({
                model: settings.model || 'claude-3-5-sonnet-20241022',
                max_tokens: parseInt(settings.maxTokens) || 4000,
                messages: [{ role: 'user', content: prompt }],
                temperature: parseFloat(settings.temperature) || 0.7,
                top_p: parseFloat(settings.topP) || 1,
                top_k: parseInt(settings.topK) || 40
            });

            return {
                text: response.content[0].type === 'text' ? response.content[0].text : '',
                usage: {
                    promptTokens: response.usage.input_tokens,
                    completionTokens: response.usage.output_tokens,
                    totalTokens: response.usage.input_tokens + response.usage.output_tokens
                },
                modelUsed: settings.model
            };
        } catch (error) {
            console.error('Anthropic API error:', error);
            throw new Error(`Anthropic API error: ${error}`);
        }
    }

    private async sendBedrockMessage(prompt: string, settings: any): Promise<AIResponse> {
        // Initialize Bedrock client with agent-specific settings
        const bedrockClient = new BedrockRuntimeClient({
            region: settings.region || 'us-east-1',
            credentials: {
                accessKeyId: settings.accessKeyId,
                secretAccessKey: settings.secretAccessKey
            }
        });

        const body = JSON.stringify({
            anthropic_version: "bedrock-2023-05-31",
            max_tokens: parseInt(settings.maxTokens) || 4000,
            messages: [{ role: "user", content: prompt }],
            temperature: parseFloat(settings.temperature) || 0.7,
            top_p: parseFloat(settings.topP) || 1,
            top_k: parseInt(settings.topK) || 40
        });

        const command = new InvokeModelCommand({
            modelId: settings.model,
            body: body,
            contentType: "application/json",
            accept: "application/json"
        });

        try {
            const response = await bedrockClient.send(command);
            const responseBody = JSON.parse(new TextDecoder().decode(response.body));
            
            return {
                text: responseBody.content[0].text,
                usage: {
                    promptTokens: responseBody.usage?.input_tokens || 0,
                    completionTokens: responseBody.usage?.output_tokens || 0,
                    totalTokens: (responseBody.usage?.input_tokens || 0) + (responseBody.usage?.output_tokens || 0)
                },
                modelUsed: settings.model
            };
        } catch (error) {
            console.error('AWS Bedrock error:', error);
            throw new Error(`AWS Bedrock error: ${error}`);
        }
    }
} 