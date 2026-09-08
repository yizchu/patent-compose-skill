import os
import re
import sys

from file_tools import from_json
from config import TAB

def compose_dependent_claims(independent_claim: str, quote_num: int, quote_claim: str, tree: dict) -> str:
    '''
    Parameters:
        independent_claim: 引用的独权名称
        claim_num: 引用的权利要求编号
        claim_name: 引用的权利要求名称
        tree: 当前子树
    '''
    global claims
    if not tree.get("contains") and not tree.get("special claims"):
        return

    now_num = len(claims)+1
    claim_text_prefix = f"根据权利要求{quote_num}所述的{independent_claim}，其特征在于，所述{quote_claim}，"
    if tree.get("contains"):
        claim_text = claim_text_prefix + "包括：\n"
        for child_name in tree["contains"]:
            claim_text += f"{TAB}{tree['contains'][child_name]['description']}；\n"
        claim_text = claim_text[:-2] + "。"
        claims.append(claim_text)
    if tree.get("special claims"):
        if tree.get("contains"):
            if len(tree["special claims"]) == 1:
                claim_text = claim_text_prefix + f"具体还有：{tree['special claims'][0]}。"
            else:
                claim_text = claim_text_prefix + "具体还有：\n"
                for special_claim in tree["special claims"]:
                    claim_text += f"{TAB}{special_claim}；\n"
                claim_text = claim_text[:-2] + "。"
        elif len(tree["special claims"]) == 1:
            claim_text = claim_text_prefix + f"具体有：{tree['special claims'][0]}。"
        else:
            claim_text = claim_text_prefix + "具体有：\n"
            for special_claim in tree["special claims"]:
                claim_text += f"{TAB}{special_claim}；\n"
            claim_text = claim_text[:-2] + "。"
        claims.append(claim_text)

    if tree.get("contains"):
        for child_name in tree["contains"]:
            compose_dependent_claims(independent_claim, now_num, child_name,
                                     tree["contains"][child_name])

def tree_to_claims(claim_tree: dict, patent_title: str = "") -> str:
    global claims
    claims = []

    # 先写所有的独权
    for independent_claim in claim_tree:
        if claim_tree[independent_claim].get("contains"):
            assert len(claim_tree[independent_claim]["contains"]) >= 2, f"For independent claim {independent_claim}, 'Contains' key must have at least two steps."
            if claim_tree[independent_claim].get("special claims"):
                raise ValueError(f"Independent claim {independent_claim} has got both 'contains' and 'special claims' key, which is not allowed.")

            independent_claim_text = f"{independent_claim}，其特征在于，包括：\n"
            for child_name in claim_tree[independent_claim]["contains"]:
                independent_claim_text += f"{TAB}{claim_tree[independent_claim]['contains'][child_name]['description']}；\n"
            independent_claim_text = independent_claim_text[:-2] + "。"
            claims.append(independent_claim_text)
        elif claim_tree[independent_claim].get("special claims"):
            if len(claim_tree[independent_claim]["special claims"]) == 1:
                independent_claim_text = f"{independent_claim}，其特征在于，{claim_tree[independent_claim]['special claims'][0]}。"
                claims.append(independent_claim_text)
            elif len(claim_tree[independent_claim]["special claims"]) > 1:
                independent_claim_text = f"{independent_claim}，其特征在于，包括：\n"
                for special_claim in claim_tree[independent_claim]["special claims"]:
                    independent_claim_text += f"{TAB}{special_claim}；\n"
                independent_claim_text = independent_claim_text[:-2] + "。"
                claims.append(independent_claim_text)
        else:
            raise ValueError(f"Independent claim {independent_claim} must have either 'contains' or 'special claims' key.")

    # 之后遍历从权
    for independent_claim_num, independent_claim in enumerate(claim_tree):
        if claim_tree[independent_claim].get("contains"):
            for child_name in claim_tree[independent_claim]["contains"]:
                compose_dependent_claims(independent_claim, independent_claim_num+1, child_name,
                                         claim_tree[independent_claim]["contains"][child_name])

    claims = [f"{TAB}{i+1}. {claim}" for i, claim in enumerate(claims)]
    print(f"✅ {patent_title} 权利要求树格式正确，预计共有{len(claims)}个权利要求。")

    result = "\n\n".join(claims)
    result = re.sub(r'[【\[].*?[】\]]', '', result)
    return result


def claims_to_tree(claims_text: str) -> dict:
    pass


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python claim.py tree_to_claims <claim_tree_json_path> [output_dir]")
        print("  python claim.py claims_to_tree <claims_text_path> [output_dir]")
        print("Tips:")
        print("  1. If output_dir is specified, claims will be saved to the specified directory.")
        print("  2. If output_dir is not specified, The program will only check the format of the claims tree.")
        sys.exit(1)

    command = sys.argv[1]

    if command == "tree_to_claims":
        json_path = sys.argv[2]
        output_dir = sys.argv[3] if len(sys.argv) > 3 else None
        try:
            claim_tree = from_json(json_path)
        except Exception as e:
            print(f"读取JSON文件失败：{e}")
            sys.exit(1)

        # 如果分了多专利（如 portfolio.json）
        if "patents" in claim_tree:
            for i, patent in enumerate(claim_tree["patents"]):
                if "claim_tree" not in patent:
                    print(f"专利 P{i} 似乎没有正确的权利要求树，请检查它的 claim_tree 字段后再试。")
                    sys.exit(1)
            for i, patent in enumerate(claim_tree["patents"]):
                patent_title = patent.get('title', f'P{i}')
                claims = tree_to_claims(patent["claim_tree"], patent_title)
                if output_dir:
                    output_path = os.path.join(output_dir, patent_title,
                                               f"claims_{patent_title}.md")
                    os.makedirs(os.path.join(output_dir, patent_title), exist_ok=True)
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(claims)
        # 否则默认整个文件就是一棵权利要求树（如 claim-tree.json）
        else:
            claims = tree_to_claims(claim_tree)
            if output_dir:
                output_path = os.path.join(output_dir, f"claims_{os.path.basename(json_path).split('.')[0]}.md")
                os.makedirs(output_dir, exist_ok=True)
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(claims)

        print(f"✅ 权利要求书已保存至：{output_dir}")

    elif command == "claims_to_tree":
        pass

    else:
        print(f"Unknown command: {command}")
        print("Available commands: tree_to_claims, claims_to_tree")
        sys.exit(1)