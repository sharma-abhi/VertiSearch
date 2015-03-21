
from flask import Flask

app = Flask(__name__)
app.config.from_object('config')

# avoiding circular reference error, placing import below.
from app import views

