import requests
from base64 import b64encode

AUTHORIZE_URL = "https://api.enphaseenergy.com/oauth/authorize"
TOKEN_URL = "https://api.enphaseenergy.com/oauth/token"
DEFAULT_REDIRECT_URI = "https://api.enphaseenergy.com/oauth/redirect_uri"

def create_auth_header_dict(auth_string):
	header_string = f"Basic {client_info_b64}"
	return {"Authorization" : header_string}

class EnphaseClient:
	def __init__(self, clientID, clientSecret, redirectURI=DEFAULT_REDIRECT_URI)
		self.clientID = clientID
		self.clientSecret = clientSecret
		self.redirectURI = redirectURI

	def _generate_client_info_b64(self):
		concatenated_client_info = f"{client_id}:{client_secret}"
		client_info_bytes = concatenated_client_info.encode("utf-8")
		client_info_b64 = b64encode(client_info_bytes).decode("utf-8")
		return client_info_b64

	def generate_authorization_url(self):
		return f"{AUTHORIZE_URL}?response_type=code&client_id={self.clientID}&redirect_uri={self.redirectURI}"

	def generate_tokens(self, code):
		client_info_b64 = self._generate_client_info_b64()
		headers = create_auth_header_dict(client_info_b64)

		params = {
			"grant_type" : "authorization_code",
			"redirect_uri" : self.redirectURI,
			"code" : code,
		}

		tokens_response = requests.post(TOKEN_URL, params=params, headers=headers)
		tokens = tokens_response.json()
		return tokens

if __name__ == "__main__":
	client_id = input("Enter client id: ")
	client_secret = input("Enter client secret: ")

	client = EnphaseClient(client_id, client_secret)
	url = client.generate_authorization_url()

	print(f"Visit this URL to authorize the script")

	# Open this URL in the browser and get the code from teh web
	code = input("Enter the code from the authorization page:")
	tokens = client.generate_tokens(code)
	access_token = tokens["access_token"]
	print(access_token)

	# Future calls use the access token in the basic auth header
	# headers = create_auth_header_dict(access_token)

	# requests.get("whatever", headers=headers)
