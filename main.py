from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash

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

@app.before_request
def require_login():
    allowed_routes = ['login', 'display_blogs', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/', methods=['GET', 'POST'])
def index():
    users = User.query.all()
    return render_template('index.html', page_title="Blog Users", users=users)


@app.route('/blog', methods=['GET', 'POST'])
def display_blogs():

    if request.method == 'POST':
        blog_title = blog_body = ''
        blog_title = request.form['title']
        blog_body = request.form['body']
        blog_author = User.query.filter_by(username=session['username']).first()
        if blog_title and blog_title.strip() and blog_body and blog_body.strip():
            new_blog = Blog(blog_title, blog_body, blog_author)
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    username = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username:
            flash("Please provide your username")
        elif not password:
            flash("Please provide your password")
        else:
            user = User.query.filter_by(username=username).first()
            if not user:
                flash("Username is unregistered")
            elif check_pw_hash(password, user.pw_hash):
                session['username'] = username
                flash("{0} is logged in".format(username))
                return redirect('/newpost')
            else:
                flash("Incorrect password")

    return render_template('login.html', page_title="Login", username=username)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    username = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        if username and password and verify:
            if len(username) < 3:
                flash("Username must be at least 3 characters")
            elif len(password) < 3:
                flash("Password must be at least 3 characters")
            elif User.query.filter_by(username=username).first():
                flash("The username {0} is already in use".format(username))
            elif password != verify:
                flash("Password and confirmation did not match")
            else:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                flash("{0} is logged in".format(username))
                return redirect('/newpost')
        else:
            flash("Please provide a username, password, and password confirmation")
    
    return render_template('signup.html', page_title="Signup")

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')


if __name__ == '__main__':
    app.run()