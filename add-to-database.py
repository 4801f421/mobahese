import re

file_path = "data.txt"

regex_pattern = r"# (\d+)\n\n([\s\S]*?)(?=\n# \d+|\Z)"

with open(file_path, 'r', encoding='utf-8') as file:
    text_content = file.read()

matches = re.finditer(regex_pattern, text_content)

results = []
for match in matches:
    group1 = match.group(1)
    group2 = match.group(2)
    results.append((group1, group2))

def remove_diacritics_and_simplify(text):
    special_chars = {
        'أ':'ا',
        'ة':'ه',
        'آ':'ا',
        'إ':'ا',
        ' ۖ':'',
        ' ۚ':'',
        '۞':'',
        ' ۘ':'',
        ' ۗ':'',
        ' ۙ':'',
        'ۦ':'',
        '۩':'',
        '\n':''
    }
    
    
    # اعمال جایگزینی‌ها
    for key, value in special_chars.items():
        text = text.replace(key, value)
    
    return text

import mysql.connector

db_config = {
    'host': 'hostaddress',
    'user': 'username',
    'password': 'password',
    'database': 'db_name'
}

connection = mysql.connector.connect(**db_config)
cursor = connection.cursor()

table_name = "your table name"

for group1, group2 in results:
    number = group1
    text = remove_diacritics_and_simplify(group2)
    query = f"""
    UPDATE {table_name}
    SET process_text = %s
    WHERE number = %s;
    """
    cursor.execute(query, (text, number))

# ذخیره تغییرات
connection.commit()

# بستن اتصال
cursor.close()
connection.close()

print('data added successfully')