import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

export interface DocumentChange {
    id: string;
    type: 'insert' | 'delete' | 'replace';
    range: vscode.Range;
    oldText: string;
    newText: string;
    agentId: string;
    reasoning: string;
    timestamp: Date;
    applied: boolean;
}

export interface DocumentSession {
    documentUri: vscode.Uri;
    changes: DocumentChange[];
    snapshots: DocumentSnapshot[];
    currentSnapshot: number;
}

export interface DocumentSnapshot {
    id: string;
    content: string;
    timestamp: Date;
    changes: DocumentChange[];
}

export interface InlineDecoration {
    range: vscode.Range;
    type: 'addition' | 'deletion' | 'modification';
    hoverMessage?: string;
    agentId?: string;
}

export class DocumentEditorService {
    private static instance: DocumentEditorService;
    private activeSessions: Map<string, DocumentSession> = new Map();
    private decorationTypes: Map<string, vscode.TextEditorDecorationType> = new Map();
    private changeListeners: ((change: DocumentChange) => void)[] = [];
    private autoSaveEnabled = true;
    private rollbackDepth = 10;

    private constructor() {
        this.initializeDecorationTypes();
        this.setupDocumentListeners();
    }

    public static getInstance(): DocumentEditorService {
        if (!DocumentEditorService.instance) {
            DocumentEditorService.instance = new DocumentEditorService();
        }
        return DocumentEditorService.instance;
    }

    private initializeDecorationTypes() {
        // Addition decoration (green background like Cursor)
        this.decorationTypes.set('addition', vscode.window.createTextEditorDecorationType({
            backgroundColor: 'rgba(0, 255, 0, 0.1)',
            border: '1px solid rgba(0, 255, 0, 0.3)',
            overviewRulerColor: 'green',
            overviewRulerLane: vscode.OverviewRulerLane.Right
        }));

        // Deletion decoration (red background like Cursor)
        this.decorationTypes.set('deletion', vscode.window.createTextEditorDecorationType({
            backgroundColor: 'rgba(255, 0, 0, 0.1)',
            border: '1px solid rgba(255, 0, 0, 0.3)',
            overviewRulerColor: 'red',
            overviewRulerLane: vscode.OverviewRulerLane.Right,
            textDecoration: 'line-through'
        }));

        // Modification decoration (yellow background)
        this.decorationTypes.set('modification', vscode.window.createTextEditorDecorationType({
            backgroundColor: 'rgba(255, 255, 0, 0.1)',
            border: '1px solid rgba(255, 255, 0, 0.3)',
            overviewRulerColor: 'yellow',
            overviewRulerLane: vscode.OverviewRulerLane.Right
        }));

        // Suggestion decoration (blue background)
        this.decorationTypes.set('suggestion', vscode.window.createTextEditorDecorationType({
            backgroundColor: 'rgba(0, 100, 255, 0.05)',
            border: '1px dashed rgba(0, 100, 255, 0.3)',
            overviewRulerColor: 'blue',
            overviewRulerLane: vscode.OverviewRulerLane.Right
        }));
    }

    private setupDocumentListeners() {
        // Listen for document changes
        vscode.workspace.onDidChangeTextDocument(event => {
            this.handleDocumentChange(event);
        });

        // Listen for document saves
        vscode.workspace.onDidSaveTextDocument(document => {
            this.handleDocumentSave(document);
        });

        // Listen for active editor changes
        vscode.window.onDidChangeActiveTextEditor(editor => {
            if (editor) {
                this.refreshDecorations(editor);
            }
        });
    }

    public async createDocumentSession(documentUri: vscode.Uri): Promise<DocumentSession> {
        const document = await vscode.workspace.openTextDocument(documentUri);
        const session: DocumentSession = {
            documentUri,
            changes: [],
            snapshots: [{
                id: this.generateId(),
                content: document.getText(),
                timestamp: new Date(),
                changes: []
            }],
            currentSnapshot: 0
        };

        this.activeSessions.set(documentUri.toString(), session);
        return session;
    }

    public async suggestChange(
        documentUri: vscode.Uri,
        range: vscode.Range,
        newText: string,
        agentId: string,
        reasoning: string
    ): Promise<DocumentChange> {
        const document = await vscode.workspace.openTextDocument(documentUri);
        const oldText = document.getText(range);
        
        const change: DocumentChange = {
            id: this.generateId(),
            type: this.determineChangeType(oldText, newText),
            range,
            oldText,
            newText,
            agentId,
            reasoning,
            timestamp: new Date(),
            applied: false
        };

        const session = this.getOrCreateSession(documentUri);
        session.changes.push(change);

        // Show inline decoration
        await this.showInlineDecoration(documentUri, change);

        // Notify listeners
        this.changeListeners.forEach(listener => listener(change));

        return change;
    }

    public async applyChange(changeId: string, documentUri: vscode.Uri): Promise<boolean> {
        const session = this.activeSessions.get(documentUri.toString());
        if (!session) return false;

        const change = session.changes.find(c => c.id === changeId);
        if (!change || change.applied) return false;

        try {
            const document = await vscode.workspace.openTextDocument(documentUri);
            const editor = await vscode.window.showTextDocument(document);

            // Create snapshot before applying change
            await this.createSnapshot(documentUri, 'Before applying change');

            // Apply the change
            const edit = new vscode.WorkspaceEdit();
            edit.replace(documentUri, change.range, change.newText);
            
            const success = await vscode.workspace.applyEdit(edit);
            if (success) {
                change.applied = true;
                await this.refreshDecorations(editor);
                
                if (this.autoSaveEnabled) {
                    await document.save();
                }
            }

            return success;
        } catch (error) {
            console.error('Error applying change:', error);
            return false;
        }
    }

    public async applyAllChanges(documentUri: vscode.Uri): Promise<boolean> {
        const session = this.activeSessions.get(documentUri.toString());
        if (!session) return false;

        const unappliedChanges = session.changes.filter(c => !c.applied);
        
        try {
            const document = await vscode.workspace.openTextDocument(documentUri);
            const editor = await vscode.window.showTextDocument(document);

            // Create snapshot before applying all changes
            await this.createSnapshot(documentUri, 'Before applying all changes');

            // Apply all changes in a single edit
            const edit = new vscode.WorkspaceEdit();
            
            // Sort changes by position (reverse order to maintain ranges)
            unappliedChanges.sort((a, b) => b.range.start.compareTo(a.range.start));
            
            for (const change of unappliedChanges) {
                edit.replace(documentUri, change.range, change.newText);
                change.applied = true;
            }

            const success = await vscode.workspace.applyEdit(edit);
            if (success) {
                await this.refreshDecorations(editor);
                
                if (this.autoSaveEnabled) {
                    await document.save();
                }
            }

            return success;
        } catch (error) {
            console.error('Error applying all changes:', error);
            return false;
        }
    }

    public async rejectChange(changeId: string, documentUri: vscode.Uri): Promise<boolean> {
        const session = this.activeSessions.get(documentUri.toString());
        if (!session) return false;

        const changeIndex = session.changes.findIndex(c => c.id === changeId);
        if (changeIndex === -1) return false;

        session.changes.splice(changeIndex, 1);
        
        const editor = vscode.window.activeTextEditor;
        if (editor && editor.document.uri.toString() === documentUri.toString()) {
            await this.refreshDecorations(editor);
        }

        return true;
    }

    public async createSnapshot(documentUri: vscode.Uri, description?: string): Promise<DocumentSnapshot> {
        const document = await vscode.workspace.openTextDocument(documentUri);
        const session = this.getOrCreateSession(documentUri);

        const snapshot: DocumentSnapshot = {
            id: this.generateId(),
            content: document.getText(),
            timestamp: new Date(),
            changes: [...session.changes]
        };

        session.snapshots.push(snapshot);
        session.currentSnapshot = session.snapshots.length - 1;

        // Maintain rollback depth
        if (session.snapshots.length > this.rollbackDepth) {
            session.snapshots.splice(0, session.snapshots.length - this.rollbackDepth);
            session.currentSnapshot = Math.min(session.currentSnapshot, session.snapshots.length - 1);
        }

        return snapshot;
    }

    public async rollbackToSnapshot(documentUri: vscode.Uri, snapshotId: string): Promise<boolean> {
        const session = this.activeSessions.get(documentUri.toString());
        if (!session) return false;

        const snapshot = session.snapshots.find(s => s.id === snapshotId);
        if (!snapshot) return false;

        try {
            const document = await vscode.workspace.openTextDocument(documentUri);
            const editor = await vscode.window.showTextDocument(document);

            // Replace entire document content
            const edit = new vscode.WorkspaceEdit();
            const fullRange = new vscode.Range(
                document.positionAt(0),
                document.positionAt(document.getText().length)
            );
            edit.replace(documentUri, fullRange, snapshot.content);

            const success = await vscode.workspace.applyEdit(edit);
            if (success) {
                // Reset changes to snapshot state
                session.changes = [...snapshot.changes];
                await this.refreshDecorations(editor);
                
                if (this.autoSaveEnabled) {
                    await document.save();
                }
            }

            return success;
        } catch (error) {
            console.error('Error rolling back to snapshot:', error);
            return false;
        }
    }

    public async streamingEdit(
        documentUri: vscode.Uri,
        startPosition: vscode.Position,
        text: string,
        agentId: string
    ): Promise<void> {
        const document = await vscode.workspace.openTextDocument(documentUri);
        const editor = await vscode.window.showTextDocument(document);

        // Stream text character by character for live editing effect
        for (let i = 0; i < text.length; i++) {
            const char = text[i];
            const edit = new vscode.WorkspaceEdit();
            const insertPosition = document.positionAt(document.offsetAt(startPosition) + i);
            edit.insert(documentUri, insertPosition, char);
            
            await vscode.workspace.applyEdit(edit);
            await new Promise(resolve => setTimeout(resolve, 50)); // 50ms delay for streaming effect
        }
    }

    private async showInlineDecoration(documentUri: vscode.Uri, change: DocumentChange): Promise<void> {
        const editor = vscode.window.activeTextEditor;
        if (!editor || editor.document.uri.toString() !== documentUri.toString()) {
            return;
        }

        const decorationType = this.getDecorationTypeForChange(change);
        const decoration: vscode.DecorationOptions = {
            range: change.range,
            hoverMessage: `**${change.agentId}**: ${change.reasoning}\n\n*Click to apply change*`
        };

        editor.setDecorations(decorationType, [decoration]);
    }

    private getDecorationTypeForChange(change: DocumentChange): vscode.TextEditorDecorationType {
        switch (change.type) {
            case 'insert':
                return this.decorationTypes.get('addition')!;
            case 'delete':
                return this.decorationTypes.get('deletion')!;
            case 'replace':
                return this.decorationTypes.get('modification')!;
            default:
                return this.decorationTypes.get('suggestion')!;
        }
    }

    private async refreshDecorations(editor: vscode.TextEditor): Promise<void> {
        const session = this.activeSessions.get(editor.document.uri.toString());
        if (!session) return;

        // Clear existing decorations
        this.decorationTypes.forEach(decorationType => {
            editor.setDecorations(decorationType, []);
        });

        // Group changes by type
        const changesByType = new Map<string, vscode.DecorationOptions[]>();
        
        session.changes.filter(c => !c.applied).forEach(change => {
            const type = this.getDecorationTypeKey(change);
            if (!changesByType.has(type)) {
                changesByType.set(type, []);
            }
            
            changesByType.get(type)!.push({
                range: change.range,
                hoverMessage: `**${change.agentId}**: ${change.reasoning}\n\n*Click to apply change*`
            });
        });

        // Apply decorations
        changesByType.forEach((decorations, type) => {
            const decorationType = this.decorationTypes.get(type);
            if (decorationType) {
                editor.setDecorations(decorationType, decorations);
            }
        });
    }

    private getDecorationTypeKey(change: DocumentChange): string {
        switch (change.type) {
            case 'insert': return 'addition';
            case 'delete': return 'deletion';
            case 'replace': return 'modification';
            default: return 'suggestion';
        }
    }

    private getOrCreateSession(documentUri: vscode.Uri): DocumentSession {
        const key = documentUri.toString();
        if (!this.activeSessions.has(key)) {
            this.createDocumentSession(documentUri);
        }
        return this.activeSessions.get(key)!;
    }

    private determineChangeType(oldText: string, newText: string): 'insert' | 'delete' | 'replace' {
        if (oldText === '') return 'insert';
        if (newText === '') return 'delete';
        return 'replace';
    }

    private handleDocumentChange(event: vscode.TextDocumentChangeEvent): void {
        // Handle manual user changes
        const session = this.activeSessions.get(event.document.uri.toString());
        if (session) {
            // Update snapshots if significant changes
            if (event.contentChanges.length > 0) {
                this.createSnapshot(event.document.uri, 'User modification');
            }
        }
    }

    private handleDocumentSave(document: vscode.TextDocument): void {
        const session = this.activeSessions.get(document.uri.toString());
        if (session) {
            this.createSnapshot(document.uri, 'Document saved');
        }
    }

    private generateId(): string {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }

    public addChangeListener(listener: (change: DocumentChange) => void): void {
        this.changeListeners.push(listener);
    }

    public removeChangeListener(listener: (change: DocumentChange) => void): void {
        const index = this.changeListeners.indexOf(listener);
        if (index > -1) {
            this.changeListeners.splice(index, 1);
        }
    }

    public getSessionChanges(documentUri: vscode.Uri): DocumentChange[] {
        const session = this.activeSessions.get(documentUri.toString());
        return session ? session.changes : [];
    }

    public getSessionSnapshots(documentUri: vscode.Uri): DocumentSnapshot[] {
        const session = this.activeSessions.get(documentUri.toString());
        return session ? session.snapshots : [];
    }

    public dispose(): void {
        this.decorationTypes.forEach(decorationType => decorationType.dispose());
        this.activeSessions.clear();
        this.changeListeners = [];
    }
} 