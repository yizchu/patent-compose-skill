---
name: patent-compose-skill
description: AI-powered patent drafting workflow automating project analysis, prior art search, disclosure generation, and claims writing.
user-invocable: true
allowed-tools: Read, Write, Edit, Grep, Glob, WebSearch, Bash
---

## 概述

本 Skill 用于辅助完成专利撰写全流程，包含四个阶段：分析项目生成权利要求树、项目成果查新、生成最终交底书、撰写权利要求书并绘制流程图。

## 核心原则
- **固定输出目录**：专利项目根目录下的 `patent-compose output`。不要默认写到其他任何目录。
- **真实性原则**：所有分析必须严格基于项目的真实文件，不得凭空捏造或臆测不存在的技术方案。
- **全面覆盖**：不能遗漏任何技术细节，只有明显属于行业常规实现的内容才可以省略。
- **术语标准**：必须采用所属技术领域的通用技术术语，优先使用国家标准、行业标准规定的规范名词，以及国际专利分类表（IPC）中的标准技术术语。国家有统一规定的自然科学名词，应当采用官方统一术语；无官方规定的，可采用本领域约定俗成的表述，不得自行编造非通用词汇。禁止使用口头俗称、网络热词、行业黑话、非技术类表述替代专业术语。
- **通俗易懂**：用清晰直白的语言描述技术方案，确保非本领域技术人员也能理解，避免空泛赞美、营销口号、万能句式、结构模板、正确废话等具有"AI味"套话。

## 工作流程

本 Skill 按顺序执行四个阶段，每个阶段完成后需经用户确认方可进入下一阶段。

### Stage 1: 分析项目，初步生成"权利要求树"

**`Read`** `${SKILL_DIR}/prompts/stage1_analyze_project.md`，按其中的提示词执行。

**输出文件**：
- `${输出目录}/materials/disclosure-v1.md` - 初始交底书
- `${输出目录}/materials/claim-tree-v1.json` - 初始权利要求树

### Stage 2: 项目成果查新

**`Read`** `${SKILL_DIR}/prompts/stage2_prior_search.md`，按其中的提示词执行。

**重要说明**：执行数据库检索脚本时，启动后应立即退出当前执行，不要等待完成，向用户提示后等待确认再继续。

**输出文件**：
- `${输出目录}/materials/keyword-cn.json` - 中文检索词
- `${输出目录}/materials/keyword-en.json` - 英文检索词
- `${输出目录}/materials/prior-art.md` - 检索结果汇总
- `${输出目录}/materials/prior-art-report.md` - 查新报告

### Stage 3: 生成最终交底书

**`Read`** `${SKILL_DIR}/prompts/stage3_generate_disclosure.md`，按其中的提示词执行。

**输出文件**：
- `${输出目录}/materials/disclosure-v2.md` - 最终交底书
- `${输出目录}/materials/claim-tree-v2.json` - 最终权利要求树

### Stage 4: 撰写权利要求书，绘制核心技术流程图

**`Read`** `${SKILL_DIR}/prompts/stage4_generate_claim.md`，按其中的提示词执行。

**输出文件**：
- `${输出目录}/materials/claims.md` - 权利要求书
- `${输出目录}/materials/abstract.md` - 专利摘要
- `${输出目录}/materials/flowcharts.md` - 核心技术流程图

## 输出目录结构

```
patent-compose output/
├── materials/
│   ├── disclosure-v1.md          # 初始交底书
│   ├── disclosure-v2.md          # 最终交底书
│   ├── claim-tree-v1.json        # 初始权利要求树
│   ├── claim-tree-v2.json        # 最终权利要求树
│   ├── claims.md                 # 权利要求书
│   ├── abstract.md               # 专利摘要
│   ├── flowcharts.md             # 核心技术流程图
│   ├── keyword-cn.json           # 中文检索词
│   ├── keyword-en.json           # 英文检索词
│   ├── prior-art.md              # 检索结果汇总
│   └── prior-art-report.md       # 查新报告
├── prior art/
│   ├── <检索词>.json              # 各检索词的专利检索结果
│   └── WebSearch-results.md      # 网络检索结果
└── project files/                 # 项目文件镜像结构及分析结果
    └── files_info.json            # 项目文件信息树
```

## 脚本说明

| 脚本文件 | 功能 | 调用方式 |
|---------|------|---------|
| `scripts/analyze_project.py` | 分析项目文件结构，提取文件信息 | `python analyze_project.py get_files_info <项目根目录> <项目根目录>` |
| `scripts/prior_search.py` | 专利数据库检索 | `python prior_search.py <项目根目录>` |
| `scripts/config.py` | 配置输出目录常量 | 被其他脚本导入使用 |
| `scripts/file_tools.py` | 文件读写工具函数 | 被其他脚本导入使用 |
