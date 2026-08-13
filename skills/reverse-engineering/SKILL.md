---
name: reverse-engineering
description: This skill should be used when the user asks to "reverse engineer", "decompile", "disassemble", "analyze an APK/DEX/SO/DLL/ELF/i64", "find xrefs/cross-references", "hook a function", "do dynamic analysis", "trace network/crypto", "dump Lua/DEX/assetbundle", "analyze a crash dump / BSOD", "kernel debug", "set a breakpoint / single-step on Windows", or any binary/app reverse-engineering task. Orchestrates five MCP servers — jadx-mcp-server (Java/DEX static), frida_mcp (dynamic instrumentation), idalib (headless native static), ida-pro-mcp (IDA GUI front-end), windbg-mcp (Windows native debugging, optional) — into a unified workflow.
version: 1.0.0
---

# Reverse Engineering with the MCP Toolkit

Five MCP servers form a complete reverse-engineering pipeline (windbg-mcp is optional, Windows-only). Select the correct one per task, then chain them. Before calling any tool, confirm the right MCP and the exact parameter shape — wrong parameter formats are the #1 cause of silent failures.

## The Five MCPs

| MCP | Layer | Mode | Use for |
|---|---|---|---|
| **jadx-mcp-server** | Java/DEX | static | APK/DEX/JAR Java source, AndroidManifest, resources, smali, Java xrefs |
| **frida_mcp** | runtime | dynamic | hook functions, read/write memory, trace calls, dump decrypted assets (Lua/DEX/assetbundle) on a live process |
| **idalib** | native | headless static | ARM/x86 `.so`/`.dll`/`.elf`/`.i64` — decompile, xrefs, find_bytes — WITHOUT opening IDA GUI |
| **ida-pro-mcp** | native | GUI front-end | same analysis as idalib but operates on the IDB open in the user's IDA window (live front-end linkage) |
| **windbg-mcp** | Windows native | dynamic (debugger, cdb session) | crash dump / BSOD analysis, breakpoints / single-step / registers / heap, kernel & driver debugging, exploit verification (**Windows-only, optional**) |

## Selection Matrix

| Task | MCP |
|---|---|
| Read Java/smali, manifest, resources of an APK | jadx |
| Static analysis of a native binary, no GUI needed | idalib |
| Static analysis with the user watching IDA live | ida-pro-mcp |
| Hook/dump at runtime on a device or process | frida_mcp |
| Find a native function by symbol/bytes | idalib or ida-pro-mcp (`find_bytes`, `lookup_funcs`) |
| Decrypt an encrypted asset at load time | frida_mcp (hook the loader, e.g. `luaL_loadbuffer`) |
| Number base conversion during analysis | idalib/ida-pro-mcp `int_convert` — never convert by hand |
| Root-cause a crash dump / BSOD on Windows | windbg-mcp (`open(kind=dump)` → `analyze` → `stack`/`regs`/`disasm`) |
| Verify exploit / RIP control on Windows (breakpoint, single-step, registers, heap) | windbg-mcp (`open(kind=launch)` → `bp`/`go`/`regs`) |
| Debug a Windows kernel target or driver | windbg-mcp (`open(kind=kernel)` → `run("!process 0 0")`) |
| Hook / trace at runtime WITHOUT stopping the target | frida_mcp |
| Breakpoint-style deep debugging on Windows (stops the target) | windbg-mcp |

## Core Workflow

1. **Triage** — call the overview tool first: `survey_binary` (idalib/ida-pro-mcp) or `get_package_tree` + `get_android_manifest` (jadx). Identify layer (Java vs native), imports, strings, entry points.
2. **Locate** — find the target by name (`lookup_funcs`/`find_process`), bytes (`find_bytes`), string (`find_regex`/`search_classes_by_keyword`), or xref (`xrefs_to`).
3. **Read** — `decompile` / `get_method_by_name` / `get_class_source`. Use `int_convert` for number bases.
4. **Confirm at runtime** — frida_mcp: hook the located function, dump args/return/memory.
5. **Persist** — `rename` / `set_comments` to record findings in the IDB/database.

**Windows deep-debug / crash branch (windbg-mcp, optional, cdb-session):** `open(target)` returns a `token_key`, then drive a persistent cdb session. Crash dump → `open(kind=dump)` → `analyze` (!analyze -v) → `threads`/`select_thread`/`stack`/`frame`/`locals`/`regs`/`disasm` (interactive — !analyze is just the start). Exploit verification → `open(kind=launch)` → `bp` → `go` → `regs`. Any cdb command via `run(token, cmd)`; `interrupt(token)` breaks a blocked `g`; `close(token)` ends. Breakpoint-style (it **stops** the target) — use frida_mcp when the process must keep running.

## Critical: Parameter Formats (avoid the common error)

Many query tools take `queries`/`patterns` as a **list of dicts/strings**, NOT a bare scalar. Sending `{"queries":*}` or `{"queries":"main"}` causes `InputValidationError`. Correct shapes:

- idalib / ida-pro-mcp `list_funcs` → `queries=[{"count": N}]` (list of dict; dict keys: `filter`, `offset`, `count`; empty/`"*"` filter = all)
- idalib / ida-pro-mcp `find_bytes` → `patterns=["AB CD ?? EF"]` (list of strings)
- idalib / ida-pro-mcp `func_query` / `list_globals` / `entity_query` → same `list[dict]` pattern
- idalib `idb_open(input_path, preferred_session_id="name")` → EVERY later call on that DB needs `database="name"`
- frida_mcp flow: `spawn_process` → `attach_to_process` → `load_script`/`exec_script` → `resume_process` → `get_messages`
- jadx `search_classes_by_keyword(search_term=..., search_in="code,method,class", count=N)`

Full tool + parameter catalogue: see `references/mcp-tools.md`.

## MCP State & Health

- idalib: `idb_list` lists open headless sessions; `idb_close` releases a worker.
- ida-pro-mcp: operates on the user's currently-open IDA DB. Verify the HTTP server is up (port 127.0.0.1:13337) before calling.
- frida_mcp: `list_sessions` shows attached processes + loaded scripts + pending messages.
- windbg-mcp: `sessions()` lists active `{token_key, alive}`; each session is a persistent cdb process obtained from `open()`.
- If a tool errors with "session not found" / "database required" / "connect failed" / "not connected", open/attach/probe first.

## idalib vs ida-pro-mcp — Do Not Confuse

- idalib spawns a **headless worker** (separate process, no window). `idb_open` results do NOT appear in the user's IDA.
- ida-pro-mcp drives the **user's open IDA GUI** via HTTP. What it changes, the user sees live.
- They are independent processes. To operate on the user's visible DB, use ida-pro-mcp. To analyze without touching the GUI, use idalib.

## frida_mcp vs windbg-mcp — Do Not Confuse

- **frida_mcp** = lightweight, **non-blocking** instrumentation: hook, trace, read/write memory, dump decrypted assets on a live process (cross-platform, incl. Windows). Target keeps running.
- **windbg-mcp** = **breakpoint-style** deep debugging on Windows: single-step, registers, hardware breakpoints, kernel/driver debugging, crash dump analysis. The target **stops** at breakpoints.
- Rule: if interrupting the target is OK (or you're analyzing a dump / kernel) → windbg-mcp; if the target must keep running → frida_mcp.

## Environment Prerequisites (quick)

- **jadx**: jadx-gui running with the AI MCP plugin loaded; an APK/DEX open.
- **frida_mcp**: `pip install frida` on host; `frida-server` running on device; bypass anti-frida (e.g. Alibaba SecurityGuard) if present.
- **idalib**: `uv` installed; idalib activated (`py-activate-idalib.py`); IDA launched once to accept license.
- **ida-pro-mcp**: IDA's Python switched to ≥3.11 via `idapyswitch` (IDA 9.x may default to an old 3.8); IDA open with a DB so the HTTP server autostarts on 13337.
- **windbg-mcp** (optional, Windows-only): self-built cdb-session server (https://github.com/276793422/windbg_mcp, `git clone` 获取); needs `mcp` SDK + Debugging Tools for Windows (`cdb.exe`, auto-detected or via `WINDBGMCP_CDB`); `_NT_SYMBOL_PATH` set. Enable the `.mcp.json` entry only after cdb is found.

Install/config/troubleshooting details: see `references/setup.md`.

## Additional Resources

### Reference Files
- **`references/mcp-tools.md`** — full tool catalogue with exact parameter schemas for all five MCPs.
- **`references/setup.md`** — quick installation, `.mcp.json` config, `deploy.py` usage, and troubleshooting (Python version, PATH, anti-frida, parameter errors).

### Installation Docs (detailed, with common pitfalls)
- **`docs/README.md`** — overview, architecture, environment, shared pitfalls, doc index.
- **`docs/install-jadx.md`** — jadx-mcp-server (type:command trap, health check, get_resource_file bug).
- **`docs/install-frida-mcp.md`** — frida_mcp (custom implementation; `-m` launch, device frida-server).
- **`docs/install-idalib.md`** — idalib headless (ctypes binding, activate=write JSON, full-path uv).
- **`docs/install-ida-pro-mcp.md`** — IDA GUI front-end (Python 3.8→3.13 idapyswitch, HTTP 13337).
- **`docs/install-windbg.md`** — WinDbg/cdb MCP (optional, Windows-only; self-built cdb-session; token_key lifecycle; zero third-party deps).
