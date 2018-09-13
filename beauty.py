#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, flash, redirect, url_for, \
    session, request, logging
from data import Articles
from flaskext.mysql import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, \
    validators
from passlib.hash import sha256_crypt
from functools import wraps

# init Mysql

mysql = MySQL()

app = Flask(__name__, static_url_path='/public')

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'thaothui'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

Articles = Articles()


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/articles')
def articles():
    return render_template('articles.html', articles=Articles)


@app.route('/articles/<string:id>/')
def article(id):
    return render_template('single.html', id=id)


class RegisterForm(Form):

    name = StringField('Name', [validators.Length(min=3, max=50)])
    username = StringField('Username', [validators.Length(min=3,
                           max=25)])
    email = StringField('Email', [validators.Length(min=3, max=50)])
    password = PasswordField('Password', [validators.DataRequired(),
                             validators.EqualTo('confirm',
                             message='M\xe1\xba\xadt kh\xe1\xba\xa9u kh\xc3\xb4ng tr\xc3\xb9ng'
                             )])
    confirm = PasswordField('Confirm Password')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.hash(str(form.password.data))
        print(password)

        # create cursor
        # cur = mysql.connect().cursor()

        cur = mysql.get_db().cursor()

        # execute query

        cur.execute('INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s);'
                    , (name, email, username, password))

        # commit to db

        mysql.get_db().commit()

        # mysql.connect().commit()
        # close db

        cur.close()

        flash('You are now registered and can log in', 'success')

        redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        username = request.form['username']
        password_candidate = request.form['password']

        # create cursor

        cur = mysql.get_db().cursor()

        # get user by username

        result = cur.execute('SELECT * FROM users WHERE username = %s '
                             , [username])
        if result > 0:

            data = cur.fetchone()
            password = data[4]
            print (password)

            if sha256_crypt.verify(password_candidate, password):
                app.logger.info('PASSWORD MATCHED')
                session['logged_in'] = True
                session['username'] = username

                flash("You're now logged in!", 'success')
                return redirect(url_for('dashboard'))
            else:
                app.logger.info('PASSWORD NOT MATCH!')
                return render_template('login.html')
        else:
            err = 'Invalid login'
            return render_template('login.html', err=err)

    return render_template('login.html')


# check if user logged in

def is_logged_in(f):

    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You are not logged in', 'danger')
            return redirect(url_for('login'))
    return wrap


# logout

@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out!', 'success')
    return redirect(url_for('login'))


@app.route('/dashboard')
@is_logged_in
def dashboard():

        # create cursor

    cur = mysql.get_db().cursor()

        # execute query

    result = cur.execute('SELECT * FROM articles')

    articles = cur.fetchall()

    if result > 0:
        return render_template('dashboard.html', articles=articles)
    else:
        msg = 'NO ARTICLE FOUND'
        return render_template('dashboard.html', msg=msg)

        # close db

    cur.close()


# Article form class

class ArticleForm(Form):

    title = StringField('Title', [validators.Length(min=3, max=200)])
    body = TextAreaField('Body', [validators.Length(min=30)])


# add Article

@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data
        author = session['username']

        # create cursor

        cur = mysql.get_db().cursor()

        # execute query

        cur.execute('INSERT INTO articles(title, author, body) VALUES(%s, %s, %s);'
                    , (title, author, body))

        # cur.execute("INSERT INTO articles(title, body, username, password) VALUES(%s, %s, %s, %s);", (name, email, username, password))
        # commit to db

        mysql.get_db().commit()

        # close db

        cur.close()

        flash('Article created', 'success')

        return redirect(url_for('dashboard'))
    return render_template('add_article.html', form=form)


# edit Article

@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article():

    # create cursor

    cur = mysql.get_db().cursor()

    # get article by id

    id = request.args.get('id')
    print(id)

    # result = cur.execute("SELECT * FROM articles WHERE id = %s", id)

    article = cur.fetchone()

    # get form

    form = ArticleForm(request.form)

    # populate article form fields

    form.title.data = article['title']
    form.body.data = article['body']

    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data
        author = session['username']

        # create cursor

        cur = mysql.get_db().cursor()

        # execute query

        cur.execute('UPDATE articles SET name= %s, body=%s WHERE id = %s'
                    , (author, body, id))

        # commit to db

        mysql.get_db().commit()

        # close db

        cur.close()

        flash('Article updated', 'success')

        return redirect(url_for('dashboard'))
    return render_template('edit_article.html', form=form)

if __name__ == '__main__':
    app.secret_key = 'thaothui'
    app.run(host='0.0.0.0', debug=True)
