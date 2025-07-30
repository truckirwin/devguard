import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

export interface DocumentContext {
    uri: vscode.Uri;
    fileName: string;
    content: string;
    lineCount: number;
    wordCount: number;
    fileType: string;
    lastModified: Date;
}

export interface ProjectContext {
    workspaceRoot: string;
    documents: DocumentContext[];
    projectFiles: string[];
    writingFiles: string[];
    totalFiles: number;
}

export class DocumentContextService {
    private static instance: DocumentContextService;
    private context: vscode.ExtensionContext;
    private projectContext: ProjectContext | null = null;
    private documentCache: Map<string, DocumentContext> = new Map();

    private constructor(context: vscode.ExtensionContext) {
        this.context = context;
        this.setupFileWatchers();
    }

    public static getInstance(context: vscode.ExtensionContext): DocumentContextService {
        if (!DocumentContextService.instance) {
            DocumentContextService.instance = new DocumentContextService(context);
        }
        return DocumentContextService.instance;
    }

    private setupFileWatchers(): void {
        // Watch for file changes in the workspace
        const watcher = vscode.workspace.createFileSystemWatcher('**/*');
        
        watcher.onDidChange(uri => {
            this.invalidateCache(uri.toString());
            this.refreshProjectContext();
        });

        watcher.onDidCreate(uri => {
            this.refreshProjectContext();
        });

        watcher.onDidDelete(uri => {
            this.documentCache.delete(uri.toString());
            this.refreshProjectContext();
        });

        this.context.subscriptions.push(watcher);
    }

    private invalidateCache(uriString: string): void {
        this.documentCache.delete(uriString);
    }

    public async getProjectContext(): Promise<ProjectContext | null> {
        if (!this.projectContext) {
            await this.refreshProjectContext();
        }
        return this.projectContext;
    }

    public async refreshProjectContext(): Promise<void> {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            this.projectContext = null;
            return;
        }

        const workspaceRoot = workspaceFolder.uri.fsPath;
        const allFiles = await this.findProjectFiles(workspaceRoot);
        
        // Filter for writing-related files
        const writingExtensions = ['.md', '.txt', '.fountain', '.fdx', '.docx', '.rtf'];
        const writingFiles = allFiles.filter(file => 
            writingExtensions.some(ext => file.toLowerCase().endsWith(ext))
        );

        // Load document contexts for writing files
        const documents: DocumentContext[] = [];
        for (const filePath of writingFiles) {
            try {
                const docContext = await this.getDocumentContext(vscode.Uri.file(filePath));
                if (docContext) {
                    documents.push(docContext);
                }
            } catch (error) {
                console.warn(`Failed to load document context for ${filePath}:`, error);
            }
        }

        this.projectContext = {
            workspaceRoot,
            documents,
            projectFiles: allFiles,
            writingFiles,
            totalFiles: allFiles.length
        };
    }

    private async findProjectFiles(rootPath: string): Promise<string[]> {
        const files: string[] = [];
        const excludePatterns = [
            'node_modules',
            '.git',
            '.vscode',
            'dist',
            'build',
            'out',
            '.DS_Store'
        ];

        const processDirectory = async (dirPath: string): Promise<void> => {
            try {
                const entries = await fs.promises.readdir(dirPath, { withFileTypes: true });
                
                for (const entry of entries) {
                    const fullPath = path.join(dirPath, entry.name);
                    
                    if (entry.isDirectory()) {
                        if (!excludePatterns.some(pattern => entry.name.includes(pattern))) {
                            await processDirectory(fullPath);
                        }
                    } else if (entry.isFile()) {
                        files.push(fullPath);
                    }
                }
            } catch (error) {
                // Directory might not be accessible, skip it
            }
        };

        await processDirectory(rootPath);
        return files;
    }

    public async getDocumentContext(uri: vscode.Uri): Promise<DocumentContext | null> {
        const uriString = uri.toString();
        
        // Check cache first
        if (this.documentCache.has(uriString)) {
            return this.documentCache.get(uriString)!;
        }

        try {
            const document = await vscode.workspace.openTextDocument(uri);
            const content = document.getText();
            const stats = await vscode.workspace.fs.stat(uri);
            
            const docContext: DocumentContext = {
                uri,
                fileName: path.basename(uri.fsPath),
                content,
                lineCount: document.lineCount,
                wordCount: this.countWords(content),
                fileType: this.getFileType(uri.fsPath),
                lastModified: new Date(stats.mtime)
            };

            // Cache the context
            this.documentCache.set(uriString, docContext);
            return docContext;
        } catch (error) {
            console.error(`Failed to get document context for ${uri.fsPath}:`, error);
            return null;
        }
    }

    public async findDocumentsByName(searchTerm: string): Promise<DocumentContext[]> {
        await this.refreshProjectContext();
        if (!this.projectContext) return [];

        const searchLower = searchTerm.toLowerCase();
        return this.projectContext.documents.filter(doc => 
            doc.fileName.toLowerCase().includes(searchLower) ||
            doc.content.toLowerCase().includes(searchLower)
        );
    }

    public async findDocumentsByType(fileType: string): Promise<DocumentContext[]> {
        await this.refreshProjectContext();
        if (!this.projectContext) return [];

        return this.projectContext.documents.filter(doc => 
            doc.fileType === fileType
        );
    }

    public async getActiveDocumentContext(): Promise<DocumentContext | null> {
        const activeEditor = vscode.window.activeTextEditor;
        if (!activeEditor) return null;

        return await this.getDocumentContext(activeEditor.document.uri);
    }

    public async analyzeDocumentForAgents(searchQuery: string): Promise<{
        relevantDocuments: DocumentContext[];
        contextSummary: string;
        suggestedDocuments: string[];
    }> {
        await this.refreshProjectContext();
        if (!this.projectContext) {
            return {
                relevantDocuments: [],
                contextSummary: "No project context available.",
                suggestedDocuments: []
            };
        }

        const queryLower = searchQuery.toLowerCase();
        const relevantDocs: DocumentContext[] = [];
        
        // Keywords that suggest document types
        const documentKeywords = {
            'plot': ['plot', 'outline', 'story', 'structure'],
            'character': ['character', 'cast', 'protagonist', 'antagonist'],
            'script': ['script', 'screenplay', 'dialogue', 'scene'],
            'treatment': ['treatment', 'synopsis', 'summary'],
            'notes': ['notes', 'ideas', 'brainstorm']
        };

        // Find documents that match the query
        for (const doc of this.projectContext.documents) {
            const docContent = doc.content.toLowerCase();
            const docName = doc.fileName.toLowerCase();
            
            // Check for direct mentions
            if (docContent.includes(queryLower) || docName.includes(queryLower)) {
                relevantDocs.push(doc);
                continue;
            }

            // Check for keyword matches
            for (const [category, keywords] of Object.entries(documentKeywords)) {
                if (keywords.some(keyword => queryLower.includes(keyword))) {
                    if (keywords.some(keyword => docName.includes(keyword) || docContent.includes(keyword))) {
                        relevantDocs.push(doc);
                        break;
                    }
                }
            }
        }

        // If no specific matches, include likely candidates
        if (relevantDocs.length === 0) {
            const likelyDocs = this.projectContext.documents.filter(doc => {
                const name = doc.fileName.toLowerCase();
                return name.includes('plot') || name.includes('outline') || 
                       name.includes('script') || name.includes('character') ||
                       name.includes('story') || name.includes('treatment');
            });
            relevantDocs.push(...likelyDocs.slice(0, 3)); // Limit to 3 most likely
        }

        // Generate context summary
        const contextSummary = this.generateContextSummary(relevantDocs, queryLower);
        
        // Suggest additional documents
        const suggestedDocuments = this.projectContext.documents
            .filter(doc => !relevantDocs.includes(doc))
            .map(doc => doc.fileName)
            .slice(0, 5);

        return {
            relevantDocuments: relevantDocs,
            contextSummary,
            suggestedDocuments
        };
    }

    private generateContextSummary(documents: DocumentContext[], query: string): string {
        if (documents.length === 0) {
            return `No documents found matching "${query}". Available documents in project: ${this.projectContext?.documents.map(d => d.fileName).join(', ') || 'none'}.`;
        }

        let summary = `Found ${documents.length} relevant document(s):\n\n`;
        
        documents.forEach((doc, index) => {
            summary += `**${doc.fileName}** (${doc.wordCount} words, ${doc.lineCount} lines)\n`;
            
            // Add preview of relevant content
            const preview = this.extractRelevantPreview(doc.content, query, 150);
            if (preview) {
                summary += `Preview: ${preview}\n\n`;
            }
        });

        return summary;
    }

    private extractRelevantPreview(content: string, query: string, maxLength: number): string {
        const lines = content.split('\n');
        const queryWords = query.split(' ').filter(w => w.length > 2);
        
        // Find lines that contain query terms
        const relevantLines = lines.filter(line => 
            queryWords.some(word => line.toLowerCase().includes(word.toLowerCase()))
        );

        if (relevantLines.length > 0) {
            let preview = relevantLines.slice(0, 3).join(' ').trim();
            if (preview.length > maxLength) {
                preview = preview.substring(0, maxLength) + '...';
            }
            return preview;
        }

        // Fallback to beginning of document
        let preview = content.substring(0, maxLength).trim();
        if (content.length > maxLength) {
            preview += '...';
        }
        return preview;
    }

    private countWords(text: string): number {
        return text.split(/\s+/).filter(word => word.length > 0).length;
    }

    private getFileType(filePath: string): string {
        const ext = path.extname(filePath).toLowerCase();
        
        const typeMap: { [key: string]: string } = {
            '.md': 'markdown',
            '.txt': 'text',
            '.fountain': 'screenplay',
            '.fdx': 'final-draft',
            '.docx': 'word',
            '.rtf': 'rich-text',
            '.pdf': 'pdf'
        };

        return typeMap[ext] || 'unknown';
    }

    public async getDocumentSnippet(uri: vscode.Uri, startLine: number, endLine: number): Promise<string> {
        const docContext = await this.getDocumentContext(uri);
        if (!docContext) return '';

        const lines = docContext.content.split('\n');
        return lines.slice(startLine, endLine + 1).join('\n');
    }

    public getProjectStats(): { fileCount: number; writingFiles: number; totalWords: number; totalLines: number } {
        if (!this.projectContext) {
            return { fileCount: 0, writingFiles: 0, totalWords: 0, totalLines: 0 };
        }

        const totalWords = this.projectContext.documents.reduce((sum, doc) => sum + doc.wordCount, 0);
        const totalLines = this.projectContext.documents.reduce((sum, doc) => sum + doc.lineCount, 0);

        return {
            fileCount: this.projectContext.totalFiles,
            writingFiles: this.projectContext.writingFiles.length,
            totalWords,
            totalLines
        };
    }

    public dispose(): void {
        this.documentCache.clear();
        this.projectContext = null;
    }
} 