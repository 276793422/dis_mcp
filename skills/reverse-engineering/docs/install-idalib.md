# 03 - idalib 安装

native 无头静态分析(276793422/fork_mrexodia_ida-pro-mcp v2.0 的 idalib headless 模式,`idalib-mcp --stdio`)。不开 IDA GUI,AI 后台直接分析二进制。

## 前置

- **uv**:`E:\Tools\uv\uv-x86_64-pc-windows-msvc\uv.exe`(单文件,`uv run` 会自动拉 Python 3.11 + 依赖)
- **IDA Pro 9.2**(已激活)
- **ida-pro-mcp 源**:`E:\Tools\IDA Professional 9.2\ida-pro-mcp`(换设备 `git clone https://github.com/276793422/fork_mrexodia_ida-pro-mcp`)

## 关键机制(理解后省事)

- `idapro` 是**纯 ctypes 绑定**(`__init__.py` 用 `ctypes.LoadLibrary(idalib.dll)`),**Python 版本无关**——本机 3.13 直接能用,不必专门装 3.11。
- "激活 idalib" 只是写一个 JSON(`%APPDATA%\Hex-Rays\IDA Pro\ida-config.json`,内容为 IDA 安装目录),不装 native、不绑 Python。

## 安装步骤

1. **激活 idalib**(写 ida-config.json,用任意 Python 跑都行):
   ```bash
   py -3.13 "E:\Tools\IDA Professional 9.2\idalib\python\py-activate-idalib.py"
   ```
2. **配置 `.mcp.json`**(关键:uv 用**全路径**,因为它不在 PATH):
   ```json
   "idalib": {
     "command": "E:\\Tools\\uv\\uv-x86_64-pc-windows-msvc\\uv.exe",
     "args": ["run", "--project", "E:\\Tools\\IDA Professional 9.2\\ida-pro-mcp", "idalib-mcp", "--stdio"]
   }
   ```
3. (可选)跑部署脚本自动完成激活+配置+连接验证:
   ```bash
   py -3.13 "E:\Tools\IDA Professional 9.2\ida-pro-mcp\deploy.py"
   ```
4. 重启 Claude Code 会话 → 批准 `idalib`。

## 验证

- `deploy.py` 第 2 步打印 `IDALIB_VERSION (9, 2, ...)` → idapro 真加载成功
- 第 4 步:mcp 官方 client 连上 `idalib-mcp`,66 工具
- 实测:`idb_open(<小二进制>)` → `auto_analysis_ready`/`hexrays_ready` 全 true

## 注意事项

- **IDA 至少启动过一次**接受许可,否则 `import idapro` 的 `init_library` 阶段失败。
- **uv 不在 PATH**,`.mcp.json` 必须用 uv.exe 全路径(或先把它加 PATH)。
- idalib 起的是**无窗口 worker 进程**,和用户开的 IDA GUI 互不可见。`idb_open` 结果不显示在 IDA 窗口;要前台联动 GUI 用 ida-pro-mcp。
