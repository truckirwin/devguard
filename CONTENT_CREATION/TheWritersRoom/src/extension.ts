import * as vscode from 'vscode';
import { AIService, TaskRequest } from './services/AIService';
import { ConfigManager } from './services/ConfigManager';

import { AgentManager } from './agents/AgentManager';
import { SidebarChatProvider } from './chat/SidebarChatProvider';
import { AgentTreeProvider } from './providers/AgentTreeProvider';
import { AppDataManager } from './config/AppDataManager';
// import { ScriptImporter } from './config/ScriptImporter';
import { SettingsWebviewProvider } from './providers/SettingsWebviewProvider';
import { DocumentEditorService } from './services/DocumentEditorService';
import { CursorAgent } from './agents/CursorAgent';
import { VisualEditorProvider } from './providers/VisualEditorProvider';
import { ChatPersistenceService } from './services/ChatPersistenceService';
import { DocumentContextService } from './services/DocumentContextService';


// Global extension state
let aiService: AIService;
let configManager: ConfigManager;
let agentManager: AgentManager;
let currentSession: any;
let statusBarItem: vscode.StatusBarItem;
let outputChannel: vscode.OutputChannel;
let agentTreeProvider: AgentTreeProvider;
let extensionContext: vscode.ExtensionContext;
let appDataManager: AppDataManager;
// let scriptImporter: ScriptImporter;
let documentEditor: DocumentEditorService;
let cursorAgent: CursorAgent;
let visualEditor: VisualEditorProvider;
let chatPersistence: ChatPersistenceService;
let documentContext: DocumentContextService;


export async function activate(context: vscode.ExtensionContext) {
    console.log('🎬 The Writers Room extension is now active!');

    // Store context globally for use in other functions
    extensionContext = context;

    // Initialize core services
    try {
        configManager = ConfigManager.getInstance(context);
        appDataManager = AppDataManager.getInstance(context);
        // scriptImporter = new ScriptImporter(appDataManager);
        aiService = AIService.getInstance();
        agentManager = new AgentManager(context);
        documentEditor = DocumentEditorService.getInstance();
        cursorAgent = CursorAgent.getInstance(context);
        visualEditor = VisualEditorProvider.getInstance(context);
        chatPersistence = ChatPersistenceService.getInstance(context);
        documentContext = DocumentContextService.getInstance(context);

        outputChannel = vscode.window.createOutputChannel('The Writers Room');
        
        // Create initial session
        initializeSession();
        
        console.log('✅ Core services initialized successfully');
    } catch (error) {
        console.error('❌ Failed to initialize core services:', error);
        vscode.window.showErrorMessage('Failed to initialize The Writers Room. Please check the logs.');
        return;
    }

    // Register all commands
    registerCommands(context);
    
    // Set up UI elements
    await setupUI(context);
    
    // Check configuration and show welcome message
    checkConfigurationAndWelcome();

    console.log('🚀 The Writers Room extension activation complete!');
}

async function initializeSession() {
    try {
        currentSession = await aiService.createSession('vscode-user');
        console.log(`📝 Session created: ${currentSession.sessionId}`);
    } catch (error) {
        console.error('Failed to create AI session:', error);
    }
}

function registerCommands(context: vscode.ExtensionContext) {
    const commands = [
        // Core AI Chat Commands
        vscode.commands.registerCommand('theWritersRoom.openAIChat', async () => {
            await openAIChat();
        }),

        vscode.commands.registerCommand('theWritersRoom.chatWithAgent', async (agentType?: string) => {
            await chatWithAgent(agentType);
        }),

        vscode.commands.registerCommand('theWritersRoom.selectAgent', async () => {
            await selectAgent();
        }),



        // Writing Enhancement Commands
        vscode.commands.registerCommand('theWritersRoom.improveDialogue', async () => {
            await improveSelectedText('dialogue');
        }),

        vscode.commands.registerCommand('theWritersRoom.developCharacter', async () => {
            await improveSelectedText('character');
        }),

        vscode.commands.registerCommand('theWritersRoom.analyzeScript', async () => {
            await analyzeCurrentDocument();
        }),

        vscode.commands.registerCommand('theWritersRoom.brainstormIdeas', async () => {
            await brainstormIdeas();
        }),

        // Project Management Commands
        vscode.commands.registerCommand('theWritersRoom.createProject', async () => {
            await createNewProject();
        }),

        vscode.commands.registerCommand('theWritersRoom.newScene', async () => {
            await createNewScene();
        }),

        vscode.commands.registerCommand('theWritersRoom.newCharacter', async () => {
            await createNewCharacter();
        }),

        // Configuration Commands
        vscode.commands.registerCommand('theWritersRoom.configureAPI', async () => {
            await configManager.configureAPIKeys();
        }),

        vscode.commands.registerCommand('theWritersRoom.switchAIProvider', async () => {
            await switchAIProvider();
        }),

        vscode.commands.registerCommand('theWritersRoom.testAIConnection', async () => {
            await testAIConnection();
        }),

        vscode.commands.registerCommand('theWritersRoom.openSettings', async () => {
            await configManager.openSettings();
        }),

        // Session Management Commands
        vscode.commands.registerCommand('theWritersRoom.clearConversation', async () => {
            await clearConversation();
        }),

        vscode.commands.registerCommand('theWritersRoom.showSessionStatus', async () => {
            await showSessionStatus();
        }),

        vscode.commands.registerCommand('theWritersRoom.newSession', async () => {
            await createNewSession();
        }),

        // Reset and Refresh Commands
        vscode.commands.registerCommand('theWritersRoom.resetTreeViews', async () => {
            await resetTreeViews();
        }),

        vscode.commands.registerCommand('theWritersRoom.refreshTreeViews', async () => {
            await refreshTreeViews();
        }),

        // Agent Model Configuration Commands
        vscode.commands.registerCommand('theWritersRoom.configureAgentModels', async () => {
            await configManager.configureAgentModels();
        }),

        // Configuration Management Commands
        vscode.commands.registerCommand('theWritersRoom.openConfigFile', async () => {
            await openConfigFile();
        }),

        vscode.commands.registerCommand('theWritersRoom.importScript', async () => {
            await importScript();
        }),

        vscode.commands.registerCommand('theWritersRoom.viewImportedScripts', async () => {
            await viewImportedScripts();
        }),

        vscode.commands.registerCommand('theWritersRoom.exportConfig', async () => {
            await exportConfiguration();
        }),

        vscode.commands.registerCommand('theWritersRoom.resetConfig', async () => {
            await resetConfiguration();
        }),

        // Settings Webview Command
        vscode.commands.registerCommand('theWritersRoom.openSettingsWebview', async () => {
            await vscode.commands.executeCommand('theWritersRoom.settingsView.focus');
        }),

        // CursorAgent Commands
        vscode.commands.registerCommand('theWritersRoom.applyAllChanges', async () => {
            await cursorAgent.applyAllPendingChanges();
        }),

        vscode.commands.registerCommand('theWritersRoom.rejectAllChanges', async () => {
            await cursorAgent.rejectAllPendingChanges();
        }),

        vscode.commands.registerCommand('theWritersRoom.toggleAutoApply', async () => {
            const isEnabled = cursorAgent.isAutoApplyEnabled();
            cursorAgent.setAutoApplyMode(!isEnabled);
        }),

        vscode.commands.registerCommand('theWritersRoom.createDocumentFromChat', async () => {
            // This will be triggered from the chat provider
            vscode.window.showInformationMessage('Document creation from chat is handled automatically');
        }),

        vscode.commands.registerCommand('theWritersRoom.rollbackDocument', async () => {
            const activeEditor = vscode.window.activeTextEditor;
            if (activeEditor) {
                const snapshots = documentEditor.getSessionSnapshots(activeEditor.document.uri);
                if (snapshots.length > 1) {
                    const previousSnapshot = snapshots[snapshots.length - 2];
                    await documentEditor.rollbackToSnapshot(activeEditor.document.uri, previousSnapshot.id);
                    vscode.window.showInformationMessage('Document rolled back to previous version');
                } else {
                    vscode.window.showWarningMessage('No previous version available');
                }
            }
        }),

        // Visual feedback commands
        vscode.commands.registerCommand('theWritersRoom.showAgentStatus', async () => {
            const activeEditor = vscode.window.activeTextEditor;
            if (activeEditor) {
                const changes = documentEditor.getSessionChanges(activeEditor.document.uri);
                const agentCounts = new Map<string, number>();
                
                changes.forEach(change => {
                    agentCounts.set(change.agentId, (agentCounts.get(change.agentId) || 0) + 1);
                });

                const agentList = Array.from(agentCounts.entries())
                    .map(([agent, count]) => `• ${agent}: ${count} suggestions`)
                    .join('\n');

                vscode.window.showInformationMessage(
                    `Active Agents:\n${agentList || 'No active suggestions'}`,
                    'View All Agents'
                ).then(selection => {
                    if (selection === 'View All Agents') {
                        vscode.commands.executeCommand('workbench.view.extension.theWritersRoom');
                    }
                });
            }
        }),

        vscode.commands.registerCommand('theWritersRoom.showPendingChanges', async () => {
            const activeEditor = vscode.window.activeTextEditor;
            if (activeEditor) {
                const changes = documentEditor.getSessionChanges(activeEditor.document.uri);
                const pendingChanges = changes.filter(c => !c.applied);
                
                if (pendingChanges.length === 0) {
                    vscode.window.showInformationMessage('No pending changes');
                    return;
                }

                const changeItems = pendingChanges.map(change => ({
                    label: `${change.agentId}: ${change.reasoning}`,
                    description: `Line ${change.range.start.line + 1}`,
                    detail: change.newText.slice(0, 100) + (change.newText.length > 100 ? '...' : ''),
                    changeId: change.id
                }));

                const selected = await vscode.window.showQuickPick(changeItems, {
                    placeHolder: 'Select a change to apply or press Escape to cancel',
                    title: `${pendingChanges.length} Pending Changes`
                });

                if (selected) {
                    await documentEditor.applyChange(selected.changeId, activeEditor.document.uri);
                    vscode.window.showInformationMessage('Change applied successfully');
                }
            }
        }),

        vscode.commands.registerCommand('theWritersRoom.showQualityReport', async () => {
            const activeEditor = vscode.window.activeTextEditor;
            if (activeEditor) {
                const text = activeEditor.document.getText();
                const lineCount = activeEditor.document.lineCount;
                const wordCount = text.split(/\s+/).filter(word => word.length > 0).length;
                const avgWordsPerLine = Math.round(wordCount / lineCount);
                
                const report = `Writing Quality Report:
• Lines: ${lineCount}
• Words: ${wordCount}
• Avg words per line: ${avgWordsPerLine}
• Estimated reading time: ${Math.ceil(wordCount / 200)} minutes

Quality assessment based on agent feedback and document analysis.`;

                vscode.window.showInformationMessage(report, 'Analyze Document').then(selection => {
                    if (selection === 'Analyze Document') {
                        vscode.commands.executeCommand('theWritersRoom.analyzeScript');
                    }
                });
            }
        }),

        vscode.commands.registerCommand('theWritersRoom.clearVisualFeedback', async () => {
            const activeEditor = vscode.window.activeTextEditor;
            if (activeEditor) {
                visualEditor.clearAllVisualFeedback(activeEditor.document.uri);
                vscode.window.showInformationMessage('Visual feedback cleared');
            }
        }),

        // Chat session management commands
        vscode.commands.registerCommand('theWritersRoom.newChatSession', async () => {
            const sessionName = await vscode.window.showInputBox({
                prompt: 'Enter a name for the new chat session',
                placeHolder: 'My Writing Session'
            });
            
            if (sessionName) {
                const session = chatPersistence.createSession('multi', sessionName);
                vscode.window.showInformationMessage(`Created new chat session: ${session.name}`);
            }
        }),

        vscode.commands.registerCommand('theWritersRoom.showChatSessions', async () => {
            const sessions = chatPersistence.getAllSessions();
            
            if (sessions.length === 0) {
                vscode.window.showInformationMessage('No chat sessions found');
                return;
            }

            const sessionItems = sessions.map(session => ({
                label: session.name,
                description: `${session.messages.length} messages`,
                detail: `Created: ${new Date(session.created).toLocaleString()} | Last updated: ${new Date(session.lastUpdated).toLocaleString()}`,
                sessionId: session.id
            }));

            const selected = await vscode.window.showQuickPick(sessionItems, {
                placeHolder: 'Select a chat session to restore',
                title: 'Chat Sessions'
            });

            if (selected) {
                chatPersistence.setActiveSession(selected.sessionId);
                vscode.window.showInformationMessage(`Restored chat session: ${selected.label}`);
                // Refresh the sidebar
                vscode.commands.executeCommand('workbench.view.extension.theWritersRoom');
            }
        }),

        vscode.commands.registerCommand('theWritersRoom.exportChatSession', async () => {
            const activeSession = chatPersistence.getActiveSession();
            if (!activeSession) {
                vscode.window.showWarningMessage('No active chat session to export');
                return;
            }

            const exportData = chatPersistence.exportSession(activeSession.id);
            if (exportData) {
                const saveUri = await vscode.window.showSaveDialog({
                    defaultUri: vscode.Uri.file(`${activeSession.name.replace(/[^a-zA-Z0-9]/g, '_')}.json`),
                    filters: {
                        'JSON Files': ['json'],
                        'All Files': ['*']
                    }
                });

                if (saveUri) {
                    await vscode.workspace.fs.writeFile(saveUri, Buffer.from(exportData, 'utf8'));
                    vscode.window.showInformationMessage('Chat session exported successfully');
                }
            }
        }),

        vscode.commands.registerCommand('theWritersRoom.cleanupChatSessions', async () => {
            const result = await vscode.window.showWarningMessage(
                'This will remove old chat sessions, keeping only the 50 most recent ones. Continue?',
                'Cleanup',
                'Cancel'
            );

            if (result === 'Cleanup') {
                chatPersistence.cleanupOldSessions(50);
                vscode.window.showInformationMessage('Chat sessions cleaned up');
            }
        }),

        // Debug command to test document context service
        vscode.commands.registerCommand('theWritersRoom.testDocumentContext', async () => {
            try {
                const query = await vscode.window.showInputBox({
                    prompt: 'Enter search query to test document context',
                    placeHolder: 'plot, character, outline, etc.'
                });

                if (!query) return;

                const analysis = await documentContext.analyzeDocumentForAgents(query);
                
                const message = `Document Analysis for "${query}":

${analysis.contextSummary}

Found ${analysis.relevantDocuments.length} relevant documents:
${analysis.relevantDocuments.map(doc => `- ${doc.fileName} (${doc.wordCount} words)`).join('\n')}

Suggested documents:
${analysis.suggestedDocuments.join(', ')}

Project stats:
${JSON.stringify(documentContext.getProjectStats(), null, 2)}`;

                vscode.window.showInformationMessage(message, 'View Details').then(selection => {
                    if (selection === 'View Details') {
                        outputChannel.appendLine('=== DOCUMENT CONTEXT DEBUG ===');
                        outputChannel.appendLine(message);
                        outputChannel.appendLine('\n=== DOCUMENT CONTENTS ===');
                        analysis.relevantDocuments.forEach(doc => {
                            outputChannel.appendLine(`\n--- ${doc.fileName} ---`);
                            outputChannel.appendLine(doc.content);
                        });
                        outputChannel.show();
                    }
                });
            } catch (error) {
                vscode.window.showErrorMessage(`Document context test failed: ${error}`);
                console.error('Document context test error:', error);
            }
        }),

        // Debug command to test agent context building
        vscode.commands.registerCommand('theWritersRoom.testAgentContext', async () => {
            try {
                const query = await vscode.window.showInputBox({
                    prompt: 'Enter message to test agent context building',
                    placeHolder: 'read the main plot and tell me your ideas'
                });

                if (!query) return;

                // Test document query extraction
                const testExtraction = (message: string): string | null => {
                    const text = message.toLowerCase();
                    const readingPatterns = [
                        /read the (.+)/,
                        /tell me about (.+)/,
                        /what does the (.+) say/,
                        /according to the (.+)/,
                        /in the (.+)/,
                        /the (.+) outline/,
                        /the (.+) document/,
                        /the (.+) script/,
                        /the (.+) treatment/,
                        /plot outline/,
                        /character document/,
                        /story outline/,
                        /main plot/,
                        /script/,
                        /treatment/,
                        /your thoughts/,
                        /analyze/,
                        /review/
                    ];
                    
                    for (const pattern of readingPatterns) {
                        const match = text.match(pattern);
                        if (match) {
                            return match[1] || match[0];
                        }
                    }
                    
                    const keywords = ['plot', 'outline', 'character', 'script', 'treatment', 'story', 'document', 'thoughts'];
                    for (const keyword of keywords) {
                        if (text.includes(keyword)) {
                            return keyword;
                        }
                    }
                    
                    return null;
                };

                const extractedQuery = testExtraction(query);
                
                let message = `Agent Context Test for "${query}":

Extracted document query: "${extractedQuery}"

`;

                if (extractedQuery) {
                    const analysis = await documentContext.analyzeDocumentForAgents(extractedQuery);
                    message += `Document analysis results:
${analysis.contextSummary}

Found ${analysis.relevantDocuments.length} relevant documents.`;
                } else {
                    message += 'No document query detected.';
                }

                vscode.window.showInformationMessage(message, 'View Full Context').then(selection => {
                    if (selection === 'View Full Context') {
                        outputChannel.appendLine('=== AGENT CONTEXT DEBUG ===');
                        outputChannel.appendLine(message);
                        outputChannel.show();
                    }
                });
            } catch (error) {
                vscode.window.showErrorMessage(`Agent context test failed: ${error}`);
                console.error('Agent context test error:', error);
            }
        })
    ];

    // Add all commands to subscriptions
    commands.forEach(command => context.subscriptions.push(command));
    
    console.log(`📋 Registered ${commands.length} commands`);
}

async function setupUI(context: vscode.ExtensionContext) {
    // Create status bar item
    statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = "$(edit) Writers Room";
    statusBarItem.tooltip = "The Writers Room - AI Writing Assistant";
    statusBarItem.command = 'workbench.view.extension.theWritersRoom';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);

    // Register webview providers
    const sidebarProvider = new SidebarChatProvider(context, agentManager);
    const settingsProvider = new SettingsWebviewProvider(context.extensionUri, context);
    
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider(SidebarChatProvider.viewType, sidebarProvider),
        vscode.window.registerWebviewViewProvider(SettingsWebviewProvider.viewType, settingsProvider)
    );

    // Set context for when extension is active FIRST
    await vscode.commands.executeCommand('setContext', 'theWritersRoom.isActive', true);
    
    // Register Tree View Provider for AI Agents
    agentTreeProvider = new AgentTreeProvider(context, agentManager);
    
    console.log('🌲 Registering agent tree data provider...');
    const agentRegistration = vscode.window.registerTreeDataProvider('theWritersRoom.agentExplorer', agentTreeProvider);
    
    context.subscriptions.push(agentRegistration);
    
    console.log('🌲 Tree data providers registered successfully');
    
    // Force refresh the agent tree view
    setTimeout(() => {
        console.log('🔄 Force refreshing agent tree view...');
        if (agentTreeProvider) {
            agentTreeProvider.refresh();
        }
    }, 1000);

    // Update status bar with session info
    updateStatusBar();
    
    // Auto-open the Writers Room sidebar on activation
    setTimeout(async () => {
        try {
            await vscode.commands.executeCommand('workbench.view.extension.theWritersRoom');
            console.log('📋 Writers Room sidebar opened automatically');
        } catch (error) {
            console.log('📋 Writers Room sidebar already visible or failed to open:', error);
        }
    }, 1000);
    
    console.log('🎨 UI elements set up successfully');
}

function updateStatusBar() {
    if (statusBarItem && currentSession) {
        const remainingPrompts = currentSession.maxPrompts - currentSession.promptCount;
        statusBarItem.text = `$(zap) Writers Room | $(pulse) ${remainingPrompts}/100`;
        statusBarItem.tooltip = `The Writers Room - ${remainingPrompts} prompts remaining`;
    }
}

async function checkConfigurationAndWelcome() {
    const apiStatus = configManager.getAPIKeyStatus();
    const hasAnyKey = Object.values(apiStatus).some(status => status);

    if (!hasAnyKey) {
        const result = await vscode.window.showWarningMessage(
            'The Writers Room: AI configuration incomplete. Set up your AI provider to start writing!',
            'Configure AI',
            'Learn More'
        );

        if (result === 'Configure AI') {
            await configManager.configureAPIKeys();
        } else if (result === 'Learn More') {
            vscode.env.openExternal(vscode.Uri.parse('https://github.com/thewritersroom/the-writers-room#setup'));
        }
    } else {
        // Show welcome message for configured users
        const result = await vscode.window.showInformationMessage(
            '🎬 The Writers Room is ready! Start collaborating with AI writers.',
            'Open AI Chat',
            'Configure Agent Models',
            'Create Project'
        );

        switch (result) {
            case 'Open AI Chat':
                await openAIChat();
                break;
            case 'Configure Agent Models':
                await configManager.configureAgentModels();
                break;
            case 'Create Project':
                await createNewProject();
                break;
        }
    }
}

// Core AI Chat Functions
async function openAIChat() {
    const message = await vscode.window.showInputBox({
        prompt: 'What would you like help with?',
        placeHolder: 'e.g., "Help me write dialogue for a dramatic scene"',
        ignoreFocusOut: true
    });

    if (message) {
        const agent = await getActiveAgent();
        await sendMessageToAI(message, agent);
    }
}

async function chatWithAgent(agentType?: string) {
    if (!agentType) {
        agentType = await selectAgent();
    }

    if (agentType) {
        const message = await vscode.window.showInputBox({
            prompt: `Chat with ${getAgentDisplayName(agentType)}`,
            placeHolder: 'What would you like to discuss?',
            ignoreFocusOut: true
        });

        if (message) {
            await sendMessageToAI(message, agentType);
        }
    }
}

async function selectAgent(): Promise<string | undefined> {
    return await configManager.selectAgent();
}

async function sendMessageToAI(message: string, agentType: string) {
    if (!currentSession) {
        await initializeSession();
    }

    const progressOptions = {
        location: vscode.ProgressLocation.Notification,
        title: `${getAgentDisplayName(agentType)} is thinking...`,
        cancellable: false
    };

    await vscode.window.withProgress(progressOptions, async (progress) => {
        try {
            progress.report({ message: 'Analyzing your request...' });

            const task: TaskRequest = {
                message,
                agentType,
                userId: 'vscode-user',
                sessionId: currentSession.sessionId
            };

            progress.report({ message: 'Getting AI response...' });
            const response = await aiService.processTask(task);

            progress.report({ message: 'Preparing response...' });
            
            // Show response in a new document
            await showAIResponse(response, agentType);
            
            // Update session info
            updateStatusBar();
            
            outputChannel.appendLine(`[${new Date().toISOString()}] ${agentType}: ${message}`);
            outputChannel.appendLine(`Response: ${response.text.substring(0, 200)}...`);
            
        } catch (error: any) {
            vscode.window.showErrorMessage(`AI Error: ${error.message}`);
            outputChannel.appendLine(`[ERROR] ${error.message}`);
        }
    });
}

async function showAIResponse(response: any, agentType: string) {
    const doc = await vscode.workspace.openTextDocument({
        content: formatAIResponse(response, agentType),
        language: 'markdown'
    });
    
    await vscode.window.showTextDocument(doc, {
        viewColumn: vscode.ViewColumn.Beside,
        preview: true
    });
}

function formatAIResponse(response: any, agentType: string): string {
    const timestamp = new Date().toLocaleString();
    const agentName = getAgentDisplayName(agentType);
    
    return `# ${agentName} Response
*Generated on ${timestamp}*

**Model Used:** ${response.modelUsed}  
**Reasoning:** ${response.reasoning || 'Standard processing'}  
**Session:** ${response.sessionId}

---

${response.text}

---

*Generated by The Writers Room - AI-Powered Creative Writing IDE*
`;
}

// Writing Enhancement Functions
async function improveSelectedText(type: 'dialogue' | 'character' | 'scene') {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showWarningMessage('Please open a document and select text to improve.');
        return;
    }

    const selection = editor.selection;
    const selectedText = editor.document.getText(selection);
    
    if (!selectedText) {
        vscode.window.showWarningMessage('Please select text to improve.');
        return;
    }

    const prompts = {
        dialogue: `Improve this dialogue to make it more natural and character-specific:\n\n${selectedText}`,
        character: `Help me develop this character description further:\n\n${selectedText}`,
        scene: `Enhance this scene description with more vivid details:\n\n${selectedText}`
    };

    const agentTypes = {
        dialogue: 'aaron-sorkin',
        character: 'character-specialist',
        scene: 'creative-visionary'
    };

    await sendMessageToAI(prompts[type], agentTypes[type]);
}

async function analyzeCurrentDocument() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showWarningMessage('Please open a document to analyze.');
        return;
    }

    const content = editor.document.getText();
    if (!content.trim()) {
        vscode.window.showWarningMessage('Document appears to be empty.');
        return;
    }

    const prompt = `Please analyze this screenplay/script and provide feedback on structure, character development, dialogue, and pacing:\n\n${content}`;
    await sendMessageToAI(prompt, 'script-doctor');
}

async function brainstormIdeas() {
    const topic = await vscode.window.showInputBox({
        prompt: 'What would you like to brainstorm about?',
        placeHolder: 'e.g., "Plot ideas for a sci-fi thriller"',
        ignoreFocusOut: true
    });

    if (topic) {
        const prompt = `Help me brainstorm creative ideas for: ${topic}`;
        await sendMessageToAI(prompt, 'creative-visionary');
    }
}

// Project Management Functions
async function createNewProject() {
    const projectName = await vscode.window.showInputBox({
        prompt: 'Enter project name',
        placeHolder: 'My Awesome Screenplay',
        ignoreFocusOut: true
    });

    if (!projectName) return;

    const projectType = await vscode.window.showQuickPick([
        { label: '🎬 Screenplay', value: 'screenplay' },
        { label: '📖 Novel', value: 'novel' },
        { label: '📝 Short Story', value: 'short-story' },
        { label: '🎭 Stage Play', value: 'stage-play' }
    ], {
        placeHolder: 'Select project type'
    });

    if (!projectType) return;

    // Create project structure
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    if (!workspaceFolder) {
        vscode.window.showWarningMessage('Please open a workspace folder first.');
        return;
    }

    try {
        const projectUri = vscode.Uri.joinPath(workspaceFolder.uri, projectName);
        
        // Create project folder
        await vscode.workspace.fs.createDirectory(projectUri);
        
        // Create project files based on type
        await createProjectFiles(projectUri, projectName, projectType.value);
        
        vscode.window.showInformationMessage(`✅ Project "${projectName}" created successfully!`);
        
        // Open main file
        const mainFile = vscode.Uri.joinPath(projectUri, getMainFileName(projectType.value));
        const doc = await vscode.workspace.openTextDocument(mainFile);
        await vscode.window.showTextDocument(doc);
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to create project: ${error.message}`);
    }
}

async function createProjectFiles(projectUri: vscode.Uri, projectName: string, projectType: string) {
    const files = getProjectTemplate(projectName, projectType);
    
    for (const [filename, content] of Object.entries(files)) {
        const fileUri = vscode.Uri.joinPath(projectUri, filename);
        const encoder = new TextEncoder();
        await vscode.workspace.fs.writeFile(fileUri, encoder.encode(content));
    }
}

function getProjectTemplate(projectName: string, projectType: string): { [filename: string]: string } {
    const date = new Date().toLocaleDateString();
    
    const templates = {
        screenplay: {
            'screenplay.fountain': `Title: ${projectName}
Author: ${process.env.USER || 'Writer'}
Draft date: ${date}

FADE IN:

EXT. LOCATION - DAY

Your story begins here...

FADE OUT.`,
            'characters.md': `# Characters

## Main Characters

### CHARACTER NAME
- **Age:** 
- **Occupation:** 
- **Personality:** 
- **Goal:** 
- **Conflict:** 

`,
            'outline.md': `# ${projectName} - Outline

## Logline
A compelling one-sentence description of your story.

## Three-Act Structure

### Act I - Setup
- 

### Act II - Confrontation
- 

### Act III - Resolution
- 

`,
            'project.json': JSON.stringify({
                name: projectName,
                type: projectType,
                created: new Date().toISOString(),
                version: '1.0.0',
                author: process.env.USER || 'Writer'
            }, null, 2)
        },
        novel: {
            'manuscript.md': `# ${projectName}

*by ${process.env.USER || 'Writer'}*

## Chapter 1

Your story begins here...

`,
            'characters.md': `# Characters

## Main Characters

### CHARACTER NAME
- **Age:** 
- **Background:** 
- **Personality:** 
- **Motivation:** 
- **Arc:** 

`,
            'outline.md': `# ${projectName} - Outline

## Premise
What is your story about?

## Structure
- Beginning: 
- Middle: 
- End: 

`,
            'project.json': JSON.stringify({
                name: projectName,
                type: projectType,
                created: new Date().toISOString(),
                version: '1.0.0',
                author: process.env.USER || 'Writer'
            }, null, 2)
        }
    };

    return templates[projectType as keyof typeof templates] || templates.screenplay;
}

function getMainFileName(projectType: string): string {
    const mainFiles = {
        screenplay: 'screenplay.fountain',
        novel: 'manuscript.md',
        'short-story': 'story.md',
        'stage-play': 'play.fountain'
    };
    
    return mainFiles[projectType as keyof typeof mainFiles] || 'screenplay.fountain';
}

async function createNewScene() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showWarningMessage('Please open a document to add a scene.');
        return;
    }

    const sceneType = await vscode.window.showQuickPick([
        'INT. LOCATION - DAY',
        'EXT. LOCATION - DAY', 
        'INT. LOCATION - NIGHT',
        'EXT. LOCATION - NIGHT',
        'Custom...'
    ], {
        placeHolder: 'Select scene heading'
    });

    if (!sceneType) return;

    let sceneHeading = sceneType;
    if (sceneType === 'Custom...') {
        const custom = await vscode.window.showInputBox({
            prompt: 'Enter scene heading',
            placeHolder: 'INT. COFFEE SHOP - DAY'
        });
        if (!custom) return;
        sceneHeading = custom;
    }

    const sceneTemplate = `\n\n${sceneHeading}\n\n`;
    
    const position = editor.selection.active;
    await editor.edit(editBuilder => {
        editBuilder.insert(position, sceneTemplate);
    });
}

async function createNewCharacter() {
    const characterName = await vscode.window.showInputBox({
        prompt: 'Enter character name',
        placeHolder: 'JANE DOE'
    });

    if (!characterName) return;

    const characterTemplate = `
## ${characterName.toUpperCase()}
- **Age:** 
- **Occupation:** 
- **Personality:** 
- **Goal:** 
- **Conflict:** 
- **Backstory:** 

`;

    const doc = await vscode.workspace.openTextDocument({
        content: characterTemplate,
        language: 'markdown'
    });
    
    await vscode.window.showTextDocument(doc);
}

// Utility Functions
async function switchAIProvider() {
    const providers = aiService.getAvailableProviders();
    const current = aiService.getCurrentProvider();
    
    const options = providers.map(p => ({
        label: p.name,
        description: p.name === current ? '(Current)' : '',
        value: p.name.toLowerCase().replace(/\s+/g, '-')
    }));

    const selected = await vscode.window.showQuickPick(options, {
        placeHolder: 'Select AI provider'
    });

    if (selected && selected.value !== current) {
        await aiService.setProvider(selected.value);
        vscode.window.showInformationMessage(`Switched to ${selected.label}`);
        updateStatusBar();
    }
}

async function testAIConnection() {
    const result = await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: 'Testing AI connection...',
        cancellable: false
    }, async () => {
        return await aiService.testConnection();
    });

    if (result) {
        vscode.window.showInformationMessage('✅ AI connection successful!');
    } else {
        vscode.window.showErrorMessage('❌ AI connection failed. Please check your configuration.');
    }
}

async function clearConversation() {
    await createNewSession();
    vscode.window.showInformationMessage('Conversation cleared. New session started.');
}

async function showSessionStatus() {
    if (!currentSession) {
        vscode.window.showWarningMessage('No active session.');
        return;
    }

    const remaining = currentSession.maxPrompts - currentSession.promptCount;
    const cost = currentSession.costAccumulated || 0;
    
    const message = `Session Status:
• Prompts used: ${currentSession.promptCount}/${currentSession.maxPrompts}
• Remaining: ${remaining}
• Estimated cost: $${cost.toFixed(4)}
• Session ID: ${currentSession.sessionId}`;

    vscode.window.showInformationMessage(message, 'New Session').then(selection => {
        if (selection === 'New Session') {
            createNewSession();
        }
    });
}

async function createNewSession() {
    currentSession = await aiService.createSession('vscode-user');
    updateStatusBar();
    outputChannel.appendLine(`[${new Date().toISOString()}] New session created: ${currentSession.sessionId}`);
}

async function getActiveAgent(): Promise<string> {
    const config = configManager.getConfiguration();
    return config.get('defaultAgent', 'script-doctor');
}

function getAgentDisplayName(agentType: string): string {
    const names: { [key: string]: string } = {
        'script-doctor': '🎬 Script Doctor',
        'aaron-sorkin': '✍️ Aaron Sorkin',
        'character-specialist': '👥 Character Specialist',
        'creative-visionary': '🎨 Creative Visionary',
        'coen-brothers': '🎭 Coen Brothers',
        'quentin-tarantino': '🎪 Quentin Tarantino',
        'taylor-sheridan': '🏔️ Taylor Sheridan',
        'jack-carr': '⚔️ Jack Carr'
    };
    
    return names[agentType] || '🤖 AI Assistant';
}

// Tree View Reset Functions
async function resetTreeViews() {
    try {
        console.log('🔄 Starting agent tree reset...');
        
        // Clear any stored state
        await vscode.commands.executeCommand('setContext', 'theWritersRoom.isActive', false);
        await new Promise(resolve => setTimeout(resolve, 100));
        await vscode.commands.executeCommand('setContext', 'theWritersRoom.isActive', true);
        
        // Reinitialize agent tree provider
        console.log('🔄 Reinitializing agent tree provider...');
        agentTreeProvider = new AgentTreeProvider(extensionContext, agentManager);
        
        // Re-register the agent tree data provider
        extensionContext.subscriptions.push(
            vscode.window.registerTreeDataProvider('theWritersRoom.agentExplorer', agentTreeProvider)
        );
        
        // Refresh the agent tree
        console.log('🔄 Refreshing agent tree after reset...');
        agentTreeProvider.refresh();
        
        vscode.window.showInformationMessage('✅ AI Agents Tree Reset Successfully');
        console.log('✅ Agent tree reset to default state');
    } catch (error: any) {
        console.error('❌ Error resetting agent tree:', error);
        vscode.window.showErrorMessage(`Failed to reset agent tree: ${error.message}`);
    }
}

async function refreshTreeViews() {
    try {
        console.log('🔄 Starting agent tree refresh...');
        
        if (!agentTreeProvider) {
            console.warn('⚠️ agentTreeProvider is null, reinitializing...');
            agentTreeProvider = new AgentTreeProvider(extensionContext, agentManager);
        }
        
        console.log('🔄 Refreshing agent tree provider...');
        agentTreeProvider.refresh();
        
        vscode.window.showInformationMessage('🔄 AI Agents Tree Refreshed');
        console.log('✅ Agent tree refreshed successfully');
    } catch (error: any) {
        console.error('❌ Error refreshing agent tree:', error);
        vscode.window.showErrorMessage(`Failed to refresh agent tree: ${error.message}`);
    }
}

// Configuration Management Functions
async function openConfigFile() {
    try {
        const configPath = appDataManager.getConfigFilePath();
        const configUri = vscode.Uri.file(configPath);
        
        // Ensure config file exists
        if (!require('fs').existsSync(configPath)) {
            appDataManager.saveConfig();
        }
        
        const doc = await vscode.workspace.openTextDocument(configUri);
        await vscode.window.showTextDocument(doc);
        
        vscode.window.showInformationMessage('Writers Room configuration file opened');
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to open config file: ${error.message}`);
    }
}

async function importScript() {
    try {
        const options: vscode.OpenDialogOptions = {
            canSelectMany: true,
            openLabel: 'Import Scripts',
            filters: {
                'Script Files': ['fountain', 'fdx', 'pdf', 'txt', 'md'],
                'All Files': ['*']
            }
        };

        const fileUris = await vscode.window.showOpenDialog(options);
        if (fileUris && fileUris.length > 0) {
            const filePaths = fileUris.map(uri => uri.fsPath);
            // await scriptImporter.importMultipleScripts(filePaths);
            vscode.window.showInformationMessage('Script import feature coming soon!');
        }
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to import scripts: ${error.message}`);
    }
}

async function viewImportedScripts() {
    try {
        // const scripts = scriptImporter.getImportedScripts();
        const scripts: any[] = [];
        
        if (scripts.length === 0) {
            vscode.window.showInformationMessage('No scripts imported yet. Use "Import Script" to add scripts to your library.');
            return;
        }

        const scriptItems = scripts.map(script => ({
            label: script.name,
            description: `${script.metadata.title || 'Untitled'} - ${script.format.toUpperCase()}`,
            detail: `${script.metadata.author || 'Unknown Author'} | ${new Date(script.importDate).toLocaleDateString()}`,
            script: script
        }));

        const selected = await vscode.window.showQuickPick(scriptItems, {
            placeHolder: 'Select a script to open',
            title: 'Imported Scripts Library'
        });

        if (selected) {
            const scriptUri = vscode.Uri.file(selected.script.filePath);
            const doc = await vscode.workspace.openTextDocument(scriptUri);
            await vscode.window.showTextDocument(doc);
        }
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to view imported scripts: ${error.message}`);
    }
}

async function exportConfiguration() {
    try {
        const configData = appDataManager.exportConfig();
        
        const options: vscode.SaveDialogOptions = {
            saveLabel: 'Export Configuration',
            filters: {
                'JSON Files': ['json'],
                'All Files': ['*']
            },
            defaultUri: vscode.Uri.file('writers-room-config.json')
        };

        const fileUri = await vscode.window.showSaveDialog(options);
        if (fileUri) {
            await vscode.workspace.fs.writeFile(fileUri, Buffer.from(configData, 'utf8'));
            vscode.window.showInformationMessage('Configuration exported successfully');
        }
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to export configuration: ${error.message}`);
    }
}

async function resetConfiguration() {
    const confirm = await vscode.window.showWarningMessage(
        'This will reset all Writers Room settings to defaults. This action cannot be undone.',
        'Reset Configuration',
        'Cancel'
    );

    if (confirm === 'Reset Configuration') {
        appDataManager.resetToDefaults();
        vscode.window.showInformationMessage('Configuration reset to defaults');
    }
}

export function deactivate() {
    if (statusBarItem) {
        statusBarItem.dispose();
    }
    if (outputChannel) {
        outputChannel.dispose();
    }
    if (chatPersistence) {
        chatPersistence.dispose();
    }
    if (visualEditor) {
        visualEditor.dispose();
    }
    if (documentEditor) {
        documentEditor.dispose();
    }
    console.log('👋 The Writers Room extension deactivated');
} 