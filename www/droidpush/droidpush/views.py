# -*- coding: utf-8 -*-
"""
    Droidpush
    ~~~~~~

    Pushing it to droid since 2012

    :copyright: (c) 2012 by Andrew Edwards
"""
from __future__ import with_statement
from droidpush import app
from contextlib import closing
from mongokit import *
from flaskext.gravatar import Gravatar
from flaskext.login import LoginManager, login_user, login_required, \
    current_user, logout_user
from datetime import datetime
import re
import hashlib
import logging
from models import *
from forms import *
from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify

# configuration
MONGODB_DATABASE = 'droidpush'
MONGODB_HOST = '127.0.0.1'
DEBUG = True
SECRET_KEY = 'kçfsdf*عربي*v*&$) رئيسرسّ+==H$&maLk?$عرewبي#1 and there it is'

# create the app
app.config.from_object(__name__)
app.config.from_envvar('DROIDPUSH_SETTINGS', silent=True)

# setup logging
#logging.basicConfig(filename='droidpush.log',level=logging.DEBUG)

# setup loginmanager
login_manager = LoginManager()
login_manager.setup_app(app)

# create the db connection
db = Connection()
db.register([User,Apikey,Hit])

# setup gravatar
gravatar = Gravatar(app,
    size=100,
    rating='g',
    default='retro',
    force_default=False,
    force_lower=False)

@login_manager.user_loader
def load_user(userid):
    # load the user from the model
    user = User()
    if user.load_user(userid):
        return user
    else:
        return None

@app.route('/')
def home():
    return render_template('home.html', homeactive=True)

@app.route('/about')
def about():
    return render_template('about.html', aboutactive=True)

@app.route('/contact')
def contact():
    return render_template('contact.html', contactactive=True)

@app.route('/register', methods=['POST','GET'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = db.User()
        user.email = form.email.data
        salt_and_hash = hash_password(form.password.data)
        user.salt = salt_and_hash[0]
        user.password = salt_and_hash[1]
        user.save()

        # now, log the user in
        if user.validate_login(form.email.data,form.password.data):
            # login credentials all good, set the user (which has now been
            # populated with the user details)
            login_user(user)

            # we also need to create the default apikey too
            apikey = db.Apikey()
            apikey.key = apikey.random_key()
            apikey.userid = unicode(user.get_id())
            apikey.save()

            # all good, lets go to the dashboard with a flash
            flash('Your account has been created.')
            return redirect(url_for('dashboard'))

    return render_template('register.html', registeractive=True, form=form)

@app.route('/login', methods=['POST','GET'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        # Login user, check for remember me
        remember_me =  form.remember.data == 'y'
        user = form.get_user()
        login_user(user, remember=remember_me)
        return redirect(url_for('dashboard'))

    return render_template('login.html', loginactive=True, form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', dashboardactive=True)

@app.route('/apikeys')
@login_required
def apikeys():
    apikey = db.Apikey()
    apikeys = apikey.find_by_user(current_user.get_id())
    return render_template('apikeys.html', apikeysactive=True, apikeys=apikeys)

@app.route('/apikeys/create', methods=['POST','GET'])
@login_required
def apikeyscreate():
    form = ApikeyscreateForm(request.form)
    if request.method == 'POST' and form.validate():
        apikey = db.Apikey()
        apikey.name = form.name.data
        apikey.key = apikey.random_key()
        apikey.userid = unicode(current_user.get_id())
        apikey.save()

        # all good, lets go to the dashboard with a flash
        flash('Your apikey has been created.')
        return redirect(url_for('apikeys'))

    return render_template('apikeyscreate.html', form=form)

@app.route('/apikeys/delete/<id>')
@login_required
def apikeysdelete(id):
    apikey = db.Apikey()

    # we need to check that the apikey id belongs to this user
    key = apikey.user_has_access_to_apikey(unicode(current_user.get_id()), id)
    if key == None:
        flash('You do not have access to that apikey!')
        return redirect(url_for('apikeys'))

    # Check that this won't leave them without a apikey
    keys = apikey.find_by_user(unicode(current_user.get_id()))
    if keys.count() == 1:
        flash('You can\'t delete all your keys... else whats the point? You \
            need to keep at least one at all times.')
        return redirect(url_for('apikeys'))

    return render_template('apikeysdelete.html', name=key['name'], id=id)

@app.route('/apikeys/deleteconfirmed/<id>')
@login_required
def apikeysdeleteconfirmed(id):
    # we need to check that the apikey id belongs to this user
    apikey = db.Apikey()
    key = apikey.user_has_access_to_apikey(unicode(current_user.get_id()), id)

    if key == None:
        flash('You do not have access to that apikey!')
        return redirect(url_for('apikeys'))

    apikey.delete(id)
    flash('The apikey has been deleted')

    return redirect(url_for('apikeys'))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('home'))

@app.route('/hit/me/<id>', methods=['POST','GET'])
@login_required
def hitcreate(id):
    # TODO need to parse the querystring, etc.
    user_agent = 'Linux, Chrome'
    ip = '127.0.0.1'
    minute = 201203221728
    apikey = 'HAD7LPACVVA4VAAARVX756UKKLCZVF9F'

    hit = db.Hit()
    apikey = hit.get_userid_from_apikey(apikey)
    if apikey == None:
        return "image failed"

    userid = apikey['userid']

    hit.userid = unicode(userid)
    hit.md5 = hashlib.md5(user_agent + ip).hexdigest()
    hit.minute = hit.getminute()
    hit.ip = ip

    return "good image"
    # form = HitscreateForm(request.form)
    # if request.method == 'POST' and form.validate():
    #     # message = db.Message()
    #     # message.level = form.level.data
    #     # message.heading = form.heading.data
    #     # message.blurb = form.blurb.data
    #     # message.body = form.body.data
    #     # message.userid = unicode(current_user.get_id())
    #     # message.apikeyid = unicode(form.apikeyid.data)
    #     # message.save()

    #     # all good, lets go to the dashboard with a flash
    #     flash('Your hit has been created.')
    #     return redirect(url_for('dashboard'))

    # return render_template('hitcreate.html', form=form)

@app.route("/services")
def services():
    return render_template('services.html', servicesactive=True)
