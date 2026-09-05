#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
import os
from pathlib import Path
from datetime import datetime

from config import OUT_ROOT


def find_input_files(project_root: str) -> list:
    possible_dirs = [
        os.path.join(project_root, OUT_ROOT, 'claim-optimization'),
        os.path.join(project_root, OUT_ROOT, 'materials')
    ]

    for dir_path in possible_dirs:
        if not os.path.exists(dir_path):
            continue

        round_files = []
        for i in range(1, 7):
            file_path = os.path.join(dir_path, f'R{i}.json')
            if os.path.exists(file_path):
                round_files.append(file_path)

        if round_files:
            return round_files

        merged_file = os.path.join(dir_path, 'claim-optimization.json')
        if os.path.exists(merged_file):
            return [merged_file]

    return []


def generate_optimization_html(project_root: str) -> str:
    input_files = find_input_files(project_root)

    if not input_files:
        raise FileNotFoundError(
            f"未找到优化过程以下位置是否存在文件以下位置是否存在文件：\n"
            f"  - {project_root}/{OUT_ROOT}/claim-optimization/R1.json ~ R6.json\n"
            f"  - {project_root}/{OUT_ROOT}/materials/claim-optimization.json"
        )

    all_rounds = []
    project_name = ''
    generation_date = datetime.now().strftime('%Y-%m-%d')

    for file_path in input_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            round_data = json.load(f)

        if not project_name:
            project_name = round_data.get('project_name', '专利项目')
            generation_date = round_data.get('generation_date', generation_date)

        if 'round_number' in round_data:
            all_rounds.append(round_data)
        elif 'rounds' in round_data:
            all_rounds.extend(round_data['rounds'])

    if not all_rounds:
        raise ValueError(f"文件中未找到有效的优化轮次数据：{input_files}")

    all_rounds.sort(key=lambda x: x.get('round_number', 0))

    data = {
        'project_name': project_name,
        'generation_date': generation_date,
        'portfolio_summary': {
            'patent_count': len(set(
                p.get('patent_id', '')
                for r in all_rounds
                for p in r.get('patents', [])
            )),
            'strategy_description': '六轮博弈优化'
        },
        'statistics': {
            'total_patents': len(set(
                p.get('patent_id', '')
                for r in all_rounds
                for p in r.get('patents', [])
            )),
            'total_rounds': len(all_rounds),
            'total_attacks_found': sum(
                len(p.get('attacks', []))
                for r in all_rounds
                for p in r.get('patents', [])
            ),
            'total_improvements_made': sum(
                len(p.get('defense', {}).get('improvements_to_claim_tree', []))
                for r in all_rounds
                for p in r.get('patents', [])
            )
        },
        'rounds': all_rounds
    }

    stats_html = generate_statistics(data)
    patents_list_html = generate_patents_list(data['rounds'])
    timeline_html = generate_timeline(data['rounds'])

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>权利要求树优化过程 - {data.get('project_name', '专利项目')}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }}

        .header .subtitle {{
            font-size: 1.1em;
            opacity: 0.95;
            margin-bottom: 20px;
        }}

        .header .meta {{
            font-size: 0.9em;
            opacity: 0.85;
        }}

        .statistics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px 40px;
            background: #f8f9fa;
            border-bottom: 2px solid #e9ecef;
        }}

        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            transition: transform 0.3s ease;
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.12);
        }}

        .stat-number {{
            font-size: 2.5em;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 5px;
        }}

        .stat-label {{
            color: #6c757d;
            font-size: 0.95em;
        }}

        .patents-list {{
            padding: 30px 40px;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-bottom: 2px solid #dee2e6;
        }}

        .patents-list h2 {{
            color: #495057;
            margin-bottom: 20px;
            font-size: 1.5em;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .patents-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
        }}

        .patent-item {{
            background: white;
            padding: 18px 22px;
            border-radius: 10px;
            border-left: 5px solid #667eea;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 15px;
        }}

        .patent-item:hover {{
            transform: translateX(5px);
            box-shadow: 0 4px 16px rgba(102, 126, 234, 0.2);
            border-left-color: #764ba2;
        }}

        .patent-prefix {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: 700;
            font-size: 1.1em;
            padding: 8px 14px;
            border-radius: 8px;
            min-width: 50px;
            text-align: center;
            box-shadow: 0 2px 6px rgba(102, 126, 234, 0.3);
        }}

        .patent-name {{
            flex: 1;
            color: #333;
            font-size: 1em;
            line-height: 1.5;
            font-weight: 500;
        }}

        .patent-info {{
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}

        .patent-abandoned .patent-prefix {{
            background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
            box-shadow: 0 2px 6px rgba(220, 53, 69, 0.3);
        }}

        .patent-abandoned .patent-name {{
            color: #6c757d;
            text-decoration: line-through;
            text-decoration-color: #dc3545;
        }}

        .abandoned-badge {{
            display: inline-block;
            background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 600;
            text-align: center;
            animation: pulse-badge 2s ease-in-out infinite;
        }}

        @keyframes pulse-badge {{
            0%, 100% {{
                opacity: 1;
                transform: scale(1);
            }}
            50% {{
                opacity: 0.85;
                transform: scale(1.02);
            }}
        }}

        .patents-summary {{
            margin-top: 20px;
            padding: 15px 20px;
            background: white;
            border-radius: 10px;
            display: flex;
            gap: 25px;
            justify-content: center;
            align-items: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            font-size: 0.95em;
            font-weight: 500;
        }}

        .summary-active {{
            color: #155724;
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .summary-abandoned {{
            color: #721c24;
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        @media (max-width: 768px) {{
            .patents-grid {{
                grid-template-columns: 1fr;
            }}

            .patent-item {{
                padding: 15px 18px;
            }}

            .patents-summary {{
                flex-direction: column;
                gap: 10px;
                text-align: center;
            }}
        }}

        .timeline {{
            position: relative;
            padding: 40px;
        }}

        .round {{
            position: relative;
            margin-bottom: 50px;
            width: 100%;
        }}

        .round-content {{
            width: 100%;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            overflow: hidden;
            transition: all 0.3s ease;
        }}

        .round-content:hover {{
            box-shadow: 0 8px 24px rgba(0,0,0,0.15);
            transform: translateY(-3px);
        }}

        .round-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            cursor: pointer;
            user-select: none;
        }}

        .round-header h3 {{
            font-size: 1.4em;
            margin-bottom: 5px;
        }}

        .round-header .subtitle {{
            font-size: 0.9em;
            opacity: 0.9;
        }}

        .round-body {{
            padding: 25px;
            overflow: visible;
        }}

        .patent {{
            margin-bottom: 25px;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            overflow: hidden;
        }}

        .patent:last-child {{
            margin-bottom: 0;
        }}

        .patent-header {{
            background: #f8f9fa;
            padding: 15px 20px;
            font-weight: 600;
            color: #495057;
            border-bottom: 2px solid #e9ecef;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .patent-status {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }}

        .status-pass {{
            background: #d4edda;
            color: #155724;
        }}

        .status-fail {{
            background: #f8d7da;
            color: #721c24;
        }}

        .attack-box {{
            background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%);
            border-left: 4px solid #dc3545;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
        }}

        .attack-box h4 {{
            color: #dc3545;
            margin-bottom: 12px;
            font-size: 1.1em;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .attack-type {{
            font-weight: 600;
            color: #c82333;
            margin-bottom: 10px;
        }}

        .attack-details {{
            background: white;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 10px;
            font-size: 0.95em;
            line-height: 1.8;
        }}

        .attack-conclusion {{
            font-weight: 600;
            padding: 10px;
            background: rgba(220, 53, 69, 0.1);
            border-radius: 6px;
            margin-top: 10px;
        }}

        .attack-successful {{
            color: #dc3545;
            font-weight: 700;
        }}

        .defense-box {{
            background: linear-gradient(135deg, #f0fff4 0%, #c6f6d5 100%);
            border-left: 4px solid #28a745;
            padding: 20px;
            border-radius: 8px;
        }}

        .defense-box h4 {{
            color: #28a745;
            margin-bottom: 12px;
            font-size: 1.1em;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .defense-response {{
            background: white;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 15px;
            font-size: 0.95em;
            line-height: 1.8;
        }}

        .defense-actions {{
            margin-bottom: 15px;
        }}

        .defense-actions strong {{
            display: block;
            margin-bottom: 8px;
            color: #155724;
        }}

        .defense-actions ul {{
            list-style: none;
            padding-left: 0;
        }}

        .defense-actions li {{
            padding: 6px 0;
            padding-left: 20px;
            position: relative;
        }}

        .defense-actions li::before {{
            content: '✓';
            position: absolute;
            left: 0;
            color: #28a745;
            font-weight: bold;
        }}

        .improvements-section {{
            margin-top: 20px;
            padding: 20px;
            background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
            border: 2px solid #f59e0b;
            border-radius: 10px;
        }}

        .improvements-section h5 {{
            color: #d97706;
            margin-bottom: 15px;
            font-size: 1.1em;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .improvement-item {{
            background: white;
            padding: 18px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 4px solid #f59e0b;
            box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        }}

        .improvement-item:last-child {{
            margin-bottom: 0;
        }}

        .improvement-type-badge {{
            display: inline-block;
            padding: 4px 12px;
            background: #f59e0b;
            color: white;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            margin-bottom: 12px;
        }}

        .improvement-location {{
            background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
            border: 2px dashed #3b82f6;
            padding: 14px;
            border-radius: 8px;
            margin-bottom: 15px;
            position: relative;
            overflow: hidden;
        }}

        .improvement-location::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: #3b82f6;
        }}

        .location-label {{
            color: #1e40af;
            font-weight: 700;
            margin-bottom: 8px;
            font-size: 0.95em;
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .location-path {{
            color: #1e40af;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.92em;
            line-height: 1.6;
            word-break: break-all;
            background: white;
            padding: 10px 12px;
            border-radius: 6px;
            border: 1px solid #93c5fd;
        }}

        .path-level {{
            display: inline-block;
            padding: 2px 8px;
            margin: 2px;
            background: #dbeafe;
            border-radius: 4px;
            font-size: 0.9em;
        }}

        .path-separator {{
            color: #3b82f6;
            font-weight: bold;
            margin: 0 4px;
        }}

        .improvement-comparison {{
            margin-top: 12px;
        }}

        .comparison-label {{
            font-weight: 600;
            color: #374151;
            margin-bottom: 8px;
            font-size: 0.95em;
        }}

        .before-text {{
            text-decoration: line-through;
            color: #dc2626;
            background: rgba(220, 38, 38, 0.08);
            padding: 12px 16px;
            border-radius: 6px;
            margin-bottom: 10px;
            line-height: 1.7;
            font-size: 0.95em;
            display: block;
            border-left: 3px solid #dc2626;
        }}

        .after-text {{
            color: #059669;
            font-weight: 600;
            background: rgba(5, 150, 105, 0.08);
            padding: 12px 16px;
            border-radius: 6px;
            line-height: 1.7;
            font-size: 0.95em;
            display: block;
            border-left: 3px solid #059669;
        }}

        .arrow-icon {{
            color: #f59e0b;
            margin: 10px 0;
            font-size: 1.8em;
            text-align: center;
            font-weight: bold;
        }}

        .improvement-reason {{
            margin-top: 14px;
            padding: 14px;
            background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
            border-left: 3px solid #10b981;
            border-radius: 6px;
            font-size: 0.93em;
            line-height: 1.7;
        }}

        .reason-label {{
            font-weight: 700;
            color: #065f46;
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        @media (max-width: 768px) {{
            .round-content {{
                width: 100%;
                margin-left: 0;
                margin-right: 0;
            }}

            .header h1 {{
                font-size: 1.8em;
            }}

            .statistics {{
                grid-template-columns: repeat(2, 1fr);
                padding: 20px;
            }}
        }}

        @media print {{
            body {{
                background: white;
                padding: 0;
            }}

            .container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚖️ 权利要求树优化过程</h1>
            <div class="subtitle">{data.get('project_name', '专利项目')}</div>
            <div class="meta">
                生成日期：{data.get('generation_date', datetime.now().strftime('%Y-%m-%d'))}
            </div>
        </div>

        {stats_html}

        {patents_list_html}

        <div class="timeline">
            {timeline_html}
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            console.log('✅ 权利要求树优化过程页面已加载');
        }});
    </script>
</body>
</html>'''

    output_dir = os.path.join(project_root, OUT_ROOT, 'claim-optimization')
    if not os.path.exists(output_dir):
        output_dir = os.path.join(project_root, OUT_ROOT, 'materials')

    output_path = os.path.join(output_dir, 'claim-optimization.html')

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    return output_path


def generate_patents_list(rounds: list) -> str:
    unique_patents = {}
    abandoned_patents = set()

    for round_data in rounds:
        current_round_patents = set()
        for patent in round_data.get('patents', []):
            patent_id = patent.get('patent_id', '')
            patent_title = patent.get('patent_title', '')
            status = patent.get('status', '')
            if patent_id:
                current_round_patents.add(patent_id)
                if patent_id not in unique_patents:
                    unique_patents[patent_id] = {
                        'title': patent_title,
                        'status': status,
                        'last_seen_round': round_data.get('round_number', 0)
                    }
                else:
                    unique_patents[patent_id]['status'] = status
                    unique_patents[patent_id]['last_seen_round'] = round_data.get('round_number', 0)

        if rounds.index(round_data) > 0:
            prev_round = rounds[rounds.index(round_data) - 1]
            prev_patents = {p.get('patent_id', '') for p in prev_round.get('patents', [])}
            abandoned_in_this_round = prev_patents - current_round_patents
            abandoned_patents.update(abandoned_in_this_round)

    last_round = rounds[-1] if rounds else None
    if last_round:
        final_patents = {p.get('patent_id', '') for p in last_round.get('patents', [])}
        all_patents_ever = set(unique_patents.keys())
        abandoned_patents.update(all_patents_ever - final_patents)

        for patent in last_round.get('patents', []):
            patent_id = patent.get('patent_id', '')
            status = patent.get('status', '')
            if patent_id and status and '放弃' in str(status):
                abandoned_patents.add(patent_id)
                if patent_id in unique_patents:
                    unique_patents[patent_id]['status'] = status

    if not unique_patents:
        return ''

    patents_html = '''
    <div class="patents-list">
        <h2>📋 专利组合清单</h2>
        <div class="patents-grid">
    '''

    active_count = 0
    abandoned_count = 0

    for idx, (patent_id, patent_info) in enumerate(unique_patents.items(), 1):
        prefix = f'P{idx}'
        is_abandoned = patent_id in abandoned_patents
        title = patent_info.get('title', patent_id)
        status = patent_info.get('status', '')

        if is_abandoned:
            abandoned_count += 1
            abandoned_class = 'patent-abandoned'
            status_badge = '<span class="abandoned-badge">❌ 已放弃</span>'
            item_style = 'style="opacity: 0.7; border-left-color: #dc3545;"'
        else:
            active_count += 1
            abandoned_class = ''
            status_badge = ''
            item_style = ''

        patents_html += f'''
            <div class="patent-item {abandoned_class}" {item_style}>
                <div class="patent-prefix">{prefix}</div>
                <div class="patent-info">
                    <div class="patent-name">{title}</div>
                    {status_badge}
                </div>
            </div>
        '''

    patents_html += '''
        </div>
    '''

    if abandoned_count > 0:
        patents_html += f'''
        <div class="patents-summary">
            <span class="summary-active">✅ 有效专利：{active_count} 项</span>
            <span class="summary-abandoned">❌ 已放弃：{abandoned_count} 项</span>
        </div>
        '''

    patents_html += '''
    </div>
    '''

    return patents_html


def generate_statistics(data: dict) -> str:
    stats = data.get('statistics', {})
    portfolio = data.get('portfolio_summary', {})

    total_patents = stats.get('total_patents', portfolio.get('patent_count', 0))
    total_rounds = stats.get('total_rounds', len(data.get('rounds', [])))
    total_attacks = stats.get('total_attacks_found', 0)
    total_improvements = stats.get('total_improvements_made', 0)

    return f'''
    <div class="statistics">
        <div class="stat-card">
            <div class="stat-number">{total_patents}</div>
            <div class="stat-label">专利数量</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{total_rounds}</div>
            <div class="stat-label">优化轮次</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{total_attacks}</div>
            <div class="stat-label">发现问题数</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{total_improvements}</div>
            <div class="stat-label">改进次数</div>
        </div>
    </div>
    '''


def generate_timeline(rounds: list) -> str:
    timeline_html = ''

    for round_data in rounds:
        round_num = round_data.get('round_number', '')
        title = round_data.get('title', '')
        subtitle = round_data.get('subtitle', '')

        patents_html = generate_patents(round_data.get('patents', []))

        timeline_html += f'''
        <div class="round">
            <div class="round-content">
                <div class="round-header">
                    <h3>第{round_num}轮：{title}</h3>
                    <div class="subtitle">{subtitle}</div>
                </div>
                <div class="round-body">
                    {patents_html}
                </div>
            </div>
        </div>
        '''

    return timeline_html


def generate_patents(patents: list) -> str:
    patents_html = ''

    for patent in patents:
        patent_id = patent.get('patent_id', '')
        patent_title = patent.get('patent_title', '')
        status = patent.get('status', '')
        attacks = patent.get('attacks', [])
        defense = patent.get('defense', {})

        status_class = 'status-pass' if status == '通过' else 'status-fail'

        attacks_html = generate_attacks(attacks)
        defense_html = generate_defense(defense)

        patents_html += f'''
        <div class="patent">
            <div class="patent-header">
                <span>{patent_id}: {patent_title}</span>
                <span class="patent-status {status_class}">{status}</span>
            </div>
            {attacks_html}
            {defense_html}
        </div>
        '''

    return patents_html


def generate_attacks(attacks: list) -> str:
    if not attacks:
        return ''

    attacks_html = ''
    for attack in attacks:
        attack_type = attack.get('type', '')
        details = attack.get('details', '')
        conclusion = attack.get('conclusion', '')
        attack_successful = attack.get('attack_successful', False)

        details_text = details.replace('\n', '<br>') if details else ''

        successful_class = 'attack-successful' if attack_successful else ''
        successful_text = '⚠️ 攻击成功' if attack_successful else '✓ 攻击未成功'

        attacks_html += f'''
        <div class="attack-box">
            <h4>⚔️ 攻击方</h4>
            <div class="attack-type">{attack_type}</div>
            {f'<div class="attack-details">{details_text}</div>' if details_text else ''}
            <div class="attack-conclusion">
                <span class="{successful_class}">{successful_text}</span><br>
                {conclusion}
            </div>
        </div>
        '''

    return attacks_html


def generate_defense(defense: dict) -> str:
    if not defense:
        return ''

    response = defense.get('response', '')
    actions_taken = defense.get('actions_taken', [])
    improvements = defense.get('improvements_to_claim_tree', [])

    actions_html = ''
    if actions_taken:
        actions_list = ''.join([f'<li>{action}</li>' for action in actions_taken])
        actions_html = f'''
        <div class="defense-actions">
            <strong>采取的行动：</strong>
            <ul>{actions_list}</ul>
        </div>
        '''

    improvements_html = ''
    if improvements:
        improvements_html = generate_improvements(improvements)

    return f'''
    <div class="defense-box">
        <h4>🛡️ 防守方</h4>
        <div class="defense-response">{response}</div>
        {actions_html}
        {improvements_html}
    </div>
    '''


def generate_improvements(improvements: list) -> str:
    if not improvements:
        return ''

    improvements_html = '''
    <div class="improvements-section">
        <h5>🔧 权利要求树改进详情</h5>
    '''

    for idx, improvement in enumerate(improvements, 1):
        imp_type = improvement.get('type', '调整表述')
        before = improvement.get('before', '')
        after = improvement.get('after', '')
        reason = improvement.get('reason', '')

        location_path = improvement.get('location_in_v1', '')
        formatted_location = format_location_path(location_path)

        location_html = f'''
        <div class="improvement-location">
            <div class="location-label">📍 原权利要求树中的位置：</div>
            <div class="location-path">{formatted_location}</div>
        </div>
        '''

        reason_html = ''
        if reason:
            reason_html = f'''
            <div class="improvement-reason">
                <div class="reason-label">💡 改进原因：</div>
                {reason}
            </div>
            '''

        improvements_html += f'''
        <div class="improvement-item">
            <span class="improvement-type-badge">改进 {idx}: {imp_type}</span>

            {location_html}

            <div class="improvement-comparison">
                <div class="comparison-label">❌ 修改前（原始表述）：</div>
                <span class="before-text">{before}</span>

                <div class="arrow-icon">↓</div>

                <div class="comparison-label">✅ 修改后（优化表述）：</div>
                <span class="after-text">{after}</span>
            </div>

            {reason_html}
        </div>
        '''

    improvements_html += '</div>'
    return improvements_html


def format_location_path(location_path: str) -> str:
    if not location_path or not location_path.strip():
        return '<span style="color: #dc2626; font-weight: 600;">⚠️ 未指定位置（请在JSON中补充 location_in_v1 字段）</span>'

    levels = [level.strip() for level in location_path.split('>')]
    levels = [level for level in levels if level]

    if not levels:
        return '<span style="color: #dc2626; font-weight: 600;">⚠️ 路径格式错误（请使用 > 分隔各层级）</span>'

    formatted_levels = []
    for i, level in enumerate(levels):
        formatted_levels.append(f'<span class="path-level">{level}</span>')

        if i < len(levels) - 1:
            formatted_levels.append('<span class="path-separator">›</span>')

    return ''.join(formatted_levels)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("用法: python generate_optimization_html.py <项目根目录>")
        print("\n脚本会自动查找输入文件并生成HTML页面：")
        print("  输入文件查找顺序：")
        print("    1. {项目根目录}/claim-optimization/R1.json ~ R6.json（分轮次文件，优先）")
        print("    2. {项目根目录}/materials/claim-optimization.json（合并文件，备选）")
        print("  输出文件：")
        print("    - {项目根目录}/claim-optimization/claim-optimization.html（优先）")
        print("    - 或 {项目根目录}/materials/claim-optimization.html（备选）")
        print("\n示例:")
        print("  python generate_optimization_html.py ./my_patent_project")
        print("  python generate_optimization_html.py /path/to/project")
        sys.exit(1)

    project_root = sys.argv[1]

    if not os.path.exists(project_root):
        print(f"❌ 错误：项目根目录不存在：{project_root}")
        sys.exit(1)

    try:
        result = generate_optimization_html(project_root)
        print(f"\n✨ 成功！可以在浏览器中打开查看：{result}")
    except FileNotFoundError as e:
        print(f"❌ 错误：{e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)