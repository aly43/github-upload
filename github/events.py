import time
import os
from hashlib import md5
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash, _app_ctx_stack
from werkzeug.security import check_password_hash, generate_password_hash

from models import db, User, Event

app = Flask(__name__)

# configuration
PER_PAGE = 30
DEBUG = True
SECRET_KEY = 'development key'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'events.db')

app.config.from_object(__name__)
app.config.from_envvar('MINITWIT_SETTINGS', silent=True)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #here to silence deprecation warning

db.init_app(app) # initialize app with app

#initialize database
@app.cli.command('initdb')
def initdb_command():
        db.create_all()

def get_user_id(username):
        rv = User.query.filter_by(username=username).first()
        return rv.user_id if rv else None

def get_event_id(event):
        rv = Event.query.filter_by(event_title=event).first()
        return rv.event_id if rv else None

def format_datetime(timestamp):
        return timestamp

@app.before_request
def check_session():
        g.user = None
        if 'user_id' in session:
                g.user = User.query.filter_by(user_id=session['user_id']).first()

@app.route("/")
def homepage():
#this is the hompage
        #events = Event.query.order_by(Event.start_date.desc()).all()
        #print('printing out events')
        #print(events)
        if not g.user:
                return redirect(url_for('public_homepage'))

        print("past redirect")

        #events = Event.query.order_by(Event.start_date.desc()).limit(PER_PAGE).all()
        return redirect(url_for('user_homepage', username=g.user.username))

@app.route('/public')
def public_homepage():
        print('public homepgae')
        print(Event.query.order_by(Event.start_date.desc()).all())
        return render_template('homepage.html', events=Event.query.order_by(Event.start_date.desc()).all())

@app.route("/<username>")
def user_homepage(username):
        print('user homepage')
        profile_user =User.query.filter_by(user_id=get_user_id(username)).first()
        if profile_user is None:
                abort(404)
        if g.user:
                print('putting events into host')
                u = User.query.filter_by(username=profile_user.username).first()
                hosted = u.hosts.order_by(Event.start_date.desc()).all()
                print(u.hosts)
        events=Event.query.order_by(Event.start_date.desc()).all()
        print('rendering homepage')
        return render_template('homepage.html', events=events, hosted=hosted, profile_user=profile_user)

@app.route('/<username>/<event>/cancel', methods=["GET", "POST"])
def remove_event(username, event):
        #removes the given event from the list of all events is user is host. 
        if not g.user:
                abort(401)
        event_ids = get_event_id(event)
        user_ids=get_user_id(username)

        user = User.query.filter_by(user_id=user_ids).first()
        event1 = Event.query.filter_by(event_id=event_ids).first()
                
        if request.method:
                user.hosts.remove(event1)
                db.session.commit()
                flash('The "%s" event has been deleted' % event)
                return redirect(url_for('user_homepage', username))

        return render_template('eventCancel.html')

@app.route('/<user>/create', methods=["GET", "POST"])
def create_event(user):
        profile_user = User.query.filter_by(user_id=get_user_id(user)).first()
        if not g.user:
                abort(401)
        error=None
        if request.method == 'POST':
                if not request.form['name']:
                        error = 'Enter a name'
                elif not request.form['start']:
                        error = 'Enter a start date'
                elif not request.form['end']:
                        error = 'Enter an end date'
                else:
                        print(profile_user)
                        new = Event(session['user_id'], request.form['name'], request.form['description'], datetime.strptime(request.form['start'], "%m/%d/%Y %X"), datetime.strptime(request.form['end'], "%m/%d/%Y %X"))
                        db.session.add(new)
                        #db.session.commit()
                        print(new.event_id)
                        profile_user.hosts.append(new)
                        print(new.event_id)
                        print(new.user_id)
                        #new.host=profile_user.user_id
                        new.host=profile_user
                        print(new.event_id)
                        print(profile_user)
                        db.session.commit()
                       # print(new.host.username)
                        #print(new.host)
                        flash('New entry was successfully posted')
                        return redirect(url_for('homepage'))
        return render_template('eventCreate.html', error=error)

@app.route('/<username>/<event>/attend')
def attend_event(username,event):
        if not g.user:
                abort(401)
        user_ids = get_user_id(username)
        if user_ids is None:
                abort(404)
        event_ids=get_event_id(event)
        if event_ids is None:
                abort(404)

        user = User.query.filter_by(user_id=user_ids).first()
        events = Event.query.filter_by(event_id=event_ids).first()
        print('printing user.hosts')
        print(user.hosts)
        if events.host is username:
                flash('You are already the host of this event')
                return redirect(url_for('user_homepage', username=username))
        print('printing user.attends')
        print(user.attends)
        if user.username in user.attends:
                flash('You are already attending this event')
                return redirect(url_for('user_homepage', username=username))
        
        user.attends.append(events)
        db.session.commit()

        flash('You are now attending this event: %s' % event)
        return redirect(url_for('user_homepage', username=username))
         
@app.route('/login/', methods=["GET", "POST"])
def login():
        if g.user:
                return redirect(url_for('homepage'))
	
        error = None
        if request.method == 'POST':
                
                user = User.query.filter_by(username=request.form['username']).first()
                if user is None:
                        error = 'Invalid username'
                elif not check_password_hash(user.pw_hash, request.form['password']):
                        error = 'Invalid password'
                else:
                        flash('You were logged in')
                        session['user_id'] = user.user_id
                        #session['username'] = user.user_id
                        print('login success')
                        return redirect(url_for('user_homepage', username=user.username))
        return render_template('userLog.html', error=error)

@app.route('/register/', methods=["GET", "POST"])
def register():
        if g.user:
               return redirect(url_for('user_homepage'))
        error = None
        print('register')
        if request.method == 'POST':
                if not request.form['username']:
                        error = 'You have to enter a username'
                elif not request.form['password']:
                        error = 'You have to enter a password'
                elif request.form['password'] != request.form['password2']:
                        error = 'The two passwords do not match'
                elif get_user_id(request.form['username']) is not None:
                        error = 'The username is already taken'
                else:
                        db.session.add(User(request.form['username'], generate_password_hash(request.form['password'])))
                        db.session.commit()
                        flash('You were successfully registered and can login now')
                        return redirect(url_for('login'))
        return render_template('userReg.html', error = error)

@app.route("/logout/")
def logout():
	# if logged in, log out, otherwise offer to log in
	if g.user:
		# note, here were calling the .clear() method for the python dictionary builtin
		session.clear()
		return redirect(url_for('homepage'))
	else:
		return redirect(url_for("login"))

app.jinja_env.filters['datetimeformat'] = format_datetime

if __name__ == "__main__":
	app.run()
