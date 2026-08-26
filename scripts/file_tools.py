import os
import json
import base64
from pathlib import Path
from pptx import Presentation
from docx import Document
import fitz
import pdfplumber
import win32com.client
import pythoncom
import zipfile


def to_json(data: dict, file_path: str):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def from_json(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def clean_filename(filename: str) -> str:
    """清理文件名中的无效字符，返回安全的文件名。 \n
    Windows 文件名无效字符: <>:"/\|?* 以及控制字符
    """
    invalid_chars = set('<>:"/\\|?*')
    # 将无效字符替换为下划线
    cleaned = ''.join(c if c not in invalid_chars else '_' for c in filename)
    # 移除控制字符（ASCII 0-31）
    cleaned = ''.join(c for c in cleaned if ord(c) >= 32)
    # 移除首尾空格和点
    cleaned = cleaned.strip('. ')
    # 如果文件名为空，返回默认名称
    if not cleaned:
        cleaned = 'unnamed_file'
    # 限制文件名长度（Windows 最大255字符）
    if len(cleaned) > 200:
        cleaned = cleaned[:200]

    return cleaned


# ============================================================
# 文件文本和图片提取器
# ============================================================
class FileReader:
    def __init__(self, file_path: str, extension: str, out_dir: str):
        self.file_path = file_path
        self.extension = extension.replace(".", "")
        self.out_dir = out_dir
        os.makedirs(self.out_dir, exist_ok=True)

    def read_texts(self) -> str:
        """读取文件的文本内容"""
        if self.extension in {'pptx', 'ppt', 'pptm'}:
            return self.get_ppt_text()
        elif self.extension in {'docx', 'doc', 'docm'} and self._zip_within_caps():
            return self.get_word_text()
        elif self.extension in {'pdf'}:
            return self.get_pdf_text()
        elif self.extension in {'ipynb'}:
            return self.get_jupyter_text()
        else:
            for encoding in ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'latin-1']:
                try:
                    with open(self.file_path, 'r', encoding=encoding, errors='ignore') as f_input:
                        content = f_input.read()
                    with open(os.path.join(self.out_dir, "content.md"), 'w', encoding=encoding, errors='ignore') as f_output:
                        f_output.write(content)
                    return content
                except:
                    pass
            return ""

    def read_images(self) -> None:
        """提取文件中的图片"""
        if self.extension in {'pptx', 'ppt', 'pptm'}:
            return self.get_ppt_image()
        elif self.extension in {'docx', 'doc', 'docm'} and self._zip_within_caps():
            return self.get_word_image()
        elif self.extension in {'pdf'}:
            return self.get_pdf_image()
        elif self.extension in {'ipynb'}:
            return self.get_jupyter_image()

    def _zip_within_caps(self) -> bool:
        """过滤掉过大的基于 zip 的 Office 文件。
        """
        path = Path(self.file_path)

        try:
            if path.stat().st_size > 50 * 1024 * 1024:
                return False
        except OSError:
            return False

        try:
            with zipfile.ZipFile(path) as zf:
                infos = zf.infolist()
                compressed = sum(i.compress_size for i in infos) or 1
                declared = sum(i.file_size for i in infos)
                if declared > 512 * 1024 * 1024:
                    return False
                if declared / compressed > 200:
                    return False
                total = 0
                for info in infos:
                    with zf.open(info) as member:
                        while True:
                            chunk = member.read(1024 * 1024)
                            if not chunk:
                                break
                            total += len(chunk)
                            if total > 512 * 1024 * 1024:
                                return False
        except (zipfile.BadZipFile, OSError, EOFError):
            return False
        return True

    def get_ppt_text(self) -> str:
        text_output = []
        if self.extension == "ppt":
            try:
                pythoncom.CoInitialize()
                app = win32com.client.Dispatch("PowerPoint.Application")
                prs = app.Presentations.Open(self.file_path, WithWindow=False)
                for slide_number, slide in enumerate(prs.Slides, start=1):
                    slide_text = []
                    for shape in slide.Shapes:
                        if shape.HasTextFrame and shape.TextFrame.HasText:
                            text = shape.TextFrame.TextRange.Text.strip()
                            if text:
                                slide_text.append(text)
                    if slide_text:
                        text_output.append(f"### Slide {slide_number}\n" + "\n".join(slide_text).strip())
                prs.Close()
                app.Quit()
                pythoncom.CoUninitialize()
            except:
                if 'app' in locals():
                    app.Quit()
                pythoncom.CoUninitialize()
                return ""
        else:
            try:
                presentation = Presentation(self.file_path)
                for slide_number, slide in enumerate(presentation.slides, start=1):
                    slide_text = []
                    for shape in slide.shapes:
                        if shape.has_text_frame:
                            for paragraph in shape.text_frame.paragraphs:
                                slide_text.append("".join(run.text for run in paragraph.runs))
                    if slide_text:
                        text_output.append(f"### Slide {slide_number}\n" + "\n".join(slide_text).strip())
            except:
                return ""
        text_output = "\n".join(text_output)
        with open(os.path.join(self.out_dir, "content.md"), 'w', encoding='utf-8') as f:
            f.write(text_output)
        return text_output

    def get_ppt_image(self) -> None:
        image_cnt = 1
        if self.extension == "ppt":
            try:
                pythoncom.CoInitialize()
                app = win32com.client.Dispatch("PowerPoint.Application")
                prs = app.Presentations.Open(self.file_path, WithWindow=False)
                for slide in prs.Slides:
                    for shape in slide.Shapes:
                        if shape.Type == 13:
                            try:
                                shape.Export(os.path.join(self.out_dir, f"image{image_cnt}.png"), 2)
                                image_cnt += 1
                            except:
                                pass
                prs.Close()
                app.Quit()
                pythoncom.CoUninitialize()
            except Exception as e:
                if 'app' in locals():
                    app.Quit()
                pythoncom.CoUninitialize()
        else:
            presentation = Presentation(self.file_path)
            for slide in presentation.slides:
                for shape in slide.shapes:
                    try:
                        if "image" in shape.image.content_type:
                            with open(os.path.join(self.out_dir, f"image{image_cnt}.{shape.image.ext}"), 'wb') as f:
                                f.write(shape.image.blob)
                            image_cnt += 1
                    except:
                        pass

    def get_word_text(self) -> str:
        '''仅支持 .docx 格式'''
        paragraphs = []
        try:
            doc = Document(self.file_path)
            for para in doc.paragraphs:
                # 跳过表格
                if para._element.getparent().tag.endswith('tbl') or para._element.getparent().tag.endswith('tc'):
                    continue
                if para.text.strip():
                    style = para.style.name if para.style else ""
                    if "Heading" in style or "标题" in style:
                        level = style.replace("Heading ", "").replace("标题 ", "")
                        prefix = "#" * int(level) if level.isdigit() else "##"
                        paragraphs.append(f"{prefix} {para.text}")
                    else:
                        paragraphs.append(para.text)
        except:
            return ""

        with open(os.path.join(self.out_dir, "content.md"), 'w', encoding='utf-8') as f:
            f.write('\n'.join(paragraphs))

        return '\n'.join(paragraphs)

    def get_word_image(self) -> None:
        if self.extension == "doc":
            try:
                pythoncom.CoInitialize()
                app = win32com.client.DispatchEx("Word.Application")
                app.Visible = False
                doc = app.Documents.Open(self.file_path)
                # 将.doc另存为临时.docx，然后提取图片
                temp_docx = os.path.join(self.out_dir, "_temp_extract.docx")
                doc.SaveAs2(temp_docx, FileFormat=16)  # 16 = wdFormatXMLDocument
                # 从临时docx中提取图片
                with zipfile.ZipFile(temp_docx, 'r') as z:
                    for item in z.namelist():
                        try:
                            if item.startswith('word/media/'):
                                with open(os.path.join(self.out_dir, os.path.basename(item)), 'wb') as f:
                                    f.write(z.read(item))
                        except:
                            pass
                # 清理临时文件
                if os.path.exists(temp_docx):
                    os.remove(temp_docx)
                doc.Close()
                app.Quit()
                pythoncom.CoUninitialize()
            except Exception as e:
                if 'app' in locals():
                    app.Quit()
                pythoncom.CoUninitialize()
        else:
            with zipfile.ZipFile(self.file_path, 'r') as z:
                for item in z.namelist():
                    try:
                        if item.startswith('word/media/'):
                            with open(os.path.join(self.out_dir, os.path.basename(item)), 'wb') as f:
                                f.write(z.read(item))
                    except:
                        pass

    def get_pdf_text(self) -> str:
        pages_text = []
        try:
            with pdfplumber.open(self.file_path) as pdf:
                for i, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        pages_text.append(f"## Page {i}\n{text}")
            with open(os.path.join(self.out_dir, "content.md"), 'w', encoding='utf-8') as f:
                f.write('\n'.join(pages_text))
            return '\n'.join(pages_text)
        except:
            return ""

    def get_pdf_image(self) -> None:
        image_cnt = 1
        doc = fitz.open(self.file_path)
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            image_list = page.get_images(full=True)
            for image in image_list:
                try:
                    xref = image[0]
                    base_image = doc.extract_image(xref)
                    image_path = os.path.join(self.out_dir, f"image{image_cnt}.{base_image['ext']}")
                    image_cnt += 1
                    with open(image_path, "wb") as f:
                        f.write(base_image["image"])
                except:
                    pass
        doc.close()

    def get_jupyter_text(self) -> str:
        cells_text = []
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                notebook = json.load(f)
            for i, cell in enumerate(notebook.get('cells', [])):
                cell_type = cell.get('cell_type', 'unknown')
                source = ''.join(cell.get('source', []))
                if source.strip():
                    if cell_type == 'code':
                        cells_text.append(f"## Cell {i+1} (Code)\n```python\n{source}\n```")
                    elif cell_type == 'markdown':
                        cells_text.append(f"## Cell {i+1} (Markdown)\n{source}")
                    elif cell_type == 'raw':
                        cells_text.append(f"## Cell {i+1} (Raw)\n{source}")
                    else:
                        cells_text.append(f"## Cell {i+1}\n{source}")
            with open(os.path.join(self.out_dir, "content.md"), 'w', encoding='utf-8') as f:
                f.write('\n'.join(cells_text))
            return '\n'.join(cells_text)
        except:
            return ""

    def get_jupyter_image(self) -> None:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                    notebook = json.load(f)
            for i, cell in enumerate(notebook.get('cells', [])):
                if cell.get('cell_type', 'unknown') == 'code':
                    image_cnt = 1
                    outputs = cell.get('outputs', [])
                    for output in outputs:
                        if 'data' in output:
                            data = output['data']
                            if 'image/png' in data:
                                png_data = base64.b64decode(data['image/png'])
                                image_path = os.path.join(self.out_dir, f"cell{i+1}_image{image_cnt}.png")
                                image_cnt += 1
                                with open(image_path, 'wb') as f:
                                    f.write(png_data)
                            if 'image/jpeg' in data:
                                jpeg_data = base64.b64decode(data['image/jpeg'])
                                image_path = os.path.join(self.out_dir, f"cell{i+1}_image{image_cnt}.jpg")
                                image_cnt += 1
                                with open(image_path, 'wb') as f:
                                    f.write(jpeg_data)
        except:
            pass
