import * as vscode from 'vscode';
import { AgentManager } from '../agents/AgentManager';
import { AIService } from '../services/AIService';
import { CursorAgent } from '../agents/CursorAgent';
import { ChatPersistenceService, PersistedMessage, ChatSession } from '../services/ChatPersistenceService';


export interface AIMessage {
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: Date;
}

export interface MultiAgentMessage {
    id: string;
    agentId: string;
    agentName: string;
    content: string;
    timestamp: Date;
    type: 'message' | 'system';
}

export class SidebarChatProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'theWritersRoom.chatView';
    
    private _view?: vscode.WebviewView;
    private context: vscode.ExtensionContext;
    private agentManager: AgentManager;
    private aiService: AIService;
    private cursorAgent: CursorAgent;
    private persistenceService: ChatPersistenceService;

    private currentAgent: string = 'script_doctor';
    private conversationHistory: AIMessage[] = [];
    
    // Multi-agent chat properties
    private selectedAgents: Set<string> = new Set();
    private multiAgentHistory: MultiAgentMessage[] = [];
    private currentRound = 0;
    private maxRounds = 3;
    private isDiscussionActive = false;
    private currentTab: 'chat' | 'multiAgent' | 'settings' = 'multiAgent';
    private currentSession: ChatSession | null = null;

    constructor(context: vscode.ExtensionContext, agentManager: AgentManager) {
        this.context = context;
        this.agentManager = agentManager;
        this.aiService = AIService.getInstance();
        this.cursorAgent = CursorAgent.getInstance(context);
        this.persistenceService = ChatPersistenceService.getInstance(context);

        
        // Initialize with existing session or create new one
        this.currentSession = this.persistenceService.getOrCreateActiveSession('multi');
        this.loadSessionData();
    }

    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken,
    ) {
        this._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this.context.extensionUri]
        };

        webviewView.webview.html = this.getHtmlForWebview(webviewView.webview);

        // Handle messages from the webview
        webviewView.webview.onDidReceiveMessage(async (data) => {
            switch (data.type) {
                case 'sendMessage':
                    await this.handleMultiAgentMessage(data.message);
                    break;
                case 'clearConversation':
                    this.clearMultiAgentChat();
                    break;
                case 'showSettings':
                    vscode.commands.executeCommand('theWritersRoom.openSettings');
                    break;
                case 'newSession':
                    this.createNewSession();
                    break;
                case 'switchSession':
                    this.switchSession(data.sessionId);
                    break;
            }
        });

        // Restore conversation from persistence
        this.restoreConversation();

        // Send initial multi-agent setup
        this.sendMultiAgentInitialState();
    }

    private loadSessionData(): void {
        if (!this.currentSession) return;

        // Convert persisted messages to conversation history
        this.multiAgentHistory = this.currentSession.messages.map(msg => ({
            id: msg.id,
            agentId: msg.agentId,
            agentName: msg.agentName,
            content: msg.content,
            timestamp: new Date(msg.timestamp),
            type: msg.type as 'message' | 'system'
        }));

        // Restore agent selections
        if (this.currentSession.selectedAgents) {
            this.selectedAgents = new Set(this.currentSession.selectedAgents);
        }

        if (this.currentSession.activeAgent) {
            this.currentAgent = this.currentSession.activeAgent;
        }
    }

    private restoreConversation(): void {
        if (!this._view || !this.currentSession) return;

        // Send all persisted messages to webview
        this.currentSession.messages.forEach(msg => {
            this._view!.webview.postMessage({
                type: 'addMultiAgentMessage',
                message: {
                    id: msg.id,
                    agentId: msg.agentId,
                    agentName: msg.agentName,
                    content: msg.content,
                    timestamp: msg.timestamp,
                    type: msg.type
                }
            });
        });

        // Send session info
        this._view.webview.postMessage({
            type: 'sessionInfo',
            session: {
                id: this.currentSession.id,
                name: this.currentSession.name,
                messageCount: this.currentSession.messages.length
            }
        });
    }

    private createNewSession(): void {
        this.currentSession = this.persistenceService.createSession('multi');
        this.multiAgentHistory = [];
        this.selectedAgents.clear();
        
        if (this._view) {
            this._view.webview.postMessage({
                type: 'clearMessages'
            });
            this.sendMultiAgentInitialState();
        }
    }

    private switchSession(sessionId: string): void {
        if (this.persistenceService.setActiveSession(sessionId)) {
            this.currentSession = this.persistenceService.getSessionById(sessionId);
            this.loadSessionData();
            
            if (this._view) {
                this._view.webview.postMessage({
                    type: 'clearMessages'
                });
                this.restoreConversation();
            }
        }
    }

    private async handleSendMessage(message: string) {
        if (!this._view) {
            return;
        }

        // Add user message to conversation history
        const userMessage: AIMessage = {
            role: 'user',
            content: message,
            timestamp: new Date()
        };
        this.conversationHistory.push(userMessage);

        // Show user message in UI
        this._view.webview.postMessage({
            type: 'addMessage',
            message: {
                content: message,
                sender: 'user',
                timestamp: new Date().toISOString()
            }
        });

        try {
            // Show typing indicator
            this._view.webview.postMessage({
                type: 'showTyping',
                agentName: this.agentManager.getAgentName(this.currentAgent)
            });

            // Get AI response
            const response = await this.aiService.sendMessage(
                message,
                this.currentAgent
            );

            // Add AI response to conversation history
            const aiMessage: AIMessage = {
                role: 'assistant',
                content: response.text,
                timestamp: new Date()
            };
            this.conversationHistory.push(aiMessage);

            // Hide typing indicator and show response
            this._view.webview.postMessage({
                type: 'hideTyping'
            });

            this._view.webview.postMessage({
                type: 'addMessage',
                message: {
                    content: response.text,
                    sender: 'ai',
                    agentName: this.agentManager.getAgentName(this.currentAgent),
                    timestamp: new Date().toISOString()
                }
            });

        } catch (error) {
            console.error('Chat error:', error);
            
            this._view.webview.postMessage({
                type: 'hideTyping'
            });

            this._view.webview.postMessage({
                type: 'addMessage',
                message: {
                    content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}`,
                    sender: 'ai',
                    agentName: this.agentManager.getAgentName(this.currentAgent),
                    isError: true,
                    timestamp: new Date().toISOString()
                }
            });
        }
    }

    public switchAgent(agentId: string) {
        this.currentAgent = agentId;
        if (this._view) {
            this._view.webview.postMessage({
                type: 'agentSwitched',
                agentId: agentId,
                agentName: this.agentManager.getAgentName(agentId)
            });
        }
    }

    public async sendMessage(message: string, agentId?: string) {
        if (agentId) {
            this.switchAgent(agentId);
        }
        await this.handleSendMessage(message);
    }

    private clearConversation() {
        this.conversationHistory = [];
        if (this._view) {
            this._view.webview.postMessage({
                type: 'clearMessages'
            });
        }
    }

    private async insertToEditor(text: string) {
        const editor = vscode.window.activeTextEditor;
        if (editor) {
            const position = editor.selection.active;
            await editor.edit(editBuilder => {
                editBuilder.insert(position, text);
            });
        }
    }

    private sendAgentList() {
        if (this._view) {
            const agents = this.agentManager.getAllAgents();
            this._view.webview.postMessage({
                type: 'agentList',
                agents: agents.map(agent => ({
                    id: agent.id,
                    name: agent.name,
                    description: agent.description || agent.title
                })),
                currentAgent: this.currentAgent
            });
        }
    }

    private sendMultiAgentInitialState() {
        if (this._view) {
            // Send welcome message for multi-agent
            this._view.webview.postMessage({
                type: 'addMultiAgentMessage',
                message: {
                    id: 'welcome-' + Date.now(),
                    agentId: 'system',
                    agentName: 'System',
                    content: '🎬 Welcome to The Writers Room!\n\nStart chatting and multiple agents will collaborate to help with your writing. Configure agent models in Settings below.',
                    timestamp: new Date().toISOString(),
                    type: 'system'
                }
            });
        }
    }

    // Multi-agent chat methods
    private switchTab(tab: 'chat' | 'multiAgent' | 'settings') {
        this.currentTab = tab;
        if (this._view) {
            this._view.webview.postMessage({
                type: 'tabSwitched',
                tab: tab
            });
        }
    }

    private toggleAgentSelection(agentId: string) {
        if (this.selectedAgents.has(agentId)) {
            this.selectedAgents.delete(agentId);
        } else {
            this.selectedAgents.add(agentId);
        }
        
        if (this._view) {
            this._view.webview.postMessage({
                type: 'agentSelectionChanged',
                selectedAgents: Array.from(this.selectedAgents)
            });
        }
    }

    private async handleMultiAgentMessage(content: string) {
        const userMessage: MultiAgentMessage = {
            id: Date.now().toString(),
            agentId: 'user',
            agentName: 'You',
            content,
            timestamp: new Date(),
            type: 'message'
        };

        this.multiAgentHistory.push(userMessage);
        
        // LOG: User message for debugging
        console.log('[Writers Room] User message:', content);
        
        // Persist user message
        if (this.currentSession) {
            const persistedMessage: PersistedMessage = {
                id: userMessage.id,
                agentId: userMessage.agentId,
                agentName: userMessage.agentName,
                content: userMessage.content,
                timestamp: userMessage.timestamp.toISOString(),
                type: 'user'
            };
            this.persistenceService.addMessage(this.currentSession.id, persistedMessage);
        }
        
        if (this._view) {
            this._view.webview.postMessage({
                type: 'addMultiAgentMessage',
                message: {
                    id: userMessage.id,
                    agentId: 'user',
                    agentName: 'You',
                    content: userMessage.content,
                    timestamp: userMessage.timestamp.toISOString(),
                    type: 'user'
                }
            });
        }

        // Note: We let agents discuss document creation first, then CursorAgent will handle the actual creation

        // Check if user is addressing a specific agent by name
        const addressedAgent = this.detectAddressedAgent(content);
        
        if (addressedAgent) {
            // Only the addressed agent responds
            await this.getAgentResponse(addressedAgent.id, content);
        } else {
            // Get responses from 2-3 random active agents for variety
            const allAgents = this.agentManager.getAllAgents();
            const availableAgents = allAgents.filter(agent => {
                // Check if agent is available and active in settings
                const config = vscode.workspace.getConfiguration('theWritersRoom');
                const normalizedAgentId = agent.id.replace(/[^a-zA-Z0-9]/g, '_');
                const isActive = config.get<boolean>(`agents.${normalizedAgentId}.active`, true);
                return agent.available !== false && isActive;
            });
            
            // Select 2-3 random agents
            const numAgents = Math.min(3, Math.max(2, availableAgents.length));
            const selectedAgents = this.shuffleArray(availableAgents).slice(0, numAgents);
            
            for (const agent of selectedAgents) {
                await this.getAgentResponse(agent.id, content);
                await new Promise(resolve => setTimeout(resolve, 800)); // Slightly longer delay for realism
            }
        }

        // After agents respond, let CursorAgent process the conversation for document changes
        await this.processCursorAgentActions();
    }

    private async processCursorAgentActions() {
        // Convert recent conversation to format expected by CursorAgent
        const recentMessages = this.multiAgentHistory
            .slice(-10) // Last 10 messages
            .filter(msg => msg.type === 'message')
            .map(msg => ({
                agentId: msg.agentId,
                content: msg.content,
                timestamp: msg.timestamp
            }));

        if (recentMessages.length > 0) {
            await this.cursorAgent.processMultiAgentConversation(recentMessages);
        }
    }

    private shuffleArray<T>(array: T[]): T[] {
        const shuffled = [...array];
        for (let i = shuffled.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
        }
        return shuffled;
    }

    private detectAddressedAgent(message: string): any {
        const messageLower = message.toLowerCase();
        const allAgents = this.agentManager.getAllAgents();
        
        // Check for direct name mentions at the beginning of the message
        for (const agent of allAgents) {
            const agentNameLower = agent.name.toLowerCase();
            const firstNameLower = agent.name.split(' ')[0].toLowerCase();
            
            // Check if message starts with agent's name or first name
            if (messageLower.startsWith(agentNameLower + ',') || 
                messageLower.startsWith(agentNameLower + ':') ||
                messageLower.startsWith(agentNameLower + ' ') ||
                messageLower.startsWith(firstNameLower + ',') ||
                messageLower.startsWith(firstNameLower + ':') ||
                messageLower.startsWith(firstNameLower + ' ')) {
                
                // Check if agent is active
                const config = vscode.workspace.getConfiguration('theWritersRoom');
                const normalizedAgentId = agent.id.replace(/[^a-zA-Z0-9]/g, '_');
                const isActive = config.get<boolean>(`agents.${normalizedAgentId}.active`, true);
                
                if (agent.available !== false && isActive) {
                    return agent;
                }
            }
        }
        
        return null;
    }

    private async startMultiAgentDiscussion(topic: string) {
        if (this.selectedAgents.size < 2) {
            if (this._view) {
                this._view.webview.postMessage({
                    type: 'showError',
                    message: 'Please select at least 2 agents for a discussion.'
                });
            }
            return;
        }

        this.isDiscussionActive = true;
        this.currentRound = 0;
        
        // Add system message about the topic
        this.addMultiAgentSystemMessage(`🎬 Multi-Agent Discussion Started: "${topic}"`);
        this.addMultiAgentSystemMessage(`Participants: ${Array.from(this.selectedAgents).map(id => this.agentManager.getAgentName(id)).join(', ')}`);

        if (this._view) {
            this._view.webview.postMessage({
                type: 'discussionStarted',
                topic,
                selectedAgents: Array.from(this.selectedAgents)
            });
        }

        // Start the discussion rounds
        await this.conductDiscussionRounds(topic);
    }

    private async conductDiscussionRounds(topic: string) {
        const agents = Array.from(this.selectedAgents);
        
        for (let round = 0; round < this.maxRounds && this.isDiscussionActive; round++) {
            this.currentRound = round + 1;
            this.addMultiAgentSystemMessage(`📍 Round ${this.currentRound} of ${this.maxRounds}`);

            for (const agentId of agents) {
                if (!this.isDiscussionActive) break;

                await this.getAgentResponse(agentId, topic);
                
                // Add a small delay between agent responses
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
        }

        if (this.isDiscussionActive) {
            this.addMultiAgentSystemMessage(`🏁 Discussion completed after ${this.maxRounds} rounds. You can continue the conversation or start a new topic.`);
            this.isDiscussionActive = false;
            
            if (this._view) {
                this._view.webview.postMessage({
                    type: 'discussionCompleted'
                });
            }
        }
    }

    private async getAgentResponse(agentId: string, topic: string) {
        const agent = this.agentManager.getAgent(agentId);
        if (!agent) return;

        try {
            // Show typing indicator
            if (this._view) {
                this._view.webview.postMessage({
                    type: 'showMultiAgentTyping',
                    agentId,
                    agentName: agent.name
                });
            }

            // Build context for the agent
            const context = await this.buildAgentContext(agentId, topic);
            
            // Get AI response
            const response = await this.aiService.sendMessage(context, agentId);

            // Hide typing indicator
            if (this._view) {
                this._view.webview.postMessage({
                    type: 'hideMultiAgentTyping',
                    agentId
                });
            }

            // Add the response to conversation
            this.addMultiAgentMessage(agentId, agent.name, response.text);

        } catch (error) {
            console.error(`Error getting response from agent ${agentId}:`, error);
            
            if (this._view) {
                this._view.webview.postMessage({
                    type: 'hideMultiAgentTyping',
                    agentId
                });
            }

            this.addMultiAgentSystemMessage(`❌ Error getting response from ${agent.name}: ${error}`);
        }
    }

    private async buildAgentContext(agentId: string, topic: string): Promise<string> {
        const agent = this.agentManager.getAgent(agentId);
        if (!agent) return topic;

        // Build natural, conversational character context
        let context = '';
        
        switch (agentId) {
            case 'script_doctor':
                context = `You're a script doctor with years of experience fixing broken stories. You've seen every structural problem imaginable and know how to solve them. Keep your advice practical and actionable. Don't overthink it - just tell them what needs fixing and how to fix it.`;
                break;
                
            case 'aaron_sorkin_agent':
                context = `You're Aaron Sorkin. You love smart, fast-paced dialogue and characters who are passionate about their work. You think the best scenes happen when characters are walking and talking, debating ideas that matter. You're not pretentious - you just care about good storytelling.`;
                break;
                
            case 'character_specialist':
                context = `You're a character development expert. You believe great stories come from great characters, and great characters come from understanding what makes people tick. You're good at finding the emotional core of a story and helping writers create authentic, flawed, interesting people.`;
                break;
                
            case 'taylor_sheridan_agent':
                context = `You're Taylor Sheridan. You write about real people in tough situations, often in the American West. You care about authenticity and getting the details right. You don't like flashy gimmicks - you prefer honest storytelling about people trying to survive and do right by their families.`;
                break;
                
            case 'quentin_tarantino_agent':
                context = `You're Quentin Tarantino. You love movies, you love talking about movies, and you love making references to other movies. You're enthusiastic about genre films, great dialogue, and creative storytelling techniques. You're not trying to be cool - you're just genuinely excited about cinema.`;
                break;
                
            case 'coen_brothers_agent':
                context = `You're the Coen Brothers (speaking as one voice). You like dark humor, flawed characters, and stories that don't always end the way people expect. You're drawn to crime stories, period pieces, and ordinary people in extraordinary circumstances.`;
                break;
                
            case 'jack_carr_agent':
                context = `You're Jack Carr. You know action, military tactics, and how to write realistic thriller plots. You care about getting the technical details right and creating authentic, gritty stories about people under pressure.`;
                break;
                
            default:
                context = `You're ${agent.name}. You're an experienced writer and storyteller. You give honest, helpful feedback without being pretentious. You focus on what works, what doesn't, and how to make it better.`;
        }
        
        // CURSOR-STYLE FILE INTEGRATION: Automatically inject current document content
        console.log(`[Writers Room] DEBUG: Building context for ${agent.name}, topic: "${topic}"`);
        
        try {
            // Get current active document content (exactly like Cursor does)
            const activeEditor = vscode.window.activeTextEditor;
            if (activeEditor) {
                const currentDocument = activeEditor.document;
                const documentContent = currentDocument.getText();
                const fileName = currentDocument.fileName.split('/').pop() || currentDocument.fileName;
                
                if (documentContent && documentContent.length > 0) {
                    context += `\n\n=== CURRENT DOCUMENT: ${fileName} ===\n`;
                    context += `Content:\n${documentContent}\n\n`;
                    console.log(`[Writers Room] ✅ Added current document: ${fileName} (${documentContent.length} chars) to ${agent.name}`);
                } else {
                    console.log(`[Writers Room] Current document is empty: ${fileName}`);
                }
            } else {
                console.log(`[Writers Room] No active editor/document available`);
            }
            
            // Also include workspace files for additional context
            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
            if (workspaceFolder) {
                const pattern = new vscode.RelativePattern(workspaceFolder, '**/*.{md,txt,fountain}');
                const files = await vscode.workspace.findFiles(pattern, '**/node_modules/**', 3);
                
                if (files.length > 0) {
                    context += `=== WORKSPACE FILES ===\n`;
                    for (const fileUri of files) {
                        try {
                            const document = await vscode.workspace.openTextDocument(fileUri);
                            const fileName = fileUri.path.split('/').pop() || fileUri.path;
                            const content = document.getText();
                            
                            if (content && content.length > 0) {
                                context += `--- ${fileName} ---\n`;
                                context += content.substring(0, 1500);
                                if (content.length > 1500) {
                                    context += '\n[Content truncated...]';
                                }
                                context += '\n\n';
                                console.log(`[Writers Room] Added workspace file: ${fileName} (${content.length} chars)`);
                            }
                        } catch (error) {
                            console.warn(`[Writers Room] Error reading ${fileUri.path}:`, error);
                        }
                    }
                }
            }
        } catch (error) {
            console.error(`[Writers Room] 💥 Error creating document context:`, error);
        }
        
        // Add conversation history
        if (this.multiAgentHistory.length > 0) {
            context += `\n\nPrevious discussion:\n`;
            const recentMessages = this.multiAgentHistory
                .filter(msg => msg.type === 'message')
                .slice(-5); // Last 5 messages for context
            
            for (const msg of recentMessages) {
                if (msg.agentId !== agentId) { // Don't include own messages
                    context += `${msg.agentName}: ${msg.content}\n`;
                }
            }
        }
        
        // FORCE AGENTS TO READ THE ACTUAL DOCUMENT CONTENT
        context += `\n\nIMPORTANT: You have access to the actual document content above. DO NOT give generic advice about "the plot outline" or "the sample plot outline." Instead, you must reference specific details from the actual content you can see above. 

For example, if you see Detective Sarah Martinez, mention her by name. If you see specific plot points like antique coins or corruption conspiracy, reference those exact details. If you see character names, locations, or specific events, use them in your response.

DO NOT say things like "the sample plot outline" or "this outline" - be specific about what you're reading. Reference actual character names, plot points, and story elements from the document content provided above.`;
        
        const topicLower = topic.toLowerCase();
        if (topicLower.includes('read') || topicLower.includes('plot') || topicLower.includes('analyze')) {
            context += `\n\nThe user is asking you to read and analyze specific content. You MUST reference specific details, characters, plot points, or elements from the content above. Be specific and actionable in your feedback about the actual content you can see.`;
        }
        
        if (topicLower.includes('create') || topicLower.includes('write') || topicLower.includes('document')) {
            context += `\n\nThe user is asking about creating new content. Be specific about what should be created and provide concrete structure suggestions.`;
        }
        
        context += `\n\nRespond naturally and conversationally, but ALWAYS reference the specific content you can see above. Don't be generic - be specific about what you're reading.`;
        
        console.log(`[Writers Room] Built context for ${agent.name}: ${context.length} chars`);
        console.log(`[Writers Room] FULL CONTEXT for ${agent.name}:`, context);
        
        return context;
    }



    private addMultiAgentMessage(agentId: string, agentName: string, content: string) {
        const message: MultiAgentMessage = {
            id: Date.now().toString(),
            agentId,
            agentName,
            content,
            timestamp: new Date(),
            type: 'message'
        };

        this.multiAgentHistory.push(message);
        
        // Persist message
        if (this.currentSession) {
            const persistedMessage: PersistedMessage = {
                id: message.id,
                agentId: message.agentId,
                agentName: message.agentName,
                content: message.content,
                timestamp: message.timestamp.toISOString(),
                type: 'agent'
            };
            this.persistenceService.addMessage(this.currentSession.id, persistedMessage);
        }
        
        if (this._view) {
            this._view.webview.postMessage({
                type: 'addMultiAgentMessage',
                message: {
                    id: message.id,
                    agentId: message.agentId,
                    agentName: message.agentName,
                    content: message.content,
                    timestamp: message.timestamp.toISOString(),
                    type: 'agent'
                }
            });
        }
    }

    private addMultiAgentSystemMessage(content: string) {
        const message: MultiAgentMessage = {
            id: Date.now().toString(),
            agentId: 'system',
            agentName: 'System',
            content,
            timestamp: new Date(),
            type: 'system'
        };

        this.multiAgentHistory.push(message);
        
        // Persist system message
        if (this.currentSession) {
            const persistedMessage: PersistedMessage = {
                id: message.id,
                agentId: message.agentId,
                agentName: message.agentName,
                content: message.content,
                timestamp: message.timestamp.toISOString(),
                type: 'system'
            };
            this.persistenceService.addMessage(this.currentSession.id, persistedMessage);
        }
        
        if (this._view) {
            this._view.webview.postMessage({
                type: 'addMultiAgentMessage',
                message: {
                    id: message.id,
                    agentId: 'system',
                    agentName: 'System',
                    content: message.content,
                    timestamp: message.timestamp.toISOString(),
                    type: 'system'
                }
            });
        }
    }

    private stopDiscussion() {
        this.isDiscussionActive = false;
        this.addMultiAgentSystemMessage('🛑 Discussion stopped by user.');
        
        if (this._view) {
            this._view.webview.postMessage({
                type: 'discussionStopped'
            });
        }
    }

    private clearMultiAgentChat() {
        this.multiAgentHistory = [];
        this.isDiscussionActive = false;
        this.currentRound = 0;
        
        // Clear from persistence
        if (this.currentSession) {
            this.persistenceService.clearSession(this.currentSession.id);
        }
        
        if (this._view) {
            this._view.webview.postMessage({
                type: 'multiAgentChatCleared'
            });
            // Re-send welcome message
            this.sendMultiAgentInitialState();
        }
    }

    private detectDocumentRequest(message: string): string | null {
        const messageLower = message.toLowerCase().trim();
        
        // Document creation keywords
        const documentKeywords = [
            'create a new document',
            'create a new md document', 
            'create an outline',
            'create a treatment',
            'create a script',
            'create a story',
            'write an outline',
            'write a treatment',
            'build an outline',
            'make a document',
            'new document',
            'new md document',
            'create document'
        ];

        for (const keyword of documentKeywords) {
            if (messageLower.includes(keyword)) {
                // Determine document type based on content
                if (messageLower.includes('outline')) return 'outline';
                if (messageLower.includes('treatment')) return 'treatment';
                if (messageLower.includes('script')) return 'script';
                if (messageLower.includes('story')) return 'story';
                return 'document'; // generic document
            }
        }

        return null;
    }

    private async createAndPopulateDocument(docType: string, originalMessage: string) {
        try {
            // Create a new document
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
            const fileName = `${docType}_${timestamp}.md`;
            
            // Create the document content based on type
            let initialContent = this.getInitialDocumentContent(docType, originalMessage);
            
            // Create new document
            const doc = await vscode.workspace.openTextDocument({
                content: initialContent,
                language: 'markdown'
            });
            
            // Show the document in editor
            const editor = await vscode.window.showTextDocument(doc);
            
            // Add system message about document creation
            this.addMultiAgentSystemMessage(`📝 Created new ${docType} document: ${fileName}`);
            
            // Start collaborative writing process
            await this.startCollaborativeWriting(editor, docType, originalMessage);
            
        } catch (error) {
            console.error('Error creating document:', error);
            this.addMultiAgentSystemMessage(`❌ Error creating document: ${error}`);
        }
    }

    private getInitialDocumentContent(docType: string, originalMessage: string): string {
        const timestamp = new Date().toLocaleDateString();
        
        switch (docType) {
            case 'outline':
                return `# Story Outline\n\n**Created:** ${timestamp}\n**Request:** ${originalMessage}\n\n## Structure\n\n### Act I\n- \n\n### Act II\n- \n\n### Act III\n- \n\n## Characters\n\n## Themes\n\n## Notes\n\n`;
            
            case 'treatment':
                return `# Treatment\n\n**Created:** ${timestamp}\n**Request:** ${originalMessage}\n\n## Logline\n\n## Synopsis\n\n## Characters\n\n### Main Characters\n\n### Supporting Characters\n\n## Story Structure\n\n### Act I\n\n### Act II\n\n### Act III\n\n## Themes\n\n## Visual Style\n\n## Notes\n\n`;
            
            case 'script':
                return `# Script\n\n**Created:** ${timestamp}\n**Request:** ${originalMessage}\n\n**FADE IN:**\n\n## Scene 1\n\n**INT. LOCATION - DAY**\n\n\n\n**FADE OUT.**\n\n---\n\n## Notes\n\n`;
            
            default:
                return `# Document\n\n**Created:** ${timestamp}\n**Request:** ${originalMessage}\n\n## Content\n\n\n\n## Notes\n\n`;
        }
    }

    private async startCollaborativeWriting(editor: vscode.TextEditor, docType: string, originalMessage: string) {
        // Get active agents for collaboration
        const allAgents = this.agentManager.getAllAgents();
        const availableAgents = allAgents.filter(agent => {
            const config = vscode.workspace.getConfiguration('theWritersRoom');
            const normalizedAgentId = agent.id.replace(/[^a-zA-Z0-9]/g, '_');
            const isActive = config.get<boolean>(`agents.${normalizedAgentId}.active`, true);
            return agent.available !== false && isActive;
        });
        
        // Select 2-3 agents for collaboration
        const collaboratingAgents = this.shuffleArray(availableAgents).slice(0, 3);
        
        this.addMultiAgentSystemMessage(`🤝 Starting collaborative writing with: ${collaboratingAgents.map(a => a.name).join(', ')}`);
        
        // Each agent contributes to the document
        for (const agent of collaboratingAgents) {
            await this.getAgentDocumentContribution(agent.id, docType, originalMessage, editor);
            await new Promise(resolve => setTimeout(resolve, 1500)); // Pause between contributions
        }
        
        this.addMultiAgentSystemMessage(`✅ Collaborative writing session completed. Continue editing the document or ask for more input!`);
    }

    private async getAgentDocumentContribution(agentId: string, docType: string, originalMessage: string, editor: vscode.TextEditor) {
        const agent = this.agentManager.getAgent(agentId);
        if (!agent) return;

        try {
            // Show typing indicator
            if (this._view) {
                this._view.webview.postMessage({
                    type: 'showMultiAgentTyping',
                    agentId,
                    agentName: agent.name
                });
            }

            // Build context for document contribution
            const context = `You are contributing to a ${docType} document. Original request: "${originalMessage}"\n\nCurrent document content:\n${editor.document.getText()}\n\nPlease provide your contribution to improve this ${docType}. Focus on your expertise and add specific, actionable content. Be concise but valuable.`;
            
            // Get AI response
            const response = await this.aiService.sendMessage(context, agentId);

            // Hide typing indicator
            if (this._view) {
                this._view.webview.postMessage({
                    type: 'hideMultiAgentTyping',
                    agentId
                });
            }

            // Add agent's contribution to chat
            this.addMultiAgentMessage(agentId, agent.name, `📝 Adding to ${docType}: ${response.text}`);

            // Add contribution to document
            await this.insertContributionToDocument(editor, agent.name, response.text);

        } catch (error) {
            console.error(`Error getting document contribution from agent ${agentId}:`, error);
            
            if (this._view) {
                this._view.webview.postMessage({
                    type: 'hideMultiAgentTyping',
                    agentId
                });
            }
        }
    }

    private async insertContributionToDocument(editor: vscode.TextEditor, agentName: string, contribution: string) {
        await editor.edit(editBuilder => {
            // Find the "Notes" section or end of document
            const text = editor.document.getText();
            const notesIndex = text.lastIndexOf('## Notes');
            
            let insertPosition: vscode.Position;
            if (notesIndex !== -1) {
                // Insert before Notes section
                const line = editor.document.positionAt(notesIndex).line;
                insertPosition = new vscode.Position(line, 0);
            } else {
                // Insert at end of document
                insertPosition = new vscode.Position(editor.document.lineCount, 0);
            }
            
            const contributionText = `\n## ${agentName}'s Input\n\n${contribution}\n\n`;
            editBuilder.insert(insertPosition, contributionText);
        });
    }

    private getHtmlForWebview(webview: vscode.Webview): string {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Writers Room</title>
    <style>
        * {
            box-sizing: border-box;
        }
        
        body {
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            color: var(--vscode-editor-foreground);
            background-color: var(--vscode-editor-background);
            margin: 0;
            padding: 0;
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .header {
            padding: 12px 16px 8px 16px;
            border-bottom: 1px solid var(--vscode-panel-border);
            background-color: var(--vscode-editor-background);
            flex-shrink: 0;
        }
        
        .header-title {
            font-size: 16px;
            font-weight: 600;
            color: var(--vscode-editor-foreground);
            margin-bottom: 8px;
        }


        
        .agent-selector {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 8px;
        }
        
        .agent-selector select {
            background: #2d2d2d;
            color: #e3e3e3;
            border: 1px solid #404040;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            flex: 1;
            outline: none;
        }
        
        .agent-selector select:focus {
            border-color: #007acc;
        }
        
        .action-buttons {
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
        }
        
        .action-btn {
            background: #2d2d2d;
            color: #cccccc;
            border: 1px solid #404040;
            padding: 4px 8px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 11px;
            transition: all 0.2s ease;
        }
        
        .action-btn:hover {
            background: #383838;
            border-color: #555555;
        }
        
        .action-btn.primary {
            background: linear-gradient(135deg, #007acc, #005a9e);
            color: white;
            border: none;
        }
        
        .action-btn.primary:hover {
            background: linear-gradient(135deg, #1e88e5, #1976d2);
        }
        
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            scroll-behavior: smooth;
        }
        
        .chat-container::-webkit-scrollbar {
            width: 8px;
        }
        
        .chat-container::-webkit-scrollbar-track {
            background: var(--vscode-editor-background);
        }
        
        .chat-container::-webkit-scrollbar-thumb {
            background: var(--vscode-scrollbarSlider-background);
            border-radius: 4px;
        }
        
        .chat-container::-webkit-scrollbar-thumb:hover {
            background: var(--vscode-scrollbarSlider-hoverBackground);
        }
        
        .message {
            margin-bottom: 16px;
            display: flex;
            flex-direction: column;
            max-width: 100%;
        }
        
        .message.user {
            align-items: flex-end;
        }
        
        .message.ai {
            align-items: flex-start;
        }
        
        .message-bubble {
            max-width: 85%;
            padding: 12px 16px;
            border-radius: 18px;
            font-size: 14px;
            line-height: 1.4;
            word-wrap: break-word;
            position: relative;
        }
        
        .message.user .message-bubble {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border-bottom-right-radius: 6px;
            margin-left: auto;
        }
        
        .message.ai .message-bubble,
        .message.agent .message-bubble {
            background: var(--vscode-list-inactiveSelectionBackground);
            color: var(--vscode-editor-foreground);
            border: 1px solid var(--vscode-panel-border);
            border-bottom-left-radius: 6px;
            margin-right: auto;
        }
        
        .message.system .message-bubble {
            background: var(--vscode-textCodeBlock-background);
            color: var(--vscode-editor-foreground);
            border: 1px solid var(--vscode-panel-border);
            border-radius: 6px;
            margin: 0 auto;
            text-align: center;
        }
        
        .message.error .message-bubble {
            background: var(--vscode-inputValidation-errorBackground);
            color: var(--vscode-errorForeground);
            border: 1px solid var(--vscode-errorForeground);
        }
        
        .message-header {
            font-size: 11px;
            color: var(--vscode-input-placeholderForeground);
            margin-bottom: 4px;
            padding: 0 4px;
            font-weight: 500;
        }
        
        .message.user .message-header {
            text-align: right;
        }
        
        .message-content {
            white-space: pre-wrap;
            margin: 0;
        }
        
        .message-actions {
            display: flex;
            gap: 6px;
            margin-top: 8px;
            padding: 0 4px;
        }
        
        .message.user .message-actions {
            justify-content: flex-end;
        }
        
        .message-action {
            background: #383838;
            color: #cccccc;
            border: none;
            padding: 4px 8px;
            border-radius: 12px;
            cursor: pointer;
            font-size: 11px;
            transition: all 0.2s ease;
        }
        
        .message-action:hover {
            background: #4a4a4a;
            color: #ffffff;
        }
        
        .typing-indicator {
            display: flex;
            align-items: center;
            padding: 12px 16px;
            font-style: italic;
            color: var(--vscode-input-placeholderForeground);
            font-size: 13px;
            margin-bottom: 8px;
        }
        
        .typing-dots {
            display: inline-flex;
            margin-left: 8px;
        }
        
        .typing-dot {
            width: 4px;
            height: 4px;
            background: var(--vscode-input-placeholderForeground);
            border-radius: 50%;
            margin: 0 1px;
            animation: typing 1.4s infinite;
        }
        
        .typing-dot:nth-child(2) {
            animation-delay: 0.2s;
        }
        
        .typing-dot:nth-child(3) {
            animation-delay: 0.4s;
        }
        
        @keyframes typing {
            0%, 60%, 100% { opacity: 0.3; }
            30% { opacity: 1; }
        }
        
        .input-container {
            padding: 16px;
            border-top: 1px solid var(--vscode-panel-border);
            background-color: var(--vscode-editor-background);
            flex-shrink: 0;
        }
        
        .quick-actions {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-bottom: 12px;
        }
        
        .quick-action {
            background: #2d2d2d;
            color: #cccccc;
            border: 1px solid #404040;
            padding: 6px 10px;
            border-radius: 12px;
            cursor: pointer;
            font-size: 11px;
            transition: all 0.2s ease;
            white-space: nowrap;
        }
        
        .quick-action:hover {
            background: #383838;
            border-color: #555555;
            color: #ffffff;
        }
        
        .quick-action.primary {
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            border: none;
        }
        
        .quick-action.primary:hover {
            background: linear-gradient(135deg, #32cd32, #20c997);
        }
        
        .input-wrapper {
            position: relative;
            display: flex;
            align-items: flex-end;
            background: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            border-radius: 12px;
            transition: border-color 0.2s ease;
        }
        
        .input-wrapper:focus-within {
            border-color: var(--vscode-focusBorder);
        }
        
        .input-wrapper textarea {
            background: transparent;
            color: var(--vscode-input-foreground);
            border: none;
            padding: 12px 16px;
            border-radius: 12px;
            resize: none;
            min-height: 20px;
            max-height: 120px;
            font-family: inherit;
            font-size: 14px;
            line-height: 1.4;
            flex: 1;
            outline: none;
        }
        
        .input-wrapper textarea::placeholder {
            color: var(--vscode-input-placeholderForeground);
        }
        
        .send-button {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            width: 32px;
            height: 32px;
            border-radius: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 6px 8px 6px 0;
            transition: all 0.2s ease;
            flex-shrink: 0;
        }
        
        .send-button:hover {
            background: var(--vscode-button-hoverBackground);
            transform: translateY(-1px);
        }
        
        .send-button:active {
            transform: translateY(0);
        }
        
        .send-button:disabled {
            background: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
            cursor: not-allowed;
            transform: none;
        }
        
        .send-icon {
            width: 16px;
            height: 16px;
            fill: currentColor;
        }
        
        .secondary-actions {
            display: flex;
            gap: 6px;
            margin-top: 8px;
        }
        
        .secondary-btn {
            background: transparent;
            color: var(--vscode-button-secondaryForeground);
            border: 1px solid var(--vscode-panel-border);
            padding: 6px 10px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 11px;
            transition: all 0.2s ease;
            flex: 1;
        }
        
        .secondary-btn:hover {
            background: var(--vscode-button-secondaryHoverBackground);
            color: var(--vscode-button-secondaryForeground);
            border-color: var(--vscode-button-background);
        }

        /* Multi-Agent Specific Styles */
        .agent-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
            gap: 6px;
            margin-bottom: 12px;
            max-height: 120px;
            overflow-y: auto;
        }

        .agent-card {
            padding: 8px 6px;
            background: var(--vscode-list-inactiveSelectionBackground);
            border: 1px solid var(--vscode-panel-border);
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
            text-align: center;
            font-size: 11px;
            color: var(--vscode-editor-foreground);
        }

        .agent-card:hover {
            background: var(--vscode-list-hoverBackground);
            border-color: var(--vscode-button-background);
        }

        .agent-card.selected {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: 1px solid var(--vscode-button-background);
        }

        .agent-name {
            font-weight: 500;
            margin-bottom: 2px;
        }

        .agent-title {
            font-size: 10px;
            color: var(--vscode-input-placeholderForeground);
            opacity: 0.8;
        }

        .agent-card.selected .agent-title {
            color: var(--vscode-button-foreground);
            opacity: 0.8;
        }

        .discussion-controls {
            display: flex;
            gap: 6px;
            margin-bottom: 12px;
        }

        .topic-input {
            flex: 1;
            background: var(--vscode-input-background);
            color: var(--vscode-input-foreground);
            border: 1px solid var(--vscode-input-border);
            padding: 6px 8px;
            border-radius: 6px;
            font-size: 12px;
            outline: none;
        }

        .topic-input:focus {
            border-color: var(--vscode-focusBorder);
        }

        .discussion-btn {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            padding: 6px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 11px;
            transition: all 0.2s ease;
        }

        .discussion-btn:hover {
            background: var(--vscode-button-hoverBackground);
        }

        .discussion-btn:disabled {
            background: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
            cursor: not-allowed;
        }

        .discussion-btn.stop {
            background: var(--vscode-errorForeground);
            color: var(--vscode-editor-background);
        }

        .discussion-btn.stop:hover {
            background: var(--vscode-errorForeground);
            opacity: 0.8;
        }

        .multi-agent-status {
            background: var(--vscode-list-inactiveSelectionBackground);
            border: 1px solid var(--vscode-panel-border);
            border-radius: 6px;
            padding: 8px;
            margin-bottom: 8px;
            font-size: 11px;
            color: var(--vscode-editor-foreground);
        }

        .multi-agent-status.active {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: 1px solid var(--vscode-button-background);
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-title">The Writers Room</div>
    </div>
    
    <!-- Multi-Agent Chat Interface (Native) -->
    <div class="multi-agent-status" id="discussionStatus">
        🎬 Welcome to The Writers Room! Configure agents and models in Settings below.
    </div>
    <div class="chat-container" id="multiAgentContainer">
        <!-- Multi-agent messages will appear here -->
    </div>
    <div class="input-container">
        <div class="input-wrapper">
            <textarea id="multiAgentInput" placeholder="Join the discussion..." rows="1"></textarea>
            <button class="send-button" onclick="sendMultiAgentMessage()" id="multiSendButton">
                <svg class="send-icon" viewBox="0 0 24 24">
                    <path d="M2,21L23,12L2,3V10L17,12L2,14V21Z"/>
                </svg>
            </button>
        </div>
        <div class="secondary-actions">
            <button class="secondary-btn" onclick="clearMultiAgentChat()">Clear Chat</button>
            <button class="secondary-btn" onclick="showSettings()">Settings</button>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        let selectedAgents = new Set();
        let isDiscussionActive = false;
        
        // Auto-resize textarea
        const multiAgentTextarea = document.getElementById('multiAgentInput');
        const multiSendButton = document.getElementById('multiSendButton');
        
        multiAgentTextarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
            
            // Enable/disable send button based on content
            const hasContent = this.value.trim().length > 0;
            multiSendButton.disabled = !hasContent;
            multiSendButton.style.opacity = hasContent ? '1' : '0.5';
        });
        
        function sendMultiAgentMessage() {
            const input = document.getElementById('multiAgentInput');
            const message = input.value.trim();
            if (message) {
                vscode.postMessage({
                    type: 'sendMessage',
                    message: message
                });
                input.value = '';
                input.style.height = 'auto';
                multiSendButton.disabled = true;
                multiSendButton.style.opacity = '0.5';
            }
        }

        // Removed agent selection functions - now handled in Settings tab

        function clearMultiAgentChat() {
            vscode.postMessage({
                type: 'clearConversation'
            });
        }
        

        function showSettings() {
            vscode.postMessage({
                type: 'showSettings'
            });
        }
        
        // Message handling
        window.addEventListener('message', event => {
            const message = event.data;
            switch (message.type) {
                case 'addMultiAgentMessage':
                    addMultiAgentMessage(message.message);
                    break;
                case 'showMultiAgentTyping':
                    showMultiAgentTyping(message.agentName);
                    break;
                case 'hideMultiAgentTyping':
                    hideMultiAgentTyping();
                    break;
                case 'multiAgentChatCleared':
                    clearMultiAgentMessages();
                    break;
            }
        });
        

        
        // Multi-agent specific functions
        function addMultiAgentMessage(messageData) {
            const container = document.getElementById('multiAgentContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message ' + messageData.type + (messageData.isError ? ' error' : '');
            
            let header = '';
            if (messageData.type === 'agent' && messageData.agentName) {
                header = '<div class="message-header">' + messageData.agentName + '</div>';
            } else if (messageData.type === 'user') {
                header = '<div class="message-header">You</div>';
            } else if (messageData.type === 'system') {
                header = '<div class="message-header">System</div>';
            }
            
            messageDiv.innerHTML = header + 
                '<div class="message-bubble"><div class="message-content">' + messageData.content + '</div></div>';
            
            container.appendChild(messageDiv);
            container.scrollTop = container.scrollHeight;
        }

        // Agent selection now handled in Settings tab

        function showMultiAgentTyping(agentName) {
            const container = document.getElementById('multiAgentContainer');
            const typingDiv = document.createElement('div');
            typingDiv.className = 'typing-indicator';
            typingDiv.id = 'multi-typing-indicator';
            typingDiv.innerHTML = agentName + ' is thinking<span class="typing-dots"><span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span></span>';
            container.appendChild(typingDiv);
            container.scrollTop = container.scrollHeight;
        }

        function hideMultiAgentTyping() {
            const typing = document.getElementById('multi-typing-indicator');
            if (typing) {
                typing.remove();
            }
        }

        function clearMultiAgentMessages() {
            const container = document.getElementById('multiAgentContainer');
            container.innerHTML = '';
        }

        // Add keyboard support for multi-agent input
        multiAgentTextarea.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (this.value.trim()) {
                    sendMultiAgentMessage();
                }
            }
        });

        // Initialize send button state
        multiSendButton.disabled = true;
        multiSendButton.style.opacity = '0.5';
    </script>
</body>
</html>`;
    }
} 