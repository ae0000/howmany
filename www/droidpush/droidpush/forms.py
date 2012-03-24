from wtforms import Form, BooleanField, TextField, PasswordField, validators
from wtforms.validators import ValidationError
from flaskext.wtf.html5 import EmailField
from flaskext.mongokit import MongoKit
from droidpush import app
from droidpush.models import check_password, User
from flaskext.login import current_user
from mongokit import ObjectId

db = MongoKit(app)

def unique_email(form, field):
    # Check to see if this email already exists
    user_search = db.users.find_one({"email": field.data})
    if user_search != None:
        raise ValidationError('Looks like this email address is already registered')

class RegistrationForm(Form):
    email = EmailField('Email Address', [
        validators.Required(),
    	validators.Length(min=6, max=200),
    	validators.Email(),
        unique_email
    ])
    password = PasswordField('Password', [
    	validators.Required(),
        validators.Length(min=6, max=200),
    ])
    terms = BooleanField('Terms and conditions', [
    	validators.Required()
    ])

class LoginForm(Form):
    email = EmailField('Email Address', [
        validators.Required(),
        validators.Length(min=6, max=200),
        validators.Email()
    ])
    password = PasswordField('Password', [
        validators.Required(),
        validators.Length(min=6, max=200),
    ])
    remember = BooleanField('Remember me', [])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def get_user(self):
        return self.user

    def validate(self):
        # for login validation we need to have a common error message for the
        # different type of login errors, so people can lot game the system and
        # work out what email exist
        error_message = 'Login failed. Perhaps check your email or password'

        # regular validation
        rv = Form.validate(self)
        if not rv:
            return False

        # check the user model to see if the login credentials are valid
        user_model = User()
        if user_model.validate_login(self.email.data,self.password.data):
            # login credentials all good, set the user (which has now been
            # populated with the user details)
            self.user = user_model
            return True
        else:
            self.email.errors.append(error_message)
            return False


class ApikeyscreateForm(Form):
    name = TextField('Name', [
        validators.Required(),
        validators.Length(min=1, max=200)
    ])

def user_has_access_to_apikey(form, field):
    # Check to see if this user has access to this apikey
    apikey_search = db.apikeys.find_one(
        {"userid": unicode(current_user.get_id()), "_id": ObjectId(field.data)})
    if apikey_search == None:
        raise ValidationError('That apikey is invalid!')

class MessagescreateForm(Form):
    level = TextField('Type', [
        validators.Required(),
        validators.Length(min=1, max=200)
    ])
    heading = TextField('Heading', [
        validators.Required(),
        validators.Length(min=1, max=50)
    ])
    blurb = TextField('Blurb', [
        validators.Required(),
        validators.Length(min=1, max=100)
    ])
    body = TextField('Message', [
        validators.Length(min=0, max=5000)
    ])
    apikeyid = TextField('Apikey', [
        validators.Required(),
        user_has_access_to_apikey       
    ])


def valid_apikey(form, field):
    # Check to see if this user has access to this apikey
    apikey_search = db.apikeys.find_one(
        {"key": field.data, "status": 1})
    if apikey_search == None:
        raise ValidationError('That apikey is invalid!')
    else:
        form.apikeyid = str(apikey_search['_id'])
        form.userid = apikey_search['userid']

class MessagescreateApi(Form):
    level = TextField('Type', [
        validators.Required(),
        validators.Length(min=1, max=200)
    ])
    heading = TextField('Heading', [
        validators.Required(),
        validators.Length(min=1, max=50)
    ])
    blurb = TextField('Blurb', [
        validators.Required(),
        validators.Length(min=1, max=100)
    ])
    body = TextField('Message', [
        validators.Length(min=0, max=5000)
    ])
    apikey = TextField('Apikey', [
        validators.Required(),
        valid_apikey
    ])


class MessagesgetApi(Form):
    apikey = TextField('Apikey', [
        validators.Required(),
        valid_apikey
    ])
    limit = TextField('Limit', [
        

    ])