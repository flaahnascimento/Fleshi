from flask import render_template, url_for
from flask_login import login_required

from appfleshi import app

@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/profile/<username>') #rota dinamica
@login_required # rota protegida, so acessa logado
def profile(username):
    return render_template('profile.html', username=username)