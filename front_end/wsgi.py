from main import app
import os

if __name__ == "__main__":
  os.environ['FLASK_APP'] = 'wisgi.py'
  app.run()
