# MCP 安装文档

五个 MCP(windbg 可选)构成完整逆向流水线。本档是**可复现安装指南**——换一台设备,照此即可装齐。

## 架构

```
   APK/DEX  ──► jadx-mcp-server   Java/DEX 静态
   运行进程 ──► frida_mcp          动态插桩(hook/内存/dump)
   .so/.dll ──► idalib             native 无头静态
               ida-pro-mcp         native IDA GUI 前台联动
   Win dump/进程 ──► windbg-mcp          Windows 原生调试(崩溃/内核/pwn,可选)
```

## 需要随设备迁移的本地资源

换设备时,这些目录要一起拷到新机(路径可变,文档里按需替换):

| 资源 | 本机路径 | 获取方式(换设备) |
|---|---|---|
| jadx-gui + AI MCP 插件 | `E:\Tools\jadx-gui-1.5.6-with-jre-win` | 插件 https://github.com/276793422/fork_zinja-coder_jadx-ai-mcp ;服务 https://github.com/276793422/fork_zinja-coder_jadx-mcp-server |
| frida_mcp(本项目实现) | `E:\Tools\Frida\frida_mcp` | `git clone https://github.com/276793422/frida_mcp.git` |
| uv | `E:\Tools\uv\uv-x86_64-pc-windows-msvc` | https://astral.sh/uv (单文件) |
| ida-pro-mcp | `E:\Tools\IDA Professional 9.2\ida-pro-mcp` | `git clone https://github.com/276793422/fork_mrexodia_ida-pro-mcp` |
| IDA Pro 9.2 | `E:\Tools\IDA Professional 9.2` | 官方 https://hex-rays.com |
| windbg-mcp(可选) | `E:\AI\ZSZS\windbg_mcp` | `git clone https://github.com/276793422/windbg_mcp` |

新机还要装:**Python 3.13+**(带 `py` 启动器)、**IDA 9.x**(已激活许可)、**Android Platform Tools**(adb,可选,连设备用)。

## 安装顺序

按依赖关系:① jadx(最简,验证 MCP 机制)→ ② frida_mcp → ③ idalib(需 uv)→ ④ ida-pro-mcp(需 uv + 切 IDA Python)。⑤ windbg-mcp 可选(Windows-only,需 Debugging Tools for Windows + 符号路径)。

每装完一个,改 `.mcp.json` 后**重启 Claude Code 会话**并批准。

## 通用注意事项

| 事项 | 说明 |
|---|---|
| `.mcp.json` 不热加载 | 改完重启会话,首次批准新 server |
| 命令启动方式 | 优先 `py -3.13 -m <pkg>` 或可执行文件**全路径**,别依赖 `Scripts/` 在 PATH |
| stdio server 配置 | `.mcp.json` 里**不要写 `"type"` 字段** |
| 工具参数 `queries` | 多数 idalib/ida-pro-mcp 查询要 `list[dict]`,如 `list_funcs(queries=[{"count":5}])` |

## 配置文件(.mcp.json)生成

`.mcp.json` 含 3 个机器特定路径(jadx 脚本、uv.exe、ida-pro-mcp 目录;启用 windbg 再 +1:--windbg-server)。换设备后用脚本生成,别手写:

```bash
py .claude/skills/reverse-engineering/scripts/gen-mcp-config.py --output .mcp.json
```

新机路径不同时加参数覆盖默认值:

```bash
py .claude/skills/reverse-engineering/scripts/gen-mcp-config.py \
    --jadx "<新机 jadx_mcp_server.py 路径>" \
    --uv "<新机 uv.exe 路径>" \
    --ida-mcp "<新机 ida-pro-mcp 目录>" \
    --output .mcp.json
```

脚本会**合并**这些 server 到目标 `.mcp.json`(windbg-mcp 需加 --with-windbg;保留已有的其他 MCP),不会覆盖。参考配置在 `assets/mcp.json`(当前机器的完整配置,也可手动改路径用)。

## 各 MCP 安装

- [01 - jadx-mcp-server](./install-jadx.md)
- [02 - frida_mcp](./install-frida-mcp.md)
- [03 - idalib](./install-idalib.md)
- [04 - ida-pro-mcp](./install-ida-pro-mcp.md)
- [05 - WinDbg MCP(可选,Windows-only)](./install-windbg.md)
