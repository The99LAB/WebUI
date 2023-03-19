import sqlite3
import json

db = sqlite3.connect('database.db')
c = db.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE,
        value TEXT
    )
''')

def add_setting(name, value):
    c.execute('''
        INSERT INTO settings (name, value)
        VALUES (?, ?)
    ''', (name, value))
    db.commit()

def remove_setting(name):
    c.execute('''
        DELETE FROM settings
        WHERE name = ?
    ''', (name,))
    db.commit()

def list_settings():
    c.execute('''
        SELECT * FROM settings
    ''')
    rows = c.fetchall()
    settings = []
    for row in rows:
        setting = {'id': row[0], 'name': row[1]}
        try:
            value = json.loads(row[2])
            if isinstance(value, list):
                setting['value'] = value
            else:
                setting['value'] = row[2]
        except json.JSONDecodeError:
            setting['value'] = row[2]
        settings.append(setting)
    return settings

while True:
    print("1. Add setting")
    print("2. Remove setting")
    print("3. List settings")
    print("4. Insert list of setting")
    print("5. Exit")
    choice = input("Enter your choice: ")
    if choice == '1':
        setting_name = input("Enter setting name: ")
        setting_value = input("Enter setting value: ")
        add_setting(setting_name, setting_value)
    elif choice == '2':
        setting_name = input("Enter setting name: ")
        remove_setting(setting_name)

    elif choice == '3':
        for setting in list_settings():
            print(f"id: {setting['id']}, name: {setting['name']}, value: {setting['value']}")
            print(type(setting['id']))
            print(type(setting['name']))
            print(type(setting['value']))

    elif choice == '4':
        new_name = 'example_list_setting'
        new_value = ['example', 'list', 'values']
        value_string = json.dumps(new_value)  # convert list to string representation
        add_setting(new_name, value_string)

    elif choice == '5':
        break

db.close()

