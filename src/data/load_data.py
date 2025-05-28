import os
from dotenv import load_dotenv
assert load_dotenv('.env') or load_dotenv('../.env')
import time
import pandas as pd
import mysql.connector
from metadata import column_mapping

# script to create and populate MySQL database of company financial data
# that will be queried by the LangChain agent
# db description resides in backend/data/agent.py

start_time = time.time()

db_config = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': 'financial_db'
}

# Read CSV file that exists in same directory as this script
df = pd.read_csv(f'{os.path.dirname(__file__)}/20_year_data.csv')
df = df.rename(columns=column_mapping)

# Remove duplicates: Keep the last entry for each company and year
df = df.sort_values('year').drop_duplicates(subset=['company_id', 'year'], keep='last')

# Drop unused columns
df = df[[col for col in df.columns if col in column_mapping.values()]]

# Connect to DB
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

columns = df.columns.tolist()

# Create table with company metadata and base financial data
with open(os.path.join(os.path.dirname(__file__),'init_company_table.sql'), 'r') as f:
    create_table_query = f.read()
cursor.execute(create_table_query)

# Insert base financial data
counter=0
for _,row in df.iterrows():
    counter += 1
    print(f'{counter} of {len(df)}')
    values = [row[col] if pd.notna(row[col]) else None for col in columns]
    # values = [df.iloc[row][col] if pd.notna(df.iloc[row][col]) else None for col in columns]
    # convert numpy numeric types to native Python types
    # values = [value.item() if isinstance(value, (np.int64, np.float64)) else value for value in values]

    insert_query = f'''
        INSERT INTO company_data ({', '.join(columns)})
        VALUES ({', '.join(['%s'] * len(columns))})
        ON DUPLICATE KEY UPDATE
        {', '.join(f"{col} = VALUES({col})" for col in columns if col not in ['company_id', 'year'])}
    '''
    cursor.execute(insert_query, values)

conn.commit()
print(f'{len(df)} rows inserted successfully')

# Create derived financial columns
# Procedure to create derived financial data
with open(os.path.join(os.path.dirname(__file__), 'calculate_financial_data.sql'), 'r') as f:
    create_procedure_query = f.read()
cursor.execute('DROP PROCEDURE IF EXISTS calculate_financial_data')
cursor.execute(create_procedure_query)
cursor.callproc('calculate_financial_data')
conn.commit()
print(f'Derived financial metrics updated successfully')

# Cleanup
cursor.close()
conn.close()

end_time = time.time()
print(f'⏱ Time taken: {end_time - start_time:.2f} seconds')
