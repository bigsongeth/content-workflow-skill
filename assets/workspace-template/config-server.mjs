#!/usr/bin/env node
import { createServer } from "node:http";
import { readFile, writeFile, access, mkdir, rm } from "node:fs/promises";
import { constants } from "node:fs";
import { extname, join, normalize, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { tmpdir } from "node:os";
import { randomUUID } from "node:crypto";

const rootDir = resolve(fileURLToPath(new URL(".", import.meta.url)));
const port = Number(process.env.CONFIG_EDITOR_PORT || 8765);
const execFileAsync = promisify(execFile);

const files = {
  html: join(rootDir, "config-editor.html"),
  yaml: join(rootDir, "config.yaml"),
  exampleYaml: join(rootDir, "config.example.yaml"),
  json: join(rootDir, "config.json"),
  user: join(rootDir, "USER.md"),
  memoryDir: join(rootDir, "memory")
};

const contentTypes = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".yaml": "text/yaml; charset=utf-8",
  ".yml": "text/yaml; charset=utf-8"
};

function send(res, status, body, type = "text/plain; charset=utf-8") {
  res.writeHead(status, {
    "Content-Type": type,
    "Cache-Control": "no-store",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type"
  });
  res.end(body);
}

function sendJson(res, status, data) {
  send(res, status, JSON.stringify(data, null, 2), "application/json; charset=utf-8");
}

async function exists(path) {
  try {
    await access(path, constants.F_OK);
    return true;
  } catch {
    return false;
  }
}

async function readConfigSource() {
  if (await exists(files.yaml)) {
    return { path: files.yaml, format: "yaml", content: await readFile(files.yaml, "utf8") };
  }
  if (await exists(files.json)) {
    return { path: files.json, format: "json", content: await readFile(files.json, "utf8") };
  }
  return { path: files.exampleYaml, format: "yaml", content: await readFile(files.exampleYaml, "utf8"), example: true };
}

async function readBody(req) {
  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  return Buffer.concat(chunks).toString("utf8");
}

function safeStaticPath(urlPath) {
  const decoded = decodeURIComponent(urlPath);
  const target = decoded === "/" ? files.html : join(rootDir, decoded);
  const normalized = normalize(target);
  if (!normalized.startsWith(rootDir)) return null;
  return normalized;
}

function todayInShanghai() {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Shanghai",
    year: "numeric",
    month: "2-digit",
    day: "2-digit"
  }).format(new Date());
}

async function parseConfigContent(format, content) {
  const tempPath = join(tmpdir(), `content-agent-config-${randomUUID()}.${format === "json" ? "json" : "yaml"}`);
  const parser = `
import json, sys
if sys.argv[1] == "json":
    with open(sys.argv[2], "r", encoding="utf-8") as handle:
        data = json.load(handle)
else:
    import yaml
    with open(sys.argv[2], "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
print(json.dumps(data or {}, ensure_ascii=False))
`;
  await writeFile(tempPath, content, "utf8");
  try {
    const { stdout } = await execFileAsync("python3", ["-c", parser, format, tempPath], {
      maxBuffer: 1024 * 1024 * 5
    });
    return JSON.parse(stdout);
  } finally {
    await rm(tempPath, { force: true });
  }
}

function list(items) {
  return Array.isArray(items) ? items.filter(Boolean) : [];
}

function summarizeStorage(config) {
  const provider = config?.storage?.default_provider || "unknown";
  const workspaces = list(config?.storage?.workspaces);
  if (!workspaces.length) {
    return `默认存储方式：${provider}`;
  }
  const workspaceNames = workspaces
    .map(item => item?.name || item?.id)
    .filter(Boolean)
    .join("、");
  return `默认存储方式：${provider}；主要位置：${workspaceNames}`;
}

function summarizeAccounts(config) {
  const accounts = list(config?.accounts);
  if (!accounts.length) {
    return ["- **主要项目或账号：** 待补充"];
  }
  const lines = ["- **主要项目或账号：**"];
  accounts.forEach((account, index) => {
    const name = account?.name || `账号 ${index + 1}`;
    const positioning = account?.positioning || "待补充";
    lines.push(`  - ${name}：${positioning}`);
  });
  return lines;
}

function summarizeInteraction(config) {
  const role = config?.assistant?.role || "待补充";
  const styles = list(config?.assistant?.interaction_style);
  const rules = list(config?.assistant?.communication_rules);
  return {
    role,
    styles: styles.length ? styles.join("、") : "待补充",
    rules: rules.length ? rules.join("；") : "待补充"
  };
}

function summarizeSensitiveActions(config) {
  const actions = list(config?.permissions?.require_confirmation_for);
  return actions.length ? actions.join("、") : "待补充";
}

function renderUserProfile(config) {
  const displayName = config?.user?.display_name || "未命名用户";
  const bio = config?.user?.bio || "待补充";
  const location = config?.user?.location || "未设置";
  const interaction = summarizeInteraction(config);
  const storageSummary = summarizeStorage(config);
  const sensitiveActions = summarizeSensitiveActions(config);

  return `# USER.md - 当前用户画像

> 本文件由 onboarding 生成，保留对协作真正有帮助的摘要。
> 运行时的结构化事实仍以仓库根目录 \`config.yaml\` 为准。

## 用户是谁

- **称呼：** ${displayName}
- **身份概述：** ${bio}
- **所在地或内容 base：** ${location}

## 用户在做什么

${summarizeAccounts(config).join("\n")}

## 用户希望我怎么协作

- **希望我扮演的角色：** ${interaction.role}
- **喜欢的风格：** ${interaction.styles}
- **沟通规则摘要：** ${interaction.rules}

## 知识库与资料习惯

- **${storageSummary}**
- **是否依赖云端 API：** ${providerNeedsApi(config) ? "是" : "否 / 未指定"}

## 需要长期记住的事

- 涉及这些敏感动作时先确认：${sensitiveActions}
- 不在公开内容中暴露用户私密备注、密钥或账户敏感信息
- 更细的结构化设置放在 \`config.yaml\`，这里只保留摘要
`;
}

function providerNeedsApi(config) {
  const provider = config?.storage?.default_provider;
  return ["feishu", "notion", "google_drive", "other"].includes(provider);
}

function renderMemoryEntry(config) {
  const displayName = config?.user?.display_name || "未命名用户";
  const provider = config?.storage?.default_provider || "unknown";
  const missingFields = list(config?.onboarding?.missing_fields);
  const workspaces = list(config?.storage?.workspaces)
    .map(item => item?.name || item?.id)
    .filter(Boolean)
    .join("、") || "未设置";

  const lines = [
    `# ${todayInShanghai()} Onboarding 日志`,
    "",
    "## 本次完成",
    "",
    `- 已为用户「${displayName}」生成真实 config.yaml`,
    `- 已确认默认存储方式：${provider}`,
    `- 已记录主要存储位置：${workspaces}`,
    `- 已同步生成 USER.md 摘要`,
    ""
  ];

  if (missingFields.length) {
    lines.push("## 待补字段", "");
    missingFields.forEach(field => lines.push(`- ${field}`));
    lines.push("");
  } else {
    lines.push("## 待补字段", "", "- 当前没有待补字段。", "");
  }

  lines.push("## 说明", "", "- 本日志由 onboarding 保存流程自动生成。", "");
  return lines.join("\n");
}

async function updateUserArtifacts(config) {
  await writeFile(files.user, `${renderUserProfile(config).trim()}\n`, "utf8");
  await mkdir(files.memoryDir, { recursive: true });
  const memoryPath = join(files.memoryDir, `${todayInShanghai()}.md`);
  await writeFile(memoryPath, `${renderMemoryEntry(config).trim()}\n`, "utf8");
  return { userPath: files.user, memoryPath };
}

async function handleApi(req, res, pathname) {
  if (req.method === "OPTIONS") {
    send(res, 204, "");
    return;
  }

  if (pathname === "/api/status" && req.method === "GET") {
    sendJson(res, 200, {
      ok: true,
      rootDir,
      configPath: files.yaml,
      hasConfigYaml: await exists(files.yaml),
      hasConfigJson: await exists(files.json)
    });
    return;
  }

  if (pathname === "/api/config" && req.method === "GET") {
    const source = await readConfigSource();
    const parsedConfig = await parseConfigContent(source.format, source.content);
    sendJson(res, 200, {
      ok: true,
      format: source.format,
      path: source.path,
      example: Boolean(source.example),
      content: source.content,
      config: parsedConfig
    });
    return;
  }

  if (pathname === "/api/config" && req.method === "POST") {
    const rawBody = await readBody(req);
    let payload;
    try {
      payload = JSON.parse(rawBody);
    } catch {
      sendJson(res, 400, { ok: false, error: "Request body must be JSON." });
      return;
    }

    const format = payload.format === "json" ? "json" : "yaml";
    const content = typeof payload.content === "string" ? payload.content : "";
    if (!content.trim()) {
      sendJson(res, 400, { ok: false, error: "Config content is empty." });
      return;
    }

    const parsedConfig = await parseConfigContent(format, content);
    const targetPath = format === "json" ? files.json : files.yaml;
    await writeFile(targetPath, content.endsWith("\n") ? content : `${content}\n`, "utf8");
    const artifacts = await updateUserArtifacts(parsedConfig);
    sendJson(res, 200, {
      ok: true,
      format,
      path: targetPath,
      bytes: Buffer.byteLength(content, "utf8"),
      userPath: artifacts.userPath,
      memoryPath: artifacts.memoryPath
    });
    return;
  }

  sendJson(res, 404, { ok: false, error: "API route not found." });
}

const server = createServer(async (req, res) => {
  try {
    const url = new URL(req.url || "/", `http://${req.headers.host || "localhost"}`);
    if (url.pathname.startsWith("/api/")) {
      await handleApi(req, res, url.pathname);
      return;
    }

    const path = safeStaticPath(url.pathname);
    if (!path) {
      send(res, 403, "Forbidden");
      return;
    }

    const body = await readFile(path);
    send(res, 200, body, contentTypes[extname(path)] || "application/octet-stream");
  } catch (error) {
    if (error.code === "ENOENT") {
      send(res, 404, "Not found");
      return;
    }
    console.error(error);
    sendJson(res, 500, { ok: false, error: error.message || "Internal server error." });
  }
});

server.listen(port, "127.0.0.1", () => {
  console.log(`Config editor running at http://127.0.0.1:${port}/`);
  console.log(`Saving YAML to ${files.yaml}`);
});
