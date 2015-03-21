from flask.ext.wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired


class LoginForm(Form):
    openid = StringField('Query', validators=[DataRequired()])
    remember_me = BooleanField('remember_query', default=False)
