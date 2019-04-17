from functools import wraps
from hashlib import sha3_512

from flask import Flask, redirect, render_template, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, EqualTo

from news_table import DB, UsersModel, NewsModel, CommentsModel

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
salt = 'qhpuY$5oPh14'

db = DB()
user = UsersModel(db.get_connection())
news = NewsModel(db.get_connection())
com = CommentsModel(db.get_connection())


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired(),
                                                   EqualTo('confirm_password',
                                                           message='Passwords must match')
                                                   ])
    confirm_password = PasswordField('Повторите пароль')
    submit = SubmitField('Войти')


class AddNewsForm(FlaskForm):
    title = StringField('Заголовок новости', validators=[DataRequired()])
    content = TextAreaField('Текст новости', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class AddComForm(FlaskForm):
    content = TextAreaField('Текст комментария', validators=[DataRequired()])
    submit = SubmitField('Добавить')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect('/login')
        return f(*args, **kwargs)

    return decorated_function


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():

        user_name = form.username.data
        password = sha3_512((str(form.password.data) + salt).encode()).hexdigest()
        exists = user.exists(user_name, password)
        if exists[0]:
            session['username'] = user_name
            session['user_id'] = exists[1]
        return redirect("/index")

    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
def logout():
    session.pop('username', 0)
    session.pop('user_id', 0)
    return redirect('/login')


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        user_name = form.username.data
        password = sha3_512((str(form.password.data) + salt).encode()).hexdigest()
        user.insert(user_name, password)
        return redirect("/login")

    return render_template('registration.html', title='Регистрация', form=form)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('main.html', title='Последние новости', news=news.get_all(last=True),
                           user_id=session['user_id'], user=user)


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', title='Последние новости', news=news.get_all(user_id=session['user_id']))


@app.route('/add_news', methods=['GET', 'POST'])
@login_required
def add_question():
    form = AddNewsForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        news.insert(title, content, session['user_id'])
        return redirect("/index")
    return render_template('add_news.html', title='Добавление новости',
                           form=form, username=session['username'])


@app.route('/add_com/<int:news_id>', methods=['GET', 'POST'])
@login_required
def add_comment(news_id):
    form = AddComForm()

    nm = news.get_one(news_id)

    news_info = {
        'title': nm[1],
        'content': nm[2],
        'user': user.get(nm[4])[1]
    }
    if form.validate_on_submit():
        content = form.content
        com.insert(nm[0], session['user_id'], content.data)
        return redirect(f'/view_com/{news_id}')
    return render_template('add_comment.html', title='Добавление комментария',
                           form=form, username=session['username'], news=news_info)


@app.route('/view_com/<int:news_id>', methods=['GET', 'POST'])
@login_required
def view_com(news_id):
    nm = news.get_one(news_id)
    news_info = {
        'title': nm[1],
        'content': nm[2],
        'user': user.get(nm[4])[1]
    }
    return render_template('view_comment.html', title='Комментарии', news=news_info, news_id=news_id,
                           com=com.get(post_id=news_id),
                           user_id=session['user_id'], user=user)


@app.route('/delete_news/<int:news_id>', methods=['GET'])
@login_required
def delete_news(news_id):
    if session['user_id'] == news.get_one(news_id)[4]:
        news.delete(news_id)
    return redirect("/index")


@app.route('/delete_com/<int:com_id>')
@login_required
def delete_com(com_id):
    info = com.get(com_id=com_id)[0]
    if session['user_id'] == info[2]:
        com.delete(com_id)
    return redirect(f'/view_com/{info[1]}')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
