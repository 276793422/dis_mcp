#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成/合并四个逆向 MCP 的 .mcp.json 配置。

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
}


def build_servers(jadx_script, uv_exe, ida_mcp_dir, python, py_version, ida_http):
    pyv = [py_version] if py_version else []
    return {
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


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    ap = argparse.ArgumentParser(description="生成/合并四个逆向 MCP 的 .mcp.json 配置")
    ap.add_argument("--output", default=".mcp.json", help="目标 .mcp.json 路径(默认当前目录 .mcp.json)")
    ap.add_argument("--jadx", default=DEFAULTS["jadx_script"], help="jadx_mcp_server.py 路径")
    ap.add_argument("--uv", default=DEFAULTS["uv_exe"], help="uv.exe 路径")
    ap.add_argument("--ida-mcp", default=DEFAULTS["ida_mcp_dir"], help="ida-pro-mcp 项目目录")
    ap.add_argument("--python", default=DEFAULTS["python"], help="python 命令(默认 py)")
    ap.add_argument("--py-version", default=DEFAULTS["py_version"], help="python 版本参数(默认 -3.13;留空字符串则不传)")
    ap.add_argument("--ida-http", default=DEFAULTS["ida_http"], help="ida-pro-mcp HTTP URL")
    args = ap.parse_args()

    # 路径存在性检查(缺失时给出获取地址提示)
    SOURCES = {
        "jadx 脚本": "https://github.com/zinja-coder/jadx-mcp-server (服务) + https://github.com/zinja-coder/jadx-ai-mcp (插件)",
        "uv.exe": "https://astral.sh/uv",
        "ida-pro-mcp 目录": "git clone https://github.com/mrexodia/ida-pro-mcp",
    }
    print("路径检查:")
    missing = []
    for label, p in [("jadx 脚本", args.jadx), ("uv.exe", args.uv), ("ida-pro-mcp 目录", args.ida_mcp)]:
        ok = os.path.exists(p)
        print(f"  [{'OK' if ok else '缺失'}] {label}: {p}")
        if not ok:
            print(f"         → 获取: {SOURCES[label]}")
            missing.append(label)
    if missing:
        print("\n提示: 上述路径缺失。按提示 clone/下载后,用 --jadx/--uv/--ida-mcp 指定正确路径再跑本脚本。")

    servers = build_servers(args.jadx, args.uv, args.ida_mcp, args.python, args.py_version, args.ida_http)

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
