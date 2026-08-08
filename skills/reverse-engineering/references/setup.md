# Setup & Troubleshooting

How the four MCPs are installed/configured, plus common pitfalls and fixes.

## `.mcp.json`(项目根目录)

```json
{
  "mcpServers": {
    "jadx-mcp-server": { "command": "py", "args": ["-3.13", "<jadx_mcp_server.py path>"] },
    "frida_mcp":       { "command": "py", "args": ["-3.13", "-m", "frida_mcp"] },
    "idalib":          { "command": "<uv.exe full path>", "args": ["run","--project","<ida-pro-mcp dir>","idalib-mcp","--stdio"] },
    "ida-pro-mcp":     { "type": "http", "url": "http://127.0.0.1:13337/mcp" }
  }
}
```

`.mcp.json` changes do NOT hot-load — **restart the Claude Code session** and approve newly-added servers.

## jadx-mcp-server
- Requires **jadx-gui running with the AI MCP plugin loaded** and an APK/DEX open. If `get_*` returns errors, check jadx-gui is up and a file is loaded.

## frida_mcp (`E:\Tools\Frida\frida_mcp\`)
- `pip install -e <dir>` + `pip install frida` (host binding).
- Launches via `py -3.13 -m frida_mcp` (NOT `frida_mcp` command — its `.exe` is in Python's `Scripts/` which is NOT on PATH; `-m` is PATH-independent).
- Device side: push `frida-server` matching the host `frida` version + device arch; run as root. Anti-frida (e.g. Alibaba SecurityGuard `libsgmain.so`, emulator check `libcheck_simu.so`) must be bypassed separately.
- `deploy.py` automates install + `.mcp.json` config + device probe.

## idalib (headless native)
- Requires `uv` (e.g. `E:\Tools\uv\uv-x86_64-pc-windows-msvc\uv.exe`) — `uv run` auto-manages Python 3.11 + deps from `uv.lock`.
- Activate idalib once: run `<IDA>\idalib\python\py-activate-idalib.py` (writes `%APPDATA%\Hex-Rays\IDA Pro\ida-config.json` pointing to the IDA install dir). `idapro` is a pure-ctypes binding — Python-version-independent.
- IDA must have been launched once to accept the license.
- `deploy.py` (in ida-pro-mcp dir) automates activate + `.mcp.json` config + connection test.

## ida-pro-mcp (IDA GUI front-end)
- Install plugin + config: `uv run --project <ida-pro-mcp dir> ida-pro-mcp --install claude --scope project --transport streamable-http`
  - Copies plugin to `%APPDATA%\Hex-Rays\IDA Pro\plugins\` (ida_mcp.py + ida_mcp/)
  - Writes the http entry into `.mcp.json`
- **Python version**: IDA's IDAPython may default to a version below 3.11. ida-pro-mcp needs ≥3.11 (uses `match` statement). Fix with idapyswitch:
  - `<IDA>\idapyswitch.exe --force-path "C:\...\Python313\python3.dll"`
  - Verify: `idapyswitch --dry-run` should show "Applying version 3.13".
  - Then **fully restart IDA**.
- The plugin autostarts an HTTP server on `127.0.0.1:13337` when IDA has a DB open. Verify with `curl http://127.0.0.1:13337/mcp` (HTTP 405 on GET = server up).

## Troubleshooting (common issues)

| Symptom | Cause / Fix |
|---|---|
| ida-pro-mcp `SyntaxError: invalid syntax` on `match` in `ida_mcp/zeromcp/mcp.py` | IDA's Python is 3.8/3.9. Run idapyswitch to switch to ≥3.11, restart IDA. |
| `frida_mcp` / `idalib-mcp` command not found | Their `.exe` is in Python `Scripts/` (not on PATH). Use `py -3.13 -m frida_mcp` or the full uv path. |
| MCP server shows "⏸ Pending approval" and tools missing | `.mcp.json` was edited mid-session. Restart Claude Code session and approve. |
| `InputValidationError: could not be parsed as JSON` on `list_funcs` | Parameter shape wrong. `queries` must be a **list of dicts**: `queries=[{"count":5}]`, not `{"queries":*}`. |
| idalib `idb_open` result not visible in IDA | idalib is a separate headless worker, not the GUI. For front-end linkage use ida-pro-mcp. |
| `idb_list` doesn't show the user's open IDA | GUI instances are only discovered if the ida-pro-mcp plugin is loaded (registers discovery). Plain IDA without the plugin is invisible to idalib. |
| ida-pro-mcp tool errors "connect failed" | IDA closed or no DB open → 13337 server down. Open a DB in IDA first. |
| frida `attach` fails immediately | Anti-frida detection. Bypass (rename frida-server, frida-gadget, patch detector) before attaching. |

## Global vs project scope
This skill lives in `<project>\.claude\skills\reverse-engineering\`. To use it across all projects, copy it to `C:\Users\<user>\.claude\skills\reverse-engineering\`.
