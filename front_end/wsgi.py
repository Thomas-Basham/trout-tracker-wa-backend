from main import app
import os
from werkzeug.serving import run_simple

if __name__ == "__main__":
  if os.environ['ENVIRONMENT'] and os.environ['ENVIRONMENT'] == 'testing':
    os.environ['FLASK_APP'] = 'wsgi.py'
    print('TESTING ENVIRONMENT')
    run_simple('localhost', 5000, app, use_reloader=True, use_debugger=True, reloader_type="stat")

  else:
    print('PROD ENVIRONMENT')
    app.run(debug=False)
