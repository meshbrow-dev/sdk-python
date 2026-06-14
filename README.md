# Meshbrow Python SDK

The official Python SDK for [Meshbrow](https://meshbrow.dev) — Managed Browser Fleet for AI Agents.

## Installation

```bash
pip install meshbrow
```

## Quick Start

```python
from meshbrow import Meshbrow

client = Meshbrow(api_key="your-api-key")

# Launch a stealth browser session
session = client.create_session(
    stealth="max",
    proxy_type="residential",
    proxy_country="US",
)

# Navigate and interact
client.navigate(session.id, "https://example.com")
content = client.extract(session.id)
screenshot = client.screenshot(session.id)

# Clean up
client.destroy_session(session.id)
client.close()
```

## Context Manager

```python
with Meshbrow(api_key="your-api-key") as client:
    session = client.create_session()
    client.navigate(session.id, "https://example.com")
    client.destroy_session(session.id)
```

## Fleet Operations

```python
fleet = client.create_fleet(
    count=10,
    proxy_type="residential",
    proxy_country="US",
)

for session in fleet.sessions:
    client.navigate(session.id, "https://example.com")

client.destroy_fleet(fleet.id)
```

## API Reference

### `Meshbrow(api_key, base_url="https://api.meshbrow.dev")`

| Method | Description |
|--------|-------------|
| `create_session(...)` | Launch a stealth browser session |
| `get_session(id)` | Get session details |
| `list_sessions()` | List all active sessions |
| `destroy_session(id)` | Destroy a session |
| `navigate(id, url)` | Navigate to URL |
| `screenshot(id)` | Take a screenshot |
| `click(id, selector)` | Click an element |
| `type_text(id, selector, text)` | Type into an input |
| `extract(id)` | Extract page text |
| `execute(id, script)` | Run JavaScript |
| `create_fleet(count)` | Launch multiple sessions |
| `destroy_fleet(id)` | Destroy a fleet |

## License

MIT
