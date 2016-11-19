import datetime
import requests
import json

def BasisTimestampFixer(timestamp):
	"""
	The BasisDateTimeFixer function focuses on translating the Basis' timestamp 
	format into the ISO format that can be parsed by datetime and used in MongoDB. 
	Basically, we just need to remove the colon from the timezone offset.
	Example: 
	Input - '1425935280'
	Output - datetime.datetime(2014, 2, 28, 22, 48, 19, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400)))
	"""
	return datetime.datetime.fromtimestamp(timestamp)

def BasisDateTimeStringFixer(datetimeString):
	return datetime.datetime.strptime(datetimeString,'%Y-%m-%dT%H:%M:%SZ')

def FindBasisUserSource(username, password):
	"""
	The FindBasisUserSource function gets a user's username and password (since Basis
	is a bit too cheap to write an API) and passes that information to the BasisRequester
	function which programmatically logs in to get the profile data and return the signupDate
	and lastData information.
	"""
	profile_URL = 'https://app.mybasis.com/api/v1/user/me'
	response = BasisRequester(profile_URL, username, password)
	profile_json = json.loads(response.text)
	name_list = ['firstName','lastName']
	basis_name_list = ['first_name', 'last_name']
	user_dict = {}
	user_dict[name_list[0]] = profile_json['profile'][basis_name_list[0]]
	user_dict[name_list[1]] = profile_json['profile'][basis_name_list[1]]
	signupDate = BasisTimestampFixer(profile_json['profile']['joined'])
	lastData = BasisTimestampFixer(profile_json['last_data_endtime'])
	return signupDate, lastData

def BasisRequester(url, username, password):
	"""
	The BasisRequester function takes a url, username and password and programmatically logs
	a user in to get back the relevant json data from Basis (since they are too cheap to make
	an API.)
	"""
	LOGIN_URL = 'https://app.mybasis.com/login'
	response = None
	payload = {"username": username, "password": password, 'action': 'login'}
	with requests.session() as s:
		s.post(LOGIN_URL, data=payload)
		response = s.get(url)
	return response

def BasisSleep(date, username, password):
	"""
	The BasisSleep function makes a call to the BasisRequester function to get sleep 
	information for the date specified. It then creates a json file for each date.
	"""
	sleep_url = "https://app.mybasis.com/api/v2/users/me/days/" + str(date) + \
			"/activities?type=sleep&expand=activities.stages,activities.events"
	try:
		sleep_response = BasisRequester(sleep_url, username, password)
		sleep = json.loads(sleep_response.text)
	except slumber.exceptions.HttpClientError:
		print(slumber.exceptions.HttpClientError)
	path_prefix = "/Sleep/basis-data-"
	path_suffix = "-sleep.json"
	date = str(date)
	with open(pathRoot+path_prefix+date+path_suffix,"w") as sleep_file:
		json.dump(sleep, sleep_file)

def BasisActivities(date, username, password, pathRoot):
	"""
	The BasisActivities function makes a call to the BasisRequester function to get metrics 
	information for the date specified. It then creates a json file for each date.
	"""
	activity_url = "https://app.mybasis.com/api/v2/users/me/days/" + str(date) + \
	"/activities?type=run,walk,bike&expand=activities"
	try:
		activity_response = BasisRequester(activity_url, username, password)
		activity = json.loads(activity_response.text)
	except slumber.exceptions.HttpClientError:
		print(slumber.exceptions.HttpClientError)
	path_prefix = "/Activities/basis-data-"
	path_suffix = "-activities.json"
	date = str(date)
	with open(pathRoot+path_prefix+date+path_suffix,"w") as activity_file:
		json.dump(activity, activity_file)

def BasisMetrics(date, username, password, pathRoot):
	"""
	The BasisMetrics function makes a call to the BasisRequester function to get metrics 
	information for the date specified. It then creates a json file for each date.
	"""
	metrics_url = "https://app.mybasis.com/api/v1/metricsday/me?day=" + str(date) + \
	"&heartrate=true&steps=true&calories=true&gsr=true&skin_temp=true"

	try:
		metrics_response = BasisRequester(metrics_url, username, password)
		metrics = json.loads(metrics_response.text)
	except slumber.exceptions.HttpClientError:
		print(slumber.exceptions.HttpClientError)
	path_prefix = "/Metrics/basis-data-"
	path_suffix = "-metrics.json"
	date = str(date)
	with open(pathRoot+path_prefix+date+path_suffix,"w") as metrics_file:
		json.dump(metrics, metrics_file)

def DateRange(start_date, end_date):
    for n in range(int (((end_date + datetime.timedelta(2)) - start_date).days)):
        yield start_date + datetime.timedelta(n)

SOURCE = "Basis"
user = "jlmitch2@gmail.com"
pw = "12345678"
rootDir = "/Users/justin/Box Sync/My_data/biohacking/Basis/data/Full-Basis-Export"
signup, lastData = FindBasisUserSource(user,pw)

for singleDate in DateRange(signup, lastData):
	dayInProgress = singleDate.strftime("%Y-%m-%d")
	BasisSleep(dayInProgress, user, pw, rootDir)
	BasisActivities(dayInProgress, user, pw, rootDir)
	BasisMetrics(dayInProgress, user, pw, rootDir)
	print(dayInProgress)