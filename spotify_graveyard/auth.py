from threading import Event, Lock
from wsgiref.simple_server import make_server, WSGIRequestHandler
from webbrowser import open_new
from urllib.parse import quote
from _thread import start_new_thread
from re import escape

from bottle import route, request, response, ServerAdapter, Bottle

REQUIRED_SCOPES = [
	"playlist-read-private",
	"playlist-read-collaborative",
	"playlist-modify-private", 
	"playlist-modify-public"
]
REQUIRED_SCOPES_JOINED = " ".join(REQUIRED_SCOPES)
CLIENT_ID = "16a978e7b5704aa28c388562721676ef"

PORT = 50719 # Spotify in leet - letters + 9
REDIRECT_URI = "http://localhost:%i/callback/" % PORT
AJAX_URL = "http://localhost:%i/ajax-callback/?" % PORT

SUCCESSFUL_TEXT = "Token received! You can now close this window. <br>" \
	"(If <b>spotify-graveyard</b> has not received the token yet, reload this page.)"

ERROR_TEXT = "Error occured, check terminal output."

__BOTTLE_APP = Bottle()

__AUTH_EVENT = Event()
__AUTH_LOCK = Lock()

__ACCESS_TOKEN = None
__EXPIRES_IN = None

CALLBACK_HTML = """
<html>
	<head>
		<style>
		.center {
			position: absolute;
			left: 50%%;
			top: 50%%;
			-webkit-transform: translate(-50%%, -50%%);
			transform: translate(-50%%, -50%%);
			text-align: center;
			font: 15px arial, sans-serif;
		}
		</style>
	</head>
	<body>

	<div class="center">
		<img src="https://user-images.githubusercontent.com/9287847/32694654-e3b2321e-c745-11e7-9e27-5eca280eddff.png" height="300">
		<p id="status">Sending token to <b>spotify-graveyard</b>...</p>
	</div>

	<script type="text/javascript">
		var url = "%s";
		var successfulText = "%s";
		var errorText = "%s";

		var xhttp = new XMLHttpRequest();
		xhttp.onreadystatechange = function() {
			if (this.readyState == 4 && this.status == 200) {
				document.getElementById("status").innerHTML = successfulText;
			}
			if (this.readyState == 4 && this.status != 200) {
				document.getElementById("status").innerHTML = errorText;
			}			
		};

		xhttp.open("GET", url + location.hash.slice(1), 
			true);
		xhttp.send();
	</script>
	</body>
</html>
""" % (AJAX_URL, escape(SUCCESSFUL_TEXT), escape(ERROR_TEXT))


# https://stackoverflow.com/a/16056443/4739690
class __WSGIRefServer(ServerAdapter):
	server = None

	def run(self, handler):
		if self.quiet:
			class QuietHandler(WSGIRequestHandler):
				def log_request(*args, **kw): pass
			self.options['handler_class'] = QuietHandler
		self.server = make_server(self.host, self.port, handler, **self.options)
		self.server.serve_forever()

	def stop(self):
		self.server.shutdown()


def auth():
	# Prevent simultaneous function execution
	__AUTH_LOCK.acquire()
	# Create event that guards __ACCESS_TOKEN
	__AUTH_EVENT.clear()
	
	server = __WSGIRefServer(host="localhost", port=PORT)

	start_new_thread(__BOTTLE_APP.run, (), {
		"server" : server,
		"quiet" : True
	})

	open_new("https://accounts.spotify.com/authorize?client_id=%s"
		"&redirect_uri=%s&scope=%s&response_type=token" % (
			quote(CLIENT_ID), quote(REDIRECT_URI), 
			quote(REQUIRED_SCOPES_JOINED)))

	# Wait until __ACCESS_TOKEN is set
	__AUTH_EVENT.wait()

	server.stop()

	__AUTH_LOCK.release()

	return __ACCESS_TOKEN, __EXPIRES_IN


	

@__BOTTLE_APP.route("/callback/")
def __auth_callback():	
	return CALLBACK_HTML


@__BOTTLE_APP.route("/ajax-callback/")
def __ajax_callback():
	global __ACCESS_TOKEN
	global __EXPIRES_IN

	decoded_query = request.query.decode()
	
	params = {}
	for item in decoded_query:
		params[item] = decoded_query[item]

	if "access_token" in params:
		__ACCESS_TOKEN = params["access_token"]
		__EXPIRES_IN = int(params["expires_in"])
		
		__AUTH_EVENT.set()

		response.status = 200
	else:
		response.status = 400

	return None

