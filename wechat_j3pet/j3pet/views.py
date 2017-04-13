# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
import hashlib
from lxml import etree
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import time
import requests
import datetime
import sys
from django.shortcuts import render
import urllib

reload(sys)
sys.setdefaultencoding('utf-8')

# Create your views here.

wechat_token = "zxcbnm3144"

@csrf_exempt
def index(request):
	if request.method == "GET":
		signature = request.GET.get('signature',None)
		timestamp = request.GET.get('timestamp',None)
		nonce = request.GET.get('nonce',None)
		echostr = request.GET.get('echostr',None)
		token = wechat_token
		tmp_list = [token, timestamp, nonce]
		tmp_list.sort()
		tmp_str = "%s%s%s" % tuple(tmp_list)
		tmp_str = hashlib.sha1(tmp_str).hexdigest()
		if tmp_str == signature:
			return HttpResponse(echostr)
		else:
			return HttpResponse('hell no')
	else:
		xml_str = smart_str(request.body)
		xml_str = xml_str.replace("body=","")
		xml_str = urllib.unquote(xml_str)
		xml_str = xml_str.replace('+Â ','\n')
		xml_str = xml_str.replace('+','')
		xml_str = xml_str.replace('</<xml>>','</xml>')
#		return HttpResponse(xml_str)
		request_xml = etree.fromstring(xml_str)
		response_xml = reply(request_xml)
		return HttpResponse(response_xml)

def reply(request_xml):
	tousername = request_xml.find('FromUserName').text
	fromusername = request_xml.find('ToUserName').text
	createtime = int(time.time())
	msgtype = 'text'
	content = response_content()
	response_str = """<xml>
	<ToUserName>%s</ToUserName>
	<FromUserName>%s</FromUserName>
	<CreateTime>%s</CreateTime>
	<MsgType>%s</MsgType>
	<Content>%s</Content>
	</xml>"""%(tousername,fromusername,createtime,msgtype,content)
	return response_str

def response_content():
	header = {"User-Agent":"Mozilla/5.0 (Windows NT 6.2; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0"}
	json_data = requests.get("http://www.j3pet.com/internal/api/servers/3/pet_serendipities",headers=header).json()
	result = ""
	partial_result_dict ={}
	pet_alias_raw_data = requests.get("http://www.j3pet.com/internal/api/servers/3/pet_aliases",headers=header).json()["data"]
	for i in json_data["data"]:
   		attribute = i["attributes"]
    		pet = attribute["pet"]
		pet_id_serendipities = pet["id"]
#    		pet_name = pet["name"].encode('utf-8')
		for j in pet_alias_raw_data:
			pet_alias_attribute = j["attributes"]
			pet_id_alias = pet_alias_attribute["pet_id"]
			if pet_id_alias == pet_id_serendipities:
				pet_name = pet_alias_attribute["alias"]
				break
    		raw_last_time = attribute['trigger_time']
    		last_time_format = datetime.datetime.strptime(raw_last_time,"%Y-%m-%dT%H:%M:%S.000+08:00")
    		last_time = last_time_format.strftime("%H:%M")
    		min_cd = float(pet['min_cd'])
    		max_cd = float(pet['max_cd'])
    		close_next_time_format = last_time_format + datetime.timedelta(hours=min_cd)
    		far_next_time_format = last_time_format + datetime.timedelta(hours=max_cd)
    		present_time_format = datetime.datetime.now()+datetime.timedelta(hours=8)
    		present_time = present_time_format.strftime("%m-%d %H:%M:%S")
    		close_next_time = close_next_time_format.strftime("%m-%d %H:%M:%S")
    		far_next_time = far_next_time_format.strftime("%m-%d %H:%M:%S")
    		if close_next_time > present_time:
        		status = u"还需"
#        		time_left_minutes = int(((close_next_time_format-present_time_format).seconds)/60)
#        		time_left_seconds = int(((close_next_time_format-present_time_format).seconds)%60)
			time_left_hours_num = int(((close_next_time_format-present_time_format).seconds)/3600)
			time_left_minutes_num = int(((close_next_time_format-present_time_format).seconds%3600)/60)
			time_left_hours_string = str(int(((close_next_time_format-present_time_format).seconds)/3600))
			time_left_minutes_string = str(int(((close_next_time_format-present_time_format).seconds%3600)/60)).zfill(2)
        		time_left = str(time_left_hours_string)+ ":"+ str(time_left_minutes_string)
			status_code = 100000
			order_num = status_code - time_left_hours_num * 60 - time_left_minutes_num
    		elif present_time > close_next_time and present_time < far_next_time:
        		status = u"已进"
#        		time_left_minutes = int(((present_time_format-close_next_time_format).seconds)/60)
#        		time_left_seconds = int(((present_time_format-close_next_time_format).seconds)%60)
			time_left_hours_num = int(((present_time_format-close_next_time_format).seconds)/3600)
			time_left_minutes_num = int(((present_time_format-close_next_time_format).seconds%3600)/60)
			time_left_hours_string = str(int(((present_time_format-close_next_time_format).seconds)/3600))
			time_left_minutes_string = str(int(((present_time_format-close_next_time_format).seconds%3600)/60)).zfill(2)
        		time_left = str(time_left_hours_string)+":" + str(time_left_minutes_string)
			status_code = 500000
			order_num = status_code + time_left_hours_num * 60 + time_left_minutes_num
    		else:
        		status = u"失联"
        		time_left = "00:00"
			status_code = -500000
			order_num = status_code
    		partial_result = pet_name+"("+last_time+")"+status+"("+time_left+")"+"\n"
#		order_num = status_code + time_left_hours_num * 60 + time_left_minutes_num
		order_num = order_num + float(pet_id_serendipities/50)
		partial_result_dict[order_num]=partial_result
#    		result += partial_result
	partial_result_dict_order = sorted(partial_result_dict.keys(),reverse=True)
	for k in partial_result_dict_order:
		result += partial_result_dict[k]
#		result += str(k)	
	return result

def test(request):
	return render(request,'test.html')
