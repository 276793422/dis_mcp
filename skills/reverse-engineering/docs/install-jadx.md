# 01 - jadx-mcp-server 安装

Java/DEX 静态分析。最简单,先装它验证整个 MCP 机制。

## 源/获取

- jadx AI MCP 插件:https://github.com/zinja-coder/jadx-ai-mcp
- jadx MCP 服务:https://github.com/zinja-coder/jadx-mcp-server
- (本机用 jadx-mcp-server-6.4.0 解压版;换设备可从上面 git 取最新,或用 release zip)

## 前置

- **jadx-gui 1.5.6**(带 JRE):`E:\Tools\jadx-gui-1.5.6-with-jre-win\jadx-gui.exe`
- **JADX AI MCP Plugin**(随 jadx-gui,脚本在 `jadx-mcp-server-6.4.0\jadx-mcp-server\jadx_mcp_server.py`)
- Python 3.13(`py -3.13`)

## 安装步骤

1. **配置 `.mcp.json`**(项目根):
   ```json
   {
     "mcpServers": {
       "jadx-mcp-server": {
         "command": "py",
         "args": ["-3.13", "E:\\Tools\\jadx-gui-1.5.6-with-jre-win\\jadx-mcp-server-6.4.0\\jadx-mcp-server\\jadx_mcp_server.py"]
       }
     }
   }
   ```
2. **启动对端**:开 jadx-gui → 加载一个 APK/DEX → 确认 AI MCP Plugin 已加载(它监听本地端口供 `jadx_mcp_server.py` 连)。
3. 重启 Claude Code 会话 → 批准 `jadx-mcp-server`。

## 验证

- 调 `get_cache_stats` 返回 JSON → 连通
- 调 `get_android_manifest` 拿到 manifest → 对端 OK

## 注意事项

- **`.mcp.json` 不要写 `"type"` 字段**。写 `"type":"command"` 会被 Claude Code 跳过(报 `unknown MCP server type "command"`)。只留 `command` + `args`。
- **对端必须先开**。jadx-gui 没开 / 插件没加载 / 没加载文件时,`jadx_mcp_server.py` 的 health check 会失败(`WinError 10061` 连接被拒)。先开 jadx-gui 并加载文件。
- `get_resource_file`(6.4 版)可能返回错误内容(参数被忽略)。读资源先 `get_all_resource_file_names` 再用代码从 APK 取。
- 大结果接口(`get_package_tree`/`get_all_classes`)带 `offset`/`count` 分页,避免存盘。
