---
name: patent-compose-skill
description: AI驱动的专利撰写工作流，自动化完成项目分析、查新检索、专利组合生成与优化、交底书和流程图撰写。
user-invocable: true
allowed-tools: Read, Write, Edit, Grep, Glob, WebSearch, RunCommand
---

## 概述

本 Skill 用于辅助完成专利撰写全流程，包含四个阶段：项目分析、查新、专利组合生成与对抗优化、交底书与流程图撰写。

## 核心原则
- **固定输出目录**：专利项目根目录下的 `patent-compose output`。不要默认写到其他任何目录。
- **真实性原则**：所有分析必须严格基于项目的真实文件，不得凭空捏造或臆测不存在的技术方案。
- **全面覆盖**：不能遗漏任何技术细节，只有明显属于行业常规实现的内容才可以省略。
- **术语标准**：必须采用所属技术领域的通用技术术语，优先使用国家标准、行业标准规定的规范名词，以及国际专利分类表（IPC）中的标准技术术语。国家有统一规定的自然科学名词，应当采用官方统一术语；无官方规定的，可采用本领域约定俗成的表述，不得自行编造非通用词汇。禁止使用口头俗称、网络热词、行业黑话、非技术类表述替代专业术语。
- **通俗易懂**：用清晰直白的语言描述技术方案，确保非本领域技术人员也能理解，避免空泛赞美、营销口号、万能句式、结构模板、正确废话等具有"AI味"套话。

## 工作流程

### Stage 1: 项目分析 → 权利要求树

**`Read`** `${SKILL_DIR}/prompts/stage1_analyze_project.md`

**功能**：分析项目源码和文档，提取核心技术方案并生成初始权利要求树

**输出**：
- `materials/disclosure-v1.md` - 第一版技术交底书，是项目的分析结果
- `materials/claim-tree-v1.json` - 初始权利要求树

### Stage 2: 项目成果查新

**`Read`** `${SKILL_DIR}/prompts/stage2_prior_search.md`

**功能**：基于关键词进行专利数据库检索，评估技术方案的新颖性和创造性

⚠️ 执行数据库检索脚本后需等待用户确认

**输出**：
- `materials/keyword-cn.json` - 中文检索词
- `materials/keyword-en.json` - 英文检索词
- `materials/prior-art.md` - 和项目相关的现有技术清单
- `materials/prior-art-report.md` - 查新分析报告

### Stage 3: 专利组合生成与权利要求树优化（含六轮博弈对抗）

**`Read`** `${SKILL_DIR}/prompts/stage3_generate_claim.md`

**功能**：布局专利组合，并通过六轮博弈对抗优化

**输出**：
- `materials/portfolio-initial.json` - 初始专利组合方案
- `materials/portfolio-v2.json` - 最终专利组合方案
- `claim-optimization/` - 六轮攻防记录（R1-R6.json）+ HTML 可视化报告

### Stage 4: 撰写最终交底书与流程图

**`Read`** `${SKILL_DIR}/prompts/stage4_generate_disclosure.md`

**功能**：为每件专利撰写完整的技术交底书（融合查新成果）并绘制 Mermaid 流程图

**输出**：
- `patents/disclosure_{专利标题}.md` - 各专利独立交底书（最终版）
- `patents/flowcharts_{专利标题}.md` - 各专利流程图
- `materials/disclosure-v2.md` - 汇总版最终交底书
- `materials/flowcharts.md` - 汇总版流程图

## 输出目录结构

```
patent-compose output/
├── materials/                          # 汇总版文件（Stage 1-4）
│   ├── disclosure-v1.md               # Stage 1: 原始技术交底书
│   ├── claim-tree-v1.json             # Stage 1: 初始权利要求树
│   ├── keyword-cn.json                # Stage 2: 中文检索词
│   ├── keyword-en.json                # Stage 2: 英文检索词
│   ├── prior-art.md                   # Stage 2: 现有技术清单
│   ├── prior-art-report.md            # Stage 2: 查新分析报告
│   ├── portfolio-initial.json         # Stage 3: 初始专利组合方案
│   ├── portfolio-v2.json             # Stage 3: 最终优化后的专利组合
│   ├── disclosure-v2.md               # Stage 4: 汇总版最终交底书
│   └── flowcharts.md                  # Stage 4: 汇总版流程图
├── claim-optimization/                 # Stage 3: 博弈对抗记录
│   ├── R1.json ~ R6.json              # 六轮攻防详情
│   └── claim-optimization.html        # 优化过程报告
├── patents/                            # Stage 4: 各专利独立文件
│   ├── disclosure_{专利标题}.md        # 各专利独立交底书
│   └── flowcharts_{专利标题}.md        # 各专利流程图
└── prior art/                         # 查新检索结果
└── project files/                     # 项目文件产物
```

## 脚本工具

| 脚本 | 功能 | 用途 |
|------|------|------|
| `analyze_project.py` | 项目源码和文档分析，提取技术方案 | Stage 1 |
| `prior_search.py` | 专利数据库检索与查新分析 | Stage 2 |
| `generate_optimization_html.py` | 六轮博弈对抗优化报告生成 | Stage 3 |
| `file_tools.py` | 文件读写、JSON 格式验证与自动修复 | 通用工具 |
| `config.py` | 全局配置（输出目录等） | 通用配置 |