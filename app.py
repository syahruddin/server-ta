from flask import Flask, request
from calendar import monthrange
import datetime
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

@app.route('/getobjectperday', methods=['GET'])
def get_object_perday():
    if not checkArgs(['month','year']):
        return "error",422
    else:
        args = request.args

        total_hari = monthrange(int(args['year']), int(args['month']))[1]
        start = datetime.datetime(int(args['year']),int(args['month']),1)
        end = datetime.datetime(int(args['year']),int(args['month']),total_hari)
        start_str = start.strftime("%Y-%m-%d %H:%M:%S")
        end_str = end.strftime("%Y-%m-%d %H:%M:%S")
        #iterasi tiap hari
        i = 1
        while i <= total_hari:
            #ambil data hari tsb dari database
            today = datetime.datetime(int(args['year']),int(args['month']),i)
            nextday = today + datetime.timedelta(days=1)
            today_str = today.strftime("%Y-%m-%d %H:%M:%S")
            nextday_str = nextday.strftime("%Y-%m-%d %H:%M:%S")
            query = "select ip_address, sum(total) as total from ((select distinct ip_address, 0 as total from (select ip_address, time, object_size from access where time between '"+ start_str +"' and '" + end_str + "') may) UNION (select ip_address, sum(object_size) as total from (select ip_address, time, object_size from access where time between '"+ start_str +"' and '" + end_str + "') may where time between '"+ today_str + "' and '"+ nextday_str + "' group by ip_address)) tabel group by ip_address order by ip_address;"
            cursor.execute(query)
            result = cursor.fetchall()
            temp_data_harian = []
            #masukan ke dalam python dictionary
            if i == 1:
                #inisiasi dictionary
                total_baris = 0
                data = {
                    "bulan":args['month'],
                    "tahun":args['year'],
                    "jumlah_hari":total_hari,
                    "total_baris":total_baris,
                    "ip_address":[]
                }
                ip = []
            for user in result:
                temp_data_harian.append(user[1])
                if i == 1:
                    total_baris = total_baris + 1
                    ip.append(user[0])
            day_x = "day_" + str(i)
            data[day_x] = temp_data_harian
            if i == 1:
                data["ip_address"] = ip
                data["total_baris"] = total_baris
            i = i+1
        #ubah python object menjadi json
        data_json = json.dumps(data, default=str)
        return data_json
@app.route('/test')
def test():
    #testing dapatkan data penggunaan selama bulan mei 2022, variabel ip address dan total objek tiap harinya 
    #dapatkan jumlah hari di bulan mei 2022
    total_hari = monthrange(2022, 5)[1]
    #iterasi tiap hari di bulan mei
    i = 1
    while i <= total_hari:
        #ambil data hari tsb dari database
        today = datetime.datetime(2022,5,i)
        nextday = today + datetime.timedelta(days=1)
        today_str = today.strftime("%Y-%m-%d %H:%M:%S")
        nextday_str = nextday.strftime("%Y-%m-%d %H:%M:%S")
        query = "select ip_address, sum(total) as total from ((select distinct ip_address, 0 as total from (select ip_address, time, object_size from access where time between '2022-05-1' and '2022-05-31') may) UNION (select ip_address, sum(object_size) as total from (select ip_address, time, object_size from access where time between '2022-05-1' and '2022-05-31') may where time between '"+ today_str + "' and '"+ nextday_str + "' group by ip_address)) tabel group by ip_address order by ip_address;"
        cursor.execute(query)
        result = cursor.fetchall()
        temp_data_harian = []
        #masukan ke dalam python dictionary
        if i == 1:
            #inisiasi dictionary
            total_baris = 0
            data = {
                "bulan":"5",
                "tahun":"2022",
                "jumlah_hari":total_hari,
                "total_baris":total_baris,
                "ip_address":[]
            }
            ip = []
        for user in result:
            temp_data_harian.append(user[1])
            if i == 1:
                total_baris = total_baris + 1
                ip.append(user[0])
        day_x = "day_" + str(i)
        data[day_x] = temp_data_harian
        if i == 1:
            data["ip_address"] = ip
            data["total_baris"] = total_baris
        i = i+1
    #ubah python object menjadi json
    data_json = json.dumps(data, default=str)
    return data_json


def checkArgs(arg):
    temp = True
    for ar in arg:
        temp = temp and (ar in request.args)
    return temp

if __name__ == "__main__":
    app.run()
          