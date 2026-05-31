# Config Editor

`config-editor.html` 是给非技术用户使用的可视化 onboarding / 配置页面。它是可选入口；默认可以先在对话中完成 onboarding。

## 推荐使用方式：本地服务

只有当用户明确想打开图形化页面时才需要启动服务。

在工作空间根目录运行：

```bash
node config-server.mjs
```

然后打开：

```text
http://127.0.0.1:8765/
```

页面会连接本地服务。点击“保存到 config.yaml”后，会直接写入：

```text
config.yaml
```

服务接口：

| 方法 | 路径 | 作用 |
|---|---|---|
| `GET` | `/` | 打开配置页面 |
| `GET` | `/api/status` | 查看服务状态和配置文件路径 |
| `GET` | `/api/config` | 读取 `config.yaml`、`config.json` 或示例配置 |
| `POST` | `/api/config` | 写入 `config.yaml` 或 `config.json` |

## 备用方式：静态 HTML

也可以直接打开 `config-editor.html`。

这种方式可以：

- 可视化编辑配置
- 实时预览 YAML / JSON
- 复制配置
- 下载 `config.yaml` / `config.json`
- 通过浏览器授权“另存为文件”

但纯静态 HTML 不能自动覆盖工作空间里的 `config.yaml`。

## 文件关系

- `config.schema.json`：配置结构约束
- `config.example.yaml`：示例配置
- `config.yaml`：实际用户配置
- `config-editor.html`：可视化页面
- `config-server.mjs`：本地保存服务

## 安全说明

- 页面和服务只绑定 `127.0.0.1`。
- 配置文件不应保存 token、密码、密钥明文。
- 凭证只记录环境变量名，例如 `BIBI_API_TOKEN`。
