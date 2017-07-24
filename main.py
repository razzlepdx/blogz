from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from helpers import valid_input, verify_pass

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:RiseHowEverybody2@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "Kw74Jnx0pSsD86bc9"

class Blog(db.Model):
    ''' creates a database record for each blog post '''
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    body = db.Column(db.String(5000))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, author):
        self.title = title
        self.body = body
        self.author = author
    
    # TODO - add Blog helper functions to /newpost
    # def has_content(self):
    #     if self.title and self.content:
    #         return True
        
    #     return False

class User(db.Model):
    ''' creates a database record for each blog user '''
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(40))
    blogs = db.relationship('Blog', backref='author')

    def __init__(self, username, password):
        self.username = username
        self.password = password
        



# TODO:
# - add 3 new templates: *signup.html, *login.html, **index.html
# - add singleUser.html to display only blogs associated with a particular author
# - add logout function that: a) handles a post request to /logout, b) redirects user to /blog after deleting username from session


# requires user to login for particular routes
@app.before_request
def require_login():
    allowed_routes = ['login', 'index', 'signup']
    print(session)
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route("/blog", methods=['GET'])
def index():
    # check for query parameters, indicating a single post needs to be displayed
    # assign any id params to a variable
    blog_id = request.args.get('id')
    if blog_id:
        single_post = Blog.query.filter_by(id = blog_id).all()
        #render blog template with contents of the single post only
        return render_template('main.html', pagetitle ="Blog Posts", mainheader = single_post[0].title, blogs = single_post)

    # otherwise, display all blog posts    
    blogs = Blog.query.all()
    mainheader = "Hi there - welcome to my blog!"
    return render_template('main.html', pagetitle = "Blog Posts", mainheader = mainheader, blogs = blogs)

@app.route("/login", methods=['GET','POST'])
def login():
    #TODO - check that validation is working
    if request.method == 'POST':
        print("This function is running!")
        username = request.form['username']
        password = request.form['password']
        user_login = User.query.filter_by(username=username).first()
        # check for existing username and password, then redirect to /newpost
        if user_login and user_login.password == password:
            session['username'] = username
            return redirect('/newpost')
        # otherwise, display error message    
        # flash('The username or password you entered did not match our system, please try again', 'error')
        print('error!')
    return render_template('login.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        # user inputs submitted through the signup form
        username = request.form['username']
        password = request.form['pass1']
        verify = request.form['pass2']
        
        # if username exists in the db, assign it to this variable
        existing_user = User.query.filter_by(username = username).first()
        # increment this variable to check for errors on page during user validation
        total_errors = 0

        # Validate the information submitted and generate error messages
        if username == '' or password == '' or verify == '':
            # flash('Sorry, one or more fields are invalid.  A username, password, and password verification are required.', 'error')
            total_errors += 1
        if valid_input(username) == False:
            # flash('Sorry, that username won\'t work!  Please enter a username between 3 and 40 characters, with no spaces.', 'error')
            total_errors += 1
        if valid_input(password) == False:
            # flash('Sorry, that password won\'t work!  Please enter a password between 3 and 40 characters, with no spaces.', 'error')
            total_errors += 1    
        if verify_pass(password, verify) == False:
            # flash('These passwords don\'t match!  Please enter your passwords again.', 'error')
            total_errors += 1
        if existing_user:
            # flash('This username is already taken. If you would like to sign in as this user, click <a href=\'/login\'>here.</a>', 'error')
            total_errors += 1
        
        # if error messages are generated, re-render the signup form to display messages
        if total_errors > 0:
            return render_template('signup.html')

        # if validation passes with 0 errors, update the db with the new user information
        if total_errors == 0:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()

            # add username to session and redirect to /newpost
            session['username']= username
            return redirect('/newpost')


    return render_template('signup.html')

@app.route('/newpost', methods = ['GET', 'POST'])
def new_post():

    if request.method == 'POST':

        blog_title = request.form['title']
        blog_content = request.form['blogpost']  
        author_id = User.query.filter_by(username=session['username']).first()
        
        # new post error validation starts here - both fields on form must be filled in

        if blog_title == '' or blog_content == '':
            if blog_title == '':
                flash("Please enter a title for this blog post!", 'error')
            if blog_content == '':
                flash("Please add content to the body of your post!", 'error')
            # return new post template with error messages 
            return render_template('newpost.html', pagetitle="Add a Blog Post", title = blog_title, blogpost = blog_content)
        
        # if no errors, then assign information and update db
        new_post = Blog(blog_title, blog_content, author_id)
        db.session.add(new_post)
        db.session.commit()  
        
        # after db update, redirect user to main page, but display only the newly created post
        return redirect('/blog?id=' + str(new_post.id))

    # in the case of a get request, render an empty new post template     
    return render_template('newpost.html', pagetitle = "Add a Blog Post")  


if __name__ == '__main__':
    app.run()