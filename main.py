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

    blog_id = request.args.get('id')
    if blog_id:
        current_blog = Blog.query.filter_by(id=blog_id).first()
        if current_blog:
            return render_template('singlepost.html', page_title=current_blog.title, blog_body=current_blog.body)
        flash("That blog post cannot be found")

    blog_posts = Blog.query.all()
    return render_template('blog.html', page_title="Build a Blog", posts=blog_posts)

@app.route('/newpost', methods=['GET'])
def new_post():
    return render_template('newpost.html', page_title="Add a Blog Entry")


if __name__ == '__main__':
    app.run()