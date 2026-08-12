# Patent Compose Skill

## 功能特性

- **Stage 1 - 项目分析**：自动遍历项目文件，分析技术架构，提取专利点，生成初始权利要求树
- **Stage 2 - 专利查新**：通过国内外专利数据库和网络检索现有技术，评估创造性，生成查新报告
- **Stage 3 - 交底书生成**：基于查新结果优化技术方案，生成符合规范的专利交底书
- **Stage 4 - 权利要求书撰写**：将结构化的权利要求树转换为符合国知局标准的权利要求书，并绘制核心技术流程图

## 快速开始

### 环境要求

- Python 3.10+

### 安装

1. 克隆本仓库：
```bash
git clone <repository-url>
cd patent-compose-skill
```

2. 安装依赖：
```bash
pip install -r requirements.txt
playwright install chromium
```

3. 将本 Skill 添加到你的 AI 助手配置中。

### 使用

启动 Skill 后，按提示依次执行四个阶段。每个阶段完成后需经用户确认方可进入下一阶段。

**固定输出目录**：所有输出文件统一保存在专利项目根目录下的 `patent-compose output` 目录中。

## 输出文件

| 文件 | 说明 |
|------|------|
| `materials/disclosure-v1.md` | 初始交底书 |
| `materials/disclosure-v2.md` | 最终交底书 |
| `materials/claim-tree-v1.json` | 初始权利要求树 |
| `materials/claim-tree-v2.json` | 最终权利要求树 |
| `materials/claims.md` | 权利要求书 |
| `materials/abstract.md` | 专利摘要 |
| `materials/flowcharts.md` | 核心技术流程图（Mermaid） |
| `materials/prior-art-report.md` | 查新报告 |
| `materials/keyword-cn.json` | 中文检索词 |
| `materials/keyword-en.json` | 英文检索词 |

## 项目结构

```
patent-compose-skill/
├── prompts/                    # 各阶段提示词文件
│   ├── stage1_analyze_project.md
│   ├── stage2_prior_search.md
│   ├── stage3_generate_disclosure.md
│   └── stage4_generate_claim.md
├── scripts/                    # 自动化脚本
│   ├── analyze_project.py      # 项目文件分析
│   ├── prior_search.py         # 专利检索
│   ├── config.py               # 配置常量
│   └── file_tools.py           # 文件工具
├── SKILL.md                    # Skill 定义文件
├── requirements.txt            # Python 依赖
└── README.md
```

## 许可证

[LICENSE](LICENSE)