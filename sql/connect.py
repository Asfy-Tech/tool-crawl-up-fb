import mysql.connector

# connection = mysql.connector.connect(
#     host='112.213.89.85', 
#     database='asfyvn666bef_FB_Dev',
#     user='asfyvn666bef_dev_hung',
#     password='@Zhung2004',
# )
connection = mysql.connector.connect(
    host='localhost', 
    database='crawl',
    user='root',
    password='',
)
try:
    connection.is_connected()
except Exception as e:
    print(f"Kết nối thất bại: {e}")