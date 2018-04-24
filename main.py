from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogzdatabaze@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '/YUBknN{Y~+wfc&('


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    body = db.Column(db.String(1000000))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, title, body, author):
        self.title = title
        self.body = body
        self.author = author

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(255))
    blogs = db.relationship('Blog', backref="author")

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)

@app.route('/', methods=['GET', 'POST'])
def index():
    return redirect('/blog', code=307)

@app.route('/blog', methods=['GET', 'POST'])
def blog():

    if request.method == 'POST':
        blog_title = blog_body = ''
        blog_title = request.form['title']
        blog_body = request.form['body']
        if blog_title and blog_title.strip() and blog_body and blog_body.strip():
            new_blog = Blog(blog_title, blog_body)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id=' + str(new_blog.id))
        else:
            if not blog_title or not blog_title.strip():
                flash("The post needs a title")
            if not blog_body or not blog_title.strip():
                flash("The post body can't be empty")
            return render_template('newpost.html', page_title="Add a Blog", blog_title=blog_title, blog_body=blog_body)

    blog_id_str = (request.args.get('id'))
    if blog_id_str:
        blog_id = int(blog_id_str)
        current_blog = Blog.query.get(blog_id)
        if current_blog:
            return render_template('singlepost.html', page_title=current_blog.title, blog_body=current_blog.body)
        flash("That blog post cannot be found")

    blog_posts = Blog.query.order_by(Blog.id.desc()).all()
    return render_template('blog.html', page_title="Build a Blog", posts=blog_posts)

@app.route('/newpost', methods=['GET'])
def newpost():
    return render_template('newpost.html', page_title="Add a Blog Entry")


if __name__ == '__main__':
    app.run()