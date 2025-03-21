import pymysql, json
from pathlib import Path

WORK_DIR = Path(__file__).parent

if __name__ == "__main__":
    
    with open(WORK_DIR / 'mysql.json', 'r') as f:
        data = json.load(f)

    conn = pymysql.connect(
        host=data['host'],
        user=data['user'],
        password=data['password'],
        database=data['database']
    )
    print("Connect successfully.")
