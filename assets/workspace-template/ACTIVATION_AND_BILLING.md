# Activation and Billing Flow

这个文档定义“卖出去的技能”如何和付费 Token 结合。

## 核心原则

1. 用户买的是内容工作流服务，不是上游 API。
2. 使用我们发放的 `CONTENT_GATEWAY_API_KEY` 是推荐路径，但不是强制路径。高级用户也可以选择自建网关/自备上游服务。
3. 默认客户侧只保存我们发放的 `CONTENT_GATEWAY_API_KEY`；上游 Token 和上游 URL 只存在于我们的网关服务器。
4. 如果用户选择自建服务，只提示“可配置自建网关地址和 Token”，不要在普通 onboarding 里展开部署细节，因为自建成本较高。
5. Token 到期、无效、额度用完时，技能必须返回人能理解、Agent 能处理的结构化错误。

## 推荐用户流程

1. 用户购买套餐。
2. 我们发放一个 Token/激活码。
3. 用户首次运行技能。
4. Agent 先读取上下文，给出用户画像草稿。
5. Agent 推荐用户粘贴我们提供的 Token；同时轻量说明“如果你有自建网关，也可以填自己的服务地址”。
6. Agent 调用 `GET /v1/entitlements/me` 验证。
7. 验证成功后写入本地配置。
8. 如果用户暂时跳过激活，则只完成基础配置，并提示付费能力稍后再激活。
9. Agent 立刻跑一次低成本 demo，比如获取微博热榜前 5 条。

## Token 状态与返回

### 1. 未提供或无效

HTTP 401

```json
{
  "success": false,
  "error": "missing_or_invalid_api_key",
  "error_type": "billing",
  "title": "需要激活内容工作流",
  "message": "我还没有检测到有效的激活码。请粘贴你购买后收到的 Token/激活码；如果还没购买，可以打开价格页选择套餐。",
  "suggested_action": "activate_or_purchase",
  "renewal_url": "微信 isjuss"
}
```

Agent 话术：

```text
我还没检测到有效激活码。
请粘贴你购买后收到的 Token，我会帮你验证套餐。
```

### 2. 已到期

HTTP 402

```json
{
  "success": false,
  "error": "subscription_expired",
  "error_type": "billing",
  "title": "订阅已到期",
  "message": "你的内容工作流订阅已经到期，所以热榜和音视频转写暂时不可用。续费后原来的配置和资料不会丢。",
  "suggested_action": "renew",
  "renewal_url": "微信 isjuss"
}
```

Agent 话术：

```text
你的订阅到期了，所以我暂时不能继续使用热榜和音视频转写。
之前的账号配置、知识库路径、历史文档都还在。续费后可以直接接着用。

可选：月付 25 元 / 年付 199 元 / 买断 599 元。
```

### 3. 授权未激活

HTTP 402，`subscription_inactive`。

可能原因：未付款、退款、风控暂停、后台未开通。

Agent 不要反复重试，应提示联系支持或重新购买。

### 4. 套餐不包含功能

HTTP 403，`feature_not_in_plan`。

Agent 应提示升级，不要把它说成系统故障。

### 5. 额度用完

HTTP 429，`quota_exceeded`。

Agent 应说明“不是坏了，是本期额度用完”，然后给等待/升级/加购选择。

## 配置字段

```yaml
integrations:
  content_gateway:
    enabled: true
    base_url: http://fm.rainplay.cn:26056
    credential_env: CONTENT_GATEWAY_API_KEY
    activation_status: active
    plan: monthly
    expires_at: 2026-06-07
```

## 体验细节

- 不要把 Token 叫 API Key，面向用户叫“激活码”。
- Token 验证成功后，立刻跑一次 demo，让用户感受到购买价值。
- 到期只停付费能力，不删除用户配置。
- 所有计费错误都必须返回 `error_type: billing`，方便 Agent 分流处理。
