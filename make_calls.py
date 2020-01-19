from db_handler import *
import urllib

calls = get_calls()

calls = [{'Aphone':'15038808741', 'Ppid':12}]

# Do only the first call
import urllib.request

if len(calls) > 0:
	url = "http://localhost:8080/make_calls?phone=" + calls[0]['Aphone'] + "&id_position=" + str(calls[0]['Ppid'])
	print(url)
	urllib.request.urlopen(url=url)