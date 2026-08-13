# reverse-engineering — Claude Code 逆向工程 skill

一个 Claude Code skill,把 **jadx / Frida / IDA Pro / WinDbg(cdb)** 通过五个 MCP server(windbg 可选)统一进 MCP 协议,让 Claude 用自然语言编排 Android 应用与 Windows 原生二进制的静态/动态逆向分析。

装上它,Claude Code 就能在一句"分析这个 APK 的网络通信"或"反编译这个 .so 的某函数"下,自动选对工具(jadx 看 Java、idalib/ida-pro-mcp 看 native、frida 跑动态)、串联流程、并避开常见的参数/配置陷阱。

## 快速安装(4 步)

### 1. 放置 skill
把整个 `reverse-engineering/` 目录放到:
- **项目级**:`<项目>/.claude/skills/reverse-engineering/`
- **用户级**(所有项目可用):`C:\Users\<user>\.claude/skills/reverse-engineering/`

### 2. 装五个 MCP(windbg 可选)
按 `docs/install-*.md` 逐个安装(每份含完整步骤 + 常见问题):

| MCP | 文档 | 作用 |
|---|---|---|
| jadx-mcp-server | [docs/install-jadx.md](docs/install-jadx.md) | Java/DEX 静态(APK 反编译) |
| frida_mcp | [docs/install-frida-mcp.md](docs/install-frida-mcp.md) | 运行时动态(hook/内存/dump) |
| idalib | [docs/install-idalib.md](docs/install-idalib.md) | native 无头静态(.so/.dll 反编译) |
| ida-pro-mcp | [docs/install-ida-pro-mcp.md](docs/install-ida-pro-mcp.md) | native IDA GUI 前台联动 |
| windbg-mcp | [docs/install-windbg.md](docs/install-windbg.md) | Windows 原生调试(崩溃/内核/pwn,可选,自研 cdb 会话) |

### 3. 生成 `.mcp.json`
```bash
py scripts/gen-mcp-config.py --jadx <jadx_mcp_server.py> --uv <uv.exe> --ida-mcp <ida-pro-mcp 目录>
```
路径缺失时脚本会**自动提示去哪个 git/官网获取**。详见 [docs/README.md](docs/README.md)。

### 4. 重启 Claude Code
重启会话,批准新出现的 MCP server(windbg 未装则不出现)。之后逆向类请求会自动触发本 skill。

## 五个 MCP 来源(windbg 可选)

| MCP | 源 |
|---|---|
| jadx-mcp-server | https://github.com/276793422/fork_zinja-coder_jadx-mcp-server |
| jadx-ai-mcp | https://github.com/276793422/fork_zinja-coder_jadx-ai-mcp |
| frida_mcp | https://github.com/276793422/frida_mcp |
| idalib / ida-pro-mcp | https://github.com/276793422/fork_mrexodia_ida-pro-mcp |
| windbg-mcp(可选,自研) | https://github.com/276793422/windbg_mcp |

## 使用

- **自动触发**:对 Claude 说"逆向/反编译/分析 APK/SO/DLL/hook/找 xref/dump"等即可
- **手动触发**:`/reverse-engineering`
- 触发后 Claude 按 `SKILL.md` 的工具选择矩阵与工作流执行,并遵守参数格式红线(如 `list_funcs(queries=[{"count":N}])`)

## 目录结构

```
reverse-engineering/
├── README.md              本文件(入口)
├── SKILL.md               skill 核心:触发词、工具选择、工作流、参数红线
├── docs/                  四 MCP 安装文档 + 总览
│   ├── README.md
│   └── install-*.md
├── references/            工具/参数手册、故障排除
│   ├── mcp-tools.md
│   └── setup.md
├── assets/mcp.json        .mcp.json 参考配置
└── scripts/gen-mcp-config.py   一键生成 .mcp.json
```

## 环境要求

- Python 3.13+(`py` 启动器)
- IDA Pro 9.x(已激活,Python 切到 ≥3.11)
- uv(管理 idalib/ida-pro-mcp 依赖)
- jadx-gui(带 AI MCP 插件)
- 连真机做动态分析时:设备 frida-server
- (可选)Windows 调试:Debugging Tools for Windows + 自研 windbg-mcp(cdb 会话,零三方依赖)

## 声明

本 skill 仅供**安全研究、学习与授权测试**。使用者需自行确保对分析对象拥有合法授权。
