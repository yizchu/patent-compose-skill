# JSON 文件生成指南

## 核心原则：YAML → JSON 两阶段生成法

**第一阶段**：AI 按照标准 YAML 语法生成 `.yaml` 文件
**第二阶段**：脚本自动将 YAML 转换为标准 JSON 文件（`.json`）

---

## 工作流程

### Step 1：生成 YAML 文件

AI 按照**标准 YAML 语法**直接生成 `.yaml` 文件，内容与原计划一致。

**文件命名规则**：
- 中间文件：`{原JSON文件名}.yaml`
- 最终文件：`{原JSON文件名}.json`

**示例**：
```
portfolio-v2.yaml  →  转换后  →  portfolio-v2.json
claim-tree-v1.yaml  →  转换后  →  claim-tree-v1.json
```

**关键要求**：
1. 使用**标准 YAML 语法**
2. 统一使用**空格缩进**（建议2空格），禁止混用 Tab
3. 布尔值使用小写 `true/false`
4. 确保文件保存为 **UTF-8 编码**

### Step 2：执行转换

```bash
python "${SKILL_DIR}/scripts/yaml_to_json.py" <YAML文件完整路径>
```

**功能说明**：
- 使用 PyYAML 库解析 YAML 文件
- 转换为标准 JSON 格式（双引号、正确括号匹配、无尾逗号）
- 输出到同目录下，文件名为 `{原文件名}.json`（去掉 `.yaml` 后缀）
- 自动处理中文编码（UTF-8）

### Step 3：验证结果

转换完成后，**必须立即验证基本格式**：

```bash
python "${SKILL_DIR}/scripts/file_tools.py" from_json <JSON文件完整路径>
```

然后再次 **Read** 该 JSON 文件，确保：
- 所有字段完整，无截断
- 嵌套结构正确
- 字符串内容准确（特别是长文本和技术描述）
- 数值和布尔值类型正确
- 中文无乱码