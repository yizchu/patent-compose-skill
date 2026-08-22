import os
import sys
import time
import subprocess
import argparse
from playwright.sync_api import sync_playwright

from config import OUT_ROOT
from file_tools import from_json, to_json, clean_filename

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36'
MAX_RETRIES = 5
RETRY_DELAY = 5


def install_playwright_chromium():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)   # 技能根目录
    # 设置镜像
    os.environ['PLAYWRIGHT_DOWNLOAD_HOST'] = 'https://npmmirror.com/mirrors/playwright/'
    print("playwright install chromium")
    # 安装
    result = subprocess.run(
        ['playwright', 'install', 'chromium'],
        cwd=parent_dir,
        capture_output=True,
        text=True,
        shell=True
    )
    if result.stderr:
        print("错误输出:")
        print(result.stderr)
    if result.returncode == 0:
        print("✓ Playwright Chromium 已安装")
    else:
        print(f"✗ 安装失败，返回码: {result.returncode}")
        sys.exit(1)


class PriorSearch:
    _shared_browser = None
    _shared_playwright = None
    _shared_context = None

    @classmethod
    def _init_shared(cls):
        if cls._shared_playwright is None:
            install_playwright_chromium()
            cls._shared_playwright = sync_playwright().start()
            cls._shared_browser = cls._shared_playwright.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
            )
            cls._shared_context = cls._shared_browser.new_context(
                user_agent=USER_AGENT,
                locale="zh-CN",
                viewport={"width": 1280, "height": 900}
            )

    def __init__(self, out_dir: str):
        self.out_dir = out_dir
        os.makedirs(self.out_dir, exist_ok=True)
        PriorSearch._init_shared()
        self.page = PriorSearch._shared_context.new_page()


class CnkiSearch(PriorSearch):
    '''
    中国知网数据库（国内专利）
    '''
    def __init__(self, out_dir: str):
        super().__init__(out_dir)

    def formula(self, keywords: list) -> str:
        '''
        将关键词列表转换为检索式
        '''
        return '*'.join(keywords)

    def search(self, keywords: list, to_page: int = 10):
        print(f"正在检索: {keywords}")
        keyword = self.formula(keywords)
        base_url = "https://kns.cnki.net/res/category/patent"
        patents = {}

        for attempt in range(MAX_RETRIES):
            try:
                self.page.goto(base_url, wait_until="load", timeout=30000)
                self.page.wait_for_timeout(3000)

                input_box = self.page.locator("input[data-v-703e12f2]")
                input_box.wait_for(state="visible", timeout=10000)
                input_box.fill(keyword)

                search_button = self.page.locator(".btn-search")
                search_button.wait_for(state="visible", timeout=10000)
                search_button.click()
                self.page.wait_for_timeout(5000)

                # 按"综合"排序。若无检索内容，这个是找不到的，于是将直接报错退出，恰好不会生成空的json文件
                zh_sort = self.page.locator('li#ZH')
                zh_sort.wait_for(state="visible", timeout=10000)
                zh_sort.click()
                self.page.wait_for_timeout(2000)

                for _page in range(to_page):
                    result_table = self.page.locator("table.result-table-list").locator("tbody")
                    result_table.wait_for(state="visible", timeout=30000)
                    rows = result_table.locator("tr")
                    rows.last.wait_for(state="visible", timeout=60000)

                    for idx in range(rows.count()):
                        row = rows.nth(idx)
                        title_link = row.locator("a.fz14")
                        patent_title = title_link.inner_text()
                        if patent_title in patents:
                            continue
                        #print(f"正在处理: {patent_title}")

                        # 监听新标签页打开
                        for _ in range(MAX_RETRIES):
                            try:
                                with PriorSearch._shared_context.expect_page() as page_info:
                                    title_link.click()
                                new_page = page_info.value
                                new_page.wait_for_load_state("load", timeout=15000)
                                break
                            except:
                                time.sleep(RETRY_DELAY)

                        try:
                            claim = new_page.locator("div.claim-text")
                            claim.wait_for(state="visible", timeout=10000)
                            claim_text = claim.inner_text()
                        except:
                            claim_text = ""

                        try:
                            abstract = new_page.locator("div.abstract-text")
                            abstract.wait_for(state="visible", timeout=10000)
                            abstract_text = abstract.inner_text()
                        except:
                            abstract_text = ""

                        patents[patent_title] = {
                            "claim": claim_text,
                            "abstract": abstract_text
                        }

                        # 关闭新标签页，回到搜索结果页
                        new_page.close()
                        self.page.wait_for_timeout(1000)
                        time.sleep(RETRY_DELAY)

                    # 模拟键盘 右方向键 翻页
                    self.page.keyboard.press("ArrowRight")
                    self.page.wait_for_timeout(5000)

                to_json(patents, os.path.join(self.out_dir,
                                    clean_filename(keyword)+".json"))
                print(f"✓ Cnki检索成功: {keyword}")
                return True

            except Exception as e:
                #print(f"✗ Cnki检索出错: {e}")
                time.sleep(RETRY_DELAY)


class FpoSearch(PriorSearch):
    '''
    FreePatentsOnline数据库（国外专利）
    '''
    def __init__(self, out_dir: str):
        super().__init__(out_dir)

    def formula(self, keywords: list) -> str:
        '''
        将关键词列表转换为检索式
        '''
        return ' AND '.join(keywords)

    def search(self, keywords: list, to_page: int = 2):
        print(f"正在检索: {keywords}")
        keyword = self.formula(keywords)
        base_url = f"https://www.freepatentsonline.com/"
        patents = {}

        # 编码查询词：空格替换为加号，特殊字符URL编码
        #query_txt = keyword.replace(' ', '+')
        #query_txt = quote(query_txt, safe='+')

        for attempt in range(MAX_RETRIES):
            try:
                self.page.goto(base_url, wait_until="load", timeout=30000)
                self.page.wait_for_timeout(3000)
                cookies_list = self.page.context.cookies()
                self.cookies = {cookie['name']: cookie['value'] for cookie in cookies_list}

                input_box = self.page.locator("input#topSearchBox")
                input_box.wait_for(state="visible", timeout=10000)
                input_box.fill(keyword)

                other_box = self.page.locator("input#patents_other")
                other_box.wait_for(state="visible", timeout=10000)
                other_box.click()

                search_button = self.page.get_by_role("button", name="Search")
                search_button.wait_for(state="visible", timeout=10000)
                search_button.click()
                self.page.wait_for_timeout(10000)

                for _page in range(to_page):
                    result_table = self.page.locator("table.listing_table").locator("tbody")
                    result_table.wait_for(state="visible", timeout=30000)
                    rows = result_table.locator("tr")
                    rows.first.wait_for(state="visible", timeout=30000)

                    for idx in range(1, rows.count()):
                        row = rows.nth(idx)
                        title_link = row.locator("a")
                        patent_title = title_link.inner_text()
                        if patent_title in patents:
                            continue
                        #print(f"正在处理: {patent_title}")

                        # 在新标签页打开链接
                        for _ in range(MAX_RETRIES):
                            try:
                                with PriorSearch._shared_context.expect_page() as page_info:
                                    title_link.click(modifiers=["Control"])

                                new_page = page_info.value
                                new_page.wait_for_load_state("load", timeout=30000)
                                doc2_elements = new_page.locator('div.disp_doc2')
                                doc2_elements.first.wait_for(state="visible", timeout=120000)
                                break
                            except:
                                time.sleep(RETRY_DELAY)

                        abstract_text = ''
                        claim_text = ''

                        for i in range(doc2_elements.count()):
                            doc2 = doc2_elements.nth(i)
                            elm_title = doc2.locator('div.disp_elm_title')
                            if elm_title.count() > 0:
                                title_text = elm_title.inner_text().strip()
                                if title_text == 'Abstract:':
                                    abstract_elm = doc2.locator('div.disp_elm_text')
                                    if abstract_elm.count() > 0:
                                        abstract_text = abstract_elm.inner_text().strip()
                                elif title_text == 'Claims:':
                                    claim_elm = doc2.locator('div.disp_elm_text')
                                    if claim_elm.count() > 0:
                                        claim_text = claim_elm.inner_text().strip()
                                    break

                        patents[patent_title] = {
                            "claim": claim_text,
                            "abstract": abstract_text
                        }

                        # 关闭新标签页，回到搜索结果页
                        new_page.close()
                        self.page.wait_for_timeout(1000)
                        time.sleep(RETRY_DELAY)

                    # 前往下一页
                    next_page_button = self.page.get_by_role("link", name=">")
                    next_page_button.first.wait_for(state="visible", timeout=10000)
                    next_href = next_page_button.first.get_attribute("href")
                    if next_href:
                        for _ in range(MAX_RETRIES):
                            try:
                                next_url = next_href if next_href.startswith("http") else f"https://www.freepatentsonline.com/{next_href}"
                                self.page.goto(next_url, wait_until="load", timeout=30000)
                                self.page.wait_for_timeout(5000)
                                break
                            except:
                                time.sleep(RETRY_DELAY)
                    else:
                        break

                to_json(patents, os.path.join(self.out_dir, clean_filename(keyword) + ".json"))
                print(f"✓ FPO检索成功: {keyword}")
                return True

            except Exception as e:
                #print(f"✗ FPO检索出错: {e}")
                time.sleep(RETRY_DELAY)


def prior_search(project_root: str, home_only: bool = False):
    '''
    Parameters:
        out_dir (str): 输出目录
        keywords_cn (list, optional): 中文检索词列表
        keywords_en (list, optional): 英文检索词列表
    '''
    if OUT_ROOT in project_root:
        if "prior art" in project_root:
            out_dir = project_root
            input_dir = os.path.join(os.path.dirname(project_root), "materials")
        else:
            out_dir = os.path.join(project_root, "prior art")
            input_dir = os.path.join(project_root, "materials")
    else:
        out_dir = os.path.join(project_root, OUT_ROOT, "prior art")
        input_dir = os.path.join(project_root, OUT_ROOT, "materials")

    keywords_cn = from_json(os.path.join(input_dir, "keyword-cn.json"))
    keywords_en = from_json(os.path.join(input_dir, "keyword-en.json"))

    cnki_search = CnkiSearch(out_dir)
    max_len = max(len(keywords_cn), len(keywords_en))

    if not home_only:
        fpo_search = FpoSearch(out_dir)
        # 国内外数据库交替检索
        for i in range(max_len):
            if i < len(keywords_cn):
                for keywords in keywords_cn[i]:
                    if cnki_search.search(keywords):
                        break
            if i < len(keywords_en):
                for keywords in keywords_en[i]:
                    if fpo_search.search(keywords):
                        break
    else:
        # 仅国内数据库检索
        for i in range(max_len):
            if i < len(keywords_cn):
                for keywords in keywords_cn[i]:
                    if cnki_search.search(keywords):
                        break
            if i < len(keywords_en):
                for keywords in keywords_en[i]:
                    if cnki_search.search(keywords):
                        break


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument("project_root", type=str, help="项目根目录")
    args.add_argument("home_only", action="store_false", help="仅检索国内数据库")
    args = args.parse_args()
    prior_search(args.project_root, args.home_only)