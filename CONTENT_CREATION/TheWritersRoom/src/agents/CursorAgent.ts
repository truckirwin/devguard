import * as vscode from 'vscode';
import { AgentManager } from './AgentManager';
import { DocumentEditorService, DocumentChange } from '../services/DocumentEditorService';
import { AIService } from '../services/AIService';
import { DocumentContextService } from '../services/DocumentContextService';

export interface CursorAgentAction {
    type: 'suggest' | 'apply' | 'create' | 'stream' | 'rollback';
    documentUri?: vscode.Uri;
    content?: string;
    reasoning?: string;
    range?: vscode.Range;
    agentId?: string;
}

export interface ConversationContext {
    messages: Array<{
        agentId: string;
        content: string;
        timestamp: Date;
    }>;
    currentDocument?: vscode.Uri;
    documentContent?: string;
    focusedRange?: vscode.Range;
}

export class CursorAgent {
    private static instance: CursorAgent;
    private documentEditor: DocumentEditorService;
    private aiService: AIService;
    private agentManager: AgentManager;
    private documentContext: DocumentContextService;
    private conversationBuffer: ConversationContext[] = [];
    private isProcessing = false;
    private autoApplyMode = false;

    private constructor(context: vscode.ExtensionContext) {
        this.documentEditor = DocumentEditorService.getInstance();
        this.aiService = AIService.getInstance();
        this.agentManager = new AgentManager(context);
        this.documentContext = DocumentContextService.getInstance(context);
        this.setupEventListeners();
    }

    public static getInstance(context: vscode.ExtensionContext): CursorAgent {
        if (!CursorAgent.instance) {
            CursorAgent.instance = new CursorAgent(context);
        }
        return CursorAgent.instance;
    }

    private setupEventListeners() {
        // Listen for document changes from the editor service
        this.documentEditor.addChangeListener((change: DocumentChange) => {
            this.handleDocumentChange(change);
        });

        // Listen for active editor changes
        vscode.window.onDidChangeActiveTextEditor(editor => {
            if (editor) {
                this.handleActiveEditorChange(editor);
            }
        });

        // Listen for text selection changes
        vscode.window.onDidChangeTextEditorSelection(event => {
            this.handleSelectionChange(event);
        });
    }

    public async processMultiAgentConversation(messages: Array<{ agentId: string; content: string; timestamp: Date }>): Promise<void> {
        if (this.isProcessing) return;
        
        this.isProcessing = true;
        
        try {
            const context: ConversationContext = {
                messages,
                currentDocument: vscode.window.activeTextEditor?.document.uri,
                documentContent: vscode.window.activeTextEditor?.document.getText(),
                focusedRange: vscode.window.activeTextEditor?.selection
            };

            // Analyze the conversation for actionable changes
            const actions = await this.analyzeConversationForActions(context);
            
            // Process each action
            for (const action of actions) {
                await this.executeAction(action);
            }

        } finally {
            this.isProcessing = false;
        }
    }

    private async analyzeConversationForActions(context: ConversationContext): Promise<CursorAgentAction[]> {
        const recentMessages = context.messages.slice(-8); // Last 8 messages for better context
        const conversationText = recentMessages.map(m => `${m.agentId}: ${m.content}`).join('\n');
        
        // Check if agents are asking to read documents
        const documentQuery = this.extractDocumentQuery(conversationText);
        let documentContext = '';
        
        if (documentQuery) {
            const analysis = await this.documentContext.analyzeDocumentForAgents(documentQuery);
            if (analysis.relevantDocuments.length > 0) {
                documentContext = `\n\n=== RELEVANT DOCUMENTS ===\n${analysis.contextSummary}\n\n`;
                
                // Include full content of most relevant documents
                for (const doc of analysis.relevantDocuments.slice(0, 2)) {
                    documentContext += `--- ${doc.fileName} ---\n${doc.content}\n\n`;
                }
            } else {
                documentContext = `\n\n=== DOCUMENT SEARCH RESULT ===\n${analysis.contextSummary}\n\n`;
            }
        }
        
        const analysisPrompt = `You are the CursorAgent, a specialized AI that analyzes multi-agent conversations about creative writing and determines what document actions need to be made.

CURRENT DOCUMENT: ${context.currentDocument?.fsPath || 'None'}
CURRENT DOCUMENT CONTENT: ${context.documentContent?.slice(0, 500) || 'None'}...

${documentContext}

CONVERSATION:
${conversationText}

Your job is to look for ACTIONABLE suggestions from the agents and convert them into document actions. Pay special attention to:

1. **DOCUMENT READING**: If agents request to read documents, they can now access the content above
2. **DOCUMENT CREATION**: If agents suggest creating new documents, outlines, treatments, scripts, or chapters
3. **TEXT CHANGES**: Specific text that agents recommend adding, changing, or improving
4. **STRUCTURAL CHANGES**: New sections, chapters, scenes that agents propose
5. **CONTENT ADDITIONS**: Dialogue, descriptions, character details that agents suggest adding

BE VERY LIBERAL in detecting creation requests. Look for phrases like:
- "let's create..." / "we should create..." / "I suggest creating..."
- "how about we write..." / "maybe we could write..."
- "let's start with..." / "we could begin with..."
- "I recommend adding..." / "let's add..."
- "we need a..." / "this needs a..."
- "read the..." / "tell me about..." / "what does the..."

When agents ask to read documents, they now have access to the actual content above. When they ask about "the plot outline" or "the character document", they can see and analyze the real content.

Respond with a JSON array of actions. PRIORITIZE CREATION ACTIONS - if agents are discussing creating something, make it happen!

[
  {
    "type": "create",
    "content": "# Story Outline\\n\\n## Act I\\n- Opening scene description\\n\\n## Act II\\n- Conflict development\\n\\n## Act III\\n- Resolution",
    "reasoning": "Agents discussed creating an outline for the story",
    "agentId": "creative-visionary"
  },
  {
    "type": "suggest", 
    "content": "The rain pounded against the window as Detective Martinez reviewed the case files.",
    "reasoning": "Script Doctor suggested improving the opening scene",
    "range": "1-1",
    "agentId": "script-doctor"
  }
]

If agents are discussing document creation but no document exists, ALWAYS include a "create" action.
If no actions are needed, return an empty array.`;

        try {
            const response = await this.aiService.sendMessage(analysisPrompt, 'cursor-agent');
            const actions = this.parseActionsFromResponse(response.text);
            
            // Enhanced detection for document creation keywords
            const hasCreationKeywords = conversationText.toLowerCase().includes('create') ||
                                       conversationText.toLowerCase().includes('write') ||
                                       conversationText.toLowerCase().includes('outline') ||
                                       conversationText.toLowerCase().includes('document') ||
                                       conversationText.toLowerCase().includes('script') ||
                                       conversationText.toLowerCase().includes('treatment');
            
            // If we detect creation keywords but no create action, add one
            if (hasCreationKeywords && !actions.some(a => a.type === 'create')) {
                actions.unshift({
                    type: 'create',
                    content: this.generateDocumentFromConversation(conversationText),
                    reasoning: 'Agents discussed creating new content - generating document based on conversation',
                    agentId: 'cursor-agent'
                });
            }
            
            return actions;
        } catch (error) {
            console.error('Error analyzing conversation:', error);
            return [];
        }
    }

    private extractDocumentQuery(conversationText: string): string | null {
        const text = conversationText.toLowerCase();
        
        // Common phrases that indicate document reading requests
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
            /treatment/
        ];
        
        for (const pattern of readingPatterns) {
            const match = text.match(pattern);
            if (match) {
                return match[1] || match[0];
            }
        }
        
        // Check for general document-related keywords
        const keywords = ['plot', 'outline', 'character', 'script', 'treatment', 'story', 'document'];
        for (const keyword of keywords) {
            if (text.includes(keyword)) {
                return keyword;
            }
        }
        
        return null;
    }

    private parseActionsFromResponse(response: string): CursorAgentAction[] {
        try {
            // Extract JSON from response
            const jsonMatch = response.match(/\[[\s\S]*\]/);
            if (!jsonMatch) return [];

            const actions = JSON.parse(jsonMatch[0]);
            return actions.map((action: any) => ({
                type: action.type,
                content: action.content,
                reasoning: action.reasoning,
                range: action.range ? this.parseRange(action.range) : undefined,
                agentId: action.agentId
            }));
        } catch (error) {
            console.error('Error parsing actions:', error);
            return [];
        }
    }

    private parseRange(rangeString: string): vscode.Range | undefined {
        try {
            const [start, end] = rangeString.split('-').map(n => parseInt(n));
            return new vscode.Range(start - 1, 0, end - 1, Number.MAX_VALUE);
        } catch {
            return undefined;
        }
    }

    private async executeAction(action: CursorAgentAction): Promise<void> {
        const activeEditor = vscode.window.activeTextEditor;
        if (!activeEditor) return;

        const documentUri = activeEditor.document.uri;

        switch (action.type) {
            case 'suggest':
                await this.suggestTextChange(documentUri, action);
                break;
            case 'apply':
                await this.applyTextChange(documentUri, action);
                break;
            case 'create':
                await this.createNewContent(action);
                break;
            case 'stream':
                await this.streamTextChange(documentUri, action);
                break;
            case 'rollback':
                await this.rollbackChanges(documentUri);
                break;
        }
    }

    private async suggestTextChange(documentUri: vscode.Uri, action: CursorAgentAction): Promise<void> {
        if (!action.content || !action.reasoning) return;

        const range = action.range || this.getSmartInsertionRange(documentUri);
        if (!range) return;

        await this.documentEditor.suggestChange(
            documentUri,
            range,
            action.content,
            action.agentId || 'cursor-agent',
            action.reasoning
        );

        // Show notification
        this.showActionNotification(`💡 Suggested by ${action.agentId}: ${action.reasoning}`);
    }

    private async applyTextChange(documentUri: vscode.Uri, action: CursorAgentAction): Promise<void> {
        if (!action.content) return;

        const range = action.range || this.getSmartInsertionRange(documentUri);
        if (!range) return;

        // Create and immediately apply the change
        const change = await this.documentEditor.suggestChange(
            documentUri,
            range,
            action.content,
            action.agentId || 'cursor-agent',
            action.reasoning || 'Applied by Cursor Agent'
        );

        await this.documentEditor.applyChange(change.id, documentUri);
        
        this.showActionNotification(`✅ Applied by ${action.agentId}: ${action.reasoning}`);
    }

    private async createNewContent(action: CursorAgentAction): Promise<void> {
        if (!action.content) return;

        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) return;

        const fileName = this.generateFileName(action.content);
        const filePath = vscode.Uri.joinPath(workspaceFolder.uri, fileName);

        try {
            await vscode.workspace.fs.writeFile(filePath, Buffer.from(action.content, 'utf8'));
            
            // Open the new file
            const document = await vscode.workspace.openTextDocument(filePath);
            await vscode.window.showTextDocument(document);

            this.showActionNotification(`📝 Created new file: ${fileName}`);
        } catch (error) {
            console.error('Error creating new content:', error);
        }
    }

    private async streamTextChange(documentUri: vscode.Uri, action: CursorAgentAction): Promise<void> {
        if (!action.content) return;

        const range = action.range || this.getSmartInsertionRange(documentUri);
        if (!range) return;

        await this.documentEditor.streamingEdit(
            documentUri,
            range.start,
            action.content,
            action.agentId || 'cursor-agent'
        );

        this.showActionNotification(`⚡ Streaming edit by ${action.agentId}`);
    }

    private async rollbackChanges(documentUri: vscode.Uri): Promise<void> {
        const snapshots = this.documentEditor.getSessionSnapshots(documentUri);
        if (snapshots.length < 2) return;

        // Rollback to previous snapshot
        const previousSnapshot = snapshots[snapshots.length - 2];
        await this.documentEditor.rollbackToSnapshot(documentUri, previousSnapshot.id);

        this.showActionNotification(`⬅️ Rolled back to previous version`);
    }

    private getSmartInsertionRange(documentUri: vscode.Uri): vscode.Range | undefined {
        const activeEditor = vscode.window.activeTextEditor;
        if (!activeEditor || activeEditor.document.uri.toString() !== documentUri.toString()) {
            return undefined;
        }

        // Use current selection if available
        if (!activeEditor.selection.isEmpty) {
            return activeEditor.selection;
        }

        // Use current cursor position
        const position = activeEditor.selection.active;
        return new vscode.Range(position, position);
    }

    private generateFileName(content: string): string {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
        
        // Try to infer file type from content
        if (content.includes('FADE IN:') || content.includes('INT.') || content.includes('EXT.')) {
            return `script_${timestamp}.fountain`;
        } else if (content.includes('# ') || content.includes('## ')) {
            return `document_${timestamp}.md`;
        } else if (content.includes('Chapter ') || content.includes('### ')) {
            return `chapter_${timestamp}.md`;
        } else {
            return `document_${timestamp}.txt`;
        }
    }

    private showActionNotification(message: string): void {
        // Show non-intrusive notification
        vscode.window.withProgress({
            location: vscode.ProgressLocation.Window,
            title: message
        }, async (progress) => {
            progress.report({ increment: 100 });
            await new Promise(resolve => setTimeout(resolve, 2000));
        });
    }

    private handleDocumentChange(change: DocumentChange): void {
        // React to document changes if needed
        console.log(`Document change detected: ${change.type} by ${change.agentId}`);
    }

    private handleActiveEditorChange(editor: vscode.TextEditor): void {
        // Update context when active editor changes
        console.log(`Active editor changed: ${editor.document.uri.fsPath}`);
    }

    private handleSelectionChange(event: vscode.TextEditorSelectionChangeEvent): void {
        // Update context when selection changes
        if (!event.selections[0].isEmpty) {
            console.log(`Selection changed: ${event.selections[0].start.line}-${event.selections[0].end.line}`);
        }
    }

    // Public API for manual control
    public async applyAllPendingChanges(): Promise<void> {
        const activeEditor = vscode.window.activeTextEditor;
        if (!activeEditor) return;

        await this.documentEditor.applyAllChanges(activeEditor.document.uri);
        this.showActionNotification('✅ Applied all pending changes');
    }

    public async rejectAllPendingChanges(): Promise<void> {
        const activeEditor = vscode.window.activeTextEditor;
        if (!activeEditor) return;

        const changes = this.documentEditor.getSessionChanges(activeEditor.document.uri);
        for (const change of changes) {
            if (!change.applied) {
                await this.documentEditor.rejectChange(change.id, activeEditor.document.uri);
            }
        }
        this.showActionNotification('❌ Rejected all pending changes');
    }

    public async createDocumentFromConversation(messages: Array<{ agentId: string; content: string; timestamp: Date }>): Promise<void> {
        const conversationSummary = messages.map(m => `${m.agentId}: ${m.content}`).join('\n\n');
        
        const prompt = `Based on this conversation between writing agents, create a document that incorporates their ideas:

${conversationSummary}

Create a cohesive document that reflects the collaborative input from all agents. Format it appropriately for the type of content discussed.`;

        try {
            const response = await this.aiService.sendMessage(prompt, 'cursor-agent');
            
            const action: CursorAgentAction = {
                type: 'create',
                content: response.text,
                reasoning: 'Document created from multi-agent conversation',
                agentId: 'cursor-agent'
            };

            await this.executeAction(action);
        } catch (error) {
            console.error('Error creating document from conversation:', error);
        }
    }

    public setAutoApplyMode(enabled: boolean): void {
        this.autoApplyMode = enabled;
        this.showActionNotification(enabled ? '🤖 Auto-apply mode enabled' : '🤖 Auto-apply mode disabled');
    }

    public isAutoApplyEnabled(): boolean {
        return this.autoApplyMode;
    }

    private generateDocumentFromConversation(conversationText: string): string {
        const timestamp = new Date().toLocaleDateString();
        
        // Analyze conversation to determine document type
        const text = conversationText.toLowerCase();
        
        if (text.includes('outline') || text.includes('structure')) {
            return `# Story Outline

**Created:** ${timestamp}
**Generated from conversation**

## Structure

### Act I - Setup
- Opening scene
- Character introduction
- Inciting incident

### Act II - Confrontation  
- Rising action
- Midpoint
- Climax approach

### Act III - Resolution
- Climax
- Falling action
- Resolution

## Characters

### Main Characters
- 

### Supporting Characters
- 

## Themes
- 

## Notes
Based on agent discussion about story structure and outline creation.
`;
        } else if (text.includes('treatment')) {
            return `# Treatment

**Created:** ${timestamp}
**Generated from conversation**

## Logline
A compelling one-sentence description of the story.

## Synopsis
Brief overview of the story from beginning to end.

## Characters

### Main Characters
- **PROTAGONIST**: Age, occupation, goal, conflict
- **ANTAGONIST**: Age, occupation, goal, conflict

### Supporting Characters
- 

## Story Structure

### Act I
Setup and character introduction.

### Act II
Conflict development and complications.

### Act III
Climax and resolution.

## Themes
Central themes and messages.

## Visual Style
Tone, mood, and aesthetic approach.

## Notes
Generated from agent conversation about treatment development.
`;
        } else if (text.includes('script') || text.includes('screenplay')) {
            return `# Script

**Created:** ${timestamp}
**Generated from conversation**

**FADE IN:**

## Scene 1

**INT. LOCATION - DAY**

Character enters and begins the story...

**CHARACTER**
Opening dialogue that establishes the tone and conflict.

**FADE OUT.**

---

## Notes
- Generated from agent discussion about script development
- Continue developing scenes based on outline
- Focus on character voice and dialogue
`;
        } else if (text.includes('character')) {
            return `# Characters

**Created:** ${timestamp}
**Generated from conversation**

## Main Characters

### CHARACTER NAME
- **Age:** 
- **Occupation:** 
- **Background:** 
- **Personality:** 
- **Goal:** 
- **Conflict:** 
- **Arc:** 

### CHARACTER NAME
- **Age:** 
- **Occupation:** 
- **Background:** 
- **Personality:** 
- **Goal:** 
- **Conflict:** 
- **Arc:** 

## Supporting Characters

### CHARACTER NAME
- **Role:** 
- **Relationship to protagonist:** 
- **Key traits:** 

## Character Relationships
- 

## Character Development Notes
Generated from agent conversation about character development.
`;
        } else {
            // Generic document
            return `# Creative Writing Document

**Created:** ${timestamp}
**Generated from conversation**

## Content

[Content generated based on agent discussion]

## Development Notes
- Continue developing based on agent feedback
- Focus areas identified in conversation
- Next steps for improvement

## Agent Suggestions
Generated from multi-agent conversation about creative writing development.

## Next Steps
1. Review and refine content
2. Expand on key areas
3. Continue agent collaboration
`;
        }
    }

    public dispose(): void {
        // Cleanup if needed
    }
} 