from flask import Flask, render_template, request,
    redirect, url_for, flash, jsonify
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Shelter, Puppy, User
from datetime import datetime
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Shelter adoption Application"

# Connect to Database and create database session
engine = create_engine('sqlite:///petshelterwithuser.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create anti-forgery state token


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    # Store user loggin data in login session
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'
    login_session['gplus_id'] = 'gplus_id'
    login_session['access_token'] = 'access_token'

    # See if user existm if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

    # DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    # credentials = login_session.get('credentials')
    c = login_session['access_token']
    if c is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


#      ------------  End Google Singin and Signout -------------

#   --------  JSON FILE START--------


@app.route('/shelters/JSON')
def shelterListJSON():
    allshelter = session.query(Shelter).all()
    return jsonify(JSONShelter=[i.serialize for i in allshelter])


@app.route('/shelters/<int:shelter_id>/petlist/JSON')
def petListJSON(shelter_id):
    shelter = session.query(Shelter).filter_by(id=shelter_id).one()
    puppies = session.query(Puppy).filter_by(shelter_id=shelter_id).all()
    return jsonify(JSONPetList=[i.serialize for i in puppies])


@app.route('/shelters/<int:shelter_id>/petlist/<int:pet_id>/JSON')
def eachPetJSON(shelter_id, pet_id):
    puppies = session.query(Puppy).filter_by(id=pet_id).one()
    return jsonify(JSONPet=puppies.serialize)

#   --------  JSON FILE END--------

# Shelter List


@app.route('/')
@app.route('/shelters/')
def allShelterList():
    allshelter = session.query(Shelter).order_by(asc(Shelter.name))
    # Check to see if the user is 'not' in loggin session, then direct to
    # public page.
    if 'username' not in login_session:
        return render_template(
            'publicshelterlist.html',
            allshelter=allshelter)
    else:
        return render_template('allshelterlist.html', allshelter=allshelter)

# Add a new Shelter


@app.route('/shelters/new/', methods=['GET', 'POST'])
def newShelter():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newShelter = Shelter(
            name=request.form['name'],
            address=request.form['address'],
            city=request.form['city'],
            state=request.form['state'],
            zipCode=request.form['zipcode'],
            website=request.form['website'],
            user_id=login_session['user_id']
        )
        session.add(newShelter)
        session.commit()
        flash('New Shelter Added!')
        return redirect(url_for('allShelterList'))
    else:
        return render_template('newshelter.html')

# Edit shelter


@app.route('/shelters/<int:shelter_id>/edit/', methods=['GET', 'POST'])
def editShelter(shelter_id):
    editedShelter = session.query(Shelter).filter_by(id=shelter_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedShelter.user_id != login_session['user_id']:
        return redirect('/login')
    if request.method == 'POST':
        if request.form['name']:
            editedShelter.name = request.form['name']
        if request.form['address']:
            editedShelter.address = request.form['address']
        if request.form['city']:
            editedShelter.city = request.form['city']
        if request.form['state']:
            editedShelter.state = request.form['state']
        if request.form['zipcode']:
            editedShelter.zipCode = request.form['zipcode']
        if request.form['website']:
            editedShelter.website = request.form['website']
        session.add(editedShelter)
        session.commit()
        flash("Shelter has been edited")
        return redirect(url_for('shelterList', shelter_id=shelter_id))
    else:
        return render_template(
            'editshelter.html',
            shelter_id=shelter_id,
            i=editedShelter)

#   Delete shelter


@app.route('/shelters/<int:shelter_id>/delete/',
           methods=[
               'GET',
               'POST'])
def deleteShelter(shelter_id):
    deletedShelter = session.query(Shelter).filter_by(id=shelter_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if deletedShelter.user_id != login_session['user_id']:
        return redirect('/login')
    if request.method == 'POST':
        session.delete(deletedShelter)
        session.commit()
        flash("Shelter has been deleted")
        return redirect(url_for('shelterList', shelter_id=shelter_id))
    else:
        return render_template('deleteshelter.html', i=deletedShelter)

# show pet lists


@app.route('/shelters/<int:shelter_id>/')
@app.route('/shelters/<int:shelter_id>/list')
def shelterList(shelter_id):
    shelter = session.query(Shelter).filter_by(id=shelter_id).one()
    #   protect each menu based on whoever created it.
    creator = getUserInfo(shelter.user_id)
    puppies = session.query(Puppy).filter_by(shelter_id=shelter.id).all()
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template(
            'publicpetlist.html',
            shelter=shelter, creator=creator, puppies=puppies)
    else:
        return render_template(
            'home.html',
            shelter=shelter,
            puppies=puppies,
            creator=creator)


#   Add a new pet
@app.route('/shelters/<int:shelter_id>/list/new/', methods=['GET', 'POST'])
def newPet(shelter_id):
    shelter = session.query(Shelter).filter_by(id=shelter_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if shelter.user_id != login_session['user_id']:
        return redirect('/login')
    if request.method == 'POST':
        addnew = Puppy(
            name=request.form['name'],
            dateOfBirth=datetime.strptime(
                request.form['dateofbirth'],
                "%Y-%m-%d"),
            gender=request.form['gender'],
            weight=request.form['weight'],
            picture=request.form['picture'],
            shelter_id=shelter_id,
            user_id=shelter.user_id)
        session.add(addnew)
        session.commit()
        flash("New Pet created")
        # redirect url_for(function: shelter)
        return redirect(url_for('shelterList', shelter_id=shelter_id))
    else:
        return render_template('newpet.html', shelter_id=shelter_id)


#   Edit a new pet

@app.route(
    '/shelters/<int:shelter_id>/<int:pet_id>/edit',
    methods=[
        'GET',
        'POST'])
def editPet(shelter_id, pet_id):
    editedPet = session.query(Puppy).filter_by(id=pet_id).one()
    shelter = session.query(Shelter).filter_by(id=shelter_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if shelter.user_id != login_session['user_id']:
        return redirect('/login')
    if request.method == 'POST':
        if request.form['name']:
            editedPet.name = request.form['name']
        if request.form['gender']:
            editedPet.gender = request.form['gender']
        if request.form['dateofbirth']:
            editedPet.dateOfBirth = datetime.strptime(
                request.form['dateofbirth'], "%Y-%m-%d")
        if request.form['weight']:
            editedPet.weight = request.form['weight']
        if request.form['picture']:
            editedPet.picture = request.form['picture']
        session.add(editedPet)
        session.commit()
        flash("Pet has been edited")
        return redirect(url_for('shelterList', shelter_id=shelter_id))
    else:
        return render_template(
            'editpet.html',
            shelter_id=shelter_id,
            pet_id=pet_id,
            i=editedPet)

#   Delete pet


@app.route(
    '/shelters/<int:shelter_id>/<int:pet_id>/delete/', methods=['GET', 'POST'])
def deletePet(shelter_id, pet_id):
    shelter = session.query(Shelter).filter_by(id=shelter_id).one()
    deletedPet = session.query(Puppy).filter_by(id=pet_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if shelter.user_id != login_session['user_id']:
        return redirect('/login')
    if request.method == 'POST':
        session.delete(deletedPet)
        session.commit()
        flash("pet has been deleted")
        return redirect(url_for('shelterList', shelter_id=shelter_id))
    else:
        return render_template('deletepet.html', i=deletedPet)


# For Sign in config
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except BaseException:
        return None


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def createUser(login_session):
    newUser = User(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

# Disconnect based on provider


@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
        # Reset the user's session:
            del login_session['access_token']
            del login_session['gplus_id']
            del login_session['username']
            del login_session['email']
            del login_session['picture']

        flash("You have successfully been logged out.")
        return redirect(url_for('allShelterList'))
    else:
        flash("You were not logged in")
        return redirect(url_for('allShelterList'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
