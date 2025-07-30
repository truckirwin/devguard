import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { exec } from 'child_process';
import { promisify } from 'util';
import archiver from 'archiver';

const execAsync = promisify(exec);

export class BackupManager {
    private backupLocation: string;

    constructor(private context: vscode.ExtensionContext) {
        this.backupLocation = this.getBackupLocation();
        this.ensureBackupDirectory();
    }

    private getBackupLocation(): string {
        const config = vscode.workspace.getConfiguration('devguard');
        const location = config.get('backupLocation', '~/DevGuard-Backups');
        
        // Expand home directory
        const os = require('os');
        return location.replace('~', os.homedir());
    }

    private async ensureBackupDirectory(): Promise<void> {
        try {
            await fs.promises.mkdir(this.backupLocation, { recursive: true });
            console.log(`🛡️ DevGuard: Backup directory ready at ${this.backupLocation}`);
        } catch (error) {
            console.error('🛡️ DevGuard: Failed to create backup directory:', error);
            vscode.window.showErrorMessage(`Failed to create backup directory: ${error}`);
        }
    }

    public async performQuickSave(): Promise<void> {
        return this.performBackup('Quick save session', false);
    }

    public async performSmartSave(message: string): Promise<void> {
        return this.performBackup(message, true);
    }

    public async performDailyBackup(): Promise<void> {
        return this.performBackup('Daily backup', true, true);
    }

    private async performBackup(message: string, isDetailed: boolean = false, isDaily: boolean = false): Promise<void> {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            vscode.window.showWarningMessage('No workspace folder open for backup');
            return;
        }

        try {
            const projectPath = workspaceFolder.uri.fsPath;
            const projectName = path.basename(projectPath);
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            
            console.log(`🛡️ DevGuard: Starting backup for ${projectName}`);

            // 1. Save all open files first
            await vscode.workspace.saveAll();

            // 2. Git operations (if enabled)
            const config = vscode.workspace.getConfiguration('devguard');
            if (config.get('autoCommitEnabled', true)) {
                await this.performGitOperations(projectPath, message);
            }

            // 3. Create external backup for detailed saves
            if (isDetailed || isDaily) {
                await this.createExternalBackup(projectPath, projectName, timestamp, message);
            }

            console.log(`🛡️ DevGuard: Backup completed for ${projectName}`);

        } catch (error) {
            console.error('🛡️ DevGuard: Backup failed:', error);
            throw error;
        }
    }

    private async performGitOperations(projectPath: string, message: string): Promise<void> {
        const config = vscode.workspace.getConfiguration('devguard');
        
        try {
            // Check if git repository exists
            await execAsync('git rev-parse --is-inside-work-tree', { cwd: projectPath });

            // Check if there are any changes to commit
            const { stdout: statusOutput } = await execAsync('git status --porcelain', { cwd: projectPath });
            
            if (!statusOutput.trim()) {
                console.log('🛡️ DevGuard: No changes to commit');
                return;
            }

            // Add all changes
            await execAsync('git add .', { cwd: projectPath });

            // Create commit message
            const commitMessage = `DevGuard save: ${message} - ${new Date().toISOString()}`;
            await execAsync(`git commit -m "${this.escapeShellArg(commitMessage)}"`, { cwd: projectPath });

            console.log(`🛡️ DevGuard: Git commit created - ${message}`);

            // Push to remote (if enabled and remote exists)
            if (config.get('pushToRemote', true)) {
                try {
                    // Check if remote exists
                    await execAsync('git remote', { cwd: projectPath });
                    
                    // Get current branch
                    const { stdout: branchOutput } = await execAsync('git branch --show-current', { cwd: projectPath });
                    const currentBranch = branchOutput.trim();
                    
                    if (currentBranch) {
                        await execAsync(`git push origin ${currentBranch}`, { cwd: projectPath });
                        console.log('🛡️ DevGuard: Changes pushed to remote');
                    }
                } catch (pushError) {
                    console.log('🛡️ DevGuard: Push failed (possibly no remote configured):', pushError);
                }
            }

        } catch (error) {
            // Git operations are optional - don't fail the entire backup
            console.log('🛡️ DevGuard: Git operations skipped (not a git repository or git not available)');
        }
    }

    private async createExternalBackup(projectPath: string, projectName: string, timestamp: string, message: string): Promise<void> {
        const backupFileName = `${projectName}-${timestamp.split('T')[0]}.zip`;
        const backupFilePath = path.join(this.backupLocation, backupFileName);

        console.log(`🛡️ DevGuard: Creating external backup: ${backupFileName}`);

        try {
            await this.createZipBackup(projectPath, backupFilePath);

            // Create info file
            const infoFilePath = path.join(this.backupLocation, `${projectName}-${timestamp}-info.txt`);
            const info = `DevGuard Backup Info
Project: ${projectName}
Timestamp: ${new Date().toISOString()}
Message: ${message}
Source: ${projectPath}
Backup File: ${backupFileName}
`;
            await fs.promises.writeFile(infoFilePath, info);

            // Clean old backups
            await this.cleanOldBackups(projectName);

            console.log(`🛡️ DevGuard: External backup created successfully`);

        } catch (error) {
            console.error('🛡️ DevGuard: External backup failed:', error);
            throw new Error(`External backup failed: ${error}`);
        }
    }

    private async createZipBackup(sourceDir: string, outputPath: string): Promise<void> {
        return new Promise((resolve, reject) => {
            const output = fs.createWriteStream(outputPath);
            const archive = archiver('zip', { zlib: { level: 9 } });

            output.on('close', () => {
                console.log(`🛡️ DevGuard: Archive created: ${archive.pointer()} total bytes`);
                resolve();
            });

            archive.on('error', (err: Error) => {
                reject(err);
            });

            archive.pipe(output);

            // Get exclude patterns from configuration
            const config = vscode.workspace.getConfiguration('devguard');
            const excludePatterns: string[] = config.get('excludePatterns', []);

            // Add files to archive with exclusions
            archive.glob('**/*', {
                cwd: sourceDir,
                ignore: excludePatterns,
                dot: false
            });

            archive.finalize();
        });
    }

    private async cleanOldBackups(projectName: string): Promise<void> {
        const config = vscode.workspace.getConfiguration('devguard');
        const retentionDays = config.get('backupRetentionDays', 5);
        const cutoffTime = Date.now() - (retentionDays * 24 * 60 * 60 * 1000);

        try {
            const files = await fs.promises.readdir(this.backupLocation);
            let cleanedCount = 0;

            for (const file of files) {
                if (file.startsWith(projectName)) {
                    const filePath = path.join(this.backupLocation, file);
                    const stats = await fs.promises.stat(filePath);
                    
                    if (stats.mtime.getTime() < cutoffTime) {
                        await fs.promises.unlink(filePath);
                        cleanedCount++;
                    }
                }
            }

            if (cleanedCount > 0) {
                console.log(`🛡️ DevGuard: Cleaned ${cleanedCount} old backup files`);
            }

        } catch (error) {
            console.log('🛡️ DevGuard: Failed to clean old backups:', error);
        }
    }

    private escapeShellArg(arg: string): string {
        return arg.replace(/'/g, "'\"'\"'");
    }

    public openBackupLocation(): void {
        vscode.env.openExternal(vscode.Uri.file(this.backupLocation));
    }

    public getBackupLocationPath(): string {
        return this.backupLocation;
    }

    public async getBackupStats(): Promise<{ totalBackups: number; totalSize: number; oldestBackup?: Date; newestBackup?: Date }> {
        try {
            const files = await fs.promises.readdir(this.backupLocation);
            const backupFiles = files.filter(f => f.endsWith('.zip'));
            
            let totalSize = 0;
            let oldestDate: Date | undefined;
            let newestDate: Date | undefined;

            for (const file of backupFiles) {
                const filePath = path.join(this.backupLocation, file);
                const stats = await fs.promises.stat(filePath);
                
                totalSize += stats.size;
                
                if (!oldestDate || stats.mtime < oldestDate) {
                    oldestDate = stats.mtime;
                }
                if (!newestDate || stats.mtime > newestDate) {
                    newestDate = stats.mtime;
                }
            }

            return {
                totalBackups: backupFiles.length,
                totalSize,
                oldestBackup: oldestDate,
                newestBackup: newestDate
            };

        } catch (error) {
            console.error('🛡️ DevGuard: Failed to get backup stats:', error);
            return { totalBackups: 0, totalSize: 0 };
        }
    }
} 