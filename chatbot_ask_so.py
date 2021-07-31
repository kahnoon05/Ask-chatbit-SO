# Lib
from flask import Flask, request, abort
import requests
import json
from flask_sslify import SSLify #SSL Flask
import ssl #SSL Flask
import pymongo
import re

# SSL flask
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain('/root/so_replyer/certinet/domain.crt', '/root/so_replyer/certinet/domain.key')

so_backend = Flask(__name__)

sslify = SSLify(so_backend)

# get vm details from mongodb
def get_vm_data_from_mongo(so_num):
    try:
        # Define MongoDB Variable
        Vreal_database_directory = pymongo.MongoClient('172.25.2.82', 27017, username='user01', password='mis@Pass01')
        vreal_database = Vreal_database_directory["uat_report"]
        Vreal_collection = vreal_database["list_vmspec_arch"]

        myquery = {"so_number": { "$regex": ''+so_num+'' , "$options" : "i" }}

        Mongo_cnodata = Vreal_collection.find(myquery,{"platform" : 1, "vm_name" : 1, "cpu" : 1, "memory" : 1, "disk" : 1, "os" : 1, "ip_private" : 1, "ip_public" : 1, "cust_name" : 1, "sale_name" : 1})
        data_from_vmname = list(Mongo_cnodata)
        Vreal_database_directory.close()
        return data_from_vmname
    except Exception as e:   
        print("error >> from get_vm_data_from_mongo : ", e)

def ReplyMessage(Reply_token, TextMessage, Line_Acees_Token):
    try:
        LINE_API = 'https://api.line.me/v2/bot/message/reply'

        Authorization = 'Bearer {}'.format(Line_Acees_Token)
        headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization':Authorization
        }
        data = {"replyToken":Reply_token,"messages":[{"type":"text","text":TextMessage}]}
        data = json.dumps(data)
        r = requests.post(LINE_API, headers=headers, data=data)
        return 200
    except Exception as e:
        print(e)
        
# SO API path
@so_backend.route('/', methods=['POST'])
def webhook():
    payload = request.json
    Reply_token = payload['events'][0]['replyToken']
    message = payload['events'][0]['message']['text']  

    if 'SO=' in message or 'so=' in message or 'So=' in message or 'sO=' in message:
        try:
            filter_so = re.findall(r'(?<=[sS][oO][=])(\S+)', message)[0]
            print(filter_so)
            try:
                vm_data_from_so = get_vm_data_from_mongo(filter_so)
                print(vm_data_from_so)
                Reply_messasge = ""
                if len(vm_data_from_so) == 0:
                    Reply_messasge = "ไม่พบ SO กรุณาติดต่อ Operation"

                for count_vm in range (len(vm_data_from_so)):
                    data_vmname = vm_data_from_so[count_vm]["vm_name"]
                    data_cpu = vm_data_from_so[count_vm]["cpu"]
                    data_mem = vm_data_from_so[count_vm]["memory"]
                    data_disk = vm_data_from_so[count_vm]["disk"]
                    data_platform = vm_data_from_so[count_vm]["platform"]
                    data_cusname = vm_data_from_so[count_vm]["cust_name"]
                    data_sale_name = vm_data_from_so[count_vm]["sale_name"] 
                            
                    output = 'VMname : '+data_vmname+'\n\u25CF CPU : '+str(data_cpu)+'\n\u25CF Mem : '+str(data_mem)+'\n\u25CF Disk : '+str(data_disk)+'\n\u25CF Platform : '+data_platform+'\n\u25CF Cus name : '+data_cusname+'\n\u25CF Sale name : '+data_sale_name+'\n\n'
                    Reply_messasge += output
                ReplyMessage(Reply_token,Reply_messasge,'Tw2XOER56qHqEFfMBHjJ0x2cL+1r3jnZZP7+w8tZI/v/PLj0q6mhJHQIXbhMTGtlN1Pn2Ir8cDh+J68eGXxtfwdZbY9KnX9LyKiinYiM7mfXuiesfYCtj66ov0EN/1guIJOkuqpDG2kbN/6bOanoZwdB04t89/1O/w1cDnyilFU=') #ใส่ Channel access token
                return request.json, 200

            except Exception as e:
                Reply_messasge = "ไม่พบ SO กรุณาติดต่อ Operation"
                ReplyMessage(Reply_token,Reply_messasge,'Tw2XOER56qHqEFfMBHjJ0x2cL+1r3jnZZP7+w8tZI/v/PLj0q6mhJHQIXbhMTGtlN1Pn2Ir8cDh+J68eGXxtfwdZbY9KnX9LyKiinYiM7mfXuiesfYCtj66ov0EN/1guIJOkuqpDG2kbN/6bOanoZwdB04t89/1O/w1cDnyilFU=') #ใส่ Channel access token
                return request.json, 200
        except:
            Reply_messasge = "ไม่พบ SO กรุณาติดต่อ Operation"
            ReplyMessage(Reply_token,Reply_messasge,'Tw2XOER56qHqEFfMBHjJ0x2cL+1r3jnZZP7+w8tZI/v/PLj0q6mhJHQIXbhMTGtlN1Pn2Ir8cDh+J68eGXxtfwdZbY9KnX9LyKiinYiM7mfXuiesfYCtj66ov0EN/1guIJOkuqpDG2kbN/6bOanoZwdB04t89/1O/w1cDnyilFU=') #ใส่ Channel access token
            return request.json, 200
#test

    else:
        return "don't check so"

def main():
    so_backend.run(debug=True, port=6500, host='0.0.0.0', threaded=True, ssl_context=context)

if __name__ == '__main__':
    main()
