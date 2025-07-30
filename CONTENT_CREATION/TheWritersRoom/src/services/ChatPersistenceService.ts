import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

export interface PersistedMessage {
    id: string;
    agentId: string;
    agentName: string;
    content: string;
    timestamp: string;
    type: 'user' | 'agent' | 'system';
    role?: 'user' | 'assistant' | 'system';
}

export interface ChatSession {
    id: string;
    name: string;
    created: string;
    lastUpdated: string;
    messages: PersistedMessage[];
    type: 'single' | 'multi';
    activeAgent?: string;
    selectedAgents?: string[];
    projectPath?: string;
}

export interface ChatWorkspace {
    sessions: ChatSession[];
    activeSessionId?: string;
    lastActiveSessionId?: string;
}

export class ChatPersistenceService {
    private static instance: ChatPersistenceService;
    private context: vscode.ExtensionContext;
    private chatDataPath: string;
    private currentWorkspace: ChatWorkspace;
    private autoSaveTimeout: NodeJS.Timeout | null = null;

    private constructor(context: vscode.ExtensionContext) {
        this.context = context;
        this.chatDataPath = this.getChatDataPath();
        this.currentWorkspace = this.loadWorkspace();
        this.setupAutoSave();
    }

    public static getInstance(context: vscode.ExtensionContext): ChatPersistenceService {
        if (!ChatPersistenceService.instance) {
            ChatPersistenceService.instance = new ChatPersistenceService(context);
        }
        return ChatPersistenceService.instance;
    }

    private getChatDataPath(): string {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (workspaceFolder) {
            // Store per-workspace
            const workspacePath = path.join(workspaceFolder.uri.fsPath, '.vscode', 'writers-room-chats.json');
            const vscodeDir = path.dirname(workspacePath);
            if (!fs.existsSync(vscodeDir)) {
                fs.mkdirSync(vscodeDir, { recursive: true });
            }
            return workspacePath;
        } else {
            // Store globally
            const globalStoragePath = this.context.globalStorageUri.fsPath;
            if (!fs.existsSync(globalStoragePath)) {
                fs.mkdirSync(globalStoragePath, { recursive: true });
            }
            return path.join(globalStoragePath, 'writers-room-chats.json');
        }
    }

    private loadWorkspace(): ChatWorkspace {
        try {
            if (fs.existsSync(this.chatDataPath)) {
                const data = fs.readFileSync(this.chatDataPath, 'utf8');
                return JSON.parse(data);
            }
        } catch (error) {
            console.error('Error loading chat workspace:', error);
        }

        return {
            sessions: [],
            activeSessionId: undefined,
            lastActiveSessionId: undefined
        };
    }

    private saveWorkspace(): void {
        try {
            const data = JSON.stringify(this.currentWorkspace, null, 2);
            fs.writeFileSync(this.chatDataPath, data, 'utf8');
            console.log('✅ Chat workspace saved');
        } catch (error) {
            console.error('❌ Error saving chat workspace:', error);
        }
    }

    private setupAutoSave(): void {
        // Auto-save every 10 seconds when there are changes
        setInterval(() => {
            if (this.autoSaveTimeout) {
                this.saveWorkspace();
                this.autoSaveTimeout = null;
            }
        }, 10000);
    }

    private scheduleAutoSave(): void {
        if (this.autoSaveTimeout) {
            clearTimeout(this.autoSaveTimeout);
        }
        this.autoSaveTimeout = setTimeout(() => {
            this.saveWorkspace();
            this.autoSaveTimeout = null;
        }, 2000); // Save 2 seconds after last change
    }

    public createSession(type: 'single' | 'multi', name?: string): ChatSession {
        const timestamp = new Date().toISOString();
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        
        const session: ChatSession = {
            id: `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            name: name || `${type === 'single' ? 'Agent Chat' : 'Multi-Agent Chat'} - ${new Date().toLocaleString()}`,
            created: timestamp,
            lastUpdated: timestamp,
            messages: [],
            type,
            projectPath: workspaceFolder?.uri.fsPath
        };

        this.currentWorkspace.sessions.push(session);
        this.currentWorkspace.activeSessionId = session.id;
        this.currentWorkspace.lastActiveSessionId = session.id;
        
        this.scheduleAutoSave();
        return session;
    }

    public getActiveSession(): ChatSession | null {
        if (!this.currentWorkspace.activeSessionId) {
            return null;
        }

        return this.currentWorkspace.sessions.find(s => s.id === this.currentWorkspace.activeSessionId) || null;
    }

    public setActiveSession(sessionId: string): boolean {
        const session = this.currentWorkspace.sessions.find(s => s.id === sessionId);
        if (session) {
            this.currentWorkspace.activeSessionId = sessionId;
            this.currentWorkspace.lastActiveSessionId = sessionId;
            this.scheduleAutoSave();
            return true;
        }
        return false;
    }

    public addMessage(sessionId: string, message: PersistedMessage): boolean {
        const session = this.currentWorkspace.sessions.find(s => s.id === sessionId);
        if (session) {
            message.timestamp = new Date().toISOString();
            session.messages.push(message);
            session.lastUpdated = message.timestamp;
            this.scheduleAutoSave();
            return true;
        }
        return false;
    }

    public updateSessionAgents(sessionId: string, activeAgent?: string, selectedAgents?: string[]): boolean {
        const session = this.currentWorkspace.sessions.find(s => s.id === sessionId);
        if (session) {
            session.activeAgent = activeAgent;
            session.selectedAgents = selectedAgents;
            session.lastUpdated = new Date().toISOString();
            this.scheduleAutoSave();
            return true;
        }
        return false;
    }

    public getAllSessions(): ChatSession[] {
        return this.currentWorkspace.sessions.sort((a, b) => 
            new Date(b.lastUpdated).getTime() - new Date(a.lastUpdated).getTime()
        );
    }

    public getSessionById(sessionId: string): ChatSession | null {
        return this.currentWorkspace.sessions.find(s => s.id === sessionId) || null;
    }

    public deleteSession(sessionId: string): boolean {
        const index = this.currentWorkspace.sessions.findIndex(s => s.id === sessionId);
        if (index !== -1) {
            this.currentWorkspace.sessions.splice(index, 1);
            
            // If deleting active session, switch to most recent
            if (this.currentWorkspace.activeSessionId === sessionId) {
                const remainingSessions = this.getAllSessions();
                this.currentWorkspace.activeSessionId = remainingSessions.length > 0 ? remainingSessions[0].id : undefined;
                this.currentWorkspace.lastActiveSessionId = this.currentWorkspace.activeSessionId;
            }
            
            this.scheduleAutoSave();
            return true;
        }
        return false;
    }

    public clearSession(sessionId: string): boolean {
        const session = this.currentWorkspace.sessions.find(s => s.id === sessionId);
        if (session) {
            session.messages = [];
            session.lastUpdated = new Date().toISOString();
            this.scheduleAutoSave();
            return true;
        }
        return false;
    }

    public renameSession(sessionId: string, newName: string): boolean {
        const session = this.currentWorkspace.sessions.find(s => s.id === sessionId);
        if (session) {
            session.name = newName;
            session.lastUpdated = new Date().toISOString();
            this.scheduleAutoSave();
            return true;
        }
        return false;
    }

    public exportSession(sessionId: string): string | null {
        const session = this.getSessionById(sessionId);
        if (!session) return null;

        const exportData = {
            session,
            exported: new Date().toISOString(),
            exportedBy: 'The Writers Room'
        };

        return JSON.stringify(exportData, null, 2);
    }

    public importSession(sessionData: string): ChatSession | null {
        try {
            const data = JSON.parse(sessionData);
            const session = data.session as ChatSession;
            
            // Generate new ID to avoid conflicts
            session.id = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            session.name = `${session.name} (Imported)`;
            session.lastUpdated = new Date().toISOString();

            this.currentWorkspace.sessions.push(session);
            this.scheduleAutoSave();
            
            return session;
        } catch (error) {
            console.error('Error importing session:', error);
            return null;
        }
    }

    // Auto-create session if none exists
    public getOrCreateActiveSession(type: 'single' | 'multi' = 'multi'): ChatSession {
        let activeSession = this.getActiveSession();
        
        if (!activeSession) {
            // Try to restore last active session
            if (this.currentWorkspace.lastActiveSessionId) {
                const lastSession = this.getSessionById(this.currentWorkspace.lastActiveSessionId);
                if (lastSession) {
                    this.currentWorkspace.activeSessionId = lastSession.id;
                    return lastSession;
                }
            }
            
            // Create new session
            activeSession = this.createSession(type);
        }
        
        return activeSession;
    }

    public cleanupOldSessions(maxSessions: number = 50): void {
        const sessions = this.getAllSessions();
        if (sessions.length > maxSessions) {
            const sessionsToRemove = sessions.slice(maxSessions);
            sessionsToRemove.forEach(session => {
                this.deleteSession(session.id);
            });
            console.log(`🧹 Cleaned up ${sessionsToRemove.length} old chat sessions`);
        }
    }

    public getSessionStats(): { totalSessions: number; totalMessages: number; oldestSession: string; newestSession: string } {
        const sessions = this.currentWorkspace.sessions;
        const totalMessages = sessions.reduce((sum, session) => sum + session.messages.length, 0);
        
        const sortedByDate = sessions.sort((a, b) => 
            new Date(a.created).getTime() - new Date(b.created).getTime()
        );

        return {
            totalSessions: sessions.length,
            totalMessages,
            oldestSession: sortedByDate.length > 0 ? sortedByDate[0].created : '',
            newestSession: sortedByDate.length > 0 ? sortedByDate[sortedByDate.length - 1].created : ''
        };
    }

    public dispose(): void {
        if (this.autoSaveTimeout) {
            clearTimeout(this.autoSaveTimeout);
        }
        this.saveWorkspace();
    }
} 