# LEARNINGS.md - 教训与发现

## Onboarding 设计

### ✅ LRN-20260505-001: 交付验收 checklist 不应写进用户使用文档
**类别**：correction

**问题**：用户要求“每次交付时提供 checklist”，目的是让用户验收我的工作质量，不是让最终使用 Skill 的用户看到。因此不应把这类 checklist 写进 `ONBOARDING_FLOW.md`。

**修正**：验收 checklist 放在最终回复里；面向 Skill 用户的文档只保留 onboarding 流程、问题、选项、字段映射和确认逻辑。

### ✅ LRN-20260505-002: 小白 onboarding 不能只用开放式问答
**类别**：correction

**问题**：纯开放式问题对没有技术或运营经验的用户不够友好，用户不知道该怎么回答。

**修正**：每个关键问题都应提供内置选项，并保留“自定义/其他”输入。程序运行时优先展示单选、多选或按钮，用户不满意选项时再自由填写。

## 飞书交互（重要！）

### ✅ 2026-04-29: feishu_ask_user_question 是唯一可靠的交互方式
**问题**：之前尝试用 message 工具发 raw interactive card，经常格式不对失败；button 没有 callback 机制，点击无法触达我。

**解决方案**：用 `feishu_ask_user_question` 工具，它会渲染成飞书原生下拉选择卡片，用户选完后直接发消息给我，整个流程零配置、零回调。

**适用场景**：
- 多选题（选题方向勾选）
- 单选题（选一个内容方向）
- 下拉菜单形式的收集用户偏好

**不适用**：
- 需要实时回调的业务（如审批流、任务状态变更）
- 需要 webhook 通知的场景（需要企业自建应用）

---

## Content Hot Tracker 技术踩坑

### ✅ 2026-04-29: rebang.today API list 字段是 JSON 字符串
**问题**：fetch_all 返回的 data["list"] 是 string 类型不是 list，直接遍历失败，导致 generate_content_suggestions 匹配结果为0。

**解决**：在 `generate_content_suggestions` 和 `format_items` 函数里，对 raw 做 json.loads 防御。

---

## 工具使用

### ✅ 2026-04-29: exec curl 比 web_crawl 更可靠
当 web_crawl 遇到限流时，直接用 curl 可以绕过，且返回原始数据更完整。

### ✅ 2026-04-29: requests 比 urllib 更好用
本地 requests 库有更好的超时管理和重试逻辑。
