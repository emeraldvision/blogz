from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:BlogBuild@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'K5_e55@-P^-cHXc9'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    body = db.Column(db.String(1000000))
    
    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/', methods=['GET', 'POST'])
def index():
    return redirect('/blog', code=307)

@app.route('/blog', methods=['GET', 'POST'])
def main_display():

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        new_blog = Blog(blog_title, blog_body)
        db.session.add(new_blog)
        db.session.commit()

    blog_posts = Blog.query.all()
    return render_template('blog.html', posts=blog_posts)

@app.route('/newpost', methods=['GET'])
def new_post():
    return render_template('newpost.html')


if __name__ == '__main__':
    app.run()