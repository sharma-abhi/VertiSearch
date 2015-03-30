from flask.ext.wtf import Form
from wtforms import BooleanField, SelectField
from wtforms.fields.html5 import SearchField
from wtforms.validators import DataRequired


# login class for user query
class LoginForm(Form):
    openid = SearchField('query', validators=[DataRequired()])
    remember_me = BooleanField('remember_query', default=False)
    prev_set = set()
    myChoices = [('10','10'), ('50', '50'), ('100','100')] # number of choices
    myField = SelectField('size', choices=myChoices)