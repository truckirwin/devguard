import * as vscode from 'vscode';
import { DocumentEditorService, DocumentChange } from '../services/DocumentEditorService';
import { CursorAgent } from '../agents/CursorAgent';

export interface WritingDiagnostic {
    range: vscode.Range;
    message: string;
    severity: 'error' | 'warning' | 'info' | 'suggestion';
    agentId: string;
    suggestedFix?: string;
    type: 'grammar' | 'style' | 'character' | 'plot' | 'dialogue' | 'pacing';
}

export interface VisualIndicator {
    range: vscode.Range;
    type: 'suggestion' | 'improvement' | 'collaboration' | 'applied' | 'pending';
    agentId: string;
    message: string;
    priority: 'low' | 'medium' | 'high';
}

export class VisualEditorProvider {
    private static instance: VisualEditorProvider;
    private documentEditor: DocumentEditorService;
    private cursorAgent: CursorAgent;
    private diagnosticsCollection: vscode.DiagnosticCollection;
    
    // Visual decoration types
    private decorationTypes: Map<string, vscode.TextEditorDecorationType> = new Map();
    private gutterDecorations: Map<string, vscode.TextEditorDecorationType> = new Map();
    
    // Active diagnostics and indicators
    private activeDiagnostics: Map<string, WritingDiagnostic[]> = new Map();
    private activeIndicators: Map<string, VisualIndicator[]> = new Map();
    
    // Status bar items
    private statusBarItems: vscode.StatusBarItem[] = [];

    private constructor(context: vscode.ExtensionContext) {
        this.documentEditor = DocumentEditorService.getInstance();
        this.cursorAgent = CursorAgent.getInstance(context);
        this.diagnosticsCollection = vscode.languages.createDiagnosticCollection('writersroom');
        
        this.initializeDecorations();
        this.setupEventListeners();
        this.createStatusBarItems();
        
        context.subscriptions.push(this.diagnosticsCollection);
    }

    public static getInstance(context: vscode.ExtensionContext): VisualEditorProvider {
        if (!VisualEditorProvider.instance) {
            VisualEditorProvider.instance = new VisualEditorProvider(context);
        }
        return VisualEditorProvider.instance;
    }

    private initializeDecorations() {
        // Agent suggestion decorations (like Cursor's inline suggestions)
        this.decorationTypes.set('agent-suggestion', vscode.window.createTextEditorDecorationType({
            backgroundColor: 'rgba(0, 150, 255, 0.1)',
            border: '1px dashed rgba(0, 150, 255, 0.4)',
            borderRadius: '3px',
            overviewRulerColor: '#0096ff',
            overviewRulerLane: vscode.OverviewRulerLane.Right,
            after: {
                contentText: ' ✨',
                color: 'rgba(0, 150, 255, 0.8)'
            }
        }));

        // Improvement suggestions (green like Cursor's additions)
        this.decorationTypes.set('improvement', vscode.window.createTextEditorDecorationType({
            backgroundColor: 'rgba(0, 255, 100, 0.1)',
            border: '1px solid rgba(0, 255, 100, 0.3)',
            borderRadius: '2px',
            overviewRulerColor: '#00ff64',
            overviewRulerLane: vscode.OverviewRulerLane.Right
        }));

        // Issues/problems (red like Cursor's errors)
        this.decorationTypes.set('writing-issue', vscode.window.createTextEditorDecorationType({
            backgroundColor: 'rgba(255, 100, 100, 0.1)',
            border: '1px solid rgba(255, 100, 100, 0.3)',
            borderRadius: '2px',
            overviewRulerColor: '#ff6464',
            overviewRulerLane: vscode.OverviewRulerLane.Left,
            textDecoration: 'underline wavy rgba(255, 100, 100, 0.8)'
        }));

        // Multi-agent collaboration indicators
        this.decorationTypes.set('collaboration', vscode.window.createTextEditorDecorationType({
            backgroundColor: 'rgba(255, 200, 0, 0.1)',
            border: '1px dotted rgba(255, 200, 0, 0.5)',
            borderRadius: '2px',
            overviewRulerColor: '#ffc800',
            overviewRulerLane: vscode.OverviewRulerLane.Center,
            after: {
                contentText: ' 👥',
                color: 'rgba(255, 200, 0, 0.8)'
            }
        }));

        // Applied changes (subtle green)
        this.decorationTypes.set('applied', vscode.window.createTextEditorDecorationType({
            backgroundColor: 'rgba(0, 255, 0, 0.05)',
            border: '1px solid rgba(0, 255, 0, 0.2)',
            borderRadius: '2px'
        }));

        // Pending changes (blue pulse)
        this.decorationTypes.set('pending', vscode.window.createTextEditorDecorationType({
            backgroundColor: 'rgba(0, 100, 255, 0.1)',
            border: '1px dashed rgba(0, 100, 255, 0.4)',
            borderRadius: '2px',
            after: {
                contentText: ' ⏳',
                color: 'rgba(0, 100, 255, 0.8)'
            }
        }));

        // Gutter decorations for agent indicators (using emoji for now since ThemeIcon not supported)
        this.gutterDecorations.set('aaron-sorkin', vscode.window.createTextEditorDecorationType({
            gutterIconSize: 'auto',
            before: {
                contentText: '💬',
                margin: '0 4px 0 0'
            }
        }));

        this.gutterDecorations.set('character-specialist', vscode.window.createTextEditorDecorationType({
            gutterIconSize: 'auto',
            before: {
                contentText: '👤',
                margin: '0 4px 0 0'
            }
        }));

        this.gutterDecorations.set('script-doctor', vscode.window.createTextEditorDecorationType({
            gutterIconSize: 'auto',
            before: {
                contentText: '❤️',
                margin: '0 4px 0 0'
            }
        }));

        this.gutterDecorations.set('creative-visionary', vscode.window.createTextEditorDecorationType({
            gutterIconSize: 'auto',
            before: {
                contentText: '💡',
                margin: '0 4px 0 0'
            }
        }));

        this.gutterDecorations.set('cursor-agent', vscode.window.createTextEditorDecorationType({
            gutterIconSize: 'auto',
            before: {
                contentText: '✏️',
                margin: '0 4px 0 0'
            }
        }));

        // Line highlight for active agent suggestions
        this.decorationTypes.set('active-line', vscode.window.createTextEditorDecorationType({
            backgroundColor: 'rgba(255, 255, 255, 0.02)',
            isWholeLine: true,
            border: '2px solid rgba(0, 150, 255, 0.6)'
        }));
    }

    private setupEventListeners() {
        // Listen for active editor changes
        vscode.window.onDidChangeActiveTextEditor(editor => {
            if (editor) {
                this.refreshAllDecorations(editor);
                this.updateStatusBar(editor);
            }
        });

        // Listen for document changes
        this.documentEditor.addChangeListener((change: DocumentChange) => {
            this.handleDocumentChange(change);
        });

        // Listen for text selection changes
        vscode.window.onDidChangeTextEditorSelection(event => {
            this.handleSelectionChange(event);
        });

        // Listen for document content changes
        vscode.workspace.onDidChangeTextDocument(event => {
            this.handleContentChange(event);
        });
    }

    private createStatusBarItems() {
        // Agent status indicator
        const agentStatusItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
        agentStatusItem.text = "$(person) Agents: Ready";
        agentStatusItem.tooltip = "Click to see active writing agents";
        agentStatusItem.command = 'theWritersRoom.showAgentStatus';
        agentStatusItem.show();
        this.statusBarItems.push(agentStatusItem);

        // Pending changes indicator
        const changesItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 99);
        changesItem.text = "$(git-commit) Changes: 0";
        changesItem.tooltip = "Click to apply or reject pending changes";
        changesItem.command = 'theWritersRoom.showPendingChanges';
        changesItem.show();
        this.statusBarItems.push(changesItem);

        // Writing quality indicator
        const qualityItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 98);
        qualityItem.text = "$(check-all) Quality: Good";
        qualityItem.tooltip = "Overall writing quality assessment";
        qualityItem.command = 'theWritersRoom.showQualityReport';
        qualityItem.show();
        this.statusBarItems.push(qualityItem);
    }

    public addAgentSuggestion(
        documentUri: vscode.Uri, 
        range: vscode.Range, 
        message: string, 
        agentId: string,
        type: 'suggestion' | 'improvement' | 'collaboration' = 'suggestion'
    ): void {
        const indicator: VisualIndicator = {
            range,
            type,
            agentId,
            message,
            priority: this.calculatePriority(type, message)
        };

        const key = documentUri.toString();
        if (!this.activeIndicators.has(key)) {
            this.activeIndicators.set(key, []);
        }
        this.activeIndicators.get(key)!.push(indicator);

        // Also add as diagnostic
        const diagnostic: WritingDiagnostic = {
            range,
            message,
            severity: type === 'improvement' ? 'warning' : 'info',
            agentId,
            type: this.inferDiagnosticType(message)
        };

        if (!this.activeDiagnostics.has(key)) {
            this.activeDiagnostics.set(key, []);
        }
        this.activeDiagnostics.get(key)!.push(diagnostic);

        this.refreshVisualFeedback(documentUri);
    }

    public addMultiAgentCollaboration(
        documentUri: vscode.Uri,
        range: vscode.Range,
        agents: string[],
        collaborationMessage: string
    ): void {
        const indicator: VisualIndicator = {
            range,
            type: 'collaboration',
            agentId: agents.join(', '),
            message: `${agents.length} agents collaborating: ${collaborationMessage}`,
            priority: 'high'
        };

        const key = documentUri.toString();
        if (!this.activeIndicators.has(key)) {
            this.activeIndicators.set(key, []);
        }
        this.activeIndicators.get(key)!.push(indicator);

        this.refreshVisualFeedback(documentUri);
    }

    public markChangeApplied(documentUri: vscode.Uri, changeId: string): void {
        // Update visual indicators to show applied state
        const changes = this.documentEditor.getSessionChanges(documentUri);
        const appliedChange = changes.find(c => c.id === changeId);
        
        if (appliedChange) {
            this.addVisualFeedback(documentUri, appliedChange.range, 'applied', 
                `Applied by ${appliedChange.agentId}: ${appliedChange.reasoning}`);
        }
    }

    public showInlineCompletion(
        documentUri: vscode.Uri,
        position: vscode.Position,
        suggestion: string,
        agentId: string
    ): void {
        const range = new vscode.Range(position, position);
        this.addVisualFeedback(documentUri, range, 'agent-suggestion', 
            `${agentId} suggests: ${suggestion}`);
    }

    private addVisualFeedback(
        documentUri: vscode.Uri,
        range: vscode.Range,
        type: string,
        message: string
    ): void {
        const editor = vscode.window.activeTextEditor;
        if (!editor || editor.document.uri.toString() !== documentUri.toString()) {
            return;
        }

        const decorationType = this.decorationTypes.get(type);
        if (!decorationType) return;

        const decoration: vscode.DecorationOptions = {
            range,
            hoverMessage: new vscode.MarkdownString(message)
        };

        editor.setDecorations(decorationType, [decoration]);
    }

    private refreshVisualFeedback(documentUri: vscode.Uri): void {
        const editor = vscode.window.activeTextEditor;
        if (!editor || editor.document.uri.toString() !== documentUri.toString()) {
            return;
        }

        this.refreshAllDecorations(editor);
        this.updateDiagnostics(documentUri);
        this.updateStatusBar(editor);
    }

    private refreshAllDecorations(editor: vscode.TextEditor): void {
        const documentUri = editor.document.uri;
        const indicators = this.activeIndicators.get(documentUri.toString()) || [];
        const changes = this.documentEditor.getSessionChanges(documentUri);

        // Clear all decorations
        this.decorationTypes.forEach(decorationType => {
            editor.setDecorations(decorationType, []);
        });

        // Group decorations by type
        const decorationsByType = new Map<string, vscode.DecorationOptions[]>();

        // Add indicators
        indicators.forEach(indicator => {
            const type = this.getDecorationTypeForIndicator(indicator);
            if (!decorationsByType.has(type)) {
                decorationsByType.set(type, []);
            }

            decorationsByType.get(type)!.push({
                range: indicator.range,
                hoverMessage: new vscode.MarkdownString(
                    `**${indicator.agentId}**: ${indicator.message}\n\n*Priority: ${indicator.priority}*`
                )
            });
        });

        // Add document changes
        changes.forEach(change => {
            const type = change.applied ? 'applied' : 'pending';
            if (!decorationsByType.has(type)) {
                decorationsByType.set(type, []);
            }

            decorationsByType.get(type)!.push({
                range: change.range,
                hoverMessage: new vscode.MarkdownString(
                    `**${change.agentId}**: ${change.reasoning}\n\n` +
                    `*Type*: ${change.type}\n` +
                    `*Status*: ${change.applied ? 'Applied' : 'Pending'}\n\n` +
                    `\`\`\`\n${change.newText}\n\`\`\``
                )
            });
        });

        // Apply all decorations
        decorationsByType.forEach((decorations, type) => {
            const decorationType = this.decorationTypes.get(type);
            if (decorationType) {
                editor.setDecorations(decorationType, decorations);
            }
        });

        // Add gutter icons for agent suggestions
        this.addGutterIcons(editor);
    }

    private addGutterIcons(editor: vscode.TextEditor): void {
        const documentUri = editor.document.uri;
        const indicators = this.activeIndicators.get(documentUri.toString()) || [];
        
        // Group by agent
        const agentRanges = new Map<string, vscode.Range[]>();
        
        indicators.forEach(indicator => {
            if (!agentRanges.has(indicator.agentId)) {
                agentRanges.set(indicator.agentId, []);
            }
            agentRanges.get(indicator.agentId)!.push(indicator.range);
        });

        // Apply gutter decorations
        agentRanges.forEach((ranges, agentId) => {
            const gutterDecoration = this.gutterDecorations.get(agentId);
            if (gutterDecoration) {
                const decorations = ranges.map(range => ({ range }));
                editor.setDecorations(gutterDecoration, decorations);
            }
        });
    }

    private updateDiagnostics(documentUri: vscode.Uri): void {
        const diagnostics = this.activeDiagnostics.get(documentUri.toString()) || [];
        
        const vscodeDiagnostics = diagnostics.map(diag => {
            const diagnostic = new vscode.Diagnostic(
                diag.range,
                diag.message,
                this.getVSCodeSeverity(diag.severity)
            );
            
            diagnostic.source = `Writers Room (${diag.agentId})`;
            diagnostic.code = diag.type;
            
            return diagnostic;
        });

        this.diagnosticsCollection.set(documentUri, vscodeDiagnostics);
    }

    private updateStatusBar(editor: vscode.TextEditor): void {
        const documentUri = editor.document.uri;
        const indicators = this.activeIndicators.get(documentUri.toString()) || [];
        const changes = this.documentEditor.getSessionChanges(documentUri);
        
        // Update agents status
        const activeAgents = [...new Set(indicators.map(i => i.agentId))];
        if (this.statusBarItems[0]) {
            this.statusBarItems[0].text = `$(person) Agents: ${activeAgents.length} active`;
        }

        // Update changes status
        const pendingChanges = changes.filter(c => !c.applied);
        if (this.statusBarItems[1]) {
            this.statusBarItems[1].text = `$(git-commit) Changes: ${pendingChanges.length} pending`;
        }

        // Update quality status
        const issues = indicators.filter(i => i.type === 'improvement').length;
        const quality = issues === 0 ? 'Excellent' : issues < 3 ? 'Good' : 'Needs Work';
        if (this.statusBarItems[2]) {
            this.statusBarItems[2].text = `$(check-all) Quality: ${quality}`;
        }
    }

    private handleDocumentChange(change: DocumentChange): void {
        // Visual feedback for new changes
        if (vscode.window.activeTextEditor) {
            this.refreshVisualFeedback(vscode.window.activeTextEditor.document.uri);
        }
    }

    private handleSelectionChange(event: vscode.TextEditorSelectionChangeEvent): void {
        // Highlight active line when selection changes
        const decorationType = this.decorationTypes.get('active-line');
        if (decorationType && !event.selections[0].isEmpty) {
            const decoration = { range: event.selections[0] };
            event.textEditor.setDecorations(decorationType, [decoration]);
        }
    }

    private handleContentChange(event: vscode.TextDocumentChangeEvent): void {
        // Real-time analysis as user types
        if (event.contentChanges.length > 0) {
            this.analyzeTextForIssues(event.document);
        }
    }

    private async analyzeTextForIssues(document: vscode.TextDocument): Promise<void> {
        // Simple real-time analysis (you can enhance this)
        const text = document.getText();
        const lines = text.split('\n');
        
        const issues: WritingDiagnostic[] = [];
        
        lines.forEach((line, lineNumber) => {
            // Check for common writing issues
            if (line.length > 100 && !line.includes('.')) {
                issues.push({
                    range: new vscode.Range(lineNumber, 0, lineNumber, line.length),
                    message: 'Consider breaking this long sentence into shorter ones',
                    severity: 'warning',
                    agentId: 'script-doctor',
                    type: 'style'
                });
            }

            // Check for repeated words
            const words = line.toLowerCase().split(/\s+/);
            const wordCounts = new Map<string, number>();
            words.forEach(word => {
                if (word.length > 3) {
                    wordCounts.set(word, (wordCounts.get(word) || 0) + 1);
                }
            });

            wordCounts.forEach((count, word) => {
                if (count > 2) {
                    issues.push({
                        range: new vscode.Range(lineNumber, 0, lineNumber, line.length),
                        message: `The word "${word}" is repeated ${count} times in this line`,
                        severity: 'info',
                        agentId: 'script-doctor',
                        type: 'style'
                    });
                }
            });
        });

        // Update diagnostics
        const key = document.uri.toString();
        this.activeDiagnostics.set(key, issues);
        this.updateDiagnostics(document.uri);
    }

    // Helper methods
    private getDecorationTypeForIndicator(indicator: VisualIndicator): string {
        switch (indicator.type) {
            case 'suggestion': return 'agent-suggestion';
            case 'improvement': return 'improvement';
            case 'collaboration': return 'collaboration';
            case 'applied': return 'applied';
            case 'pending': return 'pending';
            default: return 'agent-suggestion';
        }
    }

    private calculatePriority(type: string, message: string): 'low' | 'medium' | 'high' {
        if (message.toLowerCase().includes('critical') || message.toLowerCase().includes('error')) {
            return 'high';
        }
        if (type === 'improvement' || message.toLowerCase().includes('suggest')) {
            return 'medium';
        }
        return 'low';
    }

    private inferDiagnosticType(message: string): WritingDiagnostic['type'] {
        const msg = message.toLowerCase();
        if (msg.includes('character')) return 'character';
        if (msg.includes('dialogue')) return 'dialogue';
        if (msg.includes('plot')) return 'plot';
        if (msg.includes('pace') || msg.includes('pacing')) return 'pacing';
        if (msg.includes('grammar')) return 'grammar';
        return 'style';
    }

    private getVSCodeSeverity(severity: WritingDiagnostic['severity']): vscode.DiagnosticSeverity {
        switch (severity) {
            case 'error': return vscode.DiagnosticSeverity.Error;
            case 'warning': return vscode.DiagnosticSeverity.Warning;
            case 'info': return vscode.DiagnosticSeverity.Information;
            case 'suggestion': return vscode.DiagnosticSeverity.Hint;
            default: return vscode.DiagnosticSeverity.Information;
        }
    }

    public clearAllVisualFeedback(documentUri: vscode.Uri): void {
        this.activeIndicators.delete(documentUri.toString());
        this.activeDiagnostics.delete(documentUri.toString());
        this.diagnosticsCollection.delete(documentUri);
        
        const editor = vscode.window.activeTextEditor;
        if (editor && editor.document.uri.toString() === documentUri.toString()) {
            this.decorationTypes.forEach(decorationType => {
                editor.setDecorations(decorationType, []);
            });
        }
    }

    public dispose(): void {
        this.decorationTypes.forEach(decorationType => decorationType.dispose());
        this.gutterDecorations.forEach(decorationType => decorationType.dispose());
        this.statusBarItems.forEach(item => item.dispose());
        this.diagnosticsCollection.dispose();
    }
} 