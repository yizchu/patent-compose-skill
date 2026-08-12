import requests
import datetime

def get_cookie(headers: dict, base_url: str):
    '''
    获取访问网站的cookie
    '''
    params = (
        ('action', ''),
        ('NaviCode', 'A'), # 筛选的类别
        ('ua', '1.21'),
        ('PageName', 'ASP.brief_result_aspx'),
        ('DbPrefix', 'SCPD'),
        ('DbCatalog', '\u4E2D\u56FD\u4E13\u5229\u6570\u636E\u5E93'),
        ('ConfigFile', 'SCPD.xml'),
        ('db_opt', '\u4E2D\u56FD\u4E13\u5229\u6570\u636E\u5E93'),
        ('db_value', '\u4E2D\u56FD\u4E13\u5229\u6570\u636E\u5E93'),
        ('date_gkr_from', datetime.datetime.now().strftime("%Y-%m-%d")),
        ('date_gkr_to', datetime.datetime.now().strftime("%Y-%m-%d")),
        ('his', '0'),
    )
    session = requests.session()
    session.get(base_url, headers=headers, params=params)
    return session.cookies