import os
from pathlib import Path
from dataclasses import dataclass

from file_tools import to_json, FileReader
from config import OUT_ROOT

# 大概率无用的目录
SKIP_DIRS = {
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
}

 # 大概率有用的文件扩展名
# 大概率有用的文件
READ_EXTENSIONS = {
    # ========== 代码文件（直接读取） ==========
#    '.py', '.java', '.js', '.ts', '.jsx', '.tsx', '.go', '.cpp', '.c', '.h', '.hpp',
#    '.cs', '.rb', '.php', '.swift', '.kt', '.kts', '.scala', '.rs', '.sh', '.bash',
#    '.zsh', '.fish', '.sql', '.r', '.m', '.pl', '.lua', '.dart', '.vue', '.svelte',
#    '.asm', '.s', '.clj', '.cljs', '.erl', '.hrl', '.ex', '.exs', '.hs', '.ml',
#    '.mli', '.pas', '.pp', '.groovy', '.gradle', '.tf', '.hcl', '.cmake', '.make',
#    '.mk', '.dockerfile', '.css', '.xml', '.html', '.htm', '.xhtml', '.scss', '.sass',
#    '.less', '.styl',

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
}

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
                try:
                    file_path = Path(roots) / file
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
