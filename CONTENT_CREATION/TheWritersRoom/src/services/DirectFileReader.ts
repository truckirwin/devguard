import * as vscode from 'vscode';

export class DirectFileReader {
    private static instance: DirectFileReader;

    private constructor() {}

    public static getInstance(): DirectFileReader {
        if (!DirectFileReader.instance) {
            DirectFileReader.instance = new DirectFileReader();
        }
        return DirectFileReader.instance;
    }

    /**
     * Get the content of the currently active file
     * Returns null if no file is open or it's not a writing file
     */
    public getCurrentFileContent(): { fileName: string; content: string; fileType: string } | null {
        const activeEditor = vscode.window.activeTextEditor;
        if (!activeEditor) {
            console.log('[DirectFileReader] No active editor');
            return null;
        }

        const document = activeEditor.document;
        const fileName = document.fileName;
        const content = document.getText();

        // Check if it's a writing-related file
        const writingExtensions = ['.md', '.txt', '.fountain', '.fdx', '.rtf'];
        const isWritingFile = writingExtensions.some(ext => fileName.toLowerCase().endsWith(ext));

        if (!isWritingFile) {
            console.log('[DirectFileReader] Not a writing file:', fileName);
            return null;
        }

        const fileType = this.getFileType(fileName);
        
        console.log(`[DirectFileReader] Reading active file: ${fileName} (${content.length} chars)`);
        
        return {
            fileName: fileName.split('/').pop() || fileName,
            content,
            fileType
        };
    }

    /**
     * Get all writing files in the workspace
     */
    public async getAllWritingFiles(): Promise<Array<{ fileName: string; content: string; fileType: string }>> {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            return [];
        }

        const files: Array<{ fileName: string; content: string; fileType: string }> = [];
        
        try {
            // Find all writing files in workspace
            const pattern = new vscode.RelativePattern(workspaceFolder, '**/*.{md,txt,fountain,fdx,rtf}');
            const uris = await vscode.workspace.findFiles(pattern, '**/node_modules/**');

            for (const uri of uris.slice(0, 5)) { // Limit to 5 files to avoid overwhelming context
                try {
                    const document = await vscode.workspace.openTextDocument(uri);
                    const content = document.getText();
                    
                    if (content.length > 0) {
                        files.push({
                            fileName: uri.path.split('/').pop() || uri.path,
                            content,
                            fileType: this.getFileType(uri.path)
                        });
                    }
                } catch (error) {
                    console.warn(`[DirectFileReader] Failed to read ${uri.path}:`, error);
                }
            }

            console.log(`[DirectFileReader] Found ${files.length} writing files in workspace`);
            return files;
        } catch (error) {
            console.error('[DirectFileReader] Error finding files:', error);
            return [];
        }
    }

    /**
     * Create a file context string for AI agents
     */
    public async createFileContext(userMessage: string): Promise<string> {
        let context = '';

        console.log(`[DirectFileReader] Creating file context for: "${userMessage}"`);

        // Always try to include the active file first
        const activeFile = this.getCurrentFileContent();
        if (activeFile) {
            context += `\n=== CURRENT ACTIVE FILE: ${activeFile.fileName} ===\n`;
            context += `File Type: ${activeFile.fileType}\n`;
            context += `Content:\n${activeFile.content}\n\n`;
            console.log(`[DirectFileReader] Added active file: ${activeFile.fileName} (${activeFile.content.length} chars)`);
        } else {
            console.log(`[DirectFileReader] No active file detected`);
        }

        // ALWAYS include workspace files for file-related queries
        const isFileQuery = this.isFileRelatedQuery(userMessage);
        console.log(`[DirectFileReader] Is file-related query: ${isFileQuery}`);
        
        if (isFileQuery) {
            const workspaceFiles = await this.getAllWritingFiles();
            console.log(`[DirectFileReader] Found ${workspaceFiles.length} workspace files`);
            
            if (workspaceFiles.length > 0) {
                context += `=== WORKSPACE WRITING FILES ===\n`;
                
                for (const file of workspaceFiles.slice(0, 3)) { // Top 3 files
                    context += `--- ${file.fileName} (${file.fileType}) ---\n`;
                    context += file.content.substring(0, 2000); // Increased from 1000 to 2000 chars
                    if (file.content.length > 2000) {
                        context += '\n[Content truncated...]\n';
                    }
                    context += '\n\n';
                    console.log(`[DirectFileReader] Added workspace file: ${file.fileName} (${file.content.length} chars)`);
                }
            }
        }

        if (context) {
            console.log(`[DirectFileReader] ✅ Created file context (${context.length} chars) for query: ${userMessage}`);
        } else {
            console.log(`[DirectFileReader] ❌ No file context created for query: ${userMessage}`);
        }

        return context;
    }

    /**
     * Check if the user message is asking about files/documents
     */
    private isFileRelatedQuery(message: string): boolean {
        const msg = message.toLowerCase();
        const fileKeywords = [
            'read', 'plot', 'outline', 'document', 'file', 'script', 'treatment',
            'character', 'story', 'content', 'text', 'analyze', 'review',
            'tell me about', 'what does', 'thoughts on', 'feedback on'
        ];

        return fileKeywords.some(keyword => msg.includes(keyword));
    }

    /**
     * Get file type from file path
     */
    private getFileType(filePath: string): string {
        const ext = filePath.toLowerCase().split('.').pop();
        
        switch (ext) {
            case 'md': return 'Markdown';
            case 'txt': return 'Text';
            case 'fountain': return 'Fountain Screenplay';
            case 'fdx': return 'Final Draft';
            case 'rtf': return 'Rich Text';
            default: return 'Document';
        }
    }

    /**
     * Log current state for debugging
     */
    public logCurrentState(): void {
        const activeFile = this.getCurrentFileContent();
        console.log('[DirectFileReader] Current State:');
        console.log('- Active File:', activeFile?.fileName || 'None');
        console.log('- File Type:', activeFile?.fileType || 'N/A');
        console.log('- Content Length:', activeFile?.content.length || 0);
    }
} 