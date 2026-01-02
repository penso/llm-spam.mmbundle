# LLM Spam & Phishing Detector for MailMate

A MailMate bundle that uses Large Language Models (LLMs) to detect spam and phishing emails.

## Features

- Classify emails as spam using any OpenAI-compatible LLM API
- Detect phishing and hacking attempts with a specialized prompt
- Supports OpenAI, Ollama, LM Studio, and other compatible endpoints
- API key stored securely in macOS Keychain
- Option to move detected threats to Junk folder

## Installation

### Option 1: Symlink (for development)

```bash
ln -s /path/to/llm-mailguard.mmbundle ~/Library/Application\ Support/MailMate/Bundles/
```

### Option 2: Copy

```bash
cp -r llm-mailguard.mmbundle ~/Library/Application\ Support/MailMate/Bundles/
```

After installation, restart MailMate.

## Configuration

1. In MailMate, go to **Command > LLM MailGuard > Configure...**
2. Enter your LLM provider details:
   - **Provider Name**: A friendly name (e.g., "OpenAI", "Ollama")
   - **Endpoint URL**: The API endpoint
   - **Model**: The model name to use
   - **API Key**: Your API key (stored in macOS Keychain)

### Example Configurations

#### OpenAI

- Endpoint: `https://api.openai.com/v1/chat/completions`
- Model: `gpt-5.2` or other recent models
- API Key: Your OpenAI API key

#### Anthropic (via OpenAI-compatible endpoint)

- Endpoint: `https://api.anthropic.com/v1/messages`
- Model: `claude-3-haiku-20240307`
- API Key: Your Anthropic API key

Note: Anthropic's native API format differs slightly. For best results, use an OpenAI-compatible proxy or wrapper.

#### Ollama (local)

- Endpoint: `http://localhost:11434/v1/chat/completions`
- Model: `llama3.2` or any model you have installed
- API Key: (leave empty)

#### LM Studio (local)

- Endpoint: `http://localhost:1234/v1/chat/completions`
- Model: The model name loaded in LM Studio
- API Key: (leave empty)

## Usage

1. Select an email in MailMate
2. Choose a detection method:
   - Press `Ctrl+L` or go to **Command > LLM MailGuard > Is it spam?** for general spam detection
   - Press `Ctrl+Shift+L` or go to **Command > LLM MailGuard > Is it phishing?** for phishing/hacking detection
3. For each email, the LLM will analyze it and report:
   - If **threat detected**: You'll be asked if you want to move it to Junk
   - If **safe**: A notification will confirm it appears legitimate

The phishing detector uses a more targeted prompt that reduces false positives on legitimate emails like password resets, security alerts, and order confirmations.

**Note**: The command processes one email at a time.

## How It Works

The bundle sends the complete raw email (all headers and body) to the LLM with a prompt asking it to classify the email as spam or not. The LLM considers:

- Suspicious sender addresses or domains
- Phishing attempts
- Unsolicited commercial content
- Scam patterns
- Spoofed headers
- Social engineering tactics

## Keyboard Shortcuts

- `Ctrl+L` - Check selected email(s) for spam
- `Ctrl+Shift+L` - Check selected email(s) for phishing

## Files

```
llm-mailguard.mmbundle/
├── info.plist                     # Bundle metadata
├── Commands/
│   ├── Configure.mmCommand        # Configuration dialog
│   ├── Is it spam.mmCommand       # Spam check command
│   └── Is it phishing.mmCommand   # Phishing check command
├── Support/
│   └── bin/
│       ├── llm_common.py          # Shared utilities
│       ├── configure              # Configuration script
│       ├── check_spam             # Spam detection script
│       └── check_phishing         # Phishing detection script
└── README.md
```

## Configuration Storage

- **Settings**: `~/Library/Application Support/MailMate/LLMMailGuard/config.json`
- **API Key**: macOS Keychain (service: `com.freron.MailMate.LLMMailGuard`)

## Troubleshooting

### "Not configured" error

Run **Command > LLM MailGuard > Configure...** to set up your LLM provider.

### API errors

- Check that your endpoint URL is correct
- Verify your API key is valid
- For local endpoints (Ollama, LM Studio), ensure the server is running

### No response from LLM

- The email might be too long; it will be truncated at ~30,000 characters
- Check your network connection
- Verify the model name is correct for your provider

### Debug mode

Launch MailMate from Terminal to see script output:

```bash
/Applications/MailMate.app/Contents/MacOS/MailMate
```

Enable debug output:

```bash
defaults write com.freron.MailMate MmDebugCommands -bool YES
```

## Privacy & Security

- Your API key is stored in macOS Keychain, not in plain text
- Email content is sent to your configured LLM provider for analysis
- For maximum privacy, use a local LLM (Ollama, LM Studio)

## License

MIT License. See [LICENSE](LICENSE) for details.
