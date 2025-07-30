import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

export class ProjectTreeProvider implements vscode.TreeDataProvider<ProjectTreeItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<ProjectTreeItem | undefined | null | void> = new vscode.EventEmitter<ProjectTreeItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<ProjectTreeItem | undefined | null | void> = this._onDidChangeTreeData.event;

    constructor(private context: vscode.ExtensionContext) {}

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: ProjectTreeItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: ProjectTreeItem): Thenable<ProjectTreeItem[]> {
        if (!element) {
            // Root level - check if we have a writing project
            return this.getProjectStructure();
        }

        // Handle sub-items based on context
        switch (element.contextValue) {
            case 'current-project':
                return Promise.resolve([
                    new ProjectTreeItem('📄 Screenplay Draft', vscode.TreeItemCollapsibleState.None, 'file', {
                        command: 'vscode.open',
                        title: 'Open Screenplay',
                        arguments: [element.resourceUri ? vscode.Uri.joinPath(element.resourceUri, 'screenplay.fountain') : undefined]
                    }),
                ]);
            case 'characters':
                return this.getCharacterFiles(element.resourceUri);
            case 'scenes':
                return this.getSceneFiles(element.resourceUri);
            default:
                return Promise.resolve([]);
        }
    }

    private async getProjectStructure(): Promise<ProjectTreeItem[]> {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            return [
                new ProjectTreeItem('No Project Open', vscode.TreeItemCollapsibleState.None, 'no-project', {
                    command: 'theWritersRoom.createProject',
                    title: 'Create New Project'
                })
            ];
        }

        // Check if this looks like a writing project
        const projectJsonPath = path.join(workspaceFolder.uri.fsPath, 'project.json');
        if (fs.existsSync(projectJsonPath)) {
            try {
                const projectData = JSON.parse(fs.readFileSync(projectJsonPath, 'utf8'));
                return [
                    new ProjectTreeItem('Current Project', vscode.TreeItemCollapsibleState.Expanded, 'current-project', undefined, workspaceFolder.uri),
                    new ProjectTreeItem('👥 Characters', vscode.TreeItemCollapsibleState.Collapsed, 'characters', {
                        command: 'theWritersRoom.newCharacter',
                        title: 'Add Character'
                    }, workspaceFolder.uri),
                    new ProjectTreeItem('🎬 Scenes', vscode.TreeItemCollapsibleState.Collapsed, 'scenes', {
                        command: 'theWritersRoom.newScene',
                        title: 'Add Scene'
                    }, workspaceFolder.uri),
                    new ProjectTreeItem('📋 Outline', vscode.TreeItemCollapsibleState.None, 'file', {
                        command: 'vscode.open',
                        title: 'Open Outline',
                        arguments: [vscode.Uri.joinPath(workspaceFolder.uri, 'outline.md')]
                    }),
                    new ProjectTreeItem('📝 Notes', vscode.TreeItemCollapsibleState.None, 'file', {
                        command: 'vscode.open',
                        title: 'Open Notes',
                        arguments: [vscode.Uri.joinPath(workspaceFolder.uri, 'notes.md')]
                    })
                ];
            } catch (error) {
                console.error('Error reading project.json:', error);
            }
        }

        // No writing project detected
        return [
            new ProjectTreeItem('📁 Recent Projects', vscode.TreeItemCollapsibleState.Collapsed, 'recent-projects'),
            new ProjectTreeItem('➕ Create New Project', vscode.TreeItemCollapsibleState.None, 'create-project', {
                command: 'theWritersRoom.createProject',
                title: 'Create New Writing Project'
            })
        ];
    }

    private async getCharacterFiles(projectUri?: vscode.Uri): Promise<ProjectTreeItem[]> {
        if (!projectUri) return [];

        const charactersPath = path.join(projectUri.fsPath, 'characters.md');
        const characters: ProjectTreeItem[] = [];

        if (fs.existsSync(charactersPath)) {
            try {
                const content = fs.readFileSync(charactersPath, 'utf8');
                const characterNames = content.match(/###\s+(.+)/g);
                
                if (characterNames) {
                    characterNames.forEach(match => {
                        const name = match.replace('###', '').trim();
                        characters.push(new ProjectTreeItem(
                            name,
                            vscode.TreeItemCollapsibleState.None,
                            'character',
                            {
                                command: 'vscode.open',
                                title: 'Open Characters',
                                arguments: [vscode.Uri.joinPath(projectUri, 'characters.md')]
                            }
                        ));
                    });
                }
            } catch (error) {
                console.error('Error reading characters file:', error);
            }
        }

        characters.push(new ProjectTreeItem(
            '➕ Add Character',
            vscode.TreeItemCollapsibleState.None,
            'add-character',
            {
                command: 'theWritersRoom.newCharacter',
                title: 'Add New Character'
            }
        ));

        return characters;
    }

    private async getSceneFiles(projectUri?: vscode.Uri): Promise<ProjectTreeItem[]> {
        if (!projectUri) return [];

        const scenes: ProjectTreeItem[] = [
            new ProjectTreeItem('INT. LOCATION - DAY', vscode.TreeItemCollapsibleState.None, 'scene'),
            new ProjectTreeItem('EXT. LOCATION - NIGHT', vscode.TreeItemCollapsibleState.None, 'scene'),
            new ProjectTreeItem('➕ Add Scene', vscode.TreeItemCollapsibleState.None, 'add-scene', {
                command: 'theWritersRoom.newScene',
                title: 'Add New Scene'
            })
        ];

        return scenes;
    }
}

export class ProjectTreeItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly contextValue: string,
        public readonly command?: vscode.Command,
        public readonly resourceUri?: vscode.Uri
    ) {
        super(label, collapsibleState);
        this.tooltip = `${this.label}`;
        
        // Set icons based on context
        switch (contextValue) {
            case 'current-project':
                this.iconPath = new vscode.ThemeIcon('folder-opened');
                break;
            case 'characters':
                this.iconPath = new vscode.ThemeIcon('person');
                break;
            case 'scenes':
                this.iconPath = new vscode.ThemeIcon('play');
                break;
            case 'file':
                this.iconPath = new vscode.ThemeIcon('file');
                break;
            case 'character':
                this.iconPath = new vscode.ThemeIcon('person');
                break;
            case 'scene':
                this.iconPath = new vscode.ThemeIcon('play');
                break;
            case 'create-project':
                this.iconPath = new vscode.ThemeIcon('add');
                break;
            case 'recent-projects':
                this.iconPath = new vscode.ThemeIcon('history');
                break;
            default:
                this.iconPath = new vscode.ThemeIcon('circle-outline');
        }
    }
} 