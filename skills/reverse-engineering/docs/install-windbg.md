# 05 - WinDbg / cdb MCP 安装(可选,Windows-only)

Windows 原生调试:崩溃 dump / BSOD 事后分析、用户态/内核态断点单步、漏洞利用验证、驱动逆向。**与 frida 互补**——frida 是不打断目标的轻量 hook/trace;本 MCP 是断点式深度调试(会中断目标),并能分析 dump 与内核。

> **本项目自研版**(cdb 会话式)。直接驱动系统自带的 `cdb.exe`,**零三方调试库**(除 MCP SDK)。架构为 token_key 会话生命周期:`open → run/封装 → close`。

## 设计要点

- **会话式,不是结构化原子**:调试本质是有状态的持续交互会话。`open(target)` 返回 `token_key`,之后所有操作凭它进行,上下文(符号 / 线程 / 栈帧 / 断点)跨命令保留——和坐在 cdb 前操作一致。
- **两层工具**:5 个会话生命周期工具(`open`/`run`/`interrupt`/`close`/`sessions`)+ 17 个基础命令封装(`regs`/`read_mem`/`disasm`/`stack`/`threads`/`bp`/…)。`run` 是统一原始接口,任意 cdb 命令兜底;封装内部都走 `run`。
- **零三方依赖**:只用 `mcp` SDK + 系统的 `cdb.exe`(装 WinDbg 时就有),不引入任何三方调试绑定。

## 源

- 仓库:https://github.com/276793422/windbg_mcp(本项目自研,开源)
- 获取:`git clone https://github.com/276793422/windbg_mcp`(纯 Python,无编译,换设备 clone 即可)

## 前置

- **Windows** + **Debugging Tools for Windows**(Windows SDK 组件,提供 `cdb.exe`;装 WinDbg 时一并就有)。本 MCP 自动在常见位置搜 `cdb.exe`,找不到时设环境变量 `WINDBGMCP_CDB` 指向它。
- **Python 3.10+**(本项目用 `py -3.13`)。
- **符号路径**(强烈建议):`_NT_SYMBOL_PATH=srv*C:\Symbols*https://msdl.microsoft.com/download/symbols`,否则符号解析多半失败。

## 安装步骤

1. **获取 + 装依赖**:
   ```bash
   git clone https://github.com/276793422/windbg_mcp
   py -3.13 -m pip install -r windbg_mcp/requirements.txt   # 只装 mcp SDK
   ```

2. **配置 `.mcp.json``**(**找到 cdb 后**才加,否则 Claude Code 启动该 server 会失败):
   ```json
   "windbg-mcp": {
     "command": "py",
     "args": ["-3.13", "E:\\AI\\ZSZS\\windbg_mcp\\server.py"],
     "env": { "_NT_SYMBOL_PATH": "srv*C:\\Symbols*https://msdl.microsoft.com/download/symbols" }
   }
   ```
   > 也可用 `gen-mcp-config.py --with-windbg --windbg-server "E:\\AI\\ZSZS\\windbg_mcp\\server.py"` 一键生成。

3. 重启 Claude Code 会话 → 批准 `windbg-mcp`。

## 可配置项

下列均可通过 **环境变量**(写在 `.mcp.json` 的 `env` 里)或 **gen-mcp-config.py 参数** 配置:

| 项 | 环境变量 | gen-script 参数 | 默认 | 说明 |
|---|---|---|---|---|
| cdb.exe 路径/目录 | `WINDBGMCP_CDB` | `--cdb-path` | 自动搜索 | cdb.exe 全路径**或其目录**;空则自动找 Debugging Tools |
| 符号路径 | `_NT_SYMBOL_PATH` | `--nt-symbol-path` | MS 符号服务器 | cdb 原生识别;server 继承 |
| 符号路径(显式) | `WINDBGMCP_SYMBOL_PATH` | — | (继承系统) | 设了由 server 注入每个 cdb 子进程的 `_NT_SYMBOL_PATH`,优先级高于上者 |
| 输出编码 | `WINDBGMCP_ENCODING` | — | utf-8 | 中文系统乱码设 `gbk` |
| 日志级别 | `WINDBGMCP_LOG_LEVEL` | — | INFO | 设 `DEBUG` 排错 |
| 会话数上限 | `WINDBGMCP_MAX_SESSIONS` | — | 8 | 并发会话上限,0=不限;死会话自动清 |
| 放行危险命令 | `WINDBGMCP_ALLOW_DANGEROUS` | — | 拦截 | 设 `1` 放行 `.shell`/`.pcan`(可执行系统命令) |

换设备或自定义 WinDbg 安装位置时,设 `--cdb-path` 与 `--nt-symbol-path` 即可。示例:

```bash
py gen-mcp-config.py --with-windbg \
    --cdb-path "D:\Debuggers\x64" \
    --nt-symbol-path "srv*D:\Symbols*https://msdl.microsoft.com/download/symbols"
```

## 验证

- Claude 侧:`sessions()` 返回 `[]`(空但连通) → OK
- 开会话:`open(target="C:/path/x.dmp")` → 返回 `token_key` + `banner`(cdb 启动信息)
- 关闭:`close(token_key)` 正常返回

## 工具速查(22 个)

| 类 | 工具 |
|---|---|
| 会话生命周期 | `open` · `run`(任意 cdb 命令) · `interrupt` · `close` · `sessions` · `list_dumps` |
| 执行 | `go`(g) · `step(into?)`(p/t) · `analyze`(!analyze -v) |
| 寄存器/内存 | `regs`(r) · `read_mem`(db) · `write_mem`(eb) · `disasm`(u) |
| 符号/模块 | `resolve`(?) · `modules`(lm) |
| 栈/线程/帧/局部 | `stack`(kv) · `threads`(~) · `select_thread`(~Ns) · `frame`(.frame N) · `locals`(dv) |
| 断点 | `bp`(bp) · `breakpoints`(bl) · `remove_bp`(bc) |

`run` = 统一原始接口(任意 cdb 命令兜底);封装内部都走 `run`。完整工具说明（共 44 个，含 `hw_bp`/`set_reg`/`read_str`/`find_symbols`/`addr_to_symbol`/`capture_state`/`detach` 等）见 `references/mcp-tools.md`。

## 注意事项

- **Windows-only**。非 Windows 不要启用。
- **找到 cdb.exe 才加进 `.mcp.json`**。cdb 找不到时 server 仍能启动,但 `open` 会报错。
- **权力大**:能 attach 任意进程、写内存、内核调试,操作前确认目标与授权(本项目仅供安全研究/授权测试)。
- **断点式中断目标**:与 frida 的不打断 hook 不同,`bp`/单步会让目标停住,调试线上/敏感进程要谨慎。
- **`run` 的 timeout 与中断**:`g`/等待类命令会阻塞到事件;到 timeout 返回 `timed_out=true`,调 `interrupt` 中断(发 CTRL+BREAK)。
- **编码**:cdb 输出默认 utf-8 解码(容错);中文系统若乱码设 `WINDBGMCP_ENCODING=gbk`。
- **命令完成判定**:靠识别 cdb 提示符(`0:000>`/`kd>` 等);极少数命令输出含疑似提示符的行可能提前返回,重发即可。
