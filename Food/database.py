import pymysql
from pymysql import Error
import json
from datetime import datetime
from pymysql.cursors import DictCursor

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '1234',
    'database': 'food_analysis',
    'charset': 'utf8mb4',
    'use_unicode': True,
    # 避免在未安装/未启动MySQL时长时间卡住
    'connect_timeout': 2,
    'read_timeout': 5,
    'write_timeout': 5,
}

# 连接数据库
def get_db_connection():
    try:
        connection = pymysql.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"数据库连接错误: {e}")
        return None

# 初始化数据库
def init_database():
    # 先创建数据库
    try:
        # 连接到MySQL服务器（不指定数据库）
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            connect_timeout=DB_CONFIG.get('connect_timeout', 2),
            read_timeout=DB_CONFIG.get('read_timeout', 5),
            write_timeout=DB_CONFIG.get('write_timeout', 5),
        )
        cursor = connection.cursor()
        
        # 创建数据库
        cursor.execute("""
        CREATE DATABASE IF NOT EXISTS food_analysis 
        DEFAULT CHARACTER SET utf8mb4 
        COLLATE utf8mb4_unicode_ci;
        """)
        
        cursor.close()
        connection.close()
        
        # 重新连接到指定数据库
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # 检查products表是否存在
        cursor.execute("SHOW TABLES LIKE 'products'")
        table_exists = cursor.fetchone()
        
        # 无论表是否存在，都重新创建表以符合新的字段要求
        # 先删除旧表
        cursor.execute("DROP TABLE IF EXISTS products")
        
        # 创建新的products表，只保留必要的字段
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            barcode VARCHAR(13) PRIMARY KEY COMMENT 'EAN-13条形码（商品唯一标识）',
            product_name VARCHAR(255) NOT NULL COMMENT '商品名称（优先存储中文）',
            ingredients TEXT COMMENT '商品配料信息',
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '商品首次入库时间',
            update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '数据最后更新时间'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='食品商品信息表';
        """)
        
        # 创建ingredients表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ingredients (
            id INT AUTO_INCREMENT PRIMARY KEY COMMENT '成分自增ID',
            standard_name VARCHAR(100) NOT NULL UNIQUE COMMENT '成分标准名称（如"抗坏血酸""白砂糖"）',
            aliases VARCHAR(500) DEFAULT '' COMMENT '成分别名（逗号分隔，如"维C,维生素C"）',
            tag VARCHAR(500) DEFAULT '' COMMENT '成分标签（如"高血压风险、GRAS认证"）',
            role VARCHAR(200) DEFAULT '食品辅料' COMMENT '成分作用（如"防腐剂、甜味剂、增味剂"）',
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '数据创建时间'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='食品成分知识库表';
        """)
        
        # 创建health_risk表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS health_risk (
            id INT AUTO_INCREMENT PRIMARY KEY COMMENT '风险规则自增ID',
            health_identity VARCHAR(50) NOT NULL COMMENT '健康身份（如"糖尿病、肾病、孕妇、健身人群"）',
            ingredient_name VARCHAR(100) NOT NULL COMMENT '风险成分名称（关联ingredients.standard_name）',
            risk_tip VARCHAR(200) DEFAULT '⚠️ 该成分对当前人群有风险' COMMENT '风险提示语（前端展示）',
            risk_level VARCHAR(10) DEFAULT 'B' COMMENT '风险等级（可选，你可忽略/删除该字段）',
            FOREIGN KEY (ingredient_name) REFERENCES ingredients(standard_name) ON DELETE CASCADE,
            UNIQUE KEY idx_health_ingredient (health_identity, ingredient_name)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='健康身份-成分风险关联表';
        """)
        
        # 添加一些常见成分作为示例
        ingredients_data = [
            ("白砂糖", "白糖,蔗糖", "添加剂", "甜味剂"),
            ("山梨酸钾", "山梨酸甲", "添加剂", "防腐剂"),
            ("抗坏血酸", "维C,维生素C", "营养强化剂", "抗氧化剂"),
            ("氯化钠", "食盐", "基础成分", "调味剂"),
            ("葡萄糖", "葡糖", "基础成分", "甜味剂")
        ]
        
        for ingredient in ingredients_data:
            try:
                cursor.execute(
                    "INSERT IGNORE INTO ingredients (standard_name, aliases, tag, role) VALUES (%s, %s, %s, %s)",
                    ingredient
                )
            except Error as e:
                print(f"添加成分数据错误: {e}")
        
        # 添加健康风险数据
        health_risk_data = [
            ("糖尿病", "白砂糖", "⚠️ 高糖分，糖尿病患者应控制摄入"),
            ("健身人群", "白砂糖", "⚠️ 高糖分，健身人群应控制摄入"),
            ("糖尿病", "葡萄糖", "⚠️ 高血糖指数，糖尿病患者应控制摄入"),
            ("健身人群", "葡萄糖", "⚠️ 高血糖指数，健身人群应控制摄入"),
            ("肾病", "氯化钠", "⚠️ 高钠，肾病患者应控制摄入")
        ]
        
        for risk in health_risk_data:
            try:
                cursor.execute(
                    "INSERT IGNORE INTO health_risk (health_identity, ingredient_name, risk_tip) VALUES (%s, %s, %s)",
                    risk
                )
            except Error as e:
                print(f"添加健康风险数据错误: {e}")
        
        connection.commit()
        cursor.close()
        connection.close()
        print("数据库初始化完成")
    except Error as e:
        print(f"数据库初始化错误: {e}")
        print("提示：未检测到可用MySQL时，系统仍可运行（但本地缓存/知识库将不可用）。")
        return

# 从数据库查询商品
def query_local_product(barcode):
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(DictCursor)
        cursor.execute("SELECT * FROM products WHERE barcode = %s", (barcode,))
        product = cursor.fetchone()
        cursor.close()
        connection.close()
        
        # 转换为旧格式，保持兼容性
        if product:
            return {
                'barcode': product['barcode'],
                'product_name': product['product_name'],
                'ingredients_raw': product['ingredients'],
                'ingredients_parsed': product['ingredients']
            }
        return None
    except Error as e:
        print(f"查询商品错误: {e}")
        if connection:
            connection.close()
        return None

# 保存商品到数据库
def save_product_to_local(product):
    # 验证商品信息是否有效
    if not product:
        print("保存失败：商品信息为空")
        return False
    
    # 检查必要字段
    product_name = product.get('product_name', '').strip()
    ingredients_raw = product.get('ingredients_raw', '').strip()
    ingredients_parsed = product.get('ingredients_parsed', '').strip()
    
    # 验证商品名称
    if not product_name or product_name == '未命名商品':
        print(f"保存失败：商品名称无效 - {product_name}")
        return False
    
    # 验证配料信息 - 允许没有配料信息（API Byte不提供配料信息）
    # if not ingredients_raw and not ingredients_parsed:
    #     print("保存失败：缺少配料信息")
    #     return False
    
    # 检查是否为OCR失败的信息
    if 'OCR识别失败' in str(ingredients_raw) or 'OCR识别失败' in str(ingredients_parsed):
        print("保存失败：OCR识别失败的商品不入库")
        return False
    
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        # 检查商品是否已存在
        cursor.execute("SELECT barcode FROM products WHERE barcode = %s", (product['barcode'],))
        
        # 准备配料信息
        ingredients_raw = product.get('ingredients_raw', '').strip()
        ingredients_parsed = product.get('ingredients_parsed', '').strip()
        ingredients = ingredients_raw if ingredients_raw else ingredients_parsed
        
        if cursor.fetchone():
            # 更新现有商品
            cursor.execute("""
            UPDATE products SET 
                product_name = %s, 
                ingredients = %s 
            WHERE barcode = %s
            """, (
                product.get('product_name', ''),
                ingredients,
                product['barcode']
            ))
        else:
            # 插入新商品
            cursor.execute("""
            INSERT INTO products (barcode, product_name, ingredients) 
            VALUES (%s, %s, %s)
            """, (
                product['barcode'],
                product.get('product_name', ''),
                ingredients
            ))
        connection.commit()
        cursor.close()
        connection.close()
        print(f"保存成功：{product_name}")
        return True
    except Error as e:
        print(f"保存商品错误: {e}")
        if connection:
            connection.close()
        return False

# 标准化成分名称
def standardize_ingredient(name):
    connection = get_db_connection()
    if not connection:
        return name
    
    try:
        cursor = connection.cursor()
        # 先检查标准名称
        cursor.execute("SELECT standard_name FROM ingredients WHERE standard_name = %s", (name,))
        result = cursor.fetchone()
        if result:
            cursor.close()
            connection.close()
            return result[0]
        
        # 再检查别名
        cursor.execute("SELECT standard_name FROM ingredients WHERE aliases LIKE %s", (f"%{name}%",))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        if result:
            return result[0]
        return name
    except Error as e:
        print(f"标准化成分名称错误: {e}")
        if connection:
            connection.close()
        return name

# 获取成分信息
def get_ingredient_info(name):
    standardized_name = standardize_ingredient(name)
    connection = get_db_connection()
    if not connection:
        return {
            'standard_name': standardized_name,
            'aliases': "",
            'role': "",
            'tag': "",
            'risk_for': "",
            'description': ""
        }
    
    try:
        cursor = connection.cursor(DictCursor)
        # 获取成分基本信息
        cursor.execute("SELECT * FROM ingredients WHERE standard_name = %s", (standardized_name,))
        ingredient = cursor.fetchone()
        
        if not ingredient:
            cursor.close()
            connection.close()
            return {
                'standard_name': standardized_name,
                'aliases': "",
                'role': "",
                'tag': "",
                'risk_for': "",
                'description': ""
            }
        
        # 获取该成分对哪些健康身份有风险
        cursor.execute("SELECT health_identity FROM health_risk WHERE ingredient_name = %s", (standardized_name,))
        risks = cursor.fetchall()
        risk_for = ",".join([r['health_identity'] for r in risks])
        
        cursor.close()
        connection.close()
        
        return {
            'standard_name': ingredient['standard_name'],
            'aliases': ingredient['aliases'],
            'role': ingredient['role'],
            'tag': ingredient['tag'],
            'risk_for': risk_for,
            'description': ""
        }
    except Error as e:
        print(f"获取成分信息错误: {e}")
        if connection:
            connection.close()
        return {
            'standard_name': standardized_name,
            'aliases': "",
            'role': "",
            'tag': "",
            'risk_for': "",
            'description': ""
        }
