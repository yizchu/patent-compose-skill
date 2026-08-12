# 核心技术流程图

## 流程图1：基于AST递归解析的查询结果溯源流程

**说明**：本流程图展示了查询结果溯源算法的完整执行过程，从接收原始SQL到生成并执行溯源SQL，最终将完整数据返回前端。

```mermaid
graph TD
    A[开始] --> B[接收原始SQL查询语句]
    B --> C[使用sqlglot解析SQL为AST]
    C --> D{判断AST节点类型}
    D -->|exp.Subquery| E[提取子查询内部节点]
    E --> F[递归处理子查询]
    F --> G[保留括号结构返回新Subquery节点]
    D -->|exp.Union/Intersect/Except| H[递归处理左右子节点]
    H --> I[保持集合运算结构]
    D -->|exp.Select| J[调用_transform_single_select]
    J --> K[遍历SELECT节点所有子节点]
    K --> L[提取SELECT/JOIN/WHERE中的列引用]
    L --> M{检测星号表达式?}
    M -->|是| N[记录星号及对应表名]
    M -->|否| O[继续处理]
    N --> O
    O --> P[提取JOIN条件中的等值对]
    P --> Q[对JOIN等值列进行去重]
    Q --> R[构建新的SELECT语句]
    R --> S[复制FROM/JOIN/WHERE子句]
    S --> T[移除ORDER BY/LIMIT/GROUP BY/HAVING/DISTINCT子句]
    T --> U[生成溯源SQL]
    U --> V[执行溯源SQL获取完整数据]
    V --> W[convert_bytes_to_str转换字节数据]
    W --> X{解码成功?}
    X -->|UTF-8成功| Y[返回UTF-8解码结果]
    X -->|UTF-8失败| Z{GBK解码成功?}
    Z -->|是| AA[返回GBK解码结果]
    Z -->|否| AB[使用base64编码]
    Y --> AC[将完整数据返回前端图表区]
    AA --> AC
    AB --> AC
    AC --> AD[结束]
    G --> D
    I --> D
```

## 流程图2：数据库知识图谱自动构建流程

**说明**：本流程图展示了从数据库Schema自动构建知识图谱的完整过程，包括实体构建、关系提取、属性获取和统计信息生成。

```mermaid
graph TD
    A[开始] --> B[连接目标数据库]
    B --> C[获取数据库所有表列表]
    C --> D{遍历每个表}
    D --> E[调用build_entities_from_one_table]
    E --> F[创建表实体]
    F --> G[遍历表的所有列]
    G --> H[创建列实体]
    H --> I[建立表-列包含关系]
    I --> J[提取列属性信息]
    J --> K{get_foreign_keys=True?}
    K -->|是| L[调用check_foreign_key检查外键]
    L --> M[提取显式外键关系]
    K -->|否| N{get_hidden_relationships=True?}
    M --> N
    N -->|是| O[调用explore_crosstable_col_relationships]
    O --> P[分析列名相似度]
    P --> Q[分析数据类型匹配]
    Q --> R[分析值域重叠]
    R --> S[发现隐藏关联关系]
    N -->|否| T[调用get_table_attributes获取表属性]
    S --> T
    T --> U[调用get_col_attributes获取列属性]
    U --> V[调用_generate_common_stats生成通用统计]
    V --> W{列类型为数值?}
    W -->|是| X[调用_generate_numeric_stats生成数值统计]
    W -->|否| Y{列类型为字符串?}
    X --> Y
    Y -->|是| Z[调用_generate_string_stats生成字符串统计]
    Y -->|否| AA[调用save_to_mongodb保存图谱]
    Z --> AA
    AA --> AB[保存到MongoDB不同集合]
    AB --> AC{还有未处理的表?}
    AC -->|是| D
    AC -->|否| AD[知识图谱构建完成]
    AD --> AE[结束]
```

## 流程图3：知识图谱增强的Text-to-SQL转换流程

**说明**：本流程图展示了如何利用知识图谱上下文增强大语言模型，实现自然语言到SQL的准确转换。

```mermaid
graph TD
    A[开始] --> B[接收用户自然语言查询]
    B --> C[提取用户查询意图]
    C --> D[获取知识图谱上下文信息]
    D --> E[获取数据库表结构信息]
    E --> F[获取列信息及关系网络]
    F --> G[获取列统计信息]
    G --> H[构造LLM系统提示词]
    H --> I[将知识图谱信息注入提示词]
    I --> J[构造完整LLM请求]
    J --> K[调用大语言模型]
    K --> L[生成SQL查询语句]
    L --> M{SQL是否需要方言转换?}
    M -->|是| N[调用transform_sql转换方言]
    N --> O[递归遍历SQL AST节点]
    O --> P[转换函数名映射]
    P --> Q[转换分页语法]
    Q --> R[转换日期时间函数]
    R --> S[生成目标方言SQL]
    M -->|否| S
    S --> T[执行SQL查询]
    T --> U[获取查询结果]
    U --> V[调用溯源算法获取完整数据]
    V --> W[返回结果及溯源数据]
    W --> X[结束]
```

## 流程图4：SQL方言自动转换流程

**说明**：本流程图展示了SQL方言自动转换模块的工作过程，支持不同数据库间的SQL语法适配。

```mermaid
graph TD
    A[开始] --> B[接收源SQL及源/目标数据库类型]
    B --> C[使用sqlglot解析SQL为AST]
    C --> D[指定源数据库方言]
    D --> E[调用_process_node_recursive递归遍历]
    E --> F{节点类型判断}
    F -->|exp.Subquery| G[递归处理子查询]
    F -->|exp.Union/Intersect/Except| H[递归处理集合运算]
    F -->|exp.Select| I[调用_transform_single_select]
    I --> J[识别函数调用节点]
    J --> K{函数名需转换?}
    K -->|是| L[查函数名映射表]
    L --> M[替换为目标数据库函数名]
    K -->|否| N{分页语法需转换?}
    M --> N
    N -->|是| O[转换LIMIT/OFFSET为TOP或OFFSET/FETCH]
    N -->|否| P{日期函数需转换?}
    O --> P
    P -->|是| Q[转换DATE_FORMAT为strftime等]
    P -->|否| R[继续处理其他节点]
    Q --> R
    R --> S{还有未处理节点?}
    S -->|是| F
    S -->|否| T[生成目标方言SQL]
    T --> U[结束]
    G --> F
    H --> F
```

## 流程图5：智能数据库代理会话管理流程

**说明**：本流程图展示了用户与智能数据库代理系统进行多轮问答交互的完整会话管理过程。

```mermaid
graph TD
    A[开始] --> B[用户登录系统]
    B --> C[调用get_sessions获取会话列表]
    C --> D{选择已有会话?}
    D -->|是| E[调用select_chat加载历史消息]
    D -->|否| F[调用select_chat创建新会话]
    E --> G[创建会话目录和初始化文件]
    F --> G
    G --> H[用户输入自然语言问题]
    H --> I[调用ask_question处理问题]
    I --> J[从会话上下文提取历史对话]
    J --> K[调用Text-to-SQL模块生成SQL]
    K --> L[执行SQL获取查询结果]
    L --> M[调用溯源算法获取完整数据]
    M --> N[保存问题/SQL/结果到历史记录]
    N --> O[返回完整响应给用户]
    O --> P{用户继续提问?}
    P -->|是| H
    P -->|否| Q{用户要求重新生成?}
    Q -->|是| R[调用regenerate_output]
    R --> S[定位指定问题]
    S --> T[重新调用LLM生成新SQL]
    T --> U[更新历史记录]
    U --> O
    Q -->|否| V{用户退出?}
    V -->|否| H
    V -->|是| W[调用logout清理会话状态]
    W --> X[释放资源]
    X --> Y[结束]
```

## 流程图6：隐藏关系探索算法流程

**说明**：本流程图展示了如何发现数据库中未通过外键约束显式定义的潜在关联关系。

```mermaid
graph TD
    A[开始] --> B[获取知识图谱中所有表信息]
    B --> C{遍历所有表对}
    C --> D[获取表A的所有列]
    D --> E[获取表B的所有列]
    E --> F{遍历列对}
    F --> G[分析列名相似度]
    G --> H{列名相同或高度相似?}
    H -->|是| I[标记为候选关系]
    H -->|否| J{还有未处理列对?}
    I --> K[分析数据类型匹配]
    K --> L{数据类型兼容?}
    L -->|是| M[标记为候选关系]
    L -->|否| J
    M --> N[分析值域重叠]
    N --> O[采样两列的值]
    O --> P[计算值域重叠度]
    P --> Q{重叠度超过阈值?}
    Q -->|是| R[判定存在潜在关联]
    Q -->|否| J
    R --> S[在知识图谱中添加关联关系]
    S --> T[扩展知识图谱关系覆盖范围]
    T --> J
    J -->|是| F
    J -->|否| U[隐藏关系探索完成]
    U --> V[结束]
```