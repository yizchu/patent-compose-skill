#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import yaml

from file_tools import to_json, from_json

class YamlToJsonConverter:
    """YAML 到 JSON 的转换器"""

    def __init__(self, yaml_file_path: str):
        """
        初始化转换器

        Args:
            yaml_file_path: YAML 文件的完整路径
        """
        self.yaml_path = Path(yaml_file_path)
        self.json_path = self.yaml_path.with_suffix('.json')
        self.data: Optional[Dict[str, Any]] = None

    def validate_yaml_file(self) -> bool:
        """
        验证 YAML 文件是否存在且格式正确

        Returns:
            bool: 验证是否通过
        """
        if not self.yaml_path.exists():
            print(f"错误：YAML 文件不存在: {self.yaml_path}")
            return False

        if not self.yaml_path.suffix.lower() in ['.yaml', '.yml']:
            print(f"警告：文件扩展名不是 .yaml 或 .yml: {self.yaml_path}")

        if self.yaml_path.stat().st_size == 0:
            print(f"错误：YAML 文件为空: {self.yaml_path}")
            return False

        return True

    def read_yaml(self) -> bool:
        """
        读取并解析 YAML 文件

        Returns:
            bool: 读取是否成功
        """
        try:
            with open(self.yaml_path, 'r', encoding='utf-8') as f:
                content = f.read()

            self.data = yaml.safe_load(content)

            if self.data is None:
                print(f"警告：YAML 文件内容为空或只包含注释: {self.yaml_path}")
                self.data = {}

            return True

        except yaml.YAMLError as e:
            print(f"错误：YAML 解析失败: {e}")
            return False
        except Exception as e:
            print(f"错误：读取 YAML 文件时发生异常: {e}")
            return False

    def validate_json_data(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        验证字典数据是否能正确序列化为合法 JSON

        Args:
            data: 要验证的字典数据

        Returns:
            Tuple[bool, str]: (是否通过验证, 错误信息/成功信息)
        """
        try:
            test_json_str = json.dumps(
                data,
                ensure_ascii=False,
                indent=2,
                sort_keys=False
            )

            json.loads(test_json_str)

            info = f"✅ 数据验证通过 - 类型: {type(data).__name__}"
            if isinstance(data, dict):
                info += f", 包含 {len(data)} 个顶级键"
            elif isinstance(data, list):
                info += f", 包含 {len(data)} 个元素"

            return True, info

        except (TypeError, ValueError) as e:
            return False, f"❌ 数据无法序列化为 JSON: {e}"

    def generate_json_file(self) -> bool:
        """
        使用 file_tools.to_json 生成 JSON 文件

        Returns:
            bool: 生成是否成功
        """
        try:
            to_json(self.data, str(self.json_path))
            return True
        except Exception as e:
            print(f"错误：生成 JSON 文件时发生异常: {e}")
            return False

    def verify_generated_json(self) -> bool:
        """
        使用 file_tools.from_json 验证生成的 JSON 文件
        如果格式错误，from_json 会自动修复

        Returns:
            bool: 验证是否通过（或修复成功）
        """
        try:
            data = from_json(str(self.json_path))

            print(f"✅ JSON 文件验证通过: {self.json_path}")
            print(f"   - 文件大小: {self.json_path.stat().st_size} 字节")
            print(f"   - 数据类型: {type(data).__name__}")

            if isinstance(data, dict):
                print(f"   - 顶级键数量: {len(data)}")
            elif isinstance(data, list):
                print(f"   - 数组长度: {len(data)}")

            return True

        except Exception as e:
            print(f"❌ 验证过程中发生异常: {e}")
            return False

    def convert(self) -> bool:
        """
        执行完整的转换流程（含内置验证）

        流程：
        1. 验证 YAML 文件
        2. 读取并解析 YAML
        3. 验证数据可序列化
        4. 使用 to_json 生成 JSON 文件
        5. 使用 from_json 验证生成的 JSON 文件
        任何步骤失败则终止流程

        Returns:
            bool: 转换是否成功（所有步骤都通过）
        """
        print("YAML -> JSON")
        print(f"输入文件: {self.yaml_path}")
        print(f"输出文件: {self.json_path}\n")

        # 步骤 1: 验证 YAML 文件
        print("步骤 1/4: 验证 YAML 文件...")
        if not self.validate_yaml_file():
            return False
        print("✅ YAML 文件验证通过\n")

        # 步骤 2: 读取 YAML 数据
        print("步骤 2/4: 读取 YAML 文件...")
        if not self.read_yaml():
            return False
        print("✅ YAML 文件读取成功\n")

        # 步骤 3: 验证数据可序列化
        print("步骤 3/4: 验证数据结构...")
        is_valid, message = self.validate_json_data(self.data)
        print(message)
        if not is_valid:
            print("\n❌ 数据验证失败，终止转换流程")
            return False
        print()

        # 步骤 4: 使用 to_json 生成 JSON 文件
        print("步骤 4/4: 生成 JSON 文件（使用 file_tools.to_json）...")
        if not self.generate_json_file():
            return False
        print("✅ JSON 文件生成成功\n")

        # 最终验证：使用 from_json 检查生成的 JSON 文件
        print("最终验证: 使用 file_tools.from_json 检查生成的 JSON 文件...")
        if not self.verify_generated_json():
            print("\n❌ JSON 文件验证失败，转换未完成")
            return False

        print(f"\n输出文件路径: {self.json_path.absolute()}")

        return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'yaml_file',
        help='要转换的 YAML 文件路径'
    )

    args = parser.parse_args()

    yaml_file_path = args.yaml_file

    if not os.path.isabs(yaml_file_path):
        yaml_file_path = os.path.join(os.getcwd(), yaml_file_path)

    converter = YamlToJsonConverter(yaml_file_path)
    success = converter.convert()

    sys.exit(0 if success else 1)