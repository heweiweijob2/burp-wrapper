# burp-rest-extension

Burp Suite extension that exposes the entire Montoya API via REST HTTP. Load the JAR into Burp and get a full REST API on `http://127.0.0.1:8089`.

Built for AI agents (Claude Code, Gemini CLI, etc.) and automation scripts.

```bash
# Health check
curl http://127.0.0.1:8089/health

# Get proxy history
curl http://127.0.0.1:8089/proxy/history?limit=10

# Send a request via Repeater
curl -X POST http://127.0.0.1:8089/repeater/send \
  -H "Content-Type: application/json" \
  -d '{"request":{"method":"GET","url":"https://target.com/api"}}'

# Quick fuzz a parameter
curl -X POST http://127.0.0.1:8089/intruder/quick-fuzz \
  -H "Content-Type: application/json" \
  -d '{"requestId":0,"param":"id","payloads":["1","2","'\''OR 1=1--"]}'

# Generate Collaborator payload
curl -X POST http://127.0.0.1:8089/collaborator/generate

# Start a scan
curl -X POST http://127.0.0.1:8089/scanner/crawl-and-audit \
  -H "Content-Type: application/json" \
  -d '{"url":"https://target.com"}'
```

## Requirements

- Burp Suite Pro
- Java 17+

## Install

```bash
# Build from source
./gradlew shadowJar

# Output: build/libs/burp-rest-extension.jar
```

In Burp: **Extensions → Add → Extension Type: Java → Select JAR**

The API starts automatically on `http://127.0.0.1:8089`.

## Architecture

```
┌────────────────────────────────────────────────────────┐
│                    AI AGENT / SCRIPT                    │
│           (Claude Code / Gemini CLI / curl / etc.)      │
└────────────────────────┬───────────────────────────────┘
                         │
                         │  REST HTTP (JSON)
                         v
┌────────────────────────────────────────────────────────┐
│              BURP REST EXTENSION                        │
│                                                         │
│  Ktor Embedded Server on :8089                          │
│                                                         │
│  /proxy/*        /repeater/*      /intruder/*           │
│  /scanner/*      /collaborator/*  /target/*             │
│  /decoder/*      /sequencer/*     /comparer/*           │
│  /logger/*       /config/*        /extensions           │
│  /search         /health          /docs                 │
│                                                         │
│  Request logging → Burp output console                  │
│  Error handling  → JSON error responses                 │
│  CORS enabled    → local access from any origin         │
└────────────────────────┬───────────────────────────────┘
                         │
                         │  Montoya API (direct)
                         v
┌────────────────────────────────────────────────────────┐
│                  BURP SUITE PRO                         │
│                                                         │
│  Proxy · Repeater · Intruder · Scanner                  │
│  Collaborator · Target · Decoder · Sequencer            │
│  Comparer · Logger · Config · Extensions                │
└────────────────────────────────────────────────────────┘
```

## Endpoints

### Core (P0)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/version` | Extension version |
| GET | `/docs` | OpenAPI spec |

### Proxy

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/proxy/history` | List captured requests (`?limit=N&offset=N&host=X`) |
| GET | `/proxy/history/{id}` | Detail of a specific request |
| GET | `/proxy/websocket/history` | WebSocket history |
| POST | `/proxy/intercept/enable` | Enable interception |
| POST | `/proxy/intercept/disable` | Disable interception |
| POST | `/proxy/intercept/forward` | Forward intercepted request |
| POST | `/proxy/intercept/drop` | Drop intercepted request |

### Repeater

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/repeater/send` | Send a request |
| POST | `/repeater/send/batch` | Send multiple requests |
| POST | `/repeater/tab/create` | Create Repeater tab |

### Intruder

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/intruder/attack/create` | Configure an attack |
| POST | `/intruder/attack/{id}/start` | Start attack |
| GET | `/intruder/attack/{id}/status` | Attack status |
| GET | `/intruder/attack/{id}/results` | Attack results |
| POST | `/intruder/attack/{id}/pause` | Pause |
| POST | `/intruder/attack/{id}/resume` | Resume |
| POST | `/intruder/attack/{id}/stop` | Stop |
| POST | `/intruder/quick-fuzz` | Quick fuzz a parameter |

### Scanner

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/scanner/crawl` | Start crawl |
| POST | `/scanner/audit` | Start audit |
| POST | `/scanner/crawl-and-audit` | Start crawl + audit |
| GET | `/scanner/{id}/status` | Scan status |
| GET | `/scanner/{id}/issues` | Found issues |
| POST | `/scanner/{id}/pause` | Pause scan |
| POST | `/scanner/{id}/resume` | Resume scan |
| POST | `/scanner/{id}/stop` | Stop scan |
| GET | `/scanner/issue-definitions` | Issue type definitions |

### Collaborator

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/collaborator/generate` | Generate payload |
| POST | `/collaborator/generate/batch` | Generate multiple payloads |
| GET | `/collaborator/poll` | Poll all interactions |
| GET | `/collaborator/poll/{id}` | Poll specific payload |

### Target

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/target/sitemap` | Get sitemap (`?url=prefix`) |
| GET | `/target/scope` | Get current scope |
| POST | `/target/scope` | Set scope |
| POST | `/target/scope/add` | Add URL to scope |
| POST | `/target/scope/remove` | Remove from scope |
| GET | `/target/scope/check` | Check if URL in scope (`?url=X`) |

### Decoder

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/decoder/encode` | Encode (base64, url, hex, html) |
| POST | `/decoder/decode` | Decode |
| POST | `/decoder/hash` | Hash (md5, sha1, sha256, sha512) |
| POST | `/decoder/smart-decode` | Auto-detect and decode layers |

### Config & Extensions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/config/project` | Project config |
| PUT | `/config/project` | Update project config |
| GET | `/config/user` | User config |
| PUT | `/config/user` | Update user config |
| GET | `/extensions` | List extensions |

## Response Format

All endpoints return:

```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

On error:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Missing required field: url"
  }
}
```

## Stack

- **Kotlin** + Montoya API
- **Ktor** embedded HTTP server (Netty)
- **kotlinx.serialization** for JSON
- **Gradle** with Shadow plugin for fat JAR
- **MockK** for testing

## Project Structure

```
src/main/kotlin/com/burprest/
    BurpRestExtension.kt        # Extension entry point
    server/
        RestServer.kt            # Ktor server setup + middleware
    routes/
        HealthRoutes.kt          # /health, /version, /docs
        ProxyRoutes.kt           # /proxy/*
        RepeaterRoutes.kt        # /repeater/*
        CollaboratorRoutes.kt    # /collaborator/*
        IntruderRoutes.kt        # /intruder/*
        ScannerRoutes.kt         # /scanner/*
        TargetRoutes.kt          # /target/*
        DecoderRoutes.kt         # /decoder/*
        ConfigRoutes.kt          # /config/*, /extensions
    services/
        ProxyService.kt          # Montoya Proxy API wrapper
        RepeaterService.kt       # HTTP request sending
        CollaboratorService.kt   # Collaborator client management
        IntruderService.kt       # Attack management + quick fuzz
        ScannerService.kt        # Scan management
        TargetService.kt         # Sitemap + scope
        DecoderService.kt        # Encode/decode/hash (no Burp needed)
        ConfigService.kt         # Config + extensions info
    models/
        ApiResponse.kt           # Standard response wrapper
        ProxyModels.kt           # Proxy DTOs
        RepeaterModels.kt        # Repeater DTOs
        CollaboratorModels.kt    # Collaborator DTOs
        IntruderModels.kt        # Intruder DTOs
        ScannerModels.kt         # Scanner DTOs
        TargetModels.kt          # Target DTOs
        DecoderModels.kt         # Decoder DTOs
        SequencerModels.kt       # Sequencer DTOs
        OtherModels.kt           # Logger, Search, Config, Health DTOs

src/test/kotlin/com/burprest/
    services/
        DecoderServiceTest.kt    # 14 tests
        ProxyServiceTest.kt      # 7 tests
    routes/
        HealthRoutesTest.kt      # 3 tests
        DecoderRoutesTest.kt     # 4 tests
```

## Development

```bash
# Compile
./gradlew compileKotlin

# Run tests
./gradlew test

# Build fat JAR
./gradlew shadowJar

# Output: build/libs/burp-rest-extension.jar (15MB)
```

## License

MIT
