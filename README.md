<div align="center">

# Patent Compose Skill

> 专利点挖掘与专利撰写，国内外检索查新，专利布局与保护优化

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.com/product/claude-code)
[![AI Powered](https://img.shields.io/badge/AI-Powered-green.svg)]()
[![Principal Stages: 6](https://img.shields.io/badge/Principal%20Stages-6-important.svg)]()

<br>

**想申请专利却不知从何下手？** 技术方案描述不够规范，反复修改仍难以达到要求；
想保护核心算法，却不知道**权利要求该写多宽**：写窄了**对手绕开**，写宽了被现有技术一击无效；
担心专利**创造性高度不足**被驳回，却无法准确判断与现有技术的本质区别；<br><br>

本技能帮你解决**技术人员写专利的三道坎**：
① **项目文件智能解析** → 从代码/文档/设计稿中自动提炼创新点
② **红蓝对抗 + 组合优化** → 六轮攻防打磨出最佳专利组合方案
③ **多源联合查新** → 不只搜到，还帮你评估专利价值，告诉你怎么改权利要求

[快速开始](#-快速开始) · [权利要求树](#-权利要求树) · [主线工作流程](#-主线工作流程) · [运行效果](#-运行效果) · [TODO](#-todo-list) · [技能入口](SKILL.md)

</div>

---

## 🚀 快速开始

### 环境要求

- **运行环境**：
  - Python 3.10+
  - 支持 Skill 调用的 IDE/Agent（如 Trae IDE、Claude Code）
  - 待分析项目，包含源代码、文档、设计稿等任意项目文件

- **依赖安装**：
  ```bash
  pip install -r requirements.txt
  ```
  主要依赖包括：
  - `playwright` >= 1.62.0（浏览器自动化，用于专利检索）
  - `python-docx` / `python-pptx` / `pdfplumber`（文档解析）
  - `pywin32`（Windows COM接口，支持旧版Office文件）
  - `json-repair`（JSON格式自动修复）

### 快速上手

#### 方式一：本地部署（全局技能）

按照你的 coding agent 软件文档，找到它存放 skills 的目录，将本 Skill 克隆或下载到该目录下。

```bash
# 1. 克隆或下载本 Skill
git clone https://github.com/yizchu/patent-compose-skill.git ${AGENT_SKILLS_DIR}/patent-compose-skill

# 2. 安装依赖
cd ${AGENT_SKILLS_DIR}/patent-compose-skill
pip install -r requirements.txt

# 3. 准备待分析的项目（包含源码/文档/设计稿等）

# 4. 在IDE中调用技能，按提示完成6个阶段
```

#### 方式二：项目级部署（项目技能）

如果你的 coding agent 支持**项目级Skill**，你也可以让本 Skill 仅对当前项目生效，避免影响其他项目。

### 输出目录结构

所有输出统一保存在项目根目录下的 **`patent-compose output`** 文件夹：

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
│   └── claim-optimization.html        # 优化过程可视化报告（HTML）
├── patents/                            # 各专利申请文件夹
│   ├── {专利标题A}/
│   │   ├── disclosure_{专利标题A}.md   # Stage 4: 独立交底书
│   │   ├── flowcharts_{专利标题A}.md   # Stage 4: Mermaid流程图
│   │   ├── claims_{专利标题A}.md      # Stage 5: 权利要求书
│   │   ├── specification_{专利标题A}.md # Stage 6: 说明书
│   │   └── abstract_{专利标题A}.md     # Stage 6: 摘要
│   ├── {专利标题B}/
│   │   └── ...                        # （结构同上）
├── prior art/                         # 查新检索结果原始数据
└── project files/                     # Stage 1: 项目文件解析产物
```

---

## 🌳 权利要求树

> **权利要求树是连接技术方案与专利保护的桥梁。**

一件专利能保护多大范围？全看权利要求书怎么写。本技能以“权利要求树”贯穿始终，直接对应权利要求书的撰写逻辑，为“专利布局”和“保护范围优化”奠定了坚实的基础。

### 什么是权利要求树？

权利要求树是一种**层次化的技术特征组织结构**，它将复杂的技术方案拆解为可独立保护的技术模块。本技能采用的权利要求树基本结构如下：

```json
{
    "{独权1名称（一种……方法/系统）}": {
        "description": "{独权1描述}",
        "contains": {
            "{步骤1名称}": {
                "description": "{步骤1描述}",
                "contains": {
                    "{子步骤1名称}": {
                        "description": "{子步骤1描述}",
                        "special claims": [
                            "{子步骤1特殊设计点1}"
                        ],
                        "contains": {
                            "{子步骤1-1名称}": {
                                "description": "{子步骤1-1描述}"
                            },
                            "{子步骤1-2名称}": {
                                "description": "{子步骤1-2描述}"
                            }
                        }
                    },
                    "{子步骤2名称}": {
                        "description": "{子步骤2描述}"
                    }
                },
                "special claims": [
                    "{步骤1特殊设计点1}",
                    "{步骤1特殊设计点2}"
                ]
            },
            "{步骤2名称}": {
                "description": "{步骤2描述}",
                "special claims": [
                    "{步骤2特殊设计点1}"
                ]
            }
        }
    },
    // 若有更多独权，结构类似
    "{独权2名称（一种……方法/系统）}":{
      ......
    }
}
```
**核心字段说明：**
- `description`：该步骤的**详细描述**
- `contains`：**子步骤列表**
- `special claims`：**特殊设计点**（不构成步骤）

**对应权利要求书的撰写逻辑：**

```
  1. {独权1名称}，其特征在于，包括：
  {步骤1描述}；
  {步骤2描述}。
  2. {独权2名称}，其特征在于，包括：
  ......
  3. 根据权利要求1所述的{独权1名称}，其特征在于，所述{步骤1名称}，包括：
  {子步骤1描述}；
  {子步骤2描述}。
  4. 根据权利要求1所述的{独权1名称}，其特征在于，所述{步骤1名称}，具体还有：
  {步骤1特殊设计点1}；
  {步骤1特殊设计点2}。
  5. 根据权利要求3所述的{独权1名称}，其特征在于，所述{子步骤1名称}，包括：
  {子步骤1-1描述}；
  {子步骤1-2描述}。
  5. 根据权利要求3所述的{独权1名称}，其特征在于，所述{子步骤1名称}，具体还有：{子步骤1特殊设计点1}。
  7. 根据权利要求1所述的{独权1名称}，其特征在于，所述{步骤2名称}，具体有：{步骤2特殊设计点1}。
  ......
```

### 权利要求树在各阶段的作用

| 阶段 | 权利要求树状态 | 核心动作 |
|:-----|:-------------|:---------|
| **Stage 1** | `claim-tree-v1.json`（初始版本） | 从项目文件中直接提取原始技术特征 |
| **Stage 2** | 结合查新报告标注（特征级对比） | 标记哪些特征已被现有技术公开 |
| **Stage 3** | `portfolio-v2.json`（优化后） | 划分权利要求树的一级模块（方法/系统）到不同的专利中，每个专利对应一棵优化后的权利要求树 |
| **Stage 4** | `portfolio-v2.json`（优化后） | 基于优化后的专利组合和权利要求树，生成附图和最终交底书 |
| **Stage 5** | `portfolio-v2.json`（优化后） | 基于优化后的专利组合和权利要求树，撰写最终权利要求书 |
| **Stage 6** | `portfolio-v2.json`（优化后） | 基于优化后的专利组合和权利要求树，撰写说明书 |
---

## 📋 主线工作流程

### 🔍 Stage 1: 项目分析与权利要求树生成

**目标**：从项目文件中自动提取技术方案，构建初始权利要求树

**核心能力**：
- 📁 **多类型文件解析**：源代码（Python/Java/JS/Go等）、文档（MD/DOCX/PDF/PPT）、设计稿、配置文件
- 🔍 **智能专利点识别**：自动识别核心算法、创新结构、独特设计
- 🔒 **敏感信息过滤**：自动检测API Key、密码、内部IP等，保护安全
- 📐 **公式提取与标准化**：识别数学公式，生成LaTeX格式和符号说明表
- 🌳 **权利要求树构建**：层次化组织技术特征，对应权利要求书的撰写逻辑
- 📚 **术语标准化**：采用国标术语 + IPC 标准词汇，拒绝自造词
- 🔄 **双向映射**：建立"专利特征 ↔ 项目内容"对照表，可追溯

**输出产物**：
- `disclosure-v1.md` - 原始技术交底书
- `claim-tree-v1.json` - 初始权利要求树（JSON格式）
- `formula_inventory.md` - 公式清单

---

### 🌐 Stage 2: 多源联合查新

**目标**：通过国内外专利数据库全面检索现有技术，评估新颖性和创造性

**查新架构**：
```
AI分析权利要求树 → 生成中英文检索词 → 并行检索多个数据库 → 整理对比文件 → 生成查新报告
```

**数据源**：
- 🇨🇳 **中国知网 (CNKI)**：中文专利数据库，检索前6页（约120条）
- 🌍 **FreePatentsOnline (FPO)**：海外专利（US/EP/WO/JP/KR），检索前1页（约50条）
- 🔎 **WebSearch**：补充检索技术白皮书、博客、开源项目等

**查新报告结构**：
1. **检索概况** - 检索日期、中英文检索词、数据库说明
2. **技术特征界定** - 已公开特征（对比文件+相似点）、区别技术特征（独有创新）
3. **专利法"三性"评估**
   - 新颖性评估（第22条第2款）：是否被单篇对比文件完全公开
   - 创造性评估（第22条第3款）：三步法分析（最接近现有技术→区别特征→是否显而易见）+ 显著进步判断 + 辅助因素
   - 实用性评估（第22条第4款）：能否产业上制造使用并产生积极效果
4. **授权风险评估** - 授权可能性（高/中/低）、主要风险点、应对策略
5. **核心技术布局建议** - 重点保护特征排序、权利要求布局策略、说明书撰写要点
6. **检索局限性说明** - 未覆盖数据库、后续补充检索方向

**核心产出**：
- `prior-art.md` - 现有技术清单（按相关性分级：🔴高度相关 / 🟡部分相关 / 🟢几乎无关）
- `prior-art-report.md` - 结构化查新报告（三性评估+风险分析+布局建议）

**⏱️ 预计耗时**：30分钟 - 1小时

---

### ⚔️ Stage 3: 专利组合生成与六轮对抗优化

**目标**：并行多源数据库检索 + 补充网络检索 → 结构化三性评估报告

**核心流程**：

```
Step 1: 读取查新报告 → Step 2: 生成初始专利组合
                                  ↓
                        Step 3: 六轮博弈对抗
                        ┌─────────────────────┐
                        │ R1: 新颖性检验       │ ← 过滤无价值方案
                        │ R2: 规避路径攻击     │ ← 测试字面侵权边界
                        │ R3: 规避路径复查     │ ← 检查上位概括风险
                        │ R4: 等效侵权测试     │ ← 封堵替代方案
                        │ R5: 等效边界复查     │ ← 查漏补缺
                        │ R6: 整体质量审计     │ ← 确保撰写规范
                        └─────────────────────┘
                                  ↓
                Step 4: 输出优化结果 + 优化过程可视化报告
                                  ↓
                          Step 5: 用户确认
```

**六轮对抗速览**：

| 轮次 | 攻击角色 | 攻击重点 | 防守策略 | 核心产出 |
|:-----|:---------|:---------|:---------|:---------|
| **R1** | 审查员 | 现有技术是否完全覆盖独权？ | 提取区别特征或主动放弃 | 过滤无新颖性方案 |
| **R2** | 竞争对手法务 | 替换/省略某个特征能否规避？ | 上位概括 + 从权补充具体实施 | 封堵字面规避路径 |
| **R3** | 竞争对手法务 | 上位概括是否过宽被现有技术覆盖？ | 收窄独权 + 从权保留宽范围 | 平衡防规避与防无效 |
| **R4** | 专利律师 | 等效替换（手段/功能/效果/显而易见性）是否成立？ | 不满足等效则补充从权保护 | 封堵等效侵权漏洞 |
| **R5** | 专利律师 | 数值边界、从权层次是否有遗漏？ | 补充封闭式权利要求 | 消除等效边界盲区 |
| **R6** | 资深代理师 | 从权布局/术语一致性/单一性/专利间协调 | 移除非必要特征、统一术语、修复引用关系 | 确保撰写规范合规 |

**布局策略说明**：

| 策略类型 | 适用场景 | 保护重点 |
|:---------|:---------|:---------|
| **主攻型** | 核心技术、竞争激烈领域 | 宽保护范围，优先国际布局 |
| **防守型** | 外围实施方式 | 封堵绕开路径，配合核心专利 |
| **隐藏型** | 难以逆向的核心算法/配方 | 作为商业秘密保护，不公开 |

**文件输出**：
- `portfolio-initial.json`：初始专利组合方案
- `portfolio-v2.json`：六轮对抗优化后的最终方案
- `R1.json` ~ `R6.json`：每轮攻防详细记录
- `claim-optimization.html`：可视化 HTML 页面

---

### 📝 Stage 4: 交底书与流程图生成

**目标**：为每件专利撰写完整的技术交底书，并绘制Mermaid流程图

**交底书结构**（符合中国专利撰写规范）：
1. **发明名称** - 清楚简明反映主题
2. **技术领域** - 具体细分技术方向
3. **背景技术** - 现有技术概述+缺点（融合查新成果）
4. **发明目的** - 对应现有技术的所有缺点
5. **技术方案** - 整体构思+详细方案+关键创新点
6. **有益效果** - 技术原理支撑的效果描述
7. **核心公式与算法** - 详细公式详解（来自formula_inventory.md）
8. **具体实施方式** - 结合附图的具体实施例
9. **附图说明** - 列出所有附图的编号和简要说明
10. **与现有技术的区别** - 基于查新报告的区别技术特征对比

**附图**：
- 使用 **Mermaid** 语法绘制流程图、架构图
- 支持多种图表类型：flowchart, sequenceDiagram, classDiagram等

**输出产物**：
- `disclosure_{专利标题}.md` - 各专利独立交底书
- `flowcharts_{专利标题}.md` - 各专利Mermaid流程图
- `disclosure-v2.md` - 汇总版最终交底书

---

### 📋 Stage 5: 权利要求书生成

**目标**：基于优化后的权利要求树，自动生成符合规范的权利要求书

**自动化流程**：
```
读取portfolio-v2.json → 脚本自动转换 → 质量检查 → 用户确认
```

**质量检查维度**：
- ✅ 技术特征完整性（对照权利要求树逐节点验证）
- ✅ 逻辑连贯性（特征描述顺序符合技术实现逻辑）
- ✅ 语言通顺性（语法正确、表达清晰、无歧义）
- ✅ 无冗余内容（无重复描述、无商业宣传用语）

**输出产物**：
- `claims_{专利标题}.md` - 各专利独立的权利要求书

---

### 📄 Stage 6: 完整专利申请文件生成

**目标**：基于交底书、权利要求书和附图，生成说明书和摘要，形成**专利申请文件四件套**

**四件套组成**：
1. ✅ **权利要求书**（Stage 5已完成）
2. ✅ **说明书**（Stage 6生成）- 包含技术领域、背景技术、发明内容、附图说明、具体实施方式
3. ✅ **摘要**（Stage 6生成）- 简明扼要说明发明技术要点
4. ✅ **附图**（Stage 4已完成）- Mermaid流程图

**说明书撰写规范**：
- **法定五部分**：技术领域、背景技术、发明内容、附图说明、具体实施方式
- **附图标记注册**：统一管理图中的所有标记，确保一致性
- **交叉引用检查**：说明书与权利要求书、附图的表述保持一致

**输出产物**：
- `specification_{专利标题}.md` - 各专利独立的说明书
- `abstract_{专利标题}.md` - 各专利独立的摘要

---

## 🎨 运行效果

<table width="100%" border="1" cellpadding="12" cellspacing="0">

<!-- 第一组：Stage 1 + Stage 2 -->
<tr>
<th width="50%" align="center">Stage 1<br><sub>项目分析 → 权利要求树</sub></th>
<th width="50%" align="center">Stage 2<br><sub>多源联合查新</sub></th>
</tr>
<tr>
<td width="50%" valign="top" align="center">
<img src="docs/assets/claim-tree-v1 效果图.png" alt="Stage 1: 初始权利要求树" width="100%" /><br>
<sub>初始权利要求树（claim-tree-v1.json）</sub>
</td>
<td width="50%" valign="top" align="center">
<img src="docs/assets/prior-art 效果图.png" alt="Stage 2: 查新汇总与标注" width="100%" /><br>
<sub>查新汇总与标注</sub>
</td>
</tr>

<!-- 第二组：Stage 3 -->
<tr>
<th width="100%" align="center" colspan="2">Stage 3<br><sub>六轮对抗 + 组合优化</sub></th>
</tr>
<tr>
<th width="50%" align="center">优化过程可视化</th>
<th width="50%" align="center">专利组合及权利要求树</th>
</tr>
<tr>
<td width="50%" valign="top" align="center">
<img src="docs/assets/optimization-report 效果图.png" alt="Stage 3: 优化过程可视化" width="100%" /><br>
<sub>优化过程报告（claim-optimization.html）</sub>
</td>
<td width="50%" valign="top" align="center">
<img src="docs/assets/portfolio-v2 效果图.png" alt="Stage 3: 最终专利组合及各专利权利要求树" width="100%" /><br>
<sub>专利组合方案（portfolio-v2.json）</sub>
</td>
</tr>

<!-- 第三组：Stage 4 -->
<tr>
<th width="100%" align="center" colspan="2">Stage 4<br><sub>交底书 + 附图</sub></th>
</tr>
<tr>
<th width="50%" align="center">各专利交底书</th>
<th width="50%" align="center">附图</th>
</tr>
<tr>
<td width="50%" valign="top" align="center">
<img src="docs/assets/专利disclosure 效果图.png" alt="Stage 4: 各专利独立交底书 & 汇总版交底书" width="100%" />
</td>
<td width="50%" valign="top" align="center">
<img src="docs/assets/专利flowchart 效果图.png" alt="Stage 4: 各专利 Mermaid 流程图 & 汇总版流程图" width="100%" />
</td>
</tr>
</table>

> 💡 展示的所有运行效果均基于 https://github.com/yizchu/DBAgent 真实案例生成。

---

## 🚀 Todo List

**所有开发任务、优先级、状态和详细信息请查看：[Todo List](docs/TODO.md)**

</div>

### 适用场景

| 场景 | 典型需求 | 触发示例 | 核心价值 |
|------|----------|----------|----------|
| **创业公司/个人开发者** | 首次专利布局，成本敏感 | 「帮我们梳理可专利点」 | 从代码/文档自动提炼创新点，降低专利门槛 |
| **专利代理所** | 客户交底书质量差 | 「分析客户源码」 | 减少与发明人沟通成本，生成高质量初稿 |
| **技术研发团队** | 技术成果保护 | 「保护核心算法」 | 核心技术专利布局，防止技术规避 |
| **投资机构/孵化器** | 尽职调查，评估价值 | 「评估项目专利潜力」 | 快速识别技术价值和风险点 |

---

## 📚 参考文档

### 📖 核心文档
- [技能入口与Agent流程](SKILL.md) - 技能的完整工作流程和技术规范
- [更新日志](docs/UpdateLogs/) - 版本历史和功能变更记录
- [开发计划与进度](docs/TODO.md) - 功能路线图和待办事项

### 📝 各阶段详细说明
- [Stage 1: 项目分析与初稿生成](prompts/stage1_analyze_project.md)
- [Stage 2: 多源联合查新](prompts/stage2_prior_search.md)
- [Stage 3: 专利布局与保护优化](prompts/stage3_design_portfolio.md)
- [Stage 4: 交底书与流程图生成](prompts/stage4_generate_disclosure.md)
- [Stage 5: 权利要求书生成](prompts/stage5_compose_claim.md)
- [Stage 6: 完整申请文件生成](prompts/stage6_compose_application.md)

---

## 💬 欢迎交流

欢迎大家对本 Skill 提出宝贵的**评论、建议和改进意见**！无论是功能需求、使用体验反馈，还是代码优化建议，都非常感谢您的参与。

🙏 **感谢每一位贡献者！**

- 🐛 使用问题？欢迎提 [Issue](https://github.com/yizchu/patent-compose-skill/issues)
- 💡 有新想法？欢迎讨论或提 [Feature Request](https://github.com/yizchu/patent-compose-skill/issues)
- 🔧 想改进代码？欢迎提交 [Pull Request](https://github.com/yizchu/patent-compose-skill/pulls)

如果这个 Skill 对您有帮助，欢迎 Star 支持一下 ⭐ 您的支持是我们持续改进的动力！

---

<div align="center">

MIT License © [yizchu](https://github.com/yizchu)

</div>