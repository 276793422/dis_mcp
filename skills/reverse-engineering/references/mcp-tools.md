# MCP Tool Catalogue

Exact tool names and parameter shapes for the four reverse-engineering MCPs. When a tool takes `queries`/`patterns`, pass a **list** (of dicts or strings) — never a bare scalar.

## jadx-mcp-server — Java/DEX static

| Tool | Key params |
|---|---|
| `get_android_manifest` | — |
| `get_package_tree` | — (large output; paginated) |
| `get_main_activity_class` | — |
| `get_class_source` | `class_name` |
| `get_method_by_name` | `class_name`, `method_name`, `method_signature?` |
| `get_methods_of_class` / `get_fields_of_class` | `class_name` |
| `search_classes_by_keyword` | `search_term`, `search_in="code,method,class"`, `count`, `package?`, `offset?` |
| `search_method_by_name` | `method_name` |
| `get_xrefs_to_class` / `get_xrefs_to_method` / `get_xrefs_to_field` | `class_name` / `class_name, method_name` / `class_name, field_name` |
| `get_smali_of_class` | `class_name` |
| `get_manifest_component` | `component_type` (activity/service/receiver/provider), `only_exported?` |
| `get_strings` / `get_resource_file` / `get_all_resource_file_names` | pagination / `resource_name` |

Note: `get_resource_file` has a known bug in jadx-mcp-server 6.4 (ignores path, returns a fixed `strings.xml`). Read resources another way if it misbehaves.

## frida_mcp — dynamic instrumentation

**Device / process**
- `list_devices()`, `list_processes(device_id?)`, `find_process(name, device_id?)`
- `spawn_process(program, device_id?, paused=True)` → pid (suspended by default)
- `resume_process(pid)`, `kill_process(pid)`

**Session**
- `attach_to_process(pid, device_id?, name?)` → `session_id` (the real entry point)
- `list_sessions()`, `detach_session(session_id)`

**Script**
- `load_script(session_id, source, name?, runtime?)` → `script_id` — **persistent** (hooks/interceptors)
- `unload_script(session_id, script_id)`
- `exec_script(session_id, source, timeout?)` — one-shot, returns value + console.log
- `rpc_call(session_id, script_id, method, args?, timeout?)` — calls `rpc.exports`
- `get_messages(session_id, script_id?, clear?, limit?, include_data?)` — drains `send()` output

**Convenience**
- `read_memory(session_id, address, size)`, `list_modules(session_id)`, `list_exports(session_id, module)`, `find_export(session_id, module, export_name)`, `scan_memory(session_id, pattern, module?, max_hits?)`

**Standard hook-before-load flow**
```
spawn_process(pkg, paused=True) → pid
attach_to_process(pid)          → session_id
load_script(session_id, <hook JS>) → script_id
resume_process(pid)
get_messages(session_id)        → collect send() output
```

## idalib / ida-pro-mcp — native static

**Session (idalib only — ida-pro-mcp drives the GUI DB, no `database` needed)**
- `idb_open(input_path, preferred_session_id="x", mode?, run_auto_analysis?, build_caches?, init_hexrays?)` → session id
- `idb_list()`, `idb_close(database, save?)`, `idb_save(database)`

**Overview — call first**
- `survey_binary(detail_level="standard"|"minimal")` — metadata + segments + entrypoints + stats + top strings/functions + imports + callgraph

**Query tools — `queries` is a LIST OF DICTS**
- `list_funcs(queries=[{"filter":"*","offset":0,"count":N}])` → list of pages
- `func_query(queries=[{...}])` — richer filters (size/type/name)
- `list_globals`, `list_exports`, `entity_query`, `imports_query` — same list-of-dicts pattern
- `lookup_funcs(queries=["0x401000","main"])` — list[str]|str of addr/name
- `imports(offset=0, count=N)` — pagination scalars

**Decompile / disasm**
- `decompile(addr)`, `disasm(addr, max_instructions?, offset?)`, `analyze_function(addr)`, `analyze_batch(queries)`

**Cross-references**
- `xrefs_to(addrs)`, `xrefs_to_field(queries)`, `callees(addrs)`, `callers`, `trace_data_flow(addr, direction?, max_depth?)`, `callgraph(roots, max_depth?)`

**Search**
- `find_bytes(patterns=["AB CD ?? EF"])` — list of strings
- `find_regex(queries=["pattern"])` — string search
- `find_insns`, `find(type, targets)`, `search_text(pattern)`

**Memory read**
- `get_bytes(regions)`, `get_int(queries)`, `get_string(addrs)`, `get_global_value(queries)`, `read_struct(queries)`

**Modify (persist findings)**
- `rename(batch={"func":[...],"data":[...],"local":[...],"stack":[...]})`
- `set_comments(items)`, `append_comments(items)`, `add_bookmark(addr, name)`
- `set_type(edits)`, `declare_type(decls)`, `patch(patches)`, `define_func(items)`, `define_code(items)`

**Utility**
- `int_convert(inputs)` — number base conversion. USE THIS, never convert by hand.
- `server_health(database?)`

## idalib vs ida-pro-mcp — same tools, different target

- idalib tools take a `database="<session_id>"` arg (names which headless worker).
- ida-pro-mcp tools have NO `database` arg — they operate on whatever DB is open in the user's IDA window.

## windbg-mcp — Windows native debugging (optional, Windows-only)

Self-built, cdb-session based. Drives the system's own `cdb.exe` (no third-party debug lib,
only the `mcp` SDK). Architecture: **token_key session lifecycle** — `open(target)` returns a
`token_key`; all later ops carry it; context (symbols / thread / frame / breakpoints) persists
across calls, exactly like sitting at a cdb prompt.

Two layers: session lifecycle + thin wrappers over common cdb commands. `run` is the unified
escape hatch for any cdb command.

### Session lifecycle
- `open(target, args?, kind?, initial_commands?, ready_timeout_ms?)` → `{token_key, kind, alive, banner}`
  - kind: `dump`(.dmp/.mdmp) / `launch`(exe) / `attach`(pid) / `kernel`(connect string) / `auto`
- `run(token_key, command, timeout_ms=30000)` → `{output, alive, timed_out}` — **any cdb command**
- `interrupt(token_key)` — break the running command (CTRL+BREAK), e.g. a blocked `g`
- `close(token_key)` — quit the session
- `sessions()` → list active `{token_key, kind, target, alive}` (auto-reaps dead sessions)
- `list_dumps(directory, pattern?, limit?)` → list dump files under a dir (no session needed)

**Safety / limits**: `.shell` / `.pcan` are blocked by default (`WINDBGMCP_ALLOW_DANGEROUS=1` to allow).
Commands on the same token_key are serialized (no interleaving); different token_keys run concurrently.
Max concurrent sessions = `WINDBGMCP_MAX_SESSIONS` (default 8, 0=unlimited); dead sessions auto-reaped, all closed at exit.

### Wrappers (common cdb commands; all go through run, same session context)
- Execution: `go`(g) · `step(into?=False,count=1)`(p/t) · `step_out`(gu) · `goto(expr)`(g expr) · `trace(count)`(t N) · `analyze(verbose?)`(!analyze -v)
- Registers/Memory: `regs(name?)`(r → parsed `{registers}`) · `set_reg(name,value)`(r name=val) · `read_mem(addr,size)`(db → parsed `{hex,ascii}`) · `write_mem(addr,hex)`(eb) · `read_str(addr,wide?)`(da/du) · `read_ptr(addr,count?)`(dps) · `poi(addr)`(dps L1) · `disasm(addr?,count)`(u $ip) · `mem_info(addr)`(!vprot) · `mem_list()`(!address)
- Symbols/Modules: `resolve(symbol)`(? → parsed `{addr}`) · `find_symbols(pattern)`(x) · `addr_to_symbol(addr)`(ln) · `modules()`(lm) · `module_info(name)`(lm vm) · `get_exports(name)`(x name!*)
- Stack/Thread/Frame/Locals: `stack(frames?)`(kv) · `threads()`(~) · `select_thread(id)`(~Ns) · `frame(n)`(.frame N) · `locals()`(dv) · `get_teb()`(r $teb) · `get_peb()`(r $peb) · `get_handles()`(!handle 0 f)
- Breakpoints: `bp(expr)`(bp) · `hw_bp(addr,size?,access?)`(ba) · `breakpoints()`(bl) · `enable_bp(id)`(be) · `disable_bp(id)`(bd) · `remove_bp(id)`(bc)
- Capture: `capture_state()` — manual snapshot (registers + call stack + stack memory + disasm at `$ip`)

Session-level also includes `detach(token_key)` (cdb qd — target keeps running, unlike `close`).

`addr` accepts cdb expressions. `regs` / `read_mem` / `resolve` parse structured fields; the rest return clean text (prompt stripped).

**cdb pseudo-register gotcha (tested)**: `$ip` / `$teb` / `$peb` / `$exentry` work; **`$sp` does NOT exist** — get stack pointer via `regs()` (esp/rsp) or use `@esp`/`@rsp` (register refs need `@`). Wrappers already avoid `$sp` (`disasm` uses `$ip`, `capture_state` uses parsed stack pointer).
**`mem_list` (`!address`)**: first call builds the memory map (slow, output may lag to the next command); `mem_info` (`!vprot`) is lightweight and preferred for single-address queries.

Typical crash-dump flow (interactive — `!analyze` is just the start):
```
open("C:/x.dmp")                         → t
analyze(t)                               → faulting module / exception / stack
threads(t) → select_thread(t, 3) → stack(t) → frame(t, 2) → locals(t) → regs(t) → disasm(t, count=8)
run(t, "!heap -stat")                    → anything not wrapped goes through run
close(t)
```
