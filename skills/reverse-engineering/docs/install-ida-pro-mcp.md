# 04 - ida-pro-mcp 安装

native **IDA GUI 前台联动**。AI 操作用户 IDA 里正开着的库,用户在 IDA 实时看到改动。与 idalib(headless)互补。

## 前置

- **uv** + **ida-pro-mcp 源**(`git clone https://github.com/276793422/fork_mrexodia_ida-pro-mcp`,同 idalib)
- **IDA Pro 9.2**,且其 IDAPython 已切到 **≥3.11**(见下,这一步常被漏)

## 安装步骤

1. **装 IDA 插件 + 配 Claude Code**(一条命令):
   ```bash
   cd <项目根目录>
   "<uv.exe 路径>" run --project "<ida-pro-mcp 目录>" ida-pro-mcp --install claude --scope project --transport streamable-http
   ```
   插件装到 `%APPDATA%\Hex-Rays\IDA Pro\plugins\`(`ida_mcp.py` + `ida_mcp/`),`.mcp.json` 写入 http 条目。
2. **把 IDA 的 Python 切到 ≥3.11**(见下,必做)。
3. **完全重启 IDA** → 打开一个程序 → 插件 autostart 起 HTTP server(`127.0.0.1:13337`)。
4. 重启 Claude Code 会话 → 批准 `ida-pro-mcp`。

## 关键:IDA 的 Python 必须切到 ≥3.11

ida-pro-mcp 用了 Python 3.10 的 `match` 语句,IDA 默认的 IDAPython 若低于 3.11,插件加载即报:
```
SyntaxError: invalid syntax   (在 ida_mcp/zeromcp/mcp.py 的 match 行)
```
用 `idapyswitch` 切到 ≥3.11(本机用 3.13):
```bash
# 看可选版本(idapyswitch 列出的 = IDAPython native 兼容的)
"E:\Tools\IDA Professional 9.2\idapyswitch.exe" --dry-run --verbose
# 切到 3.13
"E:\Tools\IDA Professional 9.2\idapyswitch.exe" --force-path "C:\Users\<user>\AppData\Local\Programs\Python\Python313\python3.dll"
# 验证(应显示 Applying version 3.13)
"E:\Tools\IDA Professional 9.2\idapyswitch.exe" --dry-run
# 完全重启 IDA
```

## `.mcp.json` 配置(installer 自动写)

```json
"ida-pro-mcp": { "type": "http", "url": "http://127.0.0.1:13337/mcp" }
```

## 验证

- `curl http://127.0.0.1:13337/mcp` → HTTP 405(GET 不允许但连上了 = server 在)
- POST initialize → HTTP 200,`serverInfo ida-pro-mcp v1.0.0`
- Claude 侧:`survey_binary(detail_level="standard")` 拿程序概览,或 `list_funcs(queries=[{"count":5}])` 列函数

## 注意事项

- **插件 server 要 IDA 打开 DB 才起**。空开 IDA 不起 server;`File > Open` 打开二进制/IDB 后插件 autostart。
- **headless(idalib)与 GUI(ida-pro-mcp)是独立进程**,互不可见。前台联动用 ida-pro-mcp,后台不打扰 GUI 用 idalib。
- 工具参数 `queries` 多为 `list[dict]`,如 `list_funcs(queries=[{"count":5}])`。报 `InputValidationError: could not be parsed as JSON` 就是参数形状错。
