import os
import sys
from pathlib import Path

from file_tools import to_json, FileReader, is_sensitive_file, content_remove_sensitive
from config import OUT_ROOT

# 大概率无用的目录
SKIP_DIRS = frozenset({
    # ========== 版本控制系统 ==========
    '.git', '.svn', '.hg', '.bzr',

    # ========== IDE和编辑器配置 ==========
    '.idea', '.vscode', '.vs', '.eclipse', '.settings',
    '.project', '.classpath', '.factorypath',

    # ========== Python虚拟环境和缓存 ==========
    '__pycache__', 'venv', 'env', '.venv', '.env', '.conda',
    '.mypy_cache', '.pytest_cache', '.tox', '.nox',
    'eggs', 'wheels', 'dist-info', 'egg-info', '.eggs',
    '.hypothesis',

    # ========== Node.js相关 ==========
    'node_modules', 'bower_components', '.npm', '.yarn',
    '.pnpm-store', '.pnp',

    # ========== Java/Gradle/Maven ==========
    'target', '.gradle', 'gradle', '.mvn', '.m2',

    # ========== C/C++/Rust构建 ==========
    'cmake-build-debug', 'cmake-build-release', '.ccls-cache',
    'build', 'out', 'obj', 'Release', 'Debug',

    # ========== Go ==========
    'vendor',

    # ========== Rust ==========
    'target',

    # ========== 构建产物和分发目录 ==========
    'dist', '.next', '.nuxt', '.output', '.svelte-kit',

    # ========== .NET ==========
    'packages', '.nuget',

    # ========== 文档构建产物 ==========
    '_build', 'docs/_build', '_site',

    # ========== 测试覆盖率报告 ==========
    'htmlcov', '.coverage', '.nyc_output',

    # ========== Docker和容器 ==========
    '.docker',

    # ========== IaC工具 ==========
    '.terraform', '.serverless',

    # ========== 包管理器缓存 ==========
    '.cache', '.parcel-cache', '.vite',

    # ========== 操作系统隐藏文件 ==========
    '.Spotlight-V100', '.Trashes', '.fseventsd',

    # ========== 日志和临时文件 ==========
    'logs', 'tmp', 'temp', '.tmp',

    # ========== 文档和笔记 ==========
    '.obsidian', '.notion',

    # ========== 本技能产生的文件 ==========
    OUT_ROOT,
})

 # 大概率有用的文件扩展名
# 大概率无用的文件
SKIP_FILES = frozenset({
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "Cargo.lock", "poetry.lock", "Gemfile.lock",
    "composer.lock", "go.sum", "go.work.sum",
})
# 大概率有用的文件
READ_EXTENSIONS = frozenset({
    # ========== 标记语言（直接读取） ==========
    '.md', '.markdown', '.rst', '.adoc', '.asciidoc', '.tex', '.latex', '.wiki',
    '.org', '.textile',

    # ========== 配置文件（直接读取） ==========
    '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.properties',
    '.env', '.gitignore', '.dockerignore', '.editorconfig', '.prettierrc', '.eslintrc',
    '.babelrc', '.npmrc', '.yarnrc', '.txt', '.text',

    # ========== 脚本/命令文件（直接读取） ==========
    '.bat', '.cmd', '.ps1', '.psm1', '.psd1', '.vbs', '.wsf',

    # ========== 需要安装库才能读取的文档 ==========
    '.docx',      # Word（仅支持 .docx 格式）
    '.pptx', '.ppt', '.pptm',    # PowerPoint
    '.pdf',       # PDF
    '.ipynb',     # Jupyter Notebook

    # ========== 图片文件 ==========
#    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff', '.tif',
#    '.svg', '.ico', '.avif', '.heic', '.heif',
})
CODE_EXTENSIONS = frozenset({
    '.py', '.ts', '.tsx', '.mts', '.cts', '.js', '.jsx', '.mjs', '.cjs', '.ejs', '.ets',
    '.go', '.rs', '.java', '.groovy', '.gradle', '.cpp', '.cc', '.cxx', '.c', '.h', '.hpp',
    '.cu', '.cuh', '.metal', '.rb', '.rake', '.swift', '.kt', '.kts', '.cs', '.scala', '.php',
    '.lua', '.luau', '.toc', '.zig', '.ex', '.exs', '.m', '.mm', '.asd',
    '.ml', '.mli', '.jl', '.vue', '.svelte', '.astro', '.dart', '.v', '.sv', '.svh', '.sql',
    '.r', '.f', '.F', '.f90', '.F90', '.f95', '.F95', '.f03', '.F03', '.f08', '.F08', '.pas',
    '.pp', '.dpr', '.dpk', '.lpr', '.inc', '.dfm', '.lfm', '.lpk', '.sh', '.bash',
    '.tf', '.tfvars', '.hcl', '.dm', '.dme', '.dmi', '.dmm', '.dmf', '.sln', '.slnx', '.csproj',
    '.fsproj', '.vbproj', '.xaml', '.razor', '.cshtml', '.cls', '.trigger', '.lisp', '.cl', '.lsp',
})


def get_files_info(project_root: str, dir_path: str):
    """
    遍历目录下的所有有用的非代码和图片文件，并收集基本信息。
    Returns:
        目录的树形结构，叶子节点为文件名和文件信息，其余节点为目录名，文件信息包含：
        - path: 文件绝对路径
        - content_path: 从文件中解析出的内容的存储路径
        - name: 文件名
        - extension: 扩展名
        - preview: 前N行内容（仅针对文本文件）
    """
    files_info = {}
    for roots, dirs, files in os.walk(dir_path):
        if OUT_ROOT not in roots:
            for file in files:
                if file not in SKIP_FILES:
                    try:
                        file_path = Path(roots) / file
                        if is_sensitive_file(file_path):
                            continue
                        file_name = file_path.stem
                        file_extension = file_path.suffix.lower()
                        if file_extension in READ_EXTENSIONS:
                            out_dir = os.path.join(project_root, f"{OUT_ROOT}/project files",
                                                Path(roots).relative_to(project_root), file)
                            file_reader = FileReader(file_path, file_extension, out_dir)
                            file_reader.read_images()
                            files_info[file] = {
                                "path": str(file_path),
                                "content_path": out_dir,
                                "name": file_name,
                                "extension": file_extension,
                                "preview": "\n".join(file_reader.read_texts().splitlines()[:5])
                            }
                    except:
                        pass
            for dir in dirs:
                if dir not in SKIP_DIRS and OUT_ROOT != dir:
                    files_info[dir] = get_files_info(project_root, os.path.join(roots, dir))

    to_json(files_info, os.path.join(project_root, f"{OUT_ROOT}/project files", "files_info.json"))

    return files_info


def examine_code_file(project_root: str) -> None:
    """
    递归扫描目录下的所有代码文件，检测是否包含敏感信息。
    Args:
        project_root: 项目根目录路径
    """
    sensitive_files = []

    for root, dirs, files in os.walk(project_root):
        # 跳过不需要扫描的目录
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and OUT_ROOT != d]

        for file in files:
            # 跳过不需要扫描的文件
            if file in SKIP_FILES:
                continue

            file_path = Path(root) / file
            file_extension = file_path.suffix.lower()

            # 只检查代码文件
            if file_extension not in CODE_EXTENSIONS:
                continue

            # 尝试读取文件内容
            try:
                for encoding in ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'latin-1']:
                    try:
                        with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                            original_content = f.read()

                        # 调用敏感信息过滤函数
                        cleaned_content = content_remove_sensitive(original_content)

                        # 检查是否包含 [REDACTED] 标记
                        if '[REDACTED]' in cleaned_content:
                            # 找到所有 [REDACTED] 的位置并提取上下文
                            redacted_positions = []
                            start = 0
                            while True:
                                pos = cleaned_content.find('[REDACTED]', start)
                                if pos == -1:
                                    break

                                # 提取前后各50个字符作为上下文
                                context_start = max(0, pos - 50)
                                context_end = min(len(cleaned_content), pos + len('[REDACTED]') + 50)
                                context = cleaned_content[context_start:context_end]

                                # 计算行号
                                line_number = cleaned_content[:pos].count('\n') + 1

                                redacted_positions.append({
                                    'line': line_number,
                                    'context': context.strip()
                                })
                                start = pos + 1

                            sensitive_files.append({
                                'file_path': str(file_path),
                                'relative_path': str(file_path.relative_to(project_root)) if project_root else str(file_path),
                                'encoding': encoding,
                                'redacted_count': len(redacted_positions),
                                'redacted_positions': redacted_positions
                            })

                            rel_path = file_path.relative_to(project_root) if project_root else file_path
                            print(f"\n[警告] {rel_path} ({len(redacted_positions)}处)")
                            for idx, pos_info in enumerate(redacted_positions[:3], 1):
                                ctx = pos_info['context']
                                # 截断过长的上下文
                                if len(ctx) > 80:
                                    ctx = ctx[:77] + '...'
                                print(f"  Line {pos_info['line']}: ...{ctx}")
                            if len(redacted_positions) > 3:
                                print(f"  ...")

                        break
                    except UnicodeDecodeError:
                        continue
                    except Exception as e:
                        print(f"[错误] 读取文件失败 {file_path}: {e}")
                        break

            except Exception as e:
                print(f"[错误] 处理文件失败 {file_path}: {e}")
                continue

    # 打印汇总信息
    if sensitive_files:
        total = sum(f['redacted_count'] for f in sensitive_files)
        print(f"\n[检测完成] {len(sensitive_files)}个文件含敏感信息:")
        for file_info in sensitive_files:
            lines = ', '.join(str(p['line']) for p in file_info['redacted_positions'][:5])
            print(f"  {file_info['relative_path']}: Line {lines}")
    else:
        print(f"\n[检测完成] 未发现敏感信息")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python analyze_project.py get_files_info <project_root> <dir_path>")
        print("  python analyze_project.py examine_code_file <project_root>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "get_files_info":
        if len(sys.argv) < 4:
            print("错误: get_files_info 需要两个参数: <project_root> <dir_path>")
            sys.exit(1)
        project_root = sys.argv[2]
        dir_path = sys.argv[3]
        print(f"开始分析项目: {project_root}")
        result = get_files_info(project_root, dir_path)

    elif command == "examine_code_file":
        if len(sys.argv) < 3:
            print("错误: examine_code_file 需要一个参数: <project_root>")
            sys.exit(1)
        project_root = sys.argv[2]
        print(f"开始扫描敏感信息: {project_root}")
        examine_code_file(project_root)

    else:
        print(f"Unknown command: {command}")
        print("Available commands: get_files_info, examine_code_file")
        sys.exit(1)