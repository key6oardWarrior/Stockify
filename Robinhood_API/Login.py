from os.path import expanduser, join, exists, isfile
from os import makedirs, remove

from UI.PyGUI import Window, Text, Input, Button

from robin_stocks.robinhood.authentication import generate_device_token, pickle, \
	respond_to_challenge
from robin_stocks.robinhood.urls import login_url
from robin_stocks.urls import positions
from robin_stocks.robinhood.helper import set_login_state, update_session, \
	request_get, request_post
from Helper.creds import winName

def login(username=None, password=None, expiresIn=86400, scope='internal', by_sms=True, store_session=True, mfa_code=None, pickle_name=""):
	"""This function will effectively log the user into robinhood by getting an
	authentication token and saving it to the session header. By default, it
	will store the authentication token in a pickle file and load that value
	on subsequent logins.

	:param username: The username for your robinhood account, usually your email.
		Not required if credentials are already cached and valid.
	:type username: Optional[str]
	:param password: The password for your robinhood account. Not required if
		credentials are already cached and valid.
	:type password: Optional[str]
	:param expiresIn: The time until your login session expires. This is in seconds.
	:type expiresIn: Optional[int]
	:param scope: Specifies the scope of the authentication.
	:type scope: Optional[str]
	:param by_sms: Specifies whether to send an email(False) or an sms(True)
	:type by_sms: Optional[boolean]
	:param store_session: Specifies whether to save the log in authorization
		for future log ins.
	:type store_session: Optional[boolean]
	:param mfa_code: MFA token if enabled.
	:type mfa_code: Optional[str]
	:param pickle_name: Allows users to name Pickle token file in order to switch
		between different accounts without having to re-login every time.
	:returns:  A dictionary with log in information. The 'access_token' keyword contains the access token, and the 'detail' keyword \
	contains information on whether the access token was generated or loaded from pickle file.
	"""
	from Helper.helper import exit, exitApp

	device_token = generate_device_token()
	home_dir = expanduser("~")
	data_dir = join(home_dir, ".tokens")

	if not exists(data_dir):
		makedirs(data_dir)
	creds_file = "robinhood" + pickle_name + ".pickle"
	pickle_path = join(data_dir, creds_file)
	# Challenge type is used if not logging in with two-factor authentication.
	if by_sms:
		challenge_type = "sms"
	else:
		challenge_type = "email"

	url = login_url()
	payload = {
		'client_id': 'c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS',
		'expires_in': expiresIn,
		'grant_type': 'password',
		'password': password,
		'scope': scope,
		'username': username,
		'challenge_type': challenge_type,
		'device_token': device_token
	}

	if mfa_code:
		payload['mfa_code'] = mfa_code

	# If authentication has been stored in pickle file then load it. Stops login server from being pinged so much.
	if isfile(pickle_path):
		# If store_session has been set to false then delete the pickle file, otherwise try to load it.
		# Loading pickle file will fail if the acess_token has expired.
		if store_session:
			try:
				with open(pickle_path, 'rb') as f:
					pickle_data = pickle.load(f)
					access_token = pickle_data['access_token']
					token_type = pickle_data['token_type']
					refresh_token = pickle_data['refresh_token']
					# Set device_token to be the original device token when first logged in.
					pickle_device_token = pickle_data['device_token']
					payload['device_token'] = pickle_device_token
					# Set login status to True in order to try and get account info.
					set_login_state(True)
					update_session(
						'Authorization', '{0} {1}'.format(token_type, access_token))
					# Try to load account profile to check that authorization token is still valid.
					res = request_get(
						positions(), 'pagination', {'nonzero': 'true'}, jsonify_data=False)
					# Raises exception is response code is not 200.
					res.raise_for_status()
					return({'access_token': access_token, 'token_type': token_type,
						'expires_in': expiresIn, 'scope': scope, 'detail': 'logged in using authentication in {0}'.format(creds_file),
						'backup_code': None, 'refresh_token': refresh_token})
			except:
				set_login_state(False)
				update_session('Authorization', None)
		else:
			remove(pickle_path)

	# Try to log in normally.
	payload['username'] = username
	payload['password'] = password

	data = request_post(url, payload)
	# Handle case where mfa or challenge is required.
	if data:
		if 'mfa_required' in data:
			win = Window(winName, [[Text("Enter the Robinhood MFA code:"), Input(key="code"), Button("Submit")]], modal=True)
			event, values = win.read()

			if exitApp(event, win):
				exit(0)

			payload["mfa_code"] = values["code"].strip()
			res = request_post(url, payload, jsonify_data=False)

			while (res.status_code != 200):
				win.close()
				win = Window(winName, [[Text("That MFA code was not correct. Please type in another MFA code:"), Input(key="code"), Button("Submit")]], modal=True)
				event, values = win.read()

				if exitApp(event, win):
					exit(0)

				payload["mfa_code"] = values["code"].strip()
				res = request_post(url, payload, jsonify_data=False)

			win.close()
			data = res.json()

		elif 'challenge' in data:
			challenge_id = data['challenge']['id']
			win = Window(winName, [[Text("Enter the Robinhood texted/emailed code for validation:"), Input(key="code"), Button("Submit")]], modal=True)
			event, values = win.read()
			res = respond_to_challenge(challenge_id, values["code"].strip())

			while 'challenge' in res and res['challenge']['remaining_attempts'] > 0:
				win.close()
				win = Window(winName, [[Text("That code was not correct. {0} tries remaining. Please type in another code:".format(
					res['challenge']['remaining_attempts'])), Input(key="code"), Button("Submit")]], modal=True)
				event, values = win.read()

				res = respond_to_challenge(challenge_id, values["code"].strip())

			win.close()
			update_session(
				'X-ROBINHOOD-CHALLENGE-RESPONSE-ID', challenge_id)
			data = request_post(url, payload)
		# Update Session data with authorization or raise exception with the information present in data.
		if 'access_token' in data:
			token = '{0} {1}'.format(data['token_type'], data['access_token'])
			update_session('Authorization', token)
			set_login_state(True)
			data['detail'] = "logged in with brand new authentication code."
			if store_session:
				with open(pickle_path, 'wb') as f:
					pickle.dump({'token_type': data['token_type'],
						'access_token': data['access_token'],
						'refresh_token': data['refresh_token'],
						'device_token': payload['device_token']}, f)
		else:
			if "detail" not in data:
				return "MFA Code Required", False

			return data['detail'], False
	else:
		return "Check Internet Connection", False
	return data, True

class UserAuth:
	__isLoggedIn = False
	__loginInfo = None

	def __init__(self) -> None:
		pass

	def login(self, uName: str, passwd: str) -> None:
		# don't login twice
		if self.__isLoggedIn:
			return

		# robin_stocks.authentication.login
		self.__loginInfo, self.__isLoggedIn = login(uName, passwd)

	@property
	def isLoggedIn(self) -> bool:
		return self.__isLoggedIn

	@property
	def loginInfo(self) -> str | None:
		return self.__loginInfo