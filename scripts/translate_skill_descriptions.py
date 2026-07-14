#!/usr/bin/env python3
"""
Translate all SKILL.md descriptions from English to Simplified Chinese.

Applies translations to BOTH:
  1. Source: hermes-agent/skills/ (bundled, used to seed new installs)
  2. Runtime: data/skills/ (mounted as ~/.hermes/skills/ in container)

The translations dict maps exact English description → Chinese.
Multi-line YAML descriptions (|) are handled specially.
"""

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path("/workspaces/Hermes_offline_v2_subversion")

# ── Translation Mapping ───────────────────────────────────────────────────────
# Each entry: exact English description → Simplified Chinese
TRANSLATIONS = {
    # apple
    "Manage Apple Notes via memo CLI: create, search, edit.":
        "通过 memo CLI 管理 Apple 备忘录：创建、搜索、编辑。",
    "Apple Reminders via remindctl: add, list, complete.":
        "通过 remindctl 管理 Apple 提醒事项：添加、列表、完成。",
    "Track Apple devices/AirTags via FindMy.app on macOS.":
        "通过 macOS 上的 FindMy.app 追踪 Apple 设备/AirTag。",
    "Send and receive iMessages/SMS via the imsg CLI on macOS.":
        "通过 macOS 上的 imsg CLI 发送和接收 iMessage/SMS。",
    "Drive the macOS desktop in the background — screenshots, mouse, keyboard, scroll, drag — without stealing the user's cursor, keyboard focus, or Space. Works with any tool-capable model. Load this skill whenever the `computer_use` tool is available.":
        "在后台驱动 macOS 桌面——截图、鼠标、键盘、滚动、拖拽——不会抢占用户的光标、键盘焦点或桌面空间。适用于任何支持工具的模型。当 `computer_use` 工具可用时加载此技能。",

    # autonomous-ai-agents
    "Delegate coding to Claude Code CLI (features, PRs).":
        "将编码任务委托给 Claude Code CLI（功能开发、PR）。",
    "Delegate coding to OpenAI Codex CLI (features, PRs).":
        "将编码任务委托给 OpenAI Codex CLI（功能开发、PR）。",
    "Configure, extend, or contribute to Hermes Agent.":
        "配置、扩展 Hermes Agent 或为其贡献代码。",
    "Delegate coding to OpenCode CLI (features, PR review).":
        "将编码任务委托给 OpenCode CLI（功能开发、PR 审查）。",

    # creative
    "Dark-themed SVG architecture/cloud/infra diagrams as HTML.":
        "以 HTML 形式生成暗色主题的 SVG 架构/云/基础设施图表。",
    "ASCII art: pyfiglet, cowsay, boxes, image-to-ascii.":
        "ASCII 艺术：pyfiglet、cowsay、boxes、图片转 ASCII。",
    "ASCII video: convert video/audio to colored ASCII MP4/GIF.":
        "ASCII 视频：将视频/音频转换为彩色 ASCII MP4/GIF。",
    "Knowledge comics (知识漫画): educational, biography, tutorial.":
        "知识漫画：教育、传记、教程类知识漫画创作。",
    "Infographics: 21 layouts x 21 styles (信息图, 可视化).":
        "信息图：21 种布局 × 21 种风格（信息图、可视化）。",
    "Design one-off HTML artifacts (landing, deck, prototype).":
        "设计一次性 HTML 作品（落地页、幻灯片、原型）。",
    "Generate images, video, and audio with ComfyUI — install, launch, manage nodes/models, run workflows with parameter injection. Uses the official comfy-cli for lifecycle and direct REST/WebSocket API for execution.":
        "使用 ComfyUI 生成图像、视频和音频——安装、启动、管理节点/模型、通过参数注入运行工作流。使用官方 comfy-cli 管理生命周期，通过 REST/WebSocket API 直接执行。",
    "Generate project ideas via creative constraints.":
        "通过创意约束条件生成项目创意。",
    "Author/validate/export Google's DESIGN.md token spec files.":
        "创作/验证/导出 Google DESIGN.md 设计令牌规范文件。",
    "Hand-drawn Excalidraw JSON diagrams (arch, flow, seq).":
        "手绘风格的 Excalidraw JSON 图表（架构图、流程图、时序图）。",
    "Humanize text: strip AI-isms and add real voice.":
        "人性化文本：去除 AI 痕迹，赋予真实人声风格。",
    "Manim CE animations: 3Blue1Brown math/algo videos.":
        "Manim CE 动画：制作 3Blue1Brown 风格的数学/算法视频。",
    "p5.js sketches: gen art, shaders, interactive, 3D.":
        "p5.js 草图：生成艺术、着色器、交互式、3D 作品。",
    "Pixel art w/ era palettes (NES, Game Boy, PICO-8).":
        "像素艺术：使用各时代调色板（NES、Game Boy、PICO-8）。",
    "54 real design systems (Stripe, Linear, Vercel) as HTML/CSS.":
        "54 个真实设计系统（Stripe、Linear、Vercel）的 HTML/CSS 复刻。",
    "Use when building creative browser demos with @chenglou/pretext — DOM-free text layout for ASCII art, typographic flow around obstacles, text-as-geometry games, kinetic typography, and text-powered generative art. Produces single-file HTML demos by default.":
        "使用 @chenglou/pretext 构建创意浏览器演示——无 DOM 的文本布局，用于 ASCII 艺术、围绕障碍物的排版流动、文字几何游戏、动态排版和文本驱动的生成艺术。默认生成单文件 HTML 演示。",
    "Throwaway HTML mockups: 2-3 design variants to compare.":
        "快速 HTML 原型：生成 2-3 个设计变体用于比较。",
    "Songwriting craft and Suno AI music prompts.":
        "歌曲创作技巧与 Suno AI 音乐提示词。",
    "Control a running TouchDesigner instance via twozero MCP — create operators, set parameters, wire connections, execute Python, build real-time visuals. 36 native tools.":
        "通过 twozero MCP 控制运行中的 TouchDesigner 实例——创建算子、设置参数、连接节点、执行 Python、构建实时视觉效果。提供 36 个原生工具。",
    "Architectural minimalism meets journalistic gravitas.":
        "建筑极简主义与新闻庄重感的融合设计。",

    # data-science
    "Iterative Python via live Jupyter kernel (hamelnb).":
        "通过实时 Jupyter 内核进行交互式 Python 编程（hamelnb）。",

    # devops
    "Decomposition playbook + specialist-roster conventions + anti-temptation rules for an orchestrator profile routing work through Kanban. The \"don't do the work yourself\" rule and the basic lifecycle are auto-injected into every kanban worker's system prompt; this skill is the deeper playbook when you're specifically playing the orchestrator role.":
        "分解策略手册 + 专家角色约定 + 反诱惑规则，用于通过看板路由工作的编排器配置文件。「不要自己干活的」规则和基本生命周期会自动注入到每个看板工作器的系统提示中；此技能是专门充当编排器角色时的深度策略手册。",
    "Pitfalls, examples, and edge cases for Hermes Kanban workers. The lifecycle itself is auto-injected into every worker's system prompt as KANBAN_GUIDANCE (from agent/prompt_builder.py); this skill is what you load when you want deeper detail on specific scenarios.":
        "Hermes 看板工作器的陷阱、示例和边界情况。生命周期本身作为 KANBAN_GUIDANCE 自动注入到每个工作器的系统提示中（来自 agent/prompt_builder.py）；此技能用于需要深入了解特定场景细节时加载。",
    "Webhook subscriptions: event-driven agent runs.":
        "Webhook 订阅：事件驱动的代理运行。",

    # dogfood
    "Exploratory QA of web apps: find bugs, evidence, reports.":
        "Web 应用探索性 QA：发现 Bug、收集证据、生成报告。",

    # email
    "Himalaya CLI: IMAP/SMTP email from terminal.":
        "Himalaya CLI：从终端管理 IMAP/SMTP 电子邮件。",

    # gaming
    "Host modded Minecraft servers (CurseForge, Modrinth).":
        "托管模组化 Minecraft 服务器（CurseForge、Modrinth）。",
    "Play Pokemon via headless emulator + RAM reads.":
        "通过无头模拟器 + RAM 读取来游玩宝可梦。",

    # github
    "Inspect codebases w/ pygount: LOC, languages, ratios.":
        "使用 pygount 检查代码库：代码行数、语言、比例。",
    "GitHub auth setup: HTTPS tokens, SSH keys, gh CLI login.":
        "GitHub 认证设置：HTTPS 令牌、SSH 密钥、gh CLI 登录。",
    "Review PRs: diffs, inline comments via gh or REST.":
        "审查 PR：通过 gh 或 REST API 查看差异、添加行内评论。",
    "Create, triage, label, assign GitHub issues via gh or REST.":
        "通过 gh 或 REST API 创建、分类、标记、分配 GitHub Issues。",
    "GitHub PR lifecycle: branch, commit, open, CI, merge.":
        "GitHub PR 全生命周期：创建分支、提交、发起 PR、CI 检查、合并。",
    "Clone/create/fork repos; manage remotes, releases.":
        "克隆/创建/Fork 仓库；管理远程仓库和版本发布。",

    # mcp
    "MCP client: connect servers, register tools (stdio/HTTP).":
        "MCP 客户端：连接服务器、注册工具（stdio/HTTP）。",

    # media
    "Search/download GIFs from Tenor via curl + jq.":
        "通过 curl + jq 从 Tenor 搜索/下载 GIF。",
    "HeartMuLa: Suno-like song generation from lyrics + tags.":
        "HeartMuLa：基于歌词和标签的类 Suno 歌曲生成。",
    "Audio spectrograms/features (mel, chroma, MFCC) via CLI.":
        "通过 CLI 生成音频频谱图/特征（梅尔频谱、色度、MFCC）。",
    "Spotify: play, search, queue, manage playlists and devices.":
        "Spotify：播放、搜索、队列管理、播放列表和设备管理。",
    "YouTube transcripts to summaries, threads, blogs.":
        "将 YouTube 字幕转换为摘要、推文线程、博客文章。",

    # mlops
    "lm-eval-harness: benchmark LLMs (MMLU, GSM8K, etc.).":
        "lm-eval-harness：评估 LLM 基准测试（MMLU、GSM8K 等）。",
    "W&B: log ML experiments, sweeps, model registry, dashboards.":
        "W&B：记录 ML 实验、超参数搜索、模型注册、仪表板。",
    "HuggingFace hf CLI: search/download/upload models, datasets.":
        "HuggingFace hf CLI：搜索/下载/上传模型和数据集。",
    "llama.cpp local GGUF inference + HF Hub model discovery.":
        "llama.cpp 本地 GGUF 推理 + HuggingFace Hub 模型发现。",
    "OBLITERATUS: abliterate LLM refusals (diff-in-means).":
        "OBLITERATUS：消除 LLM 拒绝回答的倾向（均值差法）。",
    "Outlines: structured JSON/regex/Pydantic LLM generation.":
        "Outlines：结构化 JSON/正则表达式/Pydantic 约束的 LLM 生成。",
    "vLLM: high-throughput LLM serving, OpenAI API, quantization.":
        "vLLM：高吞吐量 LLM 推理服务，兼容 OpenAI API，支持量化。",
    "AudioCraft: MusicGen text-to-music, AudioGen text-to-sound.":
        "AudioCraft：MusicGen 文本转音乐、AudioGen 文本转音效。",
    "SAM: zero-shot image segmentation via points, boxes, masks.":
        "SAM：通过点、框、掩码进行零样本图像分割。",
    "DSPy: declarative LM programs, auto-optimize prompts, RAG.":
        "DSPy：声明式语言模型编程，自动优化提示词和 RAG 流程。",
    "Axolotl: YAML LLM fine-tuning (LoRA, DPO, GRPO).":
        "Axolotl：基于 YAML 配置的 LLM 微调（LoRA、DPO、GRPO）。",
    "TRL: SFT, DPO, PPO, GRPO, reward modeling for LLM RLHF.":
        "TRL：SFT、DPO、PPO、GRPO、奖励建模等 LLM RLHF 训练方法。",
    "Unsloth: 2-5x faster LoRA/QLoRA fine-tuning, less VRAM.":
        "Unsloth：2-5 倍加速 LoRA/QLoRA 微调，更低显存占用。",

    # note-taking
    "Read, search, create, and edit notes in the Obsidian vault.":
        "在 Obsidian 仓库中阅读、搜索、创建和编辑笔记。",

    # productivity
    "Airtable REST API via curl. Records CRUD, filters, upserts.":
        "通过 curl 调用 Airtable REST API：记录的增删改查、过滤、更新插入。",
    "Gmail, Calendar, Drive, Docs, Sheets via gws CLI or Python.":
        "通过 gws CLI 或 Python 管理 Gmail、日历、云端硬盘、文档、表格。",
    "Linear: manage issues, projects, teams via GraphQL + curl.":
        "Linear：通过 GraphQL + curl 管理 Issues、项目、团队。",
    "Geocode, POIs, routes, timezones via OpenStreetMap/OSRM.":
        "通过 OpenStreetMap/OSRM 进行地理编码、POI 查询、路线规划、时区查询。",
    "Edit PDF text/typos/titles via nano-pdf CLI (NL prompts).":
        "通过 nano-pdf CLI 使用自然语言编辑 PDF 文本/错别字/标题。",
    "Notion API via curl: pages, databases, blocks, search.":
        "通过 curl 调用 Notion API：页面、数据库、块、搜索。",
    "Extract text from PDFs/scans (pymupdf, marker-pdf).":
        "从 PDF/扫描件中提取文本（pymupdf、marker-pdf）。",
    "Create, read, edit .pptx decks, slides, notes, templates.":
        "创建、读取、编辑 .pptx 演示文稿、幻灯片、备注、模板。",
    "Operate the Teams meeting summary pipeline via Hermes CLI — summarize meetings, inspect pipeline status, replay jobs, manage Microsoft Graph subscriptions.":
        "通过 Hermes CLI 运行 Teams 会议摘要流水线——总结会议、检查流水线状态、重播任务、管理 Microsoft Graph 订阅。",

    # red-teaming
    "Jailbreak LLMs: Parseltongue, GODMODE, ULTRAPLINIAN.":
        "LLM 越狱测试：Parseltongue、GODMODE、ULTRAPLINIAN 技术。",

    # research
    "Search arXiv papers by keyword, author, category, or ID.":
        "按关键词、作者、分类或 ID 搜索 arXiv 论文。",
    "Monitor blogs and RSS/Atom feeds via blogwatcher-cli tool.":
        "通过 blogwatcher-cli 工具监控博客和 RSS/Atom 订阅源。",
    "Karpathy's LLM Wiki: build/query interlinked markdown KB.":
        "Karpathy 的 LLM Wiki：构建/查询互链的 Markdown 知识库。",
    "Query Polymarket: markets, prices, orderbooks, history.":
        "查询 Polymarket：市场、价格、订单簿、历史数据。",
    "Write ML papers for NeurIPS/ICML/ICLR: design→submit.":
        "撰写 ML 论文投稿 NeurIPS/ICML/ICLR：从设计到提交。",

    # smart-home
    "Control Philips Hue lights, scenes, rooms via OpenHue CLI.":
        "通过 OpenHue CLI 控制 Philips Hue 灯光、场景、房间。",

    # social-media
    "X/Twitter via xurl CLI: post, search, DM, media, v2 API.":
        "通过 xurl CLI 管理 X/Twitter：发布、搜索、私信、媒体、v2 API。",

    # software-development
    "Debug Hermes TUI slash commands: Python, gateway, Ink UI.":
        "调试 Hermes TUI 斜杠命令：Python、网关、Ink UI。",
    "Author in-repo SKILL.md: frontmatter, validator, structure.":
        "创作仓库内 SKILL.md：前置元数据、校验器、结构规范。",
    "Debug Node.js via --inspect + Chrome DevTools Protocol CLI.":
        "通过 --inspect + Chrome DevTools Protocol CLI 调试 Node.js。",
    "Plan mode: write markdown plan to .hermes/plans/, no exec.":
        "计划模式：将 Markdown 计划写入 .hermes/plans/ 目录，不执行任何操作。",
    "Debug Python: pdb REPL + debugpy remote (DAP).":
        "调试 Python：pdb REPL + debugpy 远程调试（DAP）。",
    "Pre-commit review: security scan, quality gates, auto-fix.":
        "提交前审查：安全扫描、质量门禁、自动修复。",
    "Throwaway experiments to validate an idea before build.":
        "快速实验：在正式构建前验证想法可行性。",
    "Execute plans via delegate_task subagents (2-stage review).":
        "通过 delegate_task 子代理执行计划（两阶段审查）。",
    "4-phase root cause debugging: understand bugs before fixing.":
        "四阶段根因调试：修复前先理解 Bug。",
    "TDD: enforce RED-GREEN-REFACTOR, tests before code.":
        "TDD：强制执行红-绿-重构循环，先写测试再写代码。",
    "Write implementation plans: bite-sized tasks, paths, code.":
        "编写实施计划：细粒度任务、文件路径、代码片段。",
    "Security-focused code review":
        "以安全为重点的代码审查",
    "Use when <trigger>. <one-line behavior>.":
        "当 <触发条件> 时使用。<一行行为描述>。",

    # yuanbao
    "Yuanbao (元宝) groups: @mention users, query info/members.":
        "元宝群组：@提及用户、查询信息/成员。",
}

# Multi-line descriptions (description: |)
# Key: skill relative path (without SKILL.md), Value: Chinese translation
MULTILINE_DESCRIPTIONS = {
    "apple/macos-computer-use": (
        "在后台驱动 macOS 桌面——截图、鼠标、键盘、滚动、拖拽——"
        "不会抢占用户的光标、键盘焦点或桌面空间。"
        "适用于任何支持工具的模型。当 `computer_use` 工具可用时加载此技能。"
    ),
}


def replace_description_in_file(filepath: Path, dry_run: bool = False) -> bool:
    """Replace the description field in a SKILL.md file. Returns True if changed."""
    content = filepath.read_text(encoding="utf-8")
    original = content

    # Parse frontmatter
    if not content.startswith("---"):
        return False

    # Find the full frontmatter block
    end_match = re.search(r'\n---\s*\n', content[3:])
    if not end_match:
        return False

    fm_start = 4  # after first "---\n"
    fm_end = 3 + end_match.start()
    fm_text = content[fm_start:fm_end]
    rest = content[fm_end + len(end_match.group(0)) - 1:]  # after closing ---

    # Get relative path for lookup
    try:
        rel_path = str(filepath.relative_to(PROJECT_ROOT))
    except ValueError:
        rel_path = str(filepath)

    # ── Handle multi-line descriptions (|) ──
    multi_match = re.search(r'^description:\s*\|', fm_text, re.MULTILINE)
    if multi_match:
        # Find this skill in MULTILINE_DESCRIPTIONS
        for key, trans in MULTILINE_DESCRIPTIONS.items():
            if key in rel_path or filepath.parent.name == key.split("/")[-1]:
                # Replace the multi-line description
                desc_start = multi_match.end()
                rest_of_fm = fm_text[desc_start:]
                next_field = re.search(r'^\w+:', rest_of_fm, re.MULTILINE)
                if next_field:
                    old_desc = rest_of_fm[:next_field.start()]
                    # Build new description block with proper indentation
                    new_desc_lines = trans.split("。")
                    # Keep the | style but with Chinese text
                    new_desc = "\n  " + "\n  ".join(line.strip() for line in trans.split("。") if line.strip())
                    # Actually just use single-line quoted format for simplicity
                    new_fm = fm_text[:multi_match.start()] + f'description: "{trans}"' + rest_of_fm[next_field.start():]
                    new_content = "---\n" + new_fm + "\n---" + rest
                    if new_content != original:
                        if not dry_run:
                            filepath.write_text(new_content, encoding="utf-8")
                        return True
                break
        return False

    # ── Handle single-line descriptions ──
    desc_match = re.search(r'^(description:\s*)(["\']?)(.*?)(\2\s*)$', fm_text, re.MULTILINE)
    if not desc_match:
        return False

    old_desc = desc_match.group(3).strip()
    if old_desc not in TRANSLATIONS:
        print(f"  WARNING: No translation for: {old_desc}")
        return False

    new_desc = TRANSLATIONS[old_desc]

    # If it was quoted, keep quotes; otherwise add them
    if desc_match.group(2):
        new_line = f'description: "{new_desc}"'
    else:
        # Check if original had no quotes
        orig_line = desc_match.group(0)
        if '"' in orig_line or "'" in orig_line:
            new_line = f'description: "{new_desc}"'
        else:
            new_line = f'description: "{new_desc}"'

    new_fm = fm_text[:desc_match.start()] + new_line + fm_text[desc_match.end():]
    new_content = "---\n" + new_fm + "\n---" + rest

    if new_content != original:
        if not dry_run:
            filepath.write_text(new_content, encoding="utf-8")
        return True
    return False


def process_directory(skills_dir: Path, label: str, dry_run: bool = False):
    """Process all SKILL.md files in a skills directory."""
    skill_files = sorted(skills_dir.rglob("SKILL.md"))
    changed = 0
    skipped = 0
    errors = 0

    print(f"\n{'='*60}")
    print(f"Processing {label}: {skills_dir}")
    print(f"Found {len(skill_files)} SKILL.md files")
    print(f"{'='*60}")

    for sf in skill_files:
        rel = str(sf.relative_to(skills_dir))
        try:
            if replace_description_in_file(sf, dry_run=dry_run):
                print(f"  ✓ {rel}")
                changed += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  ✗ {rel}: {e}")
            errors += 1

    print(f"\n  Changed: {changed}, Skipped: {skipped}, Errors: {errors}")
    return changed, skipped, errors


def main():
    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("DRY RUN MODE — no files will be modified\n")

    source_dir = PROJECT_ROOT / "hermes-agent" / "skills"
    runtime_dir = PROJECT_ROOT / "data" / "skills"

    results = {}

    for skills_dir, label in [
        (source_dir, "SOURCE (hermes-agent/skills/)"),
        (runtime_dir, "RUNTIME (data/skills/)"),
    ]:
        if skills_dir.exists():
            results[label] = process_directory(skills_dir, label, dry_run=dry_run)
        else:
            print(f"\n⚠ {label}: directory not found at {skills_dir}")

    if dry_run:
        print("\n\n⚠ This was a dry run. Run without --dry-run to apply changes.")
    else:
        print("\n\n✅ All translations applied. Restart the container for changes to take effect.")


if __name__ == "__main__":
    main()
