from flask import Flask
import json
import mysql.connector  as mysql

mydb = mysql.connect(
  host="127.0.0.1",
  port="3306",
  user="root",
  password="",
  database="Log"
)

cursor = mydb.cursor()

app = Flask(__name__)
@app.route('/')
def hello_world():
    return "hello world"

@app.route('/test')
def test():
    cursor.execute("select * from access where status_code = 400;")
    #print(cursor.fetchall)
    temp = ""
    
    for row in cursor:
        x = 
    return temp


if __name__ == "__main__":
    app.run()
          