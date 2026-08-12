# 专利技术交底书

## 一、发明名称
一种基于知识图谱增强的智能数据库代理系统及查询结果溯源方法

## 二、技术领域
本发明涉及数据库智能查询技术领域，尤其涉及一种结合知识图谱与大语言模型实现自然语言到SQL转换，并提供查询结果溯源能力的智能数据库代理系统。

## 三、背景技术
随着大语言模型技术的发展，Text-to-SQL（自然语言转SQL）成为数据库交互的热门研究方向。现有技术中，已有多种方案尝试将知识图谱与Text-to-SQL结合，通过引入数据库Schema的结构化知识来提升SQL转换的准确率。例如，部分专利公开了利用检索增强生成（RAG）技术或最短路径算法解决跨表关联问题的方案。

然而，现有Text-to-SQL系统存在以下技术缺陷：

1. **查询结果不完整，缺乏溯源能力**：当SQL查询语句包含LIMIT、GROUP BY、UNION/INTERSECT/EXCEPT等子句时，查询结果仅返回部分或聚合后的数据，用户无法全面了解查询涉及到的完整数据范围。现有系统未提供将部分查询还原为完整数据查询的能力，用户无法验证AI生成的SQL是否准确反映了其查询意图。

2. **数据库关系提取依赖显式外键，遗漏潜在关联**：现有知识图谱构建方法仅通过数据库的INFORMATION_SCHEMA提取显式外键约束关系，但实际数据库中大量表列之间存在潜在关联（如通过列名语义相似、数据类型匹配、值域重叠等方式关联），这些隐藏关系未被发现，导致知识图谱的关系覆盖不完整，进而影响Text-to-SQL转换时对跨表查询的理解能力。

3. **数据库统计信息分散，缺乏与业务语义的关联**：传统数据库的统计信息（如列的最大值、最小值、数据分布等）通常通过独立的元数据查询获取，与知识图谱中的实体属性没有关联，无法直接用于增强大语言模型对数据库数据特征的理解，导致生成的SQL在数据范围判断、聚合条件设置等方面容易出现偏差。

4. **缺乏从多数据库连接到查询溯源的完整技术链路**：现有Text-to-SQL系统通常针对单一数据库类型，且各功能模块（连接管理、知识图谱构建、SQL生成、结果展示）相互独立，缺乏统一架构将多数据库连接管理、知识图谱自动构建、SQL方言适配、查询结果溯源整合为完整闭环，无法支持跨数据库的统一智能查询服务。

## 四、发明目的
针对现有技术的上述缺陷，本发明的目的在于提供一种基于知识图谱增强的智能数据库代理系统及查询结果溯源方法，以解决以下技术问题：

1. 解决SQL查询结果不完整的问题，通过基于AST递归解析的溯源算法，将包含限制、分组、集合运算等子句的SQL查询转换为获取完整涉及数据的溯源SQL，使用户能够全面了解查询涉及的数据范围。

2. 解决数据库关系提取不完整的问题，通过隐藏关系探索算法，发现未通过外键约束显式定义但实际存在的潜在关联关系，扩展知识图谱的关系覆盖范围，提升Text-to-SQL转换的准确率。

3. 解决统计信息与业务语义脱节的问题，通过知识图谱驱动的统计信息自动生成系统，将数据库统计信息与知识图谱实体属性关联，为Text-to-SQL提供更丰富的上下文信息。

4. 解决Text-to-SQL系统功能分散的问题，提供从多数据库连接管理、知识图谱自动构建、智能查询转换、方言适配到结果溯源的完整技术闭环，支持跨数据库的统一智能查询服务。

## 五、技术方案
为实现上述目的，本发明采用如下技术方案：

一种基于知识图谱增强的智能数据库代理系统，包括以下模块：

**多数据库连接池统一管理模块**：提供统一的数据库连接管理接口，通过database_server参数动态支持MySQL、SQLite、MongoDB等多种数据库类型。该模块包含ConnectionPool类，通过create_pool()方法根据数据库服务器类型创建对应的连接池实例，connect()方法获取数据库连接和游标对象，close()方法安全释放连接资源。

**数据库知识图谱自动构建模块**：从数据库Schema自动构建知识图谱，包含KnowledgeGraph类，采用entities字典存储实体及其属性、relationships字典存储实体间关系、entity_classifications字典存储实体分类信息。构建流程包括：通过build_entities_from_one_table()方法从单个数据库表构建实体，创建表实体和列实体并建立"包含"关系；通过build_entities_from_database()方法遍历全库所有表进行批量构建，支持外键关系提取和隐藏关系探索；通过parse_db_doc()方法解析数据库文档并更新知识图谱属性；通过save_to_mongodb()方法将知识图谱保存到MongoDB，通过build_from_mongodb()方法从MongoDB加载重建。

**数据库关系自动发现与提取模块**：通过generate_table_col_relationships()函数提取表-列层级关系；通过check_foreign_key()函数查询INFORMATION_SCHEMA判断表间是否存在显式外键关联；通过get_crosstable_col_relationships()函数获取跨表外键关系映射；通过explore_crosstable_col_relationships()函数探索隐藏关系，该函数基于已有知识图谱信息，通过分析列名相似度、数据类型匹配、值域重叠等特征，发现未通过外键约束显式定义的潜在关联关系。

**数据库属性智能提取与规范化模块**：定义TableAttribute类和ColumnAttribute类作为数据模型，采用Pydantic BaseModel进行数据验证和序列化。通过get_table_attributes()函数获取表的行数、列数等元数据，通过get_col_attributes()函数对每个列执行数据类型识别、示例值采样、统计信息计算。通过normalize()函数对采样示例值进行去重、去空值等规范化处理。

**知识图谱驱动的统计信息生成模块**：通过_generate_common_stats()方法计算列的基础统计指标（空值数量、非空值数量、唯一值数量、唯一值比例）；通过_generate_numeric_stats()方法针对数值列计算专属统计指标（最大值、最小值、平均值、中位数、标准差、分位数）；通过_generate_string_stats()方法针对字符串列计算专属统计指标（最大长度、最小长度、平均长度、常见值模式）。

**知识图谱增强的Text-to-SQL转换模块**：通过text2sql_SP()函数将知识图谱信息字符串作为系统提示词的一部分注入到LLM请求中，提供数据库表结构、列信息、关系网络等上下文；通过text2sql()函数接收用户对话消息列表，提取自然语言查询意图，结合知识图谱上下文构造完整的LLM请求，调用大语言模型生成对应的SQL查询语句。

**SQL方言自动转换模块**：通过transform_sql()函数在不同数据库服务器间转换SQL语法，内置函数名映射表自动替换日期函数、字符串函数、聚合函数的名称差异（如MySQL的DATE_FORMAT转换为SQLite的strftime），识别并转换分页语法（将MySQL的LIMIT/OFFSET转换为SQL Server的TOP或OFFSET/FETCH），处理日期时间函数的语法差异。通过_process_node_recursive()函数递归遍历SQL抽象语法树节点，支持嵌套查询、子查询、联合查询等复杂SQL结构的完整转换。

**基于AST递归解析的查询结果溯源模块**：该模块是本发明的核心创新点之一。其工作原理为：SQL查询语句可能包含LIMIT、GROUP BY、UNION/INTERSECT/EXCEPT等子句，导致查询结果无法体现查询涉及到的所有数据。溯源算法将原始SQL查询语句转化为一段新的语句，应用到被查询数据库，获取查询涉及到的所有完整数据。具体步骤包括：
- 使用sqlglot库的parse_one()函数将SQL字符串解析为抽象语法树AST，支持指定数据库方言；
- 通过_process_node_recursive()函数递归遍历AST节点，根据节点类型进行不同处理：遇到exp.Subquery节点时提取内部节点并递归处理保留括号结构；遇到exp.Union/Intersect/Except节点时递归处理左右子节点保持集合运算结构；遇到exp.Select节点时调用_transform_single_select()进行具体转换；
- 在_transform_single_select()函数中，遍历SELECT节点的所有子节点，提取SELECT、JOIN、WHERE中提到的所有列引用exp.Column，检测并处理星号表达式，提取JOIN条件中的等值对exp.EQ并对JOIN等值列进行去重；
- 根据提取的列构建新的SELECT语句，复制原始FROM子句、所有JOIN子句和WHERE子句到新SELECT语句，保持表连接逻辑和数据筛选条件不变；
- 移除ORDER BY、LIMIT、GROUP BY、HAVING、DISTINCT等影响结果集完整性的子句；
- 执行溯源SQL获取完整数据，通过convert_bytes_to_str()函数递归遍历查询结果将所有bytes类型转换为字符串（优先UTF-8解码，失败则尝试GBK解码，最后使用base64编码），将溯源数据返回至前端图表区呈现给用户。

**智能数据库代理会话管理模块**：通过ChatState类维护用户会话状态，使用字典存储用户ID到会话历史的映射。提供get_sessions()接口查询用户会话列表，select_chat()接口选择或创建会话，ask_question()接口处理用户问题并调用Text-to-SQL模块生成SQL执行查询，regenerate_output()接口重新生成指定问题的回答，get_data()接口获取问题对应的查询结果并调用溯源算法获取完整数据，delete_session()和delete_message()接口管理会话和消息，logout()接口清理用户会话状态。

**知识图谱管理API接口模块**：提供verify_admin()接口进行管理员身份验证，get_graphs()接口查询已保存的知识图谱列表，delete_graph()接口从MongoDB删除图谱数据，create_graph()接口完成从数据库到知识图谱的全流程创建（依次调用知识图谱构建器构建实体、提取关系、获取属性、生成统计信息，最后保存到MongoDB）。

进一步地，所述溯源算法支持子查询的递归处理，当AST节点为exp.Subquery类型时，提取子查询内部节点并递归处理，保留括号结构返回新的Subquery节点，确保溯源SQL正确处理嵌套查询结构。

进一步地，所述溯源算法支持集合运算的递归处理，当AST节点为exp.Union、exp.Intersect或exp.Except类型时，分别递归处理左右子节点，保持集合运算结构不变，确保溯源SQL正确处理UNION/INTERSECT/EXCEPT等复杂查询。

进一步地，所述隐藏关系探索算法通过分析列名相似度、数据类型匹配、值域重叠等多维度特征，自动发现数据库中未通过外键约束显式定义的潜在关联关系，扩展知识图谱的关系覆盖范围。

进一步地，所述知识图谱驱动的统计信息生成系统将通用统计、数值列专项统计、字符串列专项统计与知识图谱实体属性关联，形成结构化的统计信息体系，为Text-to-SQL提供更丰富的上下文信息。

进一步地，所述SQL方言自动转换模块与溯源算法深度集成，溯源SQL生成后自动调用方言转换模块，确保溯源SQL能在目标数据库正确执行。

## 六、有益效果
与现有技术相比，本发明具有以下有益效果：

1. **提供完整的查询结果溯源能力**：通过基于AST递归解析的溯源算法，将包含LIMIT、GROUP BY、UNION/INTERSECT/EXCEPT等子句的SQL查询自动转换为获取完整涉及数据的溯源SQL，使用户能够全面了解查询涉及的数据范围，验证AI生成的SQL是否准确反映了查询意图。该算法支持子查询、集合运算等复杂SQL结构的递归处理，并实现JOIN等值列去重优化，减少溯源结果中的冗余列。

2. **发现数据库隐藏关系，提升知识图谱完整性**：通过隐藏关系探索算法，突破传统仅依赖外键约束的关系提取方法，通过分析列名相似度、数据类型匹配、值域重叠等多维度特征，自动发现未通过外键定义但实际存在关联的表列对，显著扩展知识图谱的关系覆盖范围，从而提升Text-to-SQL转换时对跨表查询的理解能力。

3. **统计信息与业务语义深度关联**：将数据库统计信息（通用统计、数值列专项统计、字符串列专项统计）与知识图谱实体属性关联，形成结构化的统计信息体系，为Text-to-SQL提供更丰富的上下文信息，包括数据分布特征、值域范围等，提升SQL生成的准确率。

4. **完整的技术闭环**：实现了从多数据库连接池统一管理（支持MySQL、SQLite、MongoDB）→ 数据库知识图谱自动构建（实体、关系、属性、统计信息）→ 知识图谱增强Text-to-SQL转换 → SQL方言自动转换 → 查询结果溯源的完整技术链路，各模块之间深度协同，支持跨数据库的统一智能查询服务。

5. **溯源算法与方言转换深度集成**：溯源SQL生成后自动调用方言转换模块，确保溯源SQL能在不同数据库间正确执行，解决了跨库溯源的技术难题。转换过程内置函数名映射表、分页语法适配、日期时间函数转换等，支持MySQL、SQLite、SQL Server等数据库间的自动转换。

6. **字节到字符串的智能转换**：溯源数据获取后，通过convert_bytes_to_str()函数递归遍历查询结果，优先UTF-8解码，失败则尝试GBK解码，最后使用base64编码，确保二进制数据的正确呈现，提升用户体验。

## 七、具体实施方式
下面结合具体实施例对本发明作进一步详细说明：

**实施例1：查询结果溯源算法的具体实施**

假设用户通过自然语言查询"列出成绩排名前10的学生"，系统生成的SQL为：
```sql
SELECT student_name, score FROM students ORDER BY score DESC LIMIT 10
```

该SQL仅返回前10条记录，用户无法了解查询涉及到的所有学生数据。溯源算法执行以下步骤：

步骤1：使用sqlglot库的parse_one()函数将上述SQL解析为抽象语法树AST。

步骤2：通过_process_node_recursive()函数递归遍历AST节点，识别到exp.Select节点，调用_transform_single_select()函数进行处理。

步骤3：在_transform_single_select()函数中，遍历SELECT节点的所有子节点，提取SELECT子句中的列引用student_name和score，提取FROM子句中的表引用students。

步骤4：构建新的SELECT语句：复制原始FROM子句（FROM students），保留原始WHERE子句（本例无WHERE子句），移除ORDER BY子句和LIMIT子句。

步骤5：生成的溯源SQL为：
```sql
SELECT student_name, score FROM students
```

步骤6：执行溯源SQL获取所有学生的完整数据，通过convert_bytes_to_str()函数处理查询结果中的字节数据，将完整数据返回至前端图表区呈现给用户。

**实施例2：包含集合运算的复杂查询溯源**

假设用户查询"找出同时选修了数学和英语的学生"，系统生成的SQL为：
```sql
SELECT student_name FROM courses WHERE subject = '数学'
INTERSECT
SELECT student_name FROM courses WHERE subject = '英语'
LIMIT 5
```

溯源算法执行以下步骤：

步骤1：解析SQL为AST，识别到exp.Intersect节点。

步骤2：递归处理Intersect节点的左右子节点，分别对两个SELECT语句调用_transform_single_select()函数。

步骤3：对左侧SELECT语句，提取列引用student_name，保留FROM子句和WHERE子句（subject = '数学'）。

步骤4：对右侧SELECT语句，提取列引用student_name，保留FROM子句和WHERE子句（subject = '英语'）。

步骤5：移除LIMIT子句，保持INTERSECT集合运算结构不变。

步骤6：生成的溯源SQL为：
```sql
SELECT student_name FROM courses WHERE subject = '数学'
INTERSECT
SELECT student_name FROM courses WHERE subject = '英语'
```

步骤7：执行溯源SQL获取完整的交集数据，返回至前端图表区。

**实施例3：包含子查询和JOIN的复杂查询溯源**

假设用户查询"找出销售额高于平均值的订单"，系统生成的SQL为：
```sql
SELECT o.order_id, o.amount, c.customer_name
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.amount > (SELECT AVG(amount) FROM orders)
GROUP BY o.order_id
HAVING o.amount > 1000
LIMIT 20
```

溯源算法执行以下步骤：

步骤1：解析SQL为AST，识别到exp.Select节点。

步骤2：调用_transform_single_select()函数，遍历所有子节点：
- 提取SELECT子句中的列引用：o.order_id、o.amount、c.customer_name
- 提取FROM子句中的表引用：orders（别名o）
- 提取JOIN子句：JOIN customers c ON o.customer_id = c.customer_id，提取等值对(o.customer_id, c.customer_id)
- 提取WHERE子句中的列引用：o.amount，并识别子查询(SELECT AVG(amount) FROM orders)
- 对子查询递归处理，提取子查询中的列引用amount和表引用orders

步骤3：JOIN等值列去重：等值条件中的o.customer_id和c.customer_id只保留一个（如保留o.customer_id）。

步骤4：构建新的SELECT语句：
- SELECT子句：包含所有提取的列（o.order_id, o.amount, c.customer_name, o.customer_id）
- FROM子句：FROM orders o
- JOIN子句：JOIN customers c ON o.customer_id = c.customer_id
- WHERE子句：WHERE o.amount > (SELECT AVG(amount) FROM orders)

步骤5：移除GROUP BY子句、HAVING子句和LIMIT子句。

步骤6：生成的溯源SQL为：
```sql
SELECT o.order_id, o.amount, c.customer_name, o.customer_id
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.amount > (SELECT AVG(amount) FROM orders)
```

步骤7：执行溯源SQL获取完整数据，返回至前端图表区。

**实施例4：隐藏关系探索算法的具体实施**

假设数据库中有两个表：orders（订单表）和products（产品表），两表之间没有显式的外键约束。隐藏关系探索算法执行以下步骤：

步骤1：从知识图谱中获取orders表和products表的所有列信息。

步骤2：分析列名相似度：发现orders表的product_code列与products表的product_code列名称完全相同。

步骤3：分析数据类型匹配：确认两列的数据类型均为VARCHAR(50)。

步骤4：分析值域重叠：分别采样两列的值，计算值域重叠度，发现orders.product_code的值全部包含在products.product_code的值域中。

步骤5：综合列名相似度、数据类型匹配、值域重叠等特征，判定两列之间存在潜在关联关系。

步骤6：在知识图谱中添加orders.product_code与products.product_code之间的关联关系，扩展知识图谱的关系覆盖范围。

步骤7：在后续Text-to-SQL转换中，LLM可以利用该隐藏关系正确理解跨表查询意图，生成包含JOIN操作的SQL。

**实施例5：SQL方言自动转换的具体实施**

假设溯源算法生成的溯源SQL为MySQL方言：
```sql
SELECT student_name, DATE_FORMAT(create_time, '%Y-%m-%d') AS create_date
FROM students
WHERE status = 'active'
ORDER BY create_time DESC
LIMIT 10 OFFSET 20
```

需要转换为SQLite方言执行溯源查询，transform_sql()函数执行以下步骤：

步骤1：使用sqlglot库解析SQL为AST，指定dialect为mysql。

步骤2：通过_process_node_recursive()函数递归遍历AST节点。

步骤3：识别到DATE_FORMAT函数调用，根据内置的函数名映射表，将DATE_FORMAT(create_time, '%Y-%m-%d')转换为strftime('%Y-%m-%d', create_time)。

步骤4：识别到LIMIT 10 OFFSET 20语法，转换为SQLite兼容的LIMIT 10 OFFSET 20（SQLite原生支持该语法，无需转换；若转换为SQL Server则需转换为OFFSET 20 ROWS FETCH NEXT 10 ROWS ONLY）。

步骤5：移除ORDER BY子句（溯源算法要求）。

步骤6：生成的SQLite方言溯源SQL为：
```sql
SELECT student_name, strftime('%Y-%m-%d', create_time) AS create_date
FROM students
WHERE status = 'active'
```

步骤7：在SQLite数据库上执行该溯源SQL，获取完整数据。

**实施例6：知识图谱驱动的统计信息生成与Text-to-SQL增强**

步骤1：对数据库的students表执行知识图谱构建，调用get_col_attributes()函数获取score列的详细属性。

步骤2：调用_generate_common_stats()方法计算score列的基础统计：空值数量5、非空值数量995、唯一值数量150、唯一值比例15.08%。

步骤3：调用_generate_numeric_stats()方法计算score列的数值统计：最大值100、最小值0、平均值75.3、中位数76.0、标准差12.5、25分位数68.0、75分位数84.0。

步骤4：将上述统计信息关联到知识图谱中score列实体的属性中。

步骤5：当用户提问"找出成绩优秀的学生（成绩大于80分）"时，text2sql_SP()函数将知识图谱信息（包含score列的统计信息）注入到LLM提示词中。

步骤6：LLM根据统计信息了解到score列的平均值为75.3、75分位数为84.0，可以合理判断80分是一个较高的分数阈值，生成正确的SQL：
```sql
SELECT student_name, score FROM students WHERE score > 80
```

## 八、与现有技术的区别
基于专利查新结果，本发明与现有技术的区别在于：

1. **基于AST递归解析的查询结果溯源算法**：现有技术中的Text-to-SQL系统仅关注SQL生成的准确率，未提供查询结果溯源能力。本发明通过递归遍历SQL抽象语法树，智能移除影响结果集完整性的子句（LIMIT、GROUP BY、HAVING、DISTINCT等），同时保留表连接和筛选条件，生成溯源SQL获取完整数据。该算法支持子查询、集合运算(UNION/INTERSECT/EXCEPT)等复杂SQL结构的递归处理，并实现JOIN等值列去重优化。

2. **数据库隐藏关系探索算法**：现有知识图谱构建方法仅依赖数据库的显式外键约束提取关系。本发明通过分析列名相似度、数据类型匹配、值域重叠等多维度特征，自动发现未通过外键约束显式定义的潜在关联关系，扩展知识图谱的关系覆盖范围，提升Text-to-SQL转换时对跨表查询的理解能力。

3. **知识图谱驱动的数据库统计信息自动生成系统**：现有技术的数据库统计信息分散且缺乏与业务语义的关联。本发明将通用统计、数值列专项统计、字符串列专项统计与知识图谱实体属性关联，形成结构化的统计信息体系，为Text-to-SQL提供更丰富的上下文信息。

4. **多数据库类型统一连接池与知识图谱构建的完整闭环系统**：现有Text-to-SQL系统通常针对单一数据库类型，功能模块相互独立。本发明实现了从多数据库连接池统一管理（支持MySQL、SQLite、MongoDB）→ 数据库知识图谱自动构建 → 知识图谱增强Text-to-SQL转换 → SQL方言自动转换 → 查询结果溯源的完整技术闭环。

5. **SQL方言自动转换与溯源算法的深度集成**：现有技术的SQL方言转换和查询溯源是独立的功能模块。本发明将溯源算法与SQL方言转换深度集成，溯源SQL生成后自动调用方言转换模块，确保溯源SQL能在不同数据库间正确执行，解决了跨库溯源的技术难题。

上述区别特征解决了查询结果不完整、隐藏关系发现、统计信息脱节、系统功能分散、跨库溯源等技术问题，带来了提升数据库查询智能化水平、降低用户使用门槛、提供查询结果溯源能力、提升Text-to-SQL转换准确率等技术效果。