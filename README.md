# burp-wrapper

Python wrapper for the Burp Suite MCP Server API. Gives AI agents (Claude Code, Gemini CLI, etc.) full programmatic access to every Burp Suite Pro tool.

```python
from burp_wrapper import BurpClient

with BurpClient(target="target.com") as burp:
    # Browse proxy history
    history = burp.proxy.get_history(limit=50, filter_host="target.com")

    # Replay a request
    response = burp.repeater.send(request_id="req-1")

    # Fuzz a parameter
    results = burp.intruder.quick_fuzz(
        request_id="req-1",
        param_name="username",
        payloads=["admin", "test", "' OR 1=1--"],
    )

    # Out-of-band testing
    collab = burp.collaborator.generate_payload()
    burp.repeater.send_modified("req-1", modifications={
        "headers": {"X-Forwarded-For": f"http://{collab['payload']}"}
    })
    interactions = burp.collaborator.poll_until(collab["interaction_id"])

    if interactions["found"]:
        burp.session.log_finding({
            "name": "SSRF via X-Forwarded-For",
            "severity": "high",
            "url": "https://target.com/api/fetch",
            "evidence": interactions
        })

# Session report generated automatically on exit
```

## Requirements

- Python 3.11+
- Burp Suite Pro with the [MCP Server extension](https://portswigger.net/burp/documentation/desktop/extensions) running on `localhost:9876`

## Install

```bash
pip install burp-wrapper
```

Or from source:

```bash
git clone https://github.com/momomuchu/burp-wrapper.git
cd burp-wrapper
pip install -e ".[dev]"
```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  AI AGENT                            │
│          (Claude Code / Gemini CLI / etc.)           │
│                                                      │
│  from burp_wrapper import BurpClient                │
└────────────────────────┬────────────────────────────┘
                         │
                         │  Python method calls
                         v
┌─────────────────────────────────────────────────────┐
│              BURP WRAPPER                            │
│                                                      │
│  BurpClient                                          │
│    .proxy     .repeater    .intruder    .scanner     │
│    .decoder   .collaborator .target    .sequencer    │
│    .comparer  .logger      .dashboard  .engagement   │
│    .organizer .search      .inspector  .extensions   │
│    .config    .clickbandit                           │
│                                                      │
│  SessionLogger  ->  JSONL logs + markdown reports    │
│  BurpTransport  ->  JSON-RPC 2.0 over HTTP          │
└────────────────────────┬────────────────────────────┘
                         │
                         │  POST /message (JSON-RPC 2.0)
                         v
┌─────────────────────────────────────────────────────┐
│          BURP SUITE PRO + MCP SERVER                 │
│                                                      │
│  PortSwigger official extension on :9876             │
│  Exposes Burp tools via MCP protocol                 │
└─────────────────────────────────────────────────────┘
```

## Features

### Session Logging

Every action is automatically logged to JSONL files for replay, debugging, and reporting.

```python
with BurpClient(target="example.com", log_dir="./logs") as burp:
    burp.proxy.get_history()
    burp.repeater.send(request_id="req-1")

    # Log a vulnerability finding
    burp.session.log_finding({
        "name": "SQL Injection",
        "severity": "high",
        "url": "https://example.com/login",
        "detail": "Error-based SQLi in username parameter"
    })

    # Export report anytime
    report = burp.export_report("markdown")
```

Session files:
```
logs/sessions/
  20260310_143022_example_com.jsonl   # Every action + finding
  20260310_143022_summary.json         # Session summary
```

Sensitive parameters (passwords, tokens, cookies) are automatically redacted in logs.

### Context Manager

```python
# Automatic cleanup: session report generated on exit
with BurpClient(target="target.com") as burp:
    ...

# Or manual lifecycle
burp = BurpClient(target="target.com")
# ... do work ...
burp.end_session()
burp.close()
```

### Exception Hierarchy

```python
from burp_wrapper import (
    BurpWrapperError,         # Base exception
    BurpAPIError,             # API returned an error
    BurpConnectionError,      # Can't connect to Burp
    NotImplementedInBurpMCP,  # Feature not in official MCP Server
    SessionError,             # Logging error
)
```

## Tools Covered

| Tool | Methods | MCP Support |
|------|---------|-------------|
| **Proxy** | `get_history`, `get_request`, `get_websocket_history`, `intercept_*`, `add_match_replace_rule` | Direct |
| **Repeater** | `send`, `send_modified`, `send_batch`, `create_tab` | Direct |
| **Intruder** | `create_attack`, `start`, `quick_fuzz`, `status`, `results`, `pause`, `resume`, `stop` | Partial |
| **Scanner** | `crawl`, `audit`, `crawl_and_audit`, `status`, `issues`, `pause`, `resume`, `stop`, `get_issue_definitions` | Needs extension |
| **Decoder** | `encode`, `decode`, `smart_decode`, `hash`, `hash_all` | Partial |
| **Collaborator** | `generate_payload`, `generate_payloads`, `poll`, `poll_until` | Direct |
| **Target** | `get_sitemap`, `get_scope`, `set_scope`, `add_to_scope`, `is_in_scope`, `get_issues` | Partial |
| **Dashboard** | `get_tasks`, `get_issues_summary` | Direct |
| **Sequencer** | `start_live_capture`, `capture_status`, `analyze`, `analyze_manual`, `results` | Needs extension |
| **Comparer** | `diff`, `diff_responses` | Needs extension |
| **Logger** | `query`, `annotate`, `export` | Needs extension |
| **Inspector** | `parse_request`, `parse_response`, `build_request` | Needs extension |
| **Engagement** | `analyze_target`, `discover_content`, `content_discovery_results`, `generate_csrf_poc` | Needs extension |
| **Search** | `find` | Needs extension |
| **Config** | `get_project`, `get_user`, `export_project`, `import_project` | Direct |
| **Organizer** | `add`, `list`, `annotate`, `get_collections`, `create_collection` | Needs extension |
| **Extensions** | `list`, `enable`, `disable`, `reload` | Needs extension |
| **Clickbandit** | `generate` | Needs extension |

**18 tools, 70+ methods.**

**MCP Support legend:**
- **Direct** -- Supported by the official PortSwigger MCP Server
- **Partial** -- Some methods supported, others need extension
- **Needs extension** -- Requires forking the MCP Server or a custom Burp extension

## Usage Examples

### Scan a target

```python
burp = BurpClient()
burp.target.add_to_scope("https://target.com")

scan = burp.scanner.crawl_and_audit("https://target.com", config={
    "crawl_strategy": "most_complete",
    "audit_optimization": "thorough",
})

status = burp.scanner.status(scan["scan_id"])
print(f"Progress: {status['audit_progress']['percentage']}%")

issues = burp.scanner.issues(scan_id=scan["scan_id"], filters={"severity": "high"})
```

### Intercept and modify traffic

```python
burp.proxy.intercept_toggle(True)

msg = burp.proxy.intercept_get_message()
if msg["has_message"]:
    modified = msg["message"]["raw"].replace("User-Agent: Chrome", "User-Agent: Bot")
    burp.proxy.intercept_forward(msg["message"]["id"], modified_raw=modified)
```

### Compare responses for access control testing

```python
admin_resp = burp.repeater.send_modified("req-1", modifications={
    "headers": {"Cookie": "session=admin_token"}
})
user_resp = burp.repeater.send_modified("req-1", modifications={
    "headers": {"Cookie": "session=user_token"}
})

diff = burp.comparer.diff(
    request_id_1=admin_resp["new_request_id"],
    request_id_2=user_resp["new_request_id"],
    options={"compare": "response"}
)
print(f"Similarity: {diff['similarity_percentage']}%")
```

### SSRF detection with Collaborator

```python
with BurpClient(target="target.com") as burp:
    collab = burp.collaborator.generate_payload()

    burp.repeater.send_modified("req-1", modifications={
        "headers": {"X-Forwarded-For": f"http://{collab['payload']}"}
    })

    result = burp.collaborator.poll_until(collab["interaction_id"], timeout_seconds=30)

    if result["found"]:
        burp.session.log_finding({
            "name": "SSRF via X-Forwarded-For",
            "severity": "high",
            "url": "https://target.com/api/fetch",
            "evidence": result
        })
```

### Token randomness analysis

```python
result = burp.sequencer.analyze_manual([
    "abc123", "def456", "ghi789",  # ... 200+ tokens
])
analysis = burp.sequencer.results(result["analysis_id"])
print(f"Entropy: {analysis['effective_entropy_bits']} bits")
print(f"FIPS: {'PASS' if analysis['fips_tests']['overall_passed'] else 'FAIL'}")
```

## Configuration

```python
# Custom host/port
burp = BurpClient(base_url="http://192.168.1.100:9876")

# Custom timeout (seconds)
burp = BurpClient(timeout=60.0)

# Disable logging
burp = BurpClient(enable_logging=False)

# Custom log directory
burp = BurpClient(target="example.com", log_dir="/tmp/burp-logs")
```

## Development

```bash
pip install -e ".[dev]"

# Run tests (146 tests, no Burp instance needed)
pytest -v

# Lint
ruff check src/ tests/
```

## Project Structure

```
src/burp_wrapper/
    __init__.py              # Public API exports
    client.py                # BurpClient with context manager + session logging
    transport.py             # JSON-RPC 2.0 transport layer
    exceptions.py            # Exception hierarchy
    session_logger.py        # JSONL action logging + markdown reports
    tools/
        base.py              # BaseTools with auto-logging + _not_implemented
        proxy.py             # 7 methods
        repeater.py          # 4 methods
        intruder.py          # 7 methods
        scanner.py           # 9 methods
        decoder.py           # 5 methods
        collaborator.py      # 4 methods
        target.py            # 6 methods
        sequencer.py         # 5 methods
        comparer.py          # 2 methods
        logger.py            # 3 methods
        dashboard.py         # 2 methods
        organizer.py         # 5 methods
        search.py            # 1 method
        inspector.py         # 3 methods
        engagement.py        # 4 methods
        extensions.py        # 4 methods
        config.py            # 4 methods
        clickbandit.py       # 1 method

tests/                       # 146 tests
```

## License

MIT
