from flask import Flask, request
from calendar import monthrange
from dateutil.relativedelta import relativedelta
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

@app.route('/check_daily_request')
def check_daily_request():
    #mengembalikan jumlah request, total object dikembalikan, dan jumlah ip address berbeda tiap harinya
    query = "SELECT CAST(time as DATE) as time, COUNT(request_line) as total_request, SUM(object_size) as total_object, COUNT(DISTINCT ip_address) as total_client FROM access GROUP BY CAST(time as DATE) ORDER BY time;"
    cursor.execute(query)
    result = cursor.fetchall()
    total_baris = 0
    waktu = []
    total_request = []
    total_object = []
    total_client = []

    for row in result:
        waktu.append(row[0])
        total_request.append(row[1])
        total_object.append(row[2])
        total_client.append(row[3])
        total_baris = total_baris + 1

    data = {
                "total_baris":total_baris,
                "waktu":waktu,
                "total_request":total_request,
                "total_object":total_object,
                "total_client":total_client
            }
    data_json = json.dumps(data, default=str)
    return data_json

@app.route('/check_daily_request_by_month')
def check_daily_request_by_month():
    #menerima bulan dan tahun, jika tanggal valid mengembalikan jumlah request, total object dikembalikan, dan jumlah ip address berbeda tiap harinya pada bulan tersebut
    if not checkArgs(['year','month']):
       return "error",422
    
    args = request.args
    range = get_Month_Range(int(args['year']), int(args['month']))
    query = "SELECT CAST(time as DATE) as time, COUNT(request_line) as total_request, SUM(object_size) as total_object, COUNT(DISTINCT ip_address) as total_client FROM access WHERE time BETWEEN '" + range[0] + "' AND '" + range[1] + "' GROUP BY CAST(time as DATE) ORDER BY time;"
    cursor.execute(query)
    result = cursor.fetchall()
    total_baris = 0
    waktu = []
    total_request = []
    total_object = []
    total_client = []

    for row in result:
        waktu.append(row[0])
        total_request.append(row[1])
        total_object.append(row[2])
        total_client.append(row[3])
        total_baris = total_baris + 1

    data = {
                "bulan":args['month'],
                "tahun":args['year'],
                "total_baris":total_baris,
                "waktu":waktu,
                "total_request":total_request,
                "total_object":total_object,
                "total_client":total_client
            }
    data_json = json.dumps(data, default=str)
    return data_json

@app.route('/check_request_on_day')
def check_request_on_day():
    #menerima hari, bulan, tahun. jika tanggal valid mengembalikan tiap ip address, jumlah requestnya, dan total object yg dikembalikannya pada hari tersebut.
    if not checkArgs(['day','year','month']):
       return "error",422
    args = request.args
    day = datetime.datetime(int(args['year']),int(args['month']),int(args['day']))
    nextday = day + datetime.timedelta(days=1)
    day_str = day.strftime("%Y-%m-%d")
    nextday_str = nextday.strftime("%Y-%m-%d")
    query = "SELECT ip_address, COUNT(request_line) as total_request, SUM(object_size) as total_object FROM access WHERE time BETWEEN '" + day_str + "' AND '" + nextday_str + "' GROUP BY ip_address;"
    cursor.execute(query)
    result = cursor.fetchall()
    total_baris = 0
    ip_address = []
    total_request = []
    total_object = []

    for row in result:
        ip_address.append(row[0])
        total_request.append(row[1])
        total_object.append(row[2])
        total_baris = total_baris + 1
    data = {
                "hari": args['day'],
                "bulan":args['month'],
                "tahun":args['year'],
                "total_baris":total_baris,
                "ip_address":ip_address,
                "total_request":total_request,
                "total_object":total_object
            }
    data_json = json.dumps(data, default=str)
    return data_json
    

@app.route('/get_request_line_and_status_code')
def get_request_line_and_status_code():
    #masukan ip address, hari, bulan, tahun. jika tanggal dan ip address valid, mengembalikan tiap request line dan status codenya dari ip address tersebut pada tanggal tersebut.
    if not checkArgs(['day','year','month','ip_address']):
       return "error",422
    args = request.args
    day = datetime.datetime(int(args['year']),int(args['month']),int(args['day']))
    nextday = day + datetime.timedelta(days=1)
    day_str = day.strftime("%Y-%m-%d")
    nextday_str = nextday.strftime("%Y-%m-%d")
    query = "SELECT request_line, status_code from access WHERE time BETWEEN '" + day_str + "' AND '" + nextday_str + "' AND ip_address ='" + args['ip_address'] + "' ORDER BY time;"
    cursor.execute(query)
    result = cursor.fetchall()
    total_baris = 0
    request_line = []
    status_code = []

    for row in result:
        request_line.append(row[0])
        status_code.append(row[1])
        total_baris = total_baris + 1
    data = {
                "ip_address": args['ip_address'],
                "hari": args['day'],
                "bulan":args['month'],
                "tahun":args['year'],
                "total_baris":total_baris,
                "request_line":request_line,
                "status_code":status_code
            }
    data_json = json.dumps(data, default=str)
    return data_json

@app.route('/search_usage_of_keyword')
def seach_usage_of_keyword():
    #masukan sebuah keyword, keluaran setiap ip address yg pernah request berisi keyword tsb dan jumlah requestnya
    if not checkArgs(['keyword']):
       return "error",422
    args = request.args
    query = "SELECT ip_address, COUNT(request_line) as total_request FROM access WHERE request_line LIKE '%" + args['keyword'] + "%' GROUP BY ip_address;"
    cursor.execute(query)
    result = cursor.fetchall()
    total_baris = 0
    ip_address = []
    total_request = []

    for row in result:
        ip_address.append(row[0])
        total_request.append(row[1])
        total_baris = total_baris + 1
    data = {
                "keyword": args['keyword'],
                "total_baris":total_baris,
                "ip_address":ip_address,
                "total_request":total_request
            }
    data_json = json.dumps(data, default=str)
    return data_json

@app.route('/search_usage_of_keyword_on_month')
def seach_usage_of_keyword_on_month():
    if not checkArgs(['keyword', 'month', 'year']):
       return "error",422
    args = request.args
    range = get_Month_Range(int(args['year']),int(args['month']))
    query = "SELECT ip_address, COUNT(request_line) as total_request FROM access WHERE time BETWEEN '" + range[0] + "' AND '" + range[1] + "' AND request_line LIKE '%" + args['keyword'] + "%' GROUP BY ip_address;"
    cursor.execute(query)
    result = cursor.fetchall()
    total_baris = 0
    ip_address = []
    total_request = []

    for row in result:
        ip_address.append(row[0])
        total_request.append(row[1])
        total_baris = total_baris + 1
    data = {
                "keyword": args['keyword'],
                "bulan":args['month'],
                "tahun":args['year'],
                "total_baris":total_baris,
                "ip_address":ip_address,
                "total_request":total_request
            }
    data_json = json.dumps(data, default=str)
    return data_json

@app.route('/check_status_code_occurence')
def check_status_code_occurence():
    #masukan keyword status code, keluaran jumlah kemunculan tiap harinya
    if not checkArgs(['keyword']):
       return "error",422
    args = request.args
    query = "SELECT CAST(time as DATE) as time, COUNT(status_code) as total_status_code FROM access WHERE status_code = '" + args["keyword"] +"' GROUP BY CAST(time as DATE);"
    cursor.execute(query)
    result = cursor.fetchall()
    total_baris = 0
    waktu =[]
    total_status = []

    for row in result:
        waktu.append(row[0])
        total_status.append(row[1])
        total_baris = total_baris + 1
    data = {
                "keyword": args['keyword'],
                "total_baris":total_baris,
                "waktu":waktu,
                "total_status":total_status
            }
    data_json = json.dumps(data, default=str)
    return data_json

@app.route('/check_status_code_occurence_per_ip')
def check_status_code_occurence_per_ip():
    #masukan keyword, hari bulan dan tahun. jika tanggal valid, keluaran tiap ip address dengan status code tersebut dan jumlah kemunculannya
    #masukan keyword status code, keluaran jumlah kemunculan tiap harinya
    if not checkArgs(['keyword','day','month','year']):
       return "error",422
    args = request.args
    day = datetime.datetime(int(args['year']),int(args['month']),int(args['day']))
    nextday = day + datetime.timedelta(days=1)
    day_str = day.strftime("%Y-%m-%d")
    nextday_str = nextday.strftime("%Y-%m-%d")
    query = "SELECT ip_address, COUNT(status_code) AS total_status_code FROM access WHERE time BETWEEN '" + day_str + "' AND '" + nextday_str + "' AND status_code ='" + args['keyword'] + "' GROUP BY ip_address;"
    cursor.execute(query)
    result = cursor.fetchall()
    total_baris = 0
    ip_address =[]
    total_status = []

    for row in result:
        ip_address.append(row[0])
        total_status.append(row[1])
        total_baris = total_baris + 1
    data = {
                "keyword": args['keyword'],
                "hari":args["day"],
                "bulan":args["month"],
                "tahun":args["year"],
                "total_baris":total_baris,
                "ip_address":ip_address,
                "total_status":total_status
            }
    data_json = json.dumps(data, default=str)
    return data_json

#fungsi testing
@app.route('/getobjectpermonth', methods=['GET'])
def get_object_permonth():
    if not checkArgs(['year']):
        return "error",422
    else:
        args = request.args

        start = datetime.datetime(int(args['year']),1,1)
        end = datetime.datetime(int(args['year']),12,31)
        start_str = start.strftime("%Y-%m-%d %H:%M:%S")
        end_str = end.strftime("%Y-%m-%d %H:%M:%S")
        #iterasi tiap hari
        i = 1
        while i <= 12:
            #ambil data hari tsb dari database
            today = datetime.datetime(int(args['year']),i,1)
            nextday = today + relativedelta(months=1)
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
                    "tahun":args['year'],
                    "total_baris":total_baris,
                    "ip_address":[]
                }
                ip = []
            for user in result:
                temp_data_harian.append(user[1])
                if i == 1:
                    total_baris = total_baris + 1
                    ip.append(user[0])
            bulan_x = "bulan_" + str(i)
            data[bulan_x] = temp_data_harian
            if i == 1:
                data["ip_address"] = ip
                data["total_baris"] = total_baris
            i = i+1
        #ubah python object menjadi json
        data_json = json.dumps(data, default=str)
        return data_json  

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

#fungsi tambahan
def checkArgs(arg):
    temp = True
    for ar in arg:
        temp = temp and (ar in request.args)
    return temp

def get_Month_Range(year, month):
    total_hari = monthrange(year, month)[1]
    start = datetime.datetime(year,month,1)
    end = datetime.datetime(year,month,total_hari) + datetime.timedelta(days=1)
    start_str = start.strftime("%Y-%m-%d %H:%M:%S")
    end_str = end.strftime("%Y-%m-%d %H:%M:%S")
    temp = [start_str,end_str]
    return temp

if __name__ == "__main__":
    app.run()
          