# Onboarding 测试手册

这份文档用于把当前工作区当成一个**首次安装的 Skill 项目**来测试。

目标不是验证“作者自己的配置还能不能用”，而是验证：

1. 没有真实 `config.yaml` 时，系统会不会正确进入 onboarding
2. 新用户保存配置后，是否会同时生成：
   - `config.yaml`
   - `USER.md`
   - `memory/YYYY-MM-DD.md`
3. Skill 运行时是否会读取新用户配置，而不是误用模板或旧用户信息

---

## 0. 测试范围

本轮重点测试以下内容：

- 对话式 onboarding 模板行为
- 可选配置编辑器和本地保存服务
- `config.yaml` 生成
- `USER.md` 自动摘要生成
- `memory/YYYY-MM-DD.md` 自动日志生成
- 默认 `知识结构/` 四分区是否存在
- `content-hot-tracker` 的运行时配置读取

本轮**不要求**测试：

- BibiGPT 真实总结能力
- 飞书 / Notion 真实 API 写入
- 定时自动化任务

这些可以放到下一轮做。

---

## 1. 准备一个干净副本

不要直接在当前工作区做“首次用户”测试。

在终端执行：

```bash
scripts/install_workspace.sh /tmp/workspace1.8-onboarding-test
rm -f /tmp/workspace1.8-onboarding-test/config.yaml
rm -f /tmp/workspace1.8-onboarding-test/config.json
find /tmp/workspace1.8-onboarding-test/memory -maxdepth 1 -type f -delete 2>/dev/null || true
```

### 预期结果

- `config.yaml` 不存在
- `config.json` 不存在
- `config.example.yaml` 仍然存在
- `USER.md` 存在，且内容是示例模板，不是具体用户
- `知识结构/知识体系`、`知识结构/竞品素材`、`知识结构/热点素材`、`知识结构/历史文章` 存在

可选检查：

```bash
ls /tmp/workspace1.8-onboarding-test
find /tmp/workspace1.8-onboarding-test/知识结构 -maxdepth 2 -type d | sort
sed -n '1,40p' /tmp/workspace1.8-onboarding-test/USER.md
```

---

## 2. 先验证“无配置时不能直接跑”

在干净副本里直接运行：

```bash
python3 /tmp/workspace1.8-onboarding-test/skills/content-hot-tracker/rebang_fetcher.py weibo
```

### 预期结果

输出应类似：

```text
配置缺失：No runtime config found. Start chat onboarding first...
```

### 通过标准

- 不能直接跑成功
- 不能偷偷读取 `config.example.yaml` 当成真实用户配置

---

## 3. 对话式 onboarding 主路径

不要先启动网页服务。按 `references/chat-onboarding.md` 在对话里完成 6 个问题，确认摘要后写入 `config.yaml`、`USER.md` 和当天 memory。

### 通过标准

- 用户不打开网页也能完成 onboarding
- `storage.workspaces[0].base_path` 默认是 `./知识结构`
- 默认路由包含 `knowledge_system`、`hot_topics`、`competitors`、`published` 和 `historical_articles`

---

## 4. 可选：启动本地配置服务

执行：

```bash
CONFIG_EDITOR_PORT=8765 node /tmp/workspace1.8-onboarding-test/config-server.mjs
```

看到类似输出即可：

```text
Config editor running at http://127.0.0.1:8765/
Saving YAML to /private/tmp/workspace1.8-onboarding-test/config.yaml
```

然后在浏览器打开：

```text
http://127.0.0.1:8765/
```

---

## 5. 以“全新用户”身份填写 onboarding

这一轮**不要**填和当前作者相似的信息。

建议刻意用一套完全不同的案例，例如：

- 用户称呼：林夏
- 身份：独立研究者 / 播客作者
- 协作角色：写作教练
- 存储方式：Obsidian 或本地 Markdown
- 账号方向：城市观察 / 知识工作 / 长文写作

### 建议重点填写字段

#### 基本信息

- `user.display_name`
- `user.bio`
- `assistant.role`

#### 账号矩阵

- 至少 1 个账号
- 填好：
  - `accounts[].id`
  - `accounts[].name`
  - `accounts[].positioning`

#### 内容存储

- 明确选一个与旧用户不同的路径
- 推荐测试：
  - `storage.default_provider = obsidian`
  - 或 `storage.default_provider = local`

至少要有：

- 1 个 workspace
- 1 个 route

#### 工作流

- `content_workflow.default_account_id`

#### Onboarding 状态

保存前确认：

- `onboarding.completed = true`
- `onboarding.missing_fields = []`

---

## 5. 点击保存

在配置页面点击：

```text
保存到 config.yaml
```

---

## 6. 保存后检查三个产物

### 6.1 检查 config.yaml

```bash
sed -n '1,220p' /private/tmp/workspace1.8-onboarding-test/config.yaml
```

### 预期结果

- 出现你刚才填写的新用户资料
- 不应再出现旧用户的人设和存储位置

重点看：

- `user.display_name`
- `assistant.role`
- `storage.default_provider`
- `accounts`

---

### 6.2 检查 USER.md

```bash
sed -n '1,220p' /private/tmp/workspace1.8-onboarding-test/USER.md
```

### 预期结果

它应该已经从“示例模板”变成“当前用户画像摘要”。

应该看到类似：

- 当前用户称呼
- 身份概述
- 主要项目或账号
- 协作方式
- 存储方式摘要

### 不应出现

- 示例用户
- 模板说明段落仍然完整保留
- token / 密钥 / 私密 ID

---

### 6.3 检查 memory 日志

```bash
find /private/tmp/workspace1.8-onboarding-test/memory -maxdepth 1 -type f | sort
sed -n '1,220p' /private/tmp/workspace1.8-onboarding-test/memory/$(date +%F).md
```

如果你的本地时区和文件日期不一致，也可以直接手动列出文件名后再打开。

### 预期结果

应新增一份当天日期的 onboarding 日志，内容至少包含：

- 已生成真实 `config.yaml`
- 默认存储方式
- 主要存储位置
- 已同步生成 `USER.md`
- 缺失字段情况

---

## 7. 再做运行时反向验证

### 7.1 验证简单命令

```bash
python3 /private/tmp/workspace1.8-onboarding-test/skills/content-hot-tracker/rebang_fetcher.py list
```

### 预期结果

列出支持平台，不报配置错误。

---

### 7.2 验证真实读取配置后执行

```bash
python3 /private/tmp/workspace1.8-onboarding-test/skills/content-hot-tracker/rebang_fetcher.py weibo
```

### 预期结果

- 可以正常运行
- 不再报“缺少配置”
- 说明运行时已经接受这份新用户配置

---

## 8. 可选：做 schema 校验

如果要更严一点，可以执行：

```bash
python3 - <<'PY'
import json, yaml
from jsonschema import Draft202012Validator
schema = json.load(open('/tmp/workspace1.8-onboarding-test/config.schema.json', encoding='utf-8'))
config = yaml.safe_load(open('/tmp/workspace1.8-onboarding-test/config.yaml', encoding='utf-8'))
errors = sorted(Draft202012Validator(schema).iter_errors(config), key=lambda e: list(e.path))
print('schema_errors', len(errors))
for e in errors:
    print('/'.join(map(str, e.path)) or '<root>', '-', e.message)
PY
```

### 预期结果

```text
schema_errors 0
```

---

## 9. 测试通过标准

这轮测试通过，至少要满足以下 6 条：

1. 无 `config.yaml` 时，skill 会阻止执行并要求 onboarding
2. 配置页面能成功保存新的 `config.yaml`
3. `config.yaml` 内容是新用户信息，不是旧用户残留
4. `USER.md` 自动从模板变成当前用户画像摘要
5. `memory/YYYY-MM-DD.md` 自动生成 onboarding 日志
6. 保存后 skill 命令可以正常运行

---

## 10. 测试失败时优先记录什么

如果有异常，优先记录这几项：

- 你填的是哪类用户画像
- 你选的是本地存储还是云端存储
- 点击保存后，哪个文件没更新
- `config.yaml` 是否生成
- `USER.md` 是否仍停留在模板
- `memory/` 是否没生成当天日志
- 终端错误信息原文

---

## 11. 测完后清理

如果只是临时测试，可以删掉副本：

```bash
rm -rf /tmp/workspace1.8-onboarding-test
```

如果要保留现场，建议把它留着，方便对照修改前后行为。
