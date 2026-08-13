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

`windbg-mcp` is **optional and NOT in the block above** — self-built cdb-session server; add it only after `cdb.exe` is found, or Claude Code will fail to start that server.

```json
"windbg-mcp": { "command": "py",
                "args": ["-3.13", "E:\\AI\\ZSZS\\windbg_mcp\\server.py"],
                "env": { "_NT_SYMBOL_PATH": "srv*C:\\Symbols*https://msdl.microsoft.com/download/symbols" } }
```

Or generate it: `py gen-mcp-config.py --with-windbg --windbg-server "E:\\AI\\ZSZS\\windbg_mcp\\server.py"`.

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

## windbg-mcp (optional, Windows-only, self-built cdb-session)
- Self-built server (https://github.com/276793422/windbg_mcp — `git clone` it); drives the system's own `cdb.exe`, **no third-party debug lib** (only the `mcp` SDK).
- Requires **Debugging Tools for Windows** (provides `cdb.exe`; bundled with WinDbg). Auto-detected; override with `WINDBGMCP_CDB` (exe path **or its dir**).
- **Symbol path**: `_NT_SYMBOL_PATH=srv*C:\Symbols*https://msdl.microsoft.com/download/symbols` (or `WINDBGMCP_SYMBOL_PATH`, which the server injects per cdb child). Without it `resolve` returns null.
- Install: `git clone https://github.com/276793422/windbg_mcp` then `pip install -r windbg_mcp/requirements.txt` (only `mcp` SDK).
- Config (add only after cdb is found):
  ```json
  "windbg-mcp": { "command": "py", "args": ["-3.13", "E:\\AI\\ZSZS\\windbg_mcp\\server.py"],
                  "env": { "_NT_SYMBOL_PATH": "srv*C:\\Symbols*https://msdl.microsoft.com/download/symbols" } }
  ```
  Or `gen-mcp-config.py --with-windbg --windbg-server "E:\\AI\\ZSZS\\windbg_mcp\\server.py"`.
- Encoding: cdb output decoded utf-8 (tolerant); if garbled on a CN system set `WINDBGMCP_ENCODING=gbk`.

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
| windbg-mcp `open` errors "找不到 cdb.exe" | Set `WINDBGMCP_CDB` to the full `cdb.exe` path, or install Debugging Tools for Windows. |
| windbg `resolve` returns addr=null | `_NT_SYMBOL_PATH` not set / symbols not downloaded. Point it at the MS symbol server and `run(t, ".reload")`. |
| windbg `run` returns early / mid-command | A command line looked like a cdb prompt; rerun the command (prompt-based completion detection). |

## Global vs project scope
This skill lives in `<project>\.claude\skills\reverse-engineering\`. To use it across all projects, copy it to `C:\Users\<user>\.claude\skills\reverse-engineering\`.
