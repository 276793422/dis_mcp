# dis_mcp

一套面向**逆向工程**的 Claude Code 工具集:一个 skill + 四个开源 MCP server 的配合方案,让 Claude Code 用自然语言做 Android 应用与原生二进制的静态/动态逆向。

## 这是什么

本仓库提供一个 Claude Code skill(`skills/reverse-engineering/`),编排四个 MCP server:

| MCP | 作用 | 源 |
|---|---|---|
| jadx-mcp-server | Java/DEX 静态(APK 反编译) | https://github.com/276793422/fork_zinja-coder_jadx-mcp-server |
| jadx-ai-mcp | jadx-gui 的 AI MCP 插件(非独立 server,随 jadx-gui) | https://github.com/276793422/fork_zinja-coder_jadx-ai-mcp |
| frida_mcp | 运行时动态(hook/内存/dump) | https://github.com/276793422/frida_mcp |
| idalib | native 无头静态(.so/.dll 反编译) | https://github.com/276793422/fork_mrexodia_ida-pro-mcp |
| ida-pro-mcp | native IDA GUI 前台联动 | https://github.com/276793422/fork_mrexodia_ida-pro-mcp |
| windbg-mcp | Windows 原生调试(崩溃 dump/内核/pwn,Windows-only,可选,自研 cdb 会话,零三方依赖) | https://github.com/276793422/windbg_mcp |

装好后,Claude Code 能在"分析这个 APK 的网络通信""反编译这个 .so 的某函数""hook 这个方法 dump 参数"等指令下,自动选对工具、串联流程、避开参数/配置陷阱。

## 仓库内容

```
skills/reverse-engineering/   逆向工程 skill
├── README.md                 ← 从这里开始读(skill 入口)
├── SKILL.md                  skill 定义(给 Claude)
├── docs/                     四 MCP 安装文档
├── references/               工具/参数手册、故障排除
├── assets/mcp.json           .mcp.json 参考配置
└── scripts/gen-mcp-config.py 一键生成 .mcp.json
```

## 快速开始

1. **clone 本仓库到 Claude Code 配置目录**:
   ```bash
   # 项目级(仅当前项目可用)
   git clone https://github.com/276793422/dis_mcp.git <项目>/.claude
   # 或用户级(所有项目可用)
   git clone https://github.com/276793422/dis_mcp.git ~/.claude
   ```
2. **按 skill README 装四个 MCP + 生成配置**:见 [`skills/reverse-engineering/README.md`](skills/reverse-engineering/README.md)(4 步,含每步细节)
3. **重启 Claude Code**,批准新出现的四个 MCP server

## 环境

Python 3.13+、IDA Pro 9.x(已激活)、uv、jadx-gui(带 AI MCP 插件);连真机做动态另需 frida-server。

## 声明

本仓库仅供**安全研究、学习与授权测试**。使用者需自行确保对分析对象拥有合法授权。
