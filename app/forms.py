from flask.ext.wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired

# login class for user query
class LoginForm(Form):
    openid = StringField('Query', validators=[DataRequired()])
    remember_me = BooleanField('remember_query', default=False)
    prev_set = set()
