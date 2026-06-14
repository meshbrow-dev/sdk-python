# Meshbrow Python SDK

The official Python SDK for [Meshbrow](https://meshbrow.dev) — persistent browser infrastructure for AI agents.

Launch cloud browsers that remember logins, stay undetected, and scale to hundreds of concurrent sessions. Connect via CDP (Playwright/Puppeteer) or use built-in helpers.

## Installation

```bash
pip install meshbrow
```

## Quick Start

```python
from meshbrow import Meshbrow

client = Meshbrow(api_key="mb_your_api_key")

# Launch a cloud browser with US residential proxy
session = client.create_session(
    stealth="max",
    proxy_type="residential",
    proxy_country="US",
    viewport={"width": 1920, "height": 1080},
)

# Connect via CDP endpoint with Playwright
print(session.cdp_endpoint)  # wss://cdp.meshbrow.dev/...

# Or use built-in helpers
client.navigate(session.id, "https://example.com")
screenshot = client.screenshot(session.id)
content = client.extract(session.id, selector="h1")

# Clean up
client.destroy_session(session.id)
client.close()
```

## Usage with Playwright

```python
from playwright.sync_api import sync_playwright
from meshbrow import Meshbrow

client = Meshbrow(api_key="mb_your_api_key")
session = client.create_session(stealth="max")

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(session.cdp_endpoint)
    page = browser.new_page()
    page.goto("https://example.com")
    page.screenshot(path="screenshot.png")
    browser.close()

client.destroy_session(session.id)
client.close()
```

## Async Client

```python
import asyncio
from meshbrow import AsyncMeshbrow

async def main():
    client = AsyncMeshbrow(api_key="mb_your_api_key")

    session = await client.create_session(
        stealth="max",
        proxy_type="residential",
        proxy_country="US",
    )

    await client.navigate(session.id, "https://example.com")
    screenshot = await client.screenshot(session.id)

    await client.destroy_session(session.id)
    await client.close()

asyncio.run(main())
```

## Context Manager

```python
with Meshbrow(api_key="mb_your_api_key") as client:
    session = client.create_session()
    client.navigate(session.id, "https://example.com")
    client.destroy_session(session.id)

# Async
async with AsyncMeshbrow(api_key="mb_your_api_key") as client:
    session = await client.create_session()
    await client.navigate(session.id, "https://example.com")
    await client.destroy_session(session.id)
```

## Built-in Helpers

### Navigate

```python
client.navigate(session.id, "https://example.com", wait_until="networkidle")
```

### Screenshot

```python
# Full page screenshot
shot = client.screenshot(session.id, full_page=True)
# shot.data is base64-encoded PNG

# Element screenshot
shot = client.screenshot(session.id, selector="#hero")
```

### Extract Content

```python
content = client.extract(session.id, selector="article", max_length=10000)
```

### Click & Type

```python
client.click(session.id, "#login-button")
client.type_text(session.id, "#email", "user@example.com")
client.type_text(session.id, "#password", "secret", clear=True)
```

### Execute JavaScript

```python
result = client.execute(session.id, "return document.title")
print(result["result"])  # "Example Domain"
```

## Fleet Operations

```python
# Launch 10 sessions in parallel
fleet = client.create_fleet(
    count=10,
    stealth="max",
    proxy_type="residential",
    proxy_country="US",
)

print(fleet.id)       # "fleet_abc123"
print(fleet.count)    # 10

for session in fleet.sessions:
    client.navigate(session.id, "https://example.com")

# Destroy all sessions in the fleet
client.destroy_fleet(fleet.id)
```

## Session Management

```python
# List all active sessions
session_list = client.list_sessions()
for s in session_list.sessions:
    print(f"{s.id}: {s.status}")

# Get session details
session = client.get_session("mb_abc123")
print(session.status)       # "running"
print(session.cdp_endpoint) # "wss://..."

# Destroy with profile save
client.destroy_session(session.id, save_profile=True)
```

## Configuration

```python
client = Meshbrow(
    api_key="mb_your_api_key",                   # Required
    base_url="https://api.meshbrow.dev",         # Optional (default)
    timeout=30.0,                                # Request timeout in seconds (default: 30)
)
```

## Session Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `stealth` | `str` | `"max"` | Anti-detection level: `"none"`, `"basic"`, `"max"` |
| `proxy_type` | `str` | `None` | `"residential"`, `"datacenter"`, `"isp"`, `"mobile"` |
| `proxy_country` | `str` | `None` | ISO 3166-1 alpha-2 country code |
| `profile_id` | `str` | `None` | Persist cookies/storage across sessions |
| `viewport` | `dict` | `None` | `{"width": 1920, "height": 1080}` |

## Error Handling

```python
import httpx
from meshbrow import Meshbrow

client = Meshbrow(api_key="mb_your_api_key")

try:
    session = client.create_session()
except httpx.HTTPStatusError as e:
    if e.response.status_code == 401:
        print("Invalid API key")
    elif e.response.status_code == 429:
        print("Rate limited — back off")
    elif e.response.status_code == 402:
        print("Quota exceeded")
    else:
        print(f"API error: {e.response.status_code}")
```

## Types

```python
from meshbrow import Session, SessionList, Screenshot, Fleet

# Session
session.id            # str — "mb_abc123"
session.status        # str — "running" | "stopped" | "error"
session.cdp_endpoint  # str — "wss://cdp.meshbrow.dev/..."
session.stealth       # str — "max"
session.proxy         # dict | None
session.created_at    # str — ISO 8601
session.expires_at    # str — ISO 8601

# Screenshot
screenshot.data       # str — base64-encoded PNG
screenshot.format     # str — "png"

# Fleet
fleet.id              # str — "fleet_abc123"
fleet.status          # str
fleet.sessions        # list[Session]
fleet.count           # int
```

## Documentation

Full docs: [docs.meshbrow.dev](https://docs.meshbrow.dev)  
SDK guide: [docs.meshbrow.dev/quickstart](https://docs.meshbrow.dev/quickstart)

## License

MIT © [Bytangle Ltd](https://bytangle.com)
