from flask import render_template, flash, redirect
from app import app
from .forms import LoginForm
from computequery import Computequery
from flask import session

@app.route('/')
@app.route('/index')
def index():
    user = {"nickname": "Abhijeet"} # fake user
    return render_template('index.html', title='Home', user=user)

# index view function suppressed for brevity

@app.route('/query', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Query requested ="%s", remember_query=%s' %
              (form.openid.data, str(form.remember_me.data)))
        cq = Computequery()
        answers = cq.fetch_results(form.openid.data)
        print len(answers)
        #session['rest'] = answers
        #return redirect('/results', form=form)
        return render_template('results.html', title='Results', results=answers)
    return render_template('query.html', title='Search', form=form)

'''@app.route('/details', methods=['GET', 'POST'])
def details():
    answers = session['rest']
    return render_template('details.html', title='Results', results=answers)'''
