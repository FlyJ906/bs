# 检查成分是否对特定健康身份有风险
def check_risk(ingredient_info, health_identity):
    risk_for = ingredient_info.get('risk_for', '')
    return health_identity in risk_for.split(',')

# 分析成分列表，生成健康提示
def analyze_ingredients(ingredients_list, health_identity, get_ingredient_info):
    ingredients_table = []
    for ingredient in ingredients_list:
        if ingredient:
            info = get_ingredient_info(ingredient)
            risk = check_risk(info, health_identity)
            health_tip = "⚠️ 身份需关注" if risk else "—"
            ingredients_table.append([
                info['standard_name'],
                info['tag'],
                info['role'],
                health_tip
            ])
    return ingredients_table
