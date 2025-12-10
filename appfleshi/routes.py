from flask import render_template, url_for, redirect, flash, request
from flask_login import login_required, login_user, logout_user, current_user
from appfleshi.forms import LoginForm, RegisterForm, PhotoForm
from appfleshi import app, db, bcrypt
from appfleshi.models import User, Photo, Like, Comment, Repost
import os
from werkzeug.utils import secure_filename
from appfleshi import app

@app.route('/', methods=['GET', 'POST'])
def homepage():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, login_form.password.data):
            login_user(user)
            return redirect(url_for('feed', user_id=user.id))
    return render_template('homepage.html', form=login_form)

@app.route("/createaccount", methods=['GET', 'POST'])
def createaccount():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        password = bcrypt.generate_password_hash(register_form.password.data)
        user = User(username=register_form.username.data, password= password, email= register_form.email.data)
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=True)
        return redirect(url_for('profile', user_id=user.id)) # rota dinamica
    return render_template('createaccount.html', form=register_form)

@app.route("/profile/<user_id>", methods=['GET', 'POST'])
@login_required
def profile(user_id):
    if int(user_id) == int(current_user.id):
        photo_form = PhotoForm()
        if photo_form.validate_on_submit() and photo_form.photo.data:
            file = photo_form.photo.data
            secure_name = secure_filename(file.filename)
            path = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config["UPLOAD_FOLDER"], secure_name)
            file.save(path)
            photo = Photo(file_name=secure_name, user_id=current_user.id)
            db.session.add(photo)
            db.session.commit()
        return render_template('profile.html', user=current_user, form=photo_form)
    else:
        user = User.query.get(int(user_id))
        return render_template('profile.html', user=user, form=None)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('homepage'))

@app.route("/feed")
@login_required
def feed():
    photos = Photo.query.order_by(Photo.upload_date.desc()).all()
    return render_template('feed.html', photos=photos)

@app.route("/deletar_photo/<photo_id>")
@login_required
def delete_photo(photo_id):
    photo = Photo.query.get(photo_id) # busquei a foto pelo id
    if not photo: # se a foto nao existir
        return redirect(url_for('profile', user_id=current_user.id)) # volta para o perfil do usuario
    if photo.user_id != current_user.id: # se a foto for diferente do que usuario tem
        return redirect(url_for('profile', user_id=current_user.id)) # volta para o perfil do usuario
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config["UPLOAD_FOLDER"], photo.file_name)
    if os.path.exists(path): # se o caminho existir
        os.remove(path) # remove ela
    db.session.delete(photo) # apagar a foto
    db.session.commit() # certeza que apaguei
    return redirect(url_for('profile', user_id=current_user.id)) # volta para o perfil do usuario


@app.route("/like/<photo_id>")
@login_required
def like_photo(photo_id):
    photo = Photo.query.get(photo_id) # busquei a foto pelo id
    if not photo: # se a foto nao existir
        return redirect(url_for('profile', user_id=current_user.id)) # volta para seu perfil
    existe_like = Like.query.filter_by(user_id=current_user.id, photo_id=photo_id).first() # verifica se ja curtiu
    if existe_like: # se ja curtiu
        flash("Você já curtiu esta foto!", "info")
        return redirect(url_for('profile',  user_id=current_user.id)) # volta para seu perfil
    novo_like = Like(user_id=current_user.id, photo_id=photo_id) # novo like, se nunca curtiu
    db.session.add(novo_like) # sobe na sessao
    db.session.commit() # salva no banco
    return redirect(url_for('profile', user_id=current_user.id))

@app.route("/comment/<photo_id>", methods=['POST'])
@login_required
def comments_photo(photo_id):
    photo = Photo.query.get(photo_id)
    if not photo:  # se a foto nao existir
        return redirect(url_for('profile', user_id=current_user.id))
    text = request.form.get('text') # pegando o texto que o usuario escreveu no form
    if not text or text.strip() == "":
        flash("O comentário não pode estar vazio!", "warning")
        return redirect(url_for('profile', user_id=current_user.id))
    novo_comments = Comment (
        text=text.strip(), user_id=current_user.id, photo_id=photo_id
    )
    db.session.add(novo_comments)
    db.session.commit()
    return redirect(url_for('profile', user_id=current_user.id))

@app.route("/repost/<photo_id>")
@login_required
def repost_photo(photo_id):
    photo = Photo.query.get(photo_id) # busquei a foto pelo id
    if not photo: # se a foto nao existir
        return redirect(url_for('profile', user_id=current_user.id)) # volta para seu perfil
    existe_repost = Repost.query.filter_by(user_id=current_user.id, photo_id=photo_id).first()  # verifica se ja repostou essa foto
    if existe_repost:  # se ja repostou
        flash("Você já repostou esta foto!", "info")
        return redirect(url_for('profile', user_id=current_user.id))  # volta para seu perfil
    novo_repost = Repost(
        user_id=current_user.id, photo_id=photo_id, repost_id = photo_id
    )
    db.session.add(novo_repost)
    db.session.commit()
    return redirect(url_for('profile', user_id=current_user.id))






