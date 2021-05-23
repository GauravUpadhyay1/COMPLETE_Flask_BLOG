from typing import Mapping
from flask import Flask, render_template, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import json
from datetime import datetime, date
from werkzeug import secure_filename
import os
import math


# reading json
with open("config.json", "r") as c:
    params = json.load(c)["params"]


local_server = True
app = Flask(__name__)
app.secret_key = "gaurav4u77"

app.config['UPLOAD_FOLDER'] = params['upload_location']
# smtp
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-pass'],
)
mail = Mail(app)

# app.config['WHOOSH_BASE'] = 'WHOOSH'

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']

else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
db = SQLAlchemy(app)


# classes


class Contact(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(50), nullable=True)


class Subscription(db.Model):
    email = db.Column(db.String(50), primary_key=True)
    date = db.Column(db.String(50), nullable=True)


class Posts(db.Model):
    # __searchable__ = ['tagline', 'content']

    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(50), nullable=False)
    tagline = db.Column(db.String(1000), nullable=False)
    content = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(20), nullable=True)
    writer_img = db.Column(db.String(20), nullable=True)
    post_right_img = db.Column(db.String(20), nullable=True)
    post_bg_img = db.Column(db.String(20), nullable=True)
    title = db.Column(db.String(500), nullable=True)
    paragraph2 = db.Column(db.String(20), nullable=True)
    praisecomment = db.Column(db.String(500), nullable=True)
    praisername = db.Column(db.String(50), nullable=True)
    fromwriter = db.Column(db.String(200), nullable=True)


# wa.whoosh_index(app, Posts)


class Comments(db.Model):
    id_no = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(50), nullable=False)
    useremail = db.Column(db.String(50), nullable=True)
    usercomment = db.Column(db.String(500), nullable=False)
    commentdate = db.Column(db.String(500), nullable=False)


class About(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    about_us_content = db.Column(db.String(1000), nullable=True)
    about_img = db.Column(db.String(20), nullable=True)


class Developers(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    developer_name = db.Column(db.String(40), nullable=True)
    developer_email = db.Column(db.String(40), primary_key=True)
    developer_content = db.Column(db.String(1000), nullable=True)
    developer_img = db.Column(db.String(20), nullable=True)
    developer_img_right = db.Column(db.String(20), nullable=True)
    dev_slug = db.Column(db.String(20), nullable=False)

# routes and functions


@app.route('/')
def home():
    posts = Posts.query.filter_by().all()[0:params['no_of_posts']]
    return render_template('index.html', posts=posts)


@app.route('/blog')
def blog():
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts)/int(params['no_of_posts_blog_page']))
    page = request.args.get('page')

    if(not str(page).isnumeric()):
        page = 1
    page = int(page)
    posts = posts[(page-1)*int(params['no_of_posts_blog_page']): (page-1) *
                  int(params['no_of_posts_blog_page'])+int(params['no_of_posts_blog_page'])]
    if (page == 1):
        prev = "#"
        next = "?page=" + str(page+1)

    elif (page == last):
        next = "#"
        prev = "?page=" + str(page-1)

    else:
        next = "?page=" + str(page+1)
        prev = "?page=" + str(page-1)
    # posts = Posts.query.filter_by().all()[0:params['no_of_posts_blog_page']]
    return render_template('blog.html', posts=posts, params=params, prev=prev, next=next)


# @app.route('/post/<string:post_slug>', methods=['GET'])
# def post_routes(post_slug):
#     post = Posts.query.filter_by(slug=post_slug).first()
#     return render_template('post.html', params=params, post=post)

@app.route('/developerdetails/<string:dev_slug>')
def developerdetails(dev_slug):
    developers = Developers.query.filter_by(dev_slug=dev_slug).first()
    return render_template('developerdetails.html', developers=developers)


@app.route('/post/<int:post_id>/<string:post_slug>', methods=['GET', "POST"])
def post_route(post_id, post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    posts = Posts.query.filter_by().all()[0:params['no_of_posts_blog_page']]
    comments = Comments.query.filter_by(post_id=post.sno).all()[
        0:params['no_of_comments']]

    if(request.method == 'POST'):
        username = request.form.get('username')
        useremail = request.form.get('useremail')
        usercomment = request.form.get('usercomment')
        commentdate = date.today()
        # post_id = post.sno
        entry = Comments(username=username, useremail=useremail,
                         usercomment=usercomment, commentdate=commentdate, post_id=post.sno)
        db.session.add(entry)
        db.session.commit()

    return render_template('post.html', params=params, post=post, comments=comments, posts=posts)


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if (request.method == 'POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        entry = Contact(name=name, email=email, subject=subject,
                        message=message, date=datetime.now())
        db.session.add(entry)
        db.session.commit()
        mail.send_message('A new message for The Digital Templo from ' + name,
                          sender=email, recipients=[params['gmail-user']], body=message+'\n' + email)
    return render_template('contact.html', params=params)


@app.route("/", methods=['GET', 'POST'])
def subscription():
    if (request.method == 'POST'):
        email = request.form.get('email')

        entry = Subscription(email=email, date=datetime.now())
        db.session.add(entry)
        db.session.commit()
        mail.send_message('A new subscription for The Digital Templo by ' + email,
                          sender=email, recipients=[params['gmail-user']])

    return render_template('index.html', params=params)


@app.route("/about", methods=['GET', 'POST'])
def about():
    about = About.query.filter_by().all()
    return render_template('about.html', about=about)


@app.route("/developers")
def developers():
    developers = Developers.query.filter_by().all()
    return render_template('developers.html', developers=developers)


@ app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    if ('user' in session and session['user'] == params['username']):
        if (request.method == 'POST'):
            f = request.files['file1']
            f.save(os.path.join(
                app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            return "UPLOADED SUCCESSFULLY"


@app.route("/faq")
def faq():
    return render_template("faq.html")


# @app.route("/search", methods=['GET'])
# def search():
#     posts = Posts.query.whoosh_search(request.args.get('Query')).all()
#     return render_template("index.html", posts=posts)


@app.route("/admin", methods=['GET', 'POST'])
def admin():
    if('user' in session and session['user'] == params['username']):
        posts = Posts.query.all()
        return render_template("adminhome.html", posts=posts, params=params)

    if request.method == 'POST':
        username = request.form.get('uname')
        password = request.form.get('pass')
        if (username == params['username'] and password == params['password']):
            session['user'] = username
            posts = Posts.query.all()
            return render_template("adminhome.html", posts=posts, params=params)
    return render_template("login.html", params=params)

    # posts = Posts.query.all()


@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/')


@app.route('/edit/<string:sno>', methods=['GET', 'POST'])
def edit(sno):
    if('user' in session and session['user'] == params['username']):
        if request.method == 'POST':
            writersname = request.form.get('writersname')
            postslug = request.form.get('slug')
            writersimage = request.form.get('writersimage')
            backgroundimage = request.form.get('backgroundimage')
            rightimage = request.form.get('rightimage')
            date = request.form.get('date')
            tagline = request.form.get('tagline')
            content = request.form.get('content')

            if sno == '0':
                post = Posts(name=writersname, tagline=tagline, content=content, slug=postslug, date=date,
                             writer_img=writersimage, post_right_img=rightimage, post_bg_img=backgroundimage)

                db.session.add(post)
                db.session.commit()

            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.name = writersname
                post.tagline = tagline
                post.content = content
                post.slug = postslug
                post.date = date
                post.writer_img = writersimage
                post.post_right_img = rightimage
                post.post_bg_img = backgroundimage
                db.session.commit()
                return redirect('/edit/' + sno)

        post = Posts.query.filter_by(sno=sno).first()
        return render_template('editpost.html', params=params, post=post, sno=sno)


@app.route('/delete/<string:sno>', methods=['GET', 'POST'])
def delete(sno):
    if('user' in session and session['user'] == params['username']):
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
        return redirect('/admin')


@app.route('/admindetails', methods=['GET', 'POST'])
def admindetails():
    if('user' in session and session['user'] == params['username']):
        developers = Developers.query.all()
        return render_template('admindetails.html', params=params, developers=developers)


@app.route('/editdeveloper/<string:sno>', methods=['GET', 'POST'])
def editdeveloper(sno):
    if('user' in session and session['user'] == params['username']):
        if request.method == 'POST':
            developername = request.form.get('developername')
            developeremail = request.form.get('developeremail')
            developerimage = request.form.get('developerimage')
            developerrightimage = request.form.get('developerrightimage')
            developerslug = request.form.get('developerslug')
            developercontent = request.form.get('developercontent')

            if sno == '0':
                developers = Developers(developer_name=developername, developer_email=developeremail, developer_content=developercontent, dev_slug=developerslug,
                                        developer_img=developerimage, developer_img_right=developerrightimage)

                db.session.add(developers)
                db.session.commit()

            else:
                developers = Developers.query.filter_by(sno=sno).first()
                developers.developer_name = developername
                developers.developer_email = developeremail
                developers.developer_content = developercontent
                developers.dev_slug = developerslug
                developers.developer_img_right = developerrightimage
                developers.developer_img = developerimage
                db.session.commit()
                return redirect('/editdeveloper/' + sno)

        developers = Developers.query.filter_by(sno=sno).first()
        return render_template('editdeveloper.html', params=params, developers=developers, sno=sno)


@app.route('/deletedeveloper/<string:sno>', methods=['GET', 'POST'])
def deletedeveloper(sno):
    if('user' in session and session['user'] == params['username']):
        developers = Developers.query.filter_by(sno=sno).first()
        db.session.delete(developers)
        db.session.commit()
        return redirect('/admindetails')


app.run(debug=True)
