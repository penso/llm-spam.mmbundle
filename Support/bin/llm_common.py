#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Common utilities for LLM email classification tools.
"""

import json
import os
import subprocess
import urllib.request
import urllib.error

# Configuration paths
CONFIG_DIR = os.path.expanduser("~/Library/Application Support/MailMate/LLMMailGuard")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
KEYCHAIN_SERVICE = "com.freron.MailMate.LLMMailGuard"
KEYCHAIN_ACCOUNT = "llm-mailguard-api-key"
MAILMATE_ICON = "/Applications/MailMate.app/Contents/Resources/MailMate.icns"

# Default configuration values
DEFAULT_PROVIDER = "OpenAI"
DEFAULT_ENDPOINT = "https://api.openai.com/v1/chat/completions"
DEFAULT_MODEL = "gpt-5.2"


def run_applescript(script):
    """Run AppleScript and return the result."""
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return None
        return result.stdout.strip()
    except Exception:
        return None


def escape_for_applescript(text):
    """Escape text for use in AppleScript strings."""
    text = text.replace("\\", "\\\\")
    text = text.replace('"', '\\"')
    return text


def show_alert(message, title="LLM MailGuard"):
    """Show an AppleScript alert (blocking) with MailMate icon."""
    message = escape_for_applescript(message)
    title = escape_for_applescript(title)
    script = f'''
    set iconPath to POSIX file "{MAILMATE_ICON}"
    tell application "System Events"
        display dialog "{message}" with title "{title}" buttons {{"OK"}} default button "OK" with icon iconPath
    end tell
    '''
    run_applescript(script)


def show_dialog(message, default_answer="", hidden=False, title="LLM MailGuard"):
    """Show an AppleScript input dialog with MailMate icon."""
    message = escape_for_applescript(message)
    default_answer = escape_for_applescript(default_answer)
    title = escape_for_applescript(title)
    hidden_str = "with hidden answer" if hidden else ""
    script = f'''
    set iconPath to POSIX file "{MAILMATE_ICON}"
    tell application "System Events"
        set dialogResult to display dialog "{message}" default answer "{default_answer}" {hidden_str} buttons {{"Cancel", "OK"}} default button "OK" with title "{title}" with icon iconPath
        return text returned of dialogResult
    end tell
    '''
    return run_applescript(script)


def show_threat_dialog(threat_type, reason, title):
    """Show dialog asking if user wants to move detected threat to Junk. Returns True if yes."""
    reason = escape_for_applescript(reason)
    title = escape_for_applescript(title)
    script = f'''
    set iconPath to POSIX file "{MAILMATE_ICON}"
    tell application "System Events"
        set dialogResult to display dialog "{threat_type}

Reason: {reason}

Move to Junk folder?" buttons {{"Keep", "Move to Junk"}} default button "Move to Junk" with title "{title}" with icon iconPath
        return button returned of dialogResult
    end tell
    '''
    result = run_applescript(script)
    return result == "Move to Junk"


def load_config():
    """Load configuration from JSON file."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return None


def save_config(config):
    """Save configuration to JSON file."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def get_api_key_from_keychain():
    """Retrieve API key from macOS Keychain."""
    try:
        result = subprocess.run(
            [
                "/usr/bin/security",
                "find-generic-password",
                "-a", KEYCHAIN_ACCOUNT,
                "-s", KEYCHAIN_SERVICE,
                "-w"
            ],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def save_api_key_to_keychain(api_key):
    """Save API key to macOS Keychain."""
    # First try to delete any existing entry
    subprocess.run(
        [
            "/usr/bin/security",
            "delete-generic-password",
            "-a", KEYCHAIN_ACCOUNT,
            "-s", KEYCHAIN_SERVICE
        ],
        capture_output=True
    )
    
    # Add the new entry
    result = subprocess.run(
        [
            "/usr/bin/security",
            "add-generic-password",
            "-a", KEYCHAIN_ACCOUNT,
            "-s", KEYCHAIN_SERVICE,
            "-w", api_key,
            "-U"
        ],
        capture_output=True
    )
    return result.returncode == 0


def call_llm_api(endpoint, model, api_key, system_prompt, email_content):
    """Call the LLM API and return the response text."""
    headers = {
        "Content-Type": "application/json",
    }
    
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    # Truncate email if too long (most APIs have token limits)
    max_chars = 30000  # Conservative limit
    if len(email_content) > max_chars:
        email_content = email_content[:max_chars] + "\n\n[... truncated due to length ...]"
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": email_content}
        ],
        "max_completion_tokens": 256,
        "temperature": 0.1  # Low temperature for more consistent classification
    }
    
    data = json.dumps(payload).encode("utf-8")
    
    req = urllib.request.Request(endpoint, data=data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))
            # Handle OpenAI-compatible response format
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            return None
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        raise Exception(f"API error {e.code}: {error_body}")
    except urllib.error.URLError as e:
        raise Exception(f"Connection error: {e.reason}")


def output_actions(actions=None):
    """Print JSON actions for MailMate."""
    if actions is None:
        actions = []
    print(json.dumps({"actions": actions}))


def move_to_junk_action():
    """Return the action to move a message to Junk."""
    return {"type": "moveMessage", "mailboxType": "junk"}
