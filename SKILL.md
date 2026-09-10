---
name: patent-compose-skill
description: AI驱动的专利撰写工作流，自动化完成项目分析、查新检索、专利组合生成与优化、交底书和流程图撰写、权利要求书及完整申请文件生成。
user-invocable: true
allowed-tools: Read, Write, Edit, Grep, Glob, WebSearch, RunCommand
---

## 概述

本 Skill 用于辅助完成专利撰写全流程，包含**六个阶段**：项目分析、查新、专利组合生成与对抗优化、交底书与流程图撰写、权利要求书生成、完整专利申请文件（说明书+摘要）生成。

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

### Stage 3: 专利组合生成与权利要求树优化

**`Read`** `${SKILL_DIR}/prompts/stage3_design_portfolio.md`

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

### Stage 5: 撰写权利要求书

**`Read`** `${SKILL_DIR}/prompts/stage5_compose_claim.md`

**功能**：自动生成每个专利的权利要求书并进行质量检查

**输出**：
- `patents/claims_{专利标题}.md` - 各专利独立的权利要求书文件

### Stage 6: 撰写完整专利申请文件

**`Read`** `${SKILL_DIR}/prompts/stage6_compose_application.md`

**功能**：基于交底书、权利要求书和附图，为每件专利撰写完整的说明书、摘要，并进行附图标记注册和一致性检查，形成符合法定要求的专利申请文件四件套

**输出**：
- `patents/specification_{专利标题}.md` - 各专利独立的说明书
- `patents/abstract_{专利标题}.md` - 各专利独立的摘要

## 输出目录结构

```
patent-compose output/
├── materials/                          # 材料文件
│   ├── disclosure-v1.md               # Stage 1: 原始技术交底书
│   ├── claim-tree-v1.json             # Stage 1: 初始权利要求树
│   ├── formula_inventory.md           # Stage 1: 公式清单
│   ├── keyword-cn.json                # Stage 2: 中文检索词
│   ├── keyword-en.json                # Stage 2: 英文检索词
│   ├── prior-art.md                   # Stage 2: 相关技术清单
│   ├── prior-art-report.md            # Stage 2: 查新分析报告
│   ├── portfolio-initial.json         # Stage 3: 初始专利组合方案
│   ├── portfolio-v2.json             # Stage 3: 优化后的专利组合
│   └── disclosure-v2.md               # Stage 4: 汇总版最终交底书
├── claim-optimization/                 # Stage 3: 博弈对抗记录
│   ├── R1.json ~ R6.json              # 六轮攻防详情
│   └── claim-optimization.html        # 优化过程报告
├── patents/                            # 各专利申请文件夹
│   ├── {专利标题}/
│   │   ├── disclosure_{专利标题}.md    # Stage 4: 独立交底书
│   │   ├── flowcharts_{专利标题}.md    # Stage 4: Mermaid流程图
│   │   ├── claims_{专利标题}.md       # Stage 5: 权利要求书
│   │   ├── specification_{专利标题}.md # Stage 6: 说明书
│   │   └── abstract_{专利标题}.md      # Stage 6: 摘要
├── prior art/                         # 查新检索结果
└── project files/                     # 项目文件副本
```

## 脚本工具

| 脚本 | 功能 | 用途 |
|------|------|------|
| `analyze_project.py` | 项目源码和文档分析，提取技术方案，敏感信息检测 | Stage 1 |
| `prior_search.py` | 专利数据库检索与查新分析（支持CNKI/FPO/WebSearch） | Stage 2 |
| `generate_optimization_html.py` | 六轮博弈对抗优化报告生成（HTML可视化） | Stage 3 |
| `claim.py` | 权利要求树转权利要求书文本，格式验证 | Stage 5 |
| `file_tools.py` | 文件读写、JSON 格式验证与自动修复 | 通用工具 |
| `config.py` | 全局配置（输出目录、缩进等） | 通用配置 |

## 环境依赖
- **Python 3.10+**
- **浏览器自动化**：Playwright（用于专利数据库检索）
- **文档解析**：python-docx, python-pptx, pdfplumber, pywin32
- **JSON 格式验证与自动修复**：json-repair

- **安装命令**：`pip install -r requirements.txt`