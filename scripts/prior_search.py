import os
import sys
import math
import asyncio
import argparse
from abc import abstractmethod
from playwright.async_api import async_playwright

from config import OUT_ROOT
from file_tools import from_json, to_json, clean_filename

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36'
MAX_RETRIES = 5
RETRY_DELAY = 5


async def install_playwright_chromium():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    os.environ['PLAYWRIGHT_DOWNLOAD_HOST'] = 'https://npmmirror.com/mirrors/playwright/'
    print("playwright install chromium")
    proc = await asyncio.create_subprocess_shell(
        'playwright install chromium',
        cwd=parent_dir,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    if stderr:
        print("错误输出:")
        print(stderr.decode('utf-8', errors='ignore'))
    if proc.returncode == 0:
        print("✓ Playwright Chromium 已安装")
    else:
        print(f"✗ 安装失败，返回码: {proc.returncode}")
        sys.exit(1)


class PriorSearch:
    _shared_browser = None
    _shared_playwright = None

    @classmethod
    async def _init_shared(cls):
        if cls._shared_playwright is None:
            cls._shared_playwright = await async_playwright().start()
            cls._shared_browser = await cls._shared_playwright.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
            )

    def __init__(self, out_dir: str):
        self.out_dir = out_dir
        os.makedirs(self.out_dir, exist_ok=True)
        self.context = None
        self.page = None
        self.kw_group = []
        self.patents = {}
        self.keyword = None

    async def _init_page(self):
        await PriorSearch._init_shared()
        self.context = await PriorSearch._shared_browser.new_context(
            user_agent=USER_AGENT,
            locale="zh-CN",
            viewport={"width": 1280, "height": 900}
        )
        self.page = await self.context.new_page()

    async def _cleanup(self):
        if self.context:
            await self.context.close()
            self.context = None
            self.page = None

    @abstractmethod
    async def search(self, keywords: list, **kwargs) -> bool:
        ...

    async def search_round(self, kw_group):
        self.patents = {}
        self.kw_group = kw_group
        for keywords in kw_group:
            if await self.search(keywords):
                break
        if len(self.patents) > 0:
            json_path = os.path.join(self.out_dir, clean_filename(self.keyword) + f".json")
            to_json(self.patents, json_path)
            await self.split_json(json_path)
            print(f"✓ 检索成功: {self.keyword}")

    async def split_json(self, file_path: str):
        if not os.path.exists(file_path):
            return
        data = from_json(file_path)
        if not isinstance(data, dict) or len(data) <= 50:
            return
        items = list(data.items())
        base_name = os.path.basename(os.path.splitext(file_path)[0])
        root = os.path.dirname(file_path)
        for i in range(0, len(items), 50):
            chunk = dict(items[i:i+50])
            chunk_file = os.path.join(root, f"{base_name}_{i//50 + 1}.json")
            to_json(chunk, chunk_file)
        try:
            os.remove(file_path)
        except:
            pass


class CnkiSearch(PriorSearch):

    def formula(self, keywords: list) -> str:
        return '*'.join(keywords)

    async def search(self, keywords: list, to_page: int = 6):
        print(f"正在检索: {keywords}")
        self.keyword = self.formula(keywords)
        base_url = "https://kns.cnki.net/res/category/patent"

        for attempt in range(MAX_RETRIES):
            try:
                await self.page.goto(base_url, wait_until="load", timeout=30000)
                await self.page.wait_for_timeout(3000)
                # 输入框的data-v属性值可能失效，需要不定期更新
                input_box = self.page.locator("input[data-v-6b55a10e]")
                await input_box.wait_for(state="visible", timeout=10000)
                await input_box.fill(self.keyword)

                search_button = self.page.locator(".btn-search")
                await search_button.wait_for(state="visible", timeout=10000)
                await search_button.click()
                await self.page.wait_for_timeout(5000)

                try:
                    no_data = self.page.locator("p.no-content")
                    await no_data.wait_for(state="visible", timeout=10000)
                    no_data_text = await no_data.inner_text()
                    if "暂无数据" in no_data_text:
                        print("× Cnki检索数量不足")
                        await asyncio.sleep(RETRY_DELAY)
                        return False
                except Exception:
                    pass

                zh_sort = self.page.locator('li#ZH')
                await zh_sort.wait_for(state="visible", timeout=10000)
                await zh_sort.click()
                await self.page.wait_for_timeout(2000)

                total_pages = self.page.locator("span.pagerTitleCell")
                await total_pages.wait_for(state="visible", timeout=10000)
                total_pages = math.ceil(int((await total_pages.inner_text()).strip().split()[1]) / 20)

                for _page in range(min(total_pages, to_page)):
                    result_table = self.page.locator("table.result-table-list").locator("tbody")
                    await result_table.wait_for(state="visible", timeout=30000)
                    rows = result_table.locator("tr")
                    await rows.last.wait_for(state="visible", timeout=60000)

                    for idx in range(await rows.count()):
                        row = rows.nth(idx)
                        title_link = row.locator("a.fz14")
                        patent_title = (await title_link.inner_text()).strip().lower()
                        if patent_title in self.patents:
                            continue

                        new_page = None
                        for _ in range(MAX_RETRIES):
                            try:
                                async with self.context.expect_page(timeout=10000) as page_info:
                                    await title_link.click()
                                new_page = await page_info.value
                                await new_page.wait_for_load_state("load", timeout=15000)
                                break
                            except:
                                await asyncio.sleep(RETRY_DELAY)

                        if new_page is None:
                            continue

                        try:
                            claim = new_page.locator("div.claim-text")
                            await claim.wait_for(state="visible", timeout=10000)
                            claim_text = await claim.inner_text()
                        except:
                            claim_text = ""

                        try:
                            abstract = new_page.locator("div.abstract-text")
                            await abstract.wait_for(state="visible", timeout=10000)
                            abstract_text = await abstract.inner_text()
                        except:
                            abstract_text = ""

                        self.patents[patent_title] = {
                            "claim": claim_text,
                            "abstract": abstract_text
                        }

                        await new_page.close()
                        await self.page.wait_for_timeout(1000)
                        await asyncio.sleep(RETRY_DELAY)

                    await self.page.keyboard.press("ArrowRight")
                    await self.page.wait_for_timeout(5000)

                if len(self.patents) >= (to_page >> 1) * 20:
                    return True
                else:
                    print("× Cnki检索数量不足")
                    await asyncio.sleep(RETRY_DELAY)
                    return False

            except Exception as e:
                print(f"× Cnki检索失败: {e}")
                await asyncio.sleep(RETRY_DELAY)

        return False


class FpoSearch(PriorSearch):

    def formula(self, keywords: list) -> str:
        return ' AND '.join(keywords)

    async def search(self, keywords: list, to_page: int = 1):
        print(f"正在检索: {keywords}")
        self.keyword = self.formula(keywords)
        base_url = f"https://www.freepatentsonline.com/"

        for attempt in range(MAX_RETRIES):
            try:
                await self.page.goto(base_url, wait_until="load", timeout=30000)
                await self.page.wait_for_timeout(3000)
                cookies_list = await self.page.context.cookies()
                self.cookies = {cookie['name']: cookie['value'] for cookie in cookies_list}

                input_box = self.page.locator("input#topSearchBox")
                await input_box.wait_for(state="visible", timeout=10000)
                await input_box.fill(self.keyword)

                other_box = self.page.locator("input#patents_other")
                await other_box.wait_for(state="visible", timeout=10000)
                await other_box.click()

                search_button = self.page.get_by_role("button", name="Search")
                await search_button.wait_for(state="visible", timeout=10000)
                await search_button.click()
                await self.page.wait_for_timeout(10000)

                matches_element = self.page.locator("td", has_text="Matches")
                await matches_element.first.wait_for(state="visible", timeout=10000)
                total_pages = math.ceil(int((await matches_element.first.inner_text()).strip().split()[-1]) / 50)

                for _page in range(min(total_pages, to_page)):
                    result_table = self.page.locator("table.listing_table").locator("tbody")
                    await result_table.wait_for(state="visible", timeout=30000)
                    rows = result_table.locator("tr")
                    await rows.first.wait_for(state="visible", timeout=30000)

                    for idx in range(1, await rows.count()):
                        row = rows.nth(idx)
                        title_link = row.locator("a")
                        patent_title = (await title_link.inner_text()).strip().lower()
                        if patent_title in self.patents:
                            continue

                        #print(f"正在处理: {patent_title}")
                        new_page = None
                        doc2_elements = None
                        for _ in range(MAX_RETRIES):
                            try:
                                async with self.context.expect_page(timeout=15000) as page_info:
                                    await title_link.click(modifiers=["Control"])

                                new_page = await page_info.value
                                await new_page.wait_for_load_state("load", timeout=30000)
                                doc2_elements = new_page.locator('div.disp_doc2')
                                await doc2_elements.first.wait_for(state="visible", timeout=120000)
                                break
                            except:
                                await asyncio.sleep(RETRY_DELAY)

                        if new_page is None or doc2_elements is None:
                            continue

                        abstract_text = ''
                        claim_text = ''

                        for i in range(await doc2_elements.count()):
                            doc2 = doc2_elements.nth(i)
                            elm_title = doc2.locator('div.disp_elm_title')
                            if await elm_title.count() > 0:
                                title_text = (await elm_title.inner_text()).strip()
                                if title_text == 'Abstract:':
                                    abstract_elm = doc2.locator('div.disp_elm_text')
                                    if await abstract_elm.count() > 0:
                                        abstract_text = (await abstract_elm.inner_text()).strip()
                                elif title_text == 'Claims:':
                                    claim_elm = doc2.locator('div.disp_elm_text')
                                    if await claim_elm.count() > 0:
                                        claim_text = (await claim_elm.inner_text()).strip()
                                    break

                        self.patents[patent_title] = {
                            "claim": claim_text,
                            "abstract": abstract_text
                        }

                        await new_page.close()
                        await self.page.wait_for_timeout(1000)
                        await asyncio.sleep(RETRY_DELAY)

                    next_page_button = self.page.get_by_role("link", name=">")
                    await next_page_button.first.wait_for(state="visible", timeout=10000)
                    next_href = await next_page_button.first.get_attribute("href")
                    if next_href:
                        for _ in range(MAX_RETRIES):
                            try:
                                next_url = next_href if next_href.startswith("http") else f"https://www.freepatentsonline.com/{next_href}"
                                await self.page.goto(next_url, wait_until="load", timeout=30000)
                                await self.page.wait_for_timeout(5000)
                                break
                            except:
                                await asyncio.sleep(RETRY_DELAY)
                    else:
                        break

                return True

            except Exception as e:
                print(f"× FPO检索失败: {e}")
                await asyncio.sleep(RETRY_DELAY)

        return False


async def prior_search(project_root: str, home_only: bool = False):
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

    max_len = max(len(keywords_cn), len(keywords_en))

    try:
        await install_playwright_chromium()
        if not home_only:
            cnki_search = CnkiSearch(out_dir)
            fpo_search = FpoSearch(out_dir)
            await asyncio.gather(cnki_search._init_page(), fpo_search._init_page())

            for i in range(max_len):
                tasks = []
                if i < len(keywords_cn):
                    tasks.append(cnki_search.search_round(keywords_cn[i]))
                if i < len(keywords_en):
                    tasks.append(fpo_search.search_round(keywords_en[i]))
                if tasks:
                    await asyncio.gather(*tasks)
            await asyncio.gather(cnki_search._cleanup(), fpo_search._cleanup())
        else:
            cnki_search = CnkiSearch(out_dir)
            await cnki_search._init_page()

            for i in range(max_len):
                if i < len(keywords_cn):
                    await cnki_search.search_round(keywords_cn[i])
                if i < len(keywords_en):
                    await cnki_search.search_round(keywords_en[i])
            await cnki_search._cleanup()
        print("√ Done.")
    except Exception as e:
        print(e)


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument("project_root", type=str, help="项目根目录")
    args.add_argument("--home_only", action="store_true", help="仅检索国内数据库")
    args = args.parse_args()
    try:
        asyncio.run(prior_search(args.project_root, args.home_only))
    except Exception:
        sys.exit(0)
