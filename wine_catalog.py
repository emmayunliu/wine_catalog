from flask import Flask, render_template, request, \
    redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Wine, MenuItem, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
from flask.ext.httpauth import HTTPBasicAuth
import requests

app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Wine Application"

auth = HTTPBasicAuth()
engine = create_engine('sqlite:///wine.db')
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
        response = make_response(json.dumps('Current user is '
                                            'already connected.'), 200)
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

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;' \
              '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(username=login_session['username'], email=login_session[
                   'email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(info):
    try:
        userid = session.query(User).filter_by(email=info).one().id
        return userid
    except:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    del login_session['access_token']
    del login_session['gplus_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']

    return redirect(url_for('showWines'))


# Log in
@auth.verify_password
def verify_password(username, password):
    print "Looking for user %s" % username
    user = session.query(User).filter_by(username=username).first()
    if not user:
        print "User not found"
        return False
    elif not user.verify_password(password):
        print "Unable to verify password"
        return False
    else:
        g.user = user
        return True


@app.route('/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        print "missing arguments"
        abort(400)

    if session.query(User).filter_by(username=username).first() is not None:
        print "existing user"
        user = session.query(User).filter_by(username=username).first()
        return jsonify({
                           'message': 'user already exists'}), 200

    user = User(username=username)
    user.hash_password(password)
    session.add(user)
    session.commit()
    return jsonify(
        {'username': user.username}), 201


@app.route('/users/<int:id>')
def get_user(id):
    user = session.query(User).filter_by(id=id).one()
    if not user:
        abort(400)
    return jsonify({'username': user.username})


@app.route('/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.username})


@app.route('/wine', methods=['GET', 'POST'])
@auth.login_required
def showAllWines():
    if request.method == 'GET':
        wines = session.query(Wine).all()
        return jsonify(wines=[wine.serialize for wine in wines])
    elif request.method == 'POST':
        name = request.json.get('name')
        description = request.json.get('description')
        location = request.json.get('location')
        taste = request.json.get('taste')
        newWine = Wine(name=name, description=description,
                       location=location, taste=taste)
        session.add(newWine)
        session.commit()
        return jsonify(newWine.serialize)


@app.route('/wine/<int:wine_id>/JSON')
def wineMenuJSON(wine_id):
    wine = session.query(Wine).filter_by(id=wine_id).one()
    items = session.query(MenuItem).filter_by(
        wine_id=wine.id).all()
    return jsonify(MenuItems=[i.serialize for i in items])


@app.route('/wine/<int:wine_id>/<int:menu_id>/JSON')
def menuItemJSON(wine_id, menu_id):
    Menu_Item = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(Menu_Item=Menu_Item.serialize)


@app.route('/wine/JSON')
def wineJSON():
    wines = session.query(Wine).all()
    return jsonify(wines=[r.serialize for r in wines])


# Show all wines
@app.route('/')
@app.route('/wine/')
def showWines():
    wines = session.query(Wine).all()
    latestAddedItem = session.query(MenuItem.name.label('name'),
                                    Wine.name.label('wine_name')).\
        filter(MenuItem.wine_id == Wine.id).order_by(desc(MenuItem.id)).\
        limit(5)
    return render_template('wines.html', wines=wines,
                           latestAddedItem=latestAddedItem,
                           login=login_session)


# Show a wine menu
@app.route('/wine/<int:wine_id>/')
def showMenu(wine_id):
    wineList = session.query(Wine).all()
    wine = session.query(Wine).filter_by(id=wine_id).one()
    items = session.query(MenuItem).filter_by(
        wine_id=wine_id).all()
    wineCount = session.query(MenuItem).filter_by(wine_id=wine_id).count()
    return render_template('menu.html', items=items, wine=wine,
                           wineList=wineList, wineCount=wineCount)


@app.route('/wine/<int:wine_id>/<int:menu_id>/')
def showItem(wine_id, menu_id):
    items = session.query(MenuItem).filter_by(
        id=menu_id).one()
    login = login_session
    return render_template('item.html', items=items, login=login)


# Create a new menu item
@app.route('/wine/new/', methods=['GET', 'POST'])
def newMenuItem():
    if request.method == 'POST':
        newItem = MenuItem(name=request.form['name'],
                           description=request.form['description'],
                           location=request.form['location'],
                           taste=request.form['taste'],
                           wine_id=request.form['wine_type'],
                           user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()

        return redirect(url_for('showMenu', wine_id=newItem.wine_id))
    else:
        return render_template('newmenuitem.html')


# Edit a menu item

@app.route('/wine/<int:wine_id>/<int:menu_id>/edit',
           methods=['GET', 'POST'])
def editMenuItem(wine_id, menu_id):
    editedItem = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['name']
        if request.form['location']:
            editedItem.price = request.form['location']
        if request.form['taste']:
            editedItem.course = request.form['taste']
        session.add(editedItem)
        session.commit()
        return redirect(url_for('showMenu', wine_id=wine_id))
    else:

        return render_template(
            'editmenuitem.html', wine_id=wine_id, menu_id=menu_id,
            item=editedItem)


# Delete a menu item


@app.route('/wine/<int:wine_id>/menu/<int:menu_id>/delete',
           methods=['GET', 'POST'])
def deleteMenuItem(wine_id, menu_id):
    itemToDelete = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('showMenu', wine_id=wine_id))
    else:
        return render_template('deleteMenuItem.html', item=itemToDelete)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=7000)
