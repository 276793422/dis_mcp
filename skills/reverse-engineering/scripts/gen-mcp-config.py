#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成/合并五个逆向 MCP(windbg 可选)的 .mcp.json 配置。

换设备后,在项目根目录跑(默认路径生成本机配置):
    py gen-mcp-config.py

路径不同时用参数覆盖:
    py gen-mcp-config.py --jadx "D:\\path\\jadx_mcp_server.py" \\
                          --uv "D:\\path\\uv.exe" \\
                          --ida-mcp "D:\\path\\ida-pro-mcp"

脚本会【合并】四个 server 到目标 .mcp.json(保留已有的其他 server),
不会覆盖你手动加的别的 MCP。换设备只需改三个路径参数。
"""
import argparse
import json
import os
import sys

# 本机默认路径 —— 换设备时用命令行参数覆盖,或直接改这里
DEFAULTS = {
    "jadx_script": r"E:\Tools\jadx-gui-1.5.6-with-jre-win\jadx-mcp-server-6.4.0\jadx-mcp-server\jadx_mcp_server.py",
    "uv_exe":      r"E:\Tools\uv\uv-x86_64-pc-windows-msvc\uv.exe",
    "ida_mcp_dir": r"E:\Tools\IDA Professional 9.2\ida-pro-mcp",
    "python":      "py",
    "py_version":  "-3.13",
    "ida_http":    "http://127.0.0.1:13337/mcp",
    # windbg-mcp(可选,Windows-only,自研 cdb 会话版;默认不写入 .mcp.json,需 --with-windbg 启用)
    "windbg_server":    r"E:\AI\ZSZS\windbg_mcp\server.py",   # 自研 server 入口(git clone https://github.com/276793422/windbg_mcp 后的 server.py)
    "windbg_cdb_path":  "",   # cdb.exe 路径或目录;空=让 server 自动搜索
    "nt_symbol_path":   r"srv*C:\Symbols*https://msdl.microsoft.com/download/symbols",
}


def build_servers(jadx_script, uv_exe, ida_mcp_dir, python, py_version, ida_http,
                  with_windbg=False, windbg_server=None, windbg_cdb_path=None, nt_symbol_path=None):
    pyv = [py_version] if py_version else []
    servers = {
        "jadx-mcp-server": {
            "command": python,
            "args": pyv + [jadx_script],
        },
        "frida_mcp": {
            "command": python,
            "args": pyv + ["-m", "frida_mcp"],
        },
        "idalib": {
            "command": uv_exe,
            "args": ["run", "--project", ida_mcp_dir, "idalib-mcp", "--stdio"],
        },
        "ida-pro-mcp": {
            "type": "http",
            "url": ida_http,
        },
    }
    # windbg-mcp:可选,Windows-only,自研 cdb 会话版;默认不含,找到 cdb 后 --with-windbg 启用
    if with_windbg:
        env = {"_NT_SYMBOL_PATH": nt_symbol_path or ""}
        if windbg_cdb_path:
            env["WINDBGMCP_CDB"] = windbg_cdb_path       # 让 server 用指定 cdb.exe/目录
        servers["windbg-mcp"] = {
            "command": python,
            "args": pyv + [windbg_server],
            "env": env,
        }
    return servers


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    ap = argparse.ArgumentParser(description="生成/合并五个逆向 MCP(windbg 可选)的 .mcp.json 配置")
    ap.add_argument("--output", default=".mcp.json", help="目标 .mcp.json 路径(默认当前目录 .mcp.json)")
    ap.add_argument("--jadx", default=DEFAULTS["jadx_script"], help="jadx_mcp_server.py 路径")
    ap.add_argument("--uv", default=DEFAULTS["uv_exe"], help="uv.exe 路径")
    ap.add_argument("--ida-mcp", default=DEFAULTS["ida_mcp_dir"], help="ida-pro-mcp 项目目录")
    ap.add_argument("--python", default=DEFAULTS["python"], help="python 命令(默认 py)")
    ap.add_argument("--py-version", default=DEFAULTS["py_version"], help="python 版本参数(默认 -3.13;留空字符串则不传)")
    ap.add_argument("--ida-http", default=DEFAULTS["ida_http"], help="ida-pro-mcp HTTP URL")
    ap.add_argument("--with-windbg", action="store_true", help="加入 windbg-mcp(自研 cdb 会话版,可选,Windows-only;找到 cdb 后启用,默认不写入)")
    ap.add_argument("--windbg-server", default=DEFAULTS["windbg_server"], help="自研 windbg server.py 路径")
    ap.add_argument("--cdb-path", default=DEFAULTS["windbg_cdb_path"], help="cdb.exe 全路径或其目录(空=server 自动搜索);写入 env WINDBGMCP_CDB")
    ap.add_argument("--nt-symbol-path", default=DEFAULTS["nt_symbol_path"], help="符号路径 _NT_SYMBOL_PATH(写入 env)")
    args = ap.parse_args()

    # 路径存在性检查(缺失时给出获取地址提示)
    SOURCES = {
        "jadx 脚本": "https://github.com/276793422/fork_zinja-coder_jadx-mcp-server (服务) + https://github.com/276793422/fork_zinja-coder_jadx-ai-mcp (插件)",
        "uv.exe": "https://astral.sh/uv",
        "ida-pro-mcp 目录": "git clone https://github.com/276793422/fork_mrexodia_ida-pro-mcp",
        "windbg-mcp server": "git clone https://github.com/276793422/windbg_mcp —— 换设备 clone,server.py 在 clone 目录",
    }
    print("路径检查:")
    missing = []
    checks = [("jadx 脚本", args.jadx), ("uv.exe", args.uv), ("ida-pro-mcp 目录", args.ida_mcp)]
    if args.with_windbg:
        checks.append(("windbg-mcp server", args.windbg_server))
    for label, p in checks:
        ok = os.path.exists(p)
        print(f"  [{'OK' if ok else '缺失'}] {label}: {p}")
        if not ok:
            print(f"         → 获取: {SOURCES[label]}")
            missing.append(label)
    if missing:
        print("\n提示: 上述路径缺失。按提示 clone/下载后,用 --jadx/--uv/--ida-mcp 指定正确路径再跑本脚本。")

    servers = build_servers(args.jadx, args.uv, args.ida_mcp, args.python, args.py_version, args.ida_http,
                            args.with_windbg, args.windbg_server, args.cdb_path, args.nt_symbol_path)

    # 合并到目标 .mcp.json(保留已有 server)
    if os.path.exists(args.output):
        try:
            with open(args.output, encoding="utf-8") as f:
                data = json.load(f)
            existing = list(data.get("mcpServers", {}).keys())
        except Exception as e:
            print(f"[错误] 读取现有 {args.output} 失败: {e}")
            sys.exit(1)
    else:
        data, existing = {"mcpServers": {}}, []

    data.setdefault("mcpServers", {}).update(servers)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n已写入 {os.path.abspath(args.output)}")
    print(f"  MCP servers: {list(data['mcpServers'].keys())}")
    if existing:
        kept = [s for s in existing if s not in servers]
        if kept:
            print(f"  (保留了原有: {kept})")
    print("\n下一步:")
    print("  1) 确保各 MCP 已装(见 docs/install-*.md)")
    print("  2) 重启 Claude Code 会话,批准新出现的 MCP server")


if __name__ == "__main__":
    main()
