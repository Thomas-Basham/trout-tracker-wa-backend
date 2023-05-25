from front_end.main import app
import os
from werkzeug.serving import run_simple

if __name__ == "__main__":

  os.environ['FLASK_APP'] = 'wsgi.py'

  if os.getenv('ENVIRONMENT') and os.getenv('ENVIRONMENT') != 'production':
    print('TESTING ENVIRONMENT')

    run_simple('localhost', 5000, app, use_reloader=True, use_debugger=True, reloader_type="stat")

  else:
    print('PROD ENVIRONMENT')
    app.run(debug=False)
