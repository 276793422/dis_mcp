# 02 - frida_mcp 安装

动态插桩(hook、内存读写、trace、dump 解密资源)。本项目自定义实现,已开源。

## 源

**https://github.com/276793422/frida_mcp.git**(本项目自定义实现,已上传;换设备直接 clone,无需拷本地目录)

## 前置

- Python 3.13
- (连真机时)设备上跑 frida-server

## 安装步骤

1. **获取源码 + 装包**:
   ```bash
   git clone https://github.com/276793422/frida_mcp.git
   py -3.13 -m pip install -e frida_mcp
   py -3.13 -m pip install frida
   ```
   `pip install -e` 注册 `frida_mcp` 命令并装依赖(`mcp`、`frida`)。
2. **配置 `.mcp.json`**:
   ```json
   "frida_mcp": {
     "command": "py",
     "args": ["-3.13", "-m", "frida_mcp"]
   }
   ```
3. (可选)跑部署脚本自动完成上面 + 探测设备:
   ```bash
   py -3.13 frida_mcp\deploy.py
   ```
4. 重启 Claude Code 会话 → 批准 `frida_mcp`。

## 验证

- `py -3.13 -c "import frida_mcp; print(frida_mcp.__version__)"` → `1.0.0`
- Claude 侧调 `list_devices` 返回设备列表 → 连通

## 设备 frida-server(连真机时)

```bash
py -3.13 -c "import frida;print(frida.__version__)"
# 下载匹配版本的 frida-server-<ver>-android-<arch>.xz (github.com/frida/frida/releases)
adb push frida-server /data/local/tmp/frida-server
adb shell "su -c 'chmod 755 /data/local/tmp/frida-server && /data/local/tmp/frida-server &'"
```

## 注意事项

- **用 `py -3.13 -m frida_mcp` 启动**,不要写 `"command":"frida_mcp"`。`frida_mcp.exe` 装在 Python `Scripts/`(常不在 PATH),`-m` 方式只依赖 `py` + 已装包,PATH 无关。
- **反 Frida**:游戏类目标(带阿里 SecurityGuard 等)会检测 frida-server,attach 即崩。需另行绕过(改名 frida-server / frida-gadget / patch 检测器)。这是目标侧对抗,与安装无关。
