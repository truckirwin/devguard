# Implementation Plan - CursorVoice Functional Completion

## Architecture Problem & Solution

### Current Architecture Issue
```md
Voice → Deepgram API → Text → OpenAI API → Command
         $$$ + latency    $$$ + latency
```

### NEW: Local-First Architecture
```md
Voice → Local Speech API → Text → Local Command Parser → Action
        FREE + FAST               FREE + FAST

Voice → Local Speech API → Text → AI (only for complex coding) → Action
        FREE + FAST               $$$ (when needed)
```

## Critical Missing/Incomplete Components

### Core Service Implementations (UPDATED)
- **LocalSpeechService.ts**: NEW - Web Speech API integration for local, free processing
- **LocalCommandParser.ts**: NEW - Pattern matching for common VSCode commands
- **SpeechService.ts**: FALLBACK - Deepgram WebSocket for premium accuracy (optional)
- **CommandService.ts**: AI calls only for complex coding tasks, not basic commands
- **VoiceControlPanel.ts**: Webview HTML/CSS/JS implementation, real-time status updates
- **ConfigurationService.ts**: Settings validation, secure storage, processing mode selection

### Local Processing Implementation
```md
- Web Speech API: Browser's built-in speech recognition (free, fast, offline)
- Command Pattern Matching: Local parsing for 90% of common commands
- Hybrid Processing: Local-first, AI-fallback architecture
- Direct VSCode Integration: Command mapping without API overhead
```

### API Integration Issues (REDUCED SCOPE)
```md
- Local Speech API: Web Speech API integration, permission handling
- OpenAI: GPT-4 API calls ONLY for complex coding tasks (10% of usage)
- Deepgram: OPTIONAL premium accuracy mode for power users
- Audio: Simple MediaRecorder for local processing, no PCM conversion needed
```

### Event System & State Management
```md
- EventEmitter disposal patterns
- State transition validation (idle->listening->processing->idle)
- Memory leak prevention in audio streams
- Proper cleanup on extension deactivate
```

## Implementation Priority Queue (UPDATED)

### P0 - Local Processing Core
1. **LocalSpeechService**: Web Speech API integration (free, fast, offline)
2. **LocalCommandParser**: Pattern matching for common VSCode commands  
3. **Hybrid VoiceControlManager**: Local-first, AI-fallback architecture
4. **Command Execution**: Direct VSCode command mapping without API overhead
5. **Error Boundaries**: Try/catch throughout service layer, user feedback via statusbar

### P1 - Premium Features  
1. **Deepgram Integration**: Optional premium accuracy mode
2. **AI Assistance**: Complex coding tasks only (10% of usage)
3. **Smart Fallback**: Learn from unrecognized patterns
4. **Code Context Analysis**: Current file type, cursor position, surrounding lines

### P2 - UI/UX
1. **VoiceControlPanel**: React/HTML webview with controls, settings, processing mode selection
2. **Settings UI**: Local vs premium modes, API key config (optional), voice command customization
3. **Status Indicators**: Visual feedback for local/AI processing states

## Specific Implementation Tasks

### LocalSpeechService.ts (NEW FILE - P0)
```typescript
// Local speech recognition using Web Speech API
class LocalSpeechService {
  private recognition: SpeechRecognition;
  private transcriptEmitter = new vscode.EventEmitter<string>();
  
  constructor() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    this.recognition = new SpeechRecognition();
    this.recognition.continuous = true;
    this.recognition.interimResults = true;
    this.recognition.lang = 'en-US';
  }
  
  startListening(): void
  stopListening(): void
  onTranscriptReceived = this.transcriptEmitter.event
  dispose(): void
}
```

### LocalCommandParser.ts (NEW FILE - P0)
```typescript
// Local pattern matching for common commands
class LocalCommandParser {
  private commandMap: Map<string, VoiceCommand>;
  
  parseCommand(text: string): LocalCommand | null
  isComplexCommand(text: string): boolean
  addCustomCommand(pattern: string, command: string): void
  
  private matchPatterns(text: string): VoiceCommand | null
  private extractParameters(text: string, pattern: string): any[]
}

interface LocalCommand {
  type: 'vscode' | 'ai';
  command?: string;
  args?: any[];
  text?: string;
}

// Implementation example:
const commandMap = {
  // File operations
  'open file': 'workbench.action.files.openFile',
  'save file': 'workbench.action.files.save',
  'new file': 'workbench.action.files.newUntitledFile',
  
  // Navigation  
  'go to line': (text: string) => {
    const lineMatch = text.match(/(\d+)/);
    if (lineMatch) {
      return { command: 'workbench.action.gotoLine', args: [parseInt(lineMatch[1])] };
    }
  },
  
  // Editing
  'copy line': 'editor.action.copyLinesDownAction',
  'delete line': 'editor.action.deleteLines', 
  'comment': 'editor.action.commentLine',
  
  // Complex triggers for AI
  aiTriggers: ['create', 'generate', 'write', 'implement', 'refactor', 'optimize']
};
```

### VoiceControlManager.ts (UPDATED - P0)
```typescript
// Hybrid processing: local-first, AI-fallback
class VoiceControlManager {
  constructor(
    private localSpeechService: LocalSpeechService,     // NEW: Primary
    private localCommandParser: LocalCommandParser,     // NEW: Primary
    private speechService: SpeechService,               // FALLBACK: Premium
    private commandService: CommandService,             // AI only for complex tasks
    private configurationService: ConfigurationService
  ) {}
  
  async handleVoiceInput(transcript: string): Promise<void>
  private executeLocalCommand(command: LocalCommand): Promise<void>
  private executeAICommand(command: AICommand): Promise<void>
  private shouldUseAI(transcript: string): boolean
}
```

### SpeechService.ts (UPDATED - P1 Premium)
```typescript
// OPTIONAL Deepgram integration for premium accuracy
// Missing implementations:
- setupDeepgramWebSocket(): WebSocket connection with auth (OPTIONAL)
- handleAudioStream(): Real-time PCM data transmission (FALLBACK)
- processTranscript(): Parse Deepgram response, emit events (PREMIUM MODE)
- testMicrophone(): Device enumeration, permission checks
- dispose(): Cleanup streams, close WS connections
```

### CommandService.ts (UPDATED - P1 AI Only)
```typescript
// AI calls ONLY for complex coding tasks
// Missing implementations:
- executeVSCodeCommand(command: string, args?: any[]): Promise<void> (MOVED TO LOCAL)
- improveTextWithAI(text: string, context: CodeContext): Promise<string> (COMPLEX ONLY)
- interpretNaturalLanguage(input: string): Promise<Command> (COMPLEX ONLY)
- getCodeContext(): { fileType, cursorPos, selectedText, nearbyLines }
```

### VoiceControlPanel.ts WebView
```html
<!-- Webview content needed -->
<div id="voice-panel">
  <div class="status-display">
    <div class="listening-indicator"></div>
    <div class="transcript-display"></div>
  </div>
  <div class="controls">
    <button id="start-voice">Start Voice Agent</button>
    <button id="toggle-dictation">Toggle Dictation</button>
    <button id="test-mic">Test Microphone</button>
  </div>
  <div class="settings">
    <input type="password" id="deepgram-key" placeholder="Deepgram API Key">
    <input type="password" id="openai-key" placeholder="OpenAI API Key">
    <select id="language-select"></select>
    <input type="range" id="sensitivity" min="0.1" max="1" step="0.1">
  </div>
</div>
```

## Dependencies & Build Issues

### package.json Additions (UPDATED)
```json
{
  "dependencies": {
    "@deepgram/sdk": "^3.0.0",    // OPTIONAL for premium mode
    "openai": "^4.0.0",           // OPTIONAL for complex coding
    "ws": "^8.16.0"               // OPTIONAL for Deepgram
  },
  "devDependencies": {
    "@types/ws": "^8.5.10"
  }
}
```

### Configuration Additions
```json
{
  "cursorVoice.processingMode": {
    "type": "string",
    "enum": ["local-only", "local-first", "ai-first", "cloud-only"],
    "default": "local-first",
    "description": "Speech processing strategy"
  },
  "cursorVoice.enableAIFallback": {
    "type": "boolean", 
    "default": true,
    "description": "Use AI for unrecognized commands"
  },
  "cursorVoice.useDeepgram": {
    "type": "boolean",
    "default": false, 
    "description": "Use Deepgram for better accuracy (premium)"
  },
  "cursorVoice.localSpeechLang": {
    "type": "string",
    "default": "en-US",
    "description": "Language for local speech recognition"
  }
}
```

## Performance Benefits & Cost Analysis

### Local-First Processing Performance
```md
Basic Commands (90% of usage):
- "save file" → 50ms local processing (vs 500ms+ API)
- "go to line 42" → 50ms local processing  
- "copy line" → 50ms local processing
- "open terminal" → 50ms local processing

Complex Commands (10% of usage):
- "create a React component" → AI call (when needed)
- "refactor this function" → AI call (when needed)
```

### Cost Comparison
```md
Current Architecture: 
- Every command = Deepgram + OpenAI = $0.02-0.05 per command
- 100 commands/day = $2-5/day

Local-First Architecture:
- 90% free local processing, 10% AI = $0.002-0.005 per command  
- 100 commands/day = $0.20-0.50/day (10x cheaper)
- Offline capable for basic commands
```

### tsconfig.json Updates
```json
{
  "compilerOptions": {
    "lib": ["DOM", "ES2020"],
    "target": "ES2020",
    "moduleResolution": "node"
  }
}
```

## Error Handling Patterns

### Service Layer
```typescript
// Standardized error handling
try {
  await operation();
} catch (error) {
  this.logger.error(`Operation failed: ${error.message}`);
  this.emitError(error);
  vscode.window.showErrorMessage(`Voice Control: ${error.message}`);
}
```

### API Resilience
```typescript
// Retry logic for API calls
async apiCallWithRetry<T>(fn: () => Promise<T>, maxRetries = 3): Promise<T> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await delay(Math.pow(2, i) * 1000);
    }
  }
}
```

## Testing Implementation

### Unit Tests
```typescript
// src/test/services/SpeechService.test.ts
describe('SpeechService', () => {
  test('should connect to Deepgram WebSocket');
  test('should handle audio stream correctly');
  test('should emit transcript events');
  test('should handle connection errors');
});
```

### Integration Tests
```typescript
// src/test/integration/VoiceFlow.test.ts
describe('Voice Flow Integration', () => {
  test('should execute "open file" command');
  test('should handle dictation mode');
  test('should process AI text improvement');
});
```

## Security Implementation

### API Key Storage
```typescript
// Secure storage using vscode.SecretStorage
class SecureConfig {
  constructor(private context: vscode.ExtensionContext) {}
  
  async storeApiKey(service: string, key: string): Promise<void> {
    await this.context.secrets.store(`cursorVoice.${service}`, key);
  }
  
  async getApiKey(service: string): Promise<string | undefined> {
    return await this.context.secrets.get(`cursorVoice.${service}`);
  }
}
```

## Performance Optimizations

### Audio Processing
```typescript
// Efficient audio buffering
class AudioBuffer {
  private buffer: Int16Array[] = [];
  private maxBufferSize = 8192; // 16kHz * 0.5s
  
  addChunk(chunk: Int16Array): void {
    this.buffer.push(chunk);
    if (this.getTotalSize() > this.maxBufferSize) {
      this.buffer.shift();
    }
  }
}
```

## Build & Package
```bash
# Development
npm run compile
npm run watch

# Testing
npm run test

# Package for distribution
npm run package
# -> cursor-voice-control-1.0.0.vsix
```

## Validation Checklist
- [ ] Audio capture working (MediaRecorder API)
- [ ] Deepgram WebSocket connection established
- [ ] OpenAI API calls successful
- [ ] VSCode command execution
- [ ] Webview panel functional
- [ ] Settings persistence
- [ ] Error handling comprehensive
- [ ] Memory leaks prevented
- [ ] Extension activation/deactivation clean

## Critical Implementation Order (UPDATED)
1. **LocalSpeechService** (Web Speech API integration - core local processing)
2. **LocalCommandParser** (pattern matching for common commands)
3. **Hybrid VoiceControlManager** (local-first, AI-fallback orchestration)
4. **Direct VSCode command execution** (local command processing)
5. **Error handling + logging** throughout service layer
6. **VoiceControlPanel webview** (UI with processing mode selection)
7. **AI integration** for complex coding tasks only (optional premium feature)
8. **Deepgram integration** for premium accuracy mode (optional)
9. **Testing suite** (focus on local processing first)
10. **Security hardening** (API key storage for optional features) 