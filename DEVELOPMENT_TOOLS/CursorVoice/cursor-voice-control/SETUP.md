# Cursor Voice Control - Setup Guide

## Quick Start

### For Users

1. **Install Dependencies**: The extension will prompt you to install required APIs
2. **Get API Keys**:
   - [Deepgram API Key](https://deepgram.com) (Required for speech recognition)
   - [OpenAI API Key](https://openai.com) (Optional, for AI assistance)
3. **Configure**: Use Command Palette → "Cursor Voice: Configure API Keys"
4. **Test**: Use Command Palette → "Cursor Voice: Test Microphone"
5. **Start**: Press `Cmd/Ctrl+Shift+V` to begin voice control

### For Developers

## Development Setup

```bash
# Clone repository
git clone <repository-url>
cd cursor-voice-control

# Install dependencies
npm install

# Compile TypeScript
npm run compile

# Watch for changes during development
npm run watch
```

## Build Extension

```bash
# Compile and package
npm run vscode:prepublish

# Create VSIX package
npm run package
```

## Testing

### Manual Testing

1. **Open Extension Development Host**:
   - Press `F5` in VS Code with the project open
   - This opens a new VS Code window with the extension loaded

2. **Test Voice Commands**:
   - Configure API keys in the development host
   - Test microphone functionality
   - Try various voice commands

3. **Debug**:
   - Set breakpoints in TypeScript files
   - Use Developer Tools console for logs
   - Check Output panel for extension logs

### Automated Testing

```bash
# Run tests (when implemented)
npm test
```

## API Configuration

### Deepgram Setup

1. Sign up at [Deepgram](https://deepgram.com)
2. Create a new project
3. Generate an API key
4. Add credits to your account (pay-as-you-go)

### OpenAI Setup

1. Sign up at [OpenAI](https://openai.com)
2. Navigate to API keys section
3. Create a new API key
4. Add billing information for usage

## File Structure

```
cursor-voice-control/
├── src/
│   ├── extension.ts           # Main extension entry point
│   ├── services/
│   │   ├── VoiceControlManager.ts   # Orchestrates voice control
│   │   ├── SpeechService.ts         # Handles speech recognition
│   │   ├── CommandService.ts        # Executes commands
│   │   └── ConfigurationService.ts  # Manages settings
│   └── ui/
│       └── VoiceControlPanel.ts     # Webview interface
├── package.json               # Extension manifest
├── tsconfig.json             # TypeScript configuration
├── README.md                 # User documentation
└── SETUP.md                  # This file
```

## Key Components

### VoiceControlManager
- Orchestrates all voice control functionality
- Manages different modes (dictation, voice agent, single command)
- Handles state transitions and error recovery

### SpeechService
- Integrates with Deepgram for real-time speech recognition
- Manages microphone access and audio streaming
- Provides microphone testing functionality

### CommandService
- Maps voice commands to VS Code actions
- Uses OpenAI for intelligent command interpretation
- Improves dictated text using AI

### ConfigurationService
- Manages all extension settings
- Validates configuration
- Provides configuration summary for UI

## Common Issues

### TypeScript Errors

**"Cannot find module 'vscode'"**
- Install VS Code extension types: `npm install @types/vscode`
- Ensure proper TypeScript configuration

**Module resolution errors**
- Check `tsconfig.json` paths configuration
- Verify all dependencies are installed

### Extension Loading

**Extension not appearing**
- Check `package.json` activation events
- Ensure proper compilation (`npm run compile`)
- Restart VS Code development host

### API Issues

**Deepgram connection errors**
- Verify API key is correct
- Check account credits
- Ensure network connectivity

**OpenAI rate limits**
- Check usage limits in OpenAI dashboard
- Implement proper error handling
- Consider using different models

## Performance Optimization

### Audio Processing
- Use appropriate sample rates (16kHz recommended)
- Implement proper buffering
- Handle WebRTC constraints properly

### API Calls
- Implement request queuing
- Add retry logic with exponential backoff
- Cache responses where appropriate

### Memory Management
- Dispose of event emitters properly
- Clean up audio contexts
- Remove event listeners on deactivation

## Security Considerations

### API Keys
- Store in VS Code secure storage
- Never log or expose in plaintext
- Validate format before use

### Audio Data
- Stream audio directly to API
- Don't store audio locally
- Use secure WebSocket connections

### Permissions
- Request minimal microphone permissions
- Provide clear privacy notices
- Allow users to revoke access

## Contributing

1. **Fork** the repository
2. **Create** a feature branch
3. **Implement** your changes
4. **Test** thoroughly
5. **Submit** a pull request

### Code Style
- Use TypeScript strict mode
- Follow VS Code extension patterns
- Add JSDoc comments for public APIs
- Use async/await for asynchronous operations

### Pull Request Process
1. Update documentation
2. Add tests for new features
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Request review

## Support

- **Documentation**: Check README.md and wiki
- **Issues**: Report bugs with detailed reproduction steps
- **Discussions**: Ask questions and share ideas
- **Email**: Contact maintainers for security issues 