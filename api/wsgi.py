import os
from werkzeug.serving import run_simple
from api.main import app
if __name__ == "__main__":

    if os.getenv('ENVIRONMENT') and os.getenv('ENVIRONMENT') != 'production':
        print('TESTING ENVIRONMENT')

        run_simple('localhost', 5050, app, use_reloader=True,
                   use_debugger=True, reloader_type="stat")

    else:
        print('PROD ENVIRONMENT')
        app.run(debug=False)
