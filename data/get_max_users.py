#from __future__ import print_function
import json,urllib
import urllib2, base64
import re
from datetime import datetime
import sys
import argparse
from urllib2 import HTTPError
import pytz
import time
from tzlocal import get_localzone

#import html2text

#max = not more than 30 000 000

#num_digits = 8

base_url = 'https://api.github.com/users?per_page=100&since='

dig_arr = []

max_digits=0

utc = pytz.timezone('UTC')
system_tz =  get_localzone()

#fancy countdown function
def countdown(t):
	t = int(t)
	while t:
		mins, secs = divmod(t, 60)
		timeformat = '{:02d}:{:02d}'.format(mins, secs)
		#python2
		#print('\r'+ timeformat, end="")
		sys.stdout.write('\r'+ timeformat)
		sys.stdout.flush()
		#python3
		#print(timeformat, end='\r')
		time.sleep(1)
		t -= 1

def send_req(url, oAuthToken):
	request = urllib2.Request(url)
	request.add_header("Authorization", "token %s" % oAuthToken)
	try:
		response = urllib2.urlopen(request)
		json_response=json.loads(response.read())
		RateLimitLimit = response.info().getheader('X-RateLimit-Limit')
		RateLimitRemaining = response.info().getheader('X-RateLimit-Remaining')
		RateLimitReset = response.info().getheader('X-RateLimit-Reset')
	except HTTPError as err:
		print("Caught HTTPError: " + str(err))
		RateLimitReset = err.headers['X-RateLimit-Reset']
		
		##put the requst to sleep until reset
		now = system_tz.localize(datetime.now())
		dt = datetime.utcfromtimestamp(int(RateLimitReset))
		dt_utc = utc.localize(dt)
		dt_sys = utc.localize(dt).astimezone(system_tz)
		diff = dt_sys -now 
		diff_sec = diff.total_seconds() + 10
		print("Putting system to sleep for %s secs..." % diff_sec)
		countdown(diff_sec)
		print("...sending request again")
		response = urllib2.urlopen(request)
		json_response=json.loads(response.read())
		RateLimitLimit = response.info().getheader('X-RateLimit-Limit')
		RateLimitRemaining = response.info().getheader('X-RateLimit-Remaining')
		RateLimitReset = response.info().getheader('X-RateLimit-Reset')
		pass

	dt = datetime.utcfromtimestamp(int(RateLimitReset))
	dt_utc = utc.localize(dt)
	dt_sys = utc.localize(dt).astimezone(system_tz)
	print("RateLimit-Limit %s" % RateLimitLimit)
	print("RateLimit-Remaining %s" % RateLimitRemaining)
	print("RateLimit-Reset %s" %( RateLimitReset))
	print("RateLimit reset in UTC: %s" % dt_utc.strftime('%Y-%m-%d %H:%M:%S'))
	print("RateLimit reset in system's %s : %s" % (system_tz.zone, dt_sys.strftime('%Y-%m-%d %H:%M:%S')))
	print()

	return_val = True if len(json_response) > 0 else False
	return return_val


def find_max_digits(max_boundary, token):
	for i in range (0, max_boundary):
		url = base_url + format(1<<i, 'b')
		print ("finding max digits for " + url)
		exists = send_req(url, token)
		print ("exists: " + str(exists))
		if exists:
			max_dig = i
		else:
			break
	return max_dig + 1


def get_max(pos, dig_arr, token):
	print('Starting pos' + str(pos) )
	for digit in range(1,10):
		dig_arr[pos] = digit
		arr_num = ''.join([str(x) for x in dig_arr])
		print ('Trying number ' + arr_num)
		url = base_url + arr_num
		print ("Sending url:" + url)
		exists = send_req(url, token)
		print ("exists: " + str(exists))
		if exists:
			continue
		else:
			dig_arr[pos] = digit - 1
			break

def main(argv):

	#get token
	oAuthToken = ''
	parser = argparse.ArgumentParser()
	parser.add_argument('-t', '--token')
	args = parser.parse_args()

	print('oAuthToken is %s' % args.token)

	#find max amout digits
	max_digits = find_max_digits(10, args.token)
	print("Max digit is: " + str(max_digits))

	#find the max number
	print("Starting looking for the actual number")
	dig_arr = [0 for i in range(max_digits)]
	for pos in range(max_digits):
		get_max(pos, dig_arr, args.token)

	arr_num = ''.join([str(x) for x in dig_arr])
	print("Max user ID is:" + arr_num)
	print("Done")

if __name__ == "__main__":
	main(sys.argv[1:])
