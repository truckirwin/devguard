# Cursor Voice Control

A native voice control extension for Cursor IDE that enables hands-free coding through AI-powered speech recognition and command interpretation.

## Features

🎤 **Voice Commands**: Execute common editor actions with natural speech  
✏️ **Intelligent Dictation**: Convert speech to code with AI-powered text improvement  
🧠 **AI-Powered Interpretation**: Uses OpenAI to understand context and intent  
⚡ **Real-time Recognition**: Powered by Deepgram for fast, accurate speech-to-text  
🔄 **Continuous Listening**: Optional always-on voice control mode  
🎯 **Code Context Awareness**: Adapts to current file type and context  

## Installation

### Prerequisites

1. **Deepgram API Key**: Sign up at [Deepgram](https://deepgram.com) for speech recognition
2. **OpenAI API Key**: Get one from [OpenAI](https://openai.com) for AI assistance (optional but recommended)

### Install Extension

1. Download the `.vsix` file from releases
2. In Cursor, run: `Extensions: Install from VSIX...`
3. Select the downloaded file
4. Reload Cursor

## Setup

1. **Configure API Keys**:
   - Open Command Palette (`Cmd/Ctrl+Shift+P`)
   - Run `Cursor Voice: Configure API Keys`
   - Enter your Deepgram and OpenAI API keys

2. **Test Your Setup**:
   - Run `Cursor Voice: Test Microphone`
   - Grant microphone permissions when prompted

3. **Start Voice Control**:
   - Press `Cmd/Ctrl+Shift+V` or run `Cursor Voice: Start Voice Agent`

## Usage

### Voice Commands

| Command | Action |
|---------|--------|
| "open file" | Opens file dialog |
| "save file" | Saves current file |
| "new file" | Creates new file |
| "close file" | Closes current file |
| "go to line [number]" | Navigates to specific line |
| "find [text]" | Searches in current file |
| "replace" | Opens find and replace |
| "toggle sidebar" | Shows/hides sidebar |
| "open terminal" | Opens terminal |
| "run code" | Executes current file |
| "format code" | Formats the document |
| "comment" | Toggles line comments |
| "copy line" | Duplicates current line |
| "delete line" | Deletes current line |
| "select all" | Selects all text |

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Cmd/Ctrl+Shift+V` | Start Voice Agent |
| `Cmd/Ctrl+Shift+D` | Toggle Dictation Mode |
| `Cmd/Ctrl+Alt+V` | Execute Single Voice Command |
| `Alt+Space` | Toggle Continuous Listening |

### Modes

**Voice Agent Mode**: Continuous listening for commands and natural language requests.
```
Press Cmd/Ctrl+Shift+V → "Hey Cursor, create a new Python file"
```

**Dictation Mode**: Convert speech directly to text with AI improvement.
```
Press Cmd/Ctrl+Shift+D → "function calculate sum parentheses x comma y parentheses"
```

## Configuration

Access settings via `Cursor Voice Control Panel` or directly in settings:

- **Language**: Speech recognition language (default: en-US)
- **Sensitivity**: Voice activation threshold (0.1-1.0)
- **Continuous Listening**: Always-on voice control
- **AI Assistance**: Enhanced command interpretation
- **Code Context**: Use file context for better recognition

## Advanced Features

### AI-Powered Text Improvement

When dictating code, the extension uses AI to:
- Fix speech recognition errors
- Convert spoken programming terms to proper syntax
- Add appropriate formatting and punctuation
- Apply language-specific conventions

### Context-Aware Commands

The extension understands your current coding context:
- File type and language
- Current cursor position
- Selected text
- Nearby code lines

This allows for more intelligent command interpretation and text processing.

### Custom Voice Commands

Customize voice commands in settings:

```json
{
  "cursorVoice.voiceCommands": {
    "openFile": ["open file", "open document"],
    "customCommand": ["my custom phrase", "alternative phrase"]
  }
}
```

## Troubleshooting

### Microphone Issues

1. **Permission Denied**: Grant microphone access in system settings
2. **No Audio Detected**: Check microphone levels and settings
3. **Poor Recognition**: Adjust sensitivity or try different microphone

### API Issues

1. **Deepgram Errors**: Verify API key and account credits
2. **OpenAI Errors**: Check API key and usage limits
3. **Network Issues**: Ensure stable internet connection

### Common Solutions

- **Restart Extension**: Disable and re-enable the extension
- **Reload Window**: `Cmd/Ctrl+Shift+P` → "Developer: Reload Window"
- **Check Logs**: View "Output" panel → "Cursor Voice Control"

## Privacy & Security

- **Audio Processing**: Audio is processed through Deepgram's secure APIs
- **API Keys**: Stored securely in VS Code settings
- **No Recording**: Audio is streamed in real-time, not recorded or stored
- **Local Processing**: Command interpretation happens locally when possible

## Development

### Building from Source

```bash
git clone <repository>
cd cursor-voice-control
npm install
npm run compile
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

- **Issues**: Report bugs on GitHub
- **Feature Requests**: Open a discussion
- **Documentation**: Check the wiki for detailed guides

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- Inspired by [Vibe Coder](https://github.com/vibe-coder/vibe-coder) for VS Code
- Built for the Cursor IDE ecosystem
- Uses Deepgram for speech recognition and OpenAI for AI assistance 