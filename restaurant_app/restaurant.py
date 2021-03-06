from flask import Flask,render_template,request,redirect,url_for
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base,Restaurant,MenuItem,User

from flask import session as login_session
import random,string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(open('client_secret.json', 'r').read())['web']['client_id']

engine = create_engine('sqlite:///restaurantmenuwithusers.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

#User helper function
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html',STATE=state)

@app.route('/gconnect',methods=['POST'])
def gconnect(): 
     if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code
     code = request.data

     try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
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

    # Verify that the access token is valid for this app.
     if result['issued_to'] != CLIENT_ID:
        response = make_response(
                   json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
     gplus_id = credentials.id_token['sub']
     if result['user_id'] != gplus_id:
        response = make_response(
                   json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

     stored_access_token = login_session.get('access_token')
     stored_gplus_id = login_session.get('gplus_id')
     if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
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

     login_session['provider'] = 'google'
     login_session['username'] = data['name']
     login_session['picture'] = data['picture']
     login_session['email'] = data['email']

     #create or fetch user
     user_id = getUserID(login_session['email'])
     if not user_id:
         user_id = createUser(login_session)
     login_session['user_id'] = user_id;    

     return login_session['username']

@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url_basic = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    #url_basic = 'https://accounts.google.com/o/oauth2/revoke'
    #params={'token': login_session['access_token']}
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    result = requests.get(url_basic,headers = headers).json()
    #h = httplib2.Http()
    #result = h.request(url, 'GET')[0]
    print '*****gdisconnect******'
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
        print '*****gdisconnect******'
        print response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        print '*****gdisconnect******'
        print response
        return response


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url_basic = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    #url_basic = 'https://accounts.google.com/o/oauth2/revoke'
    #params={'token': login_session['access_token']}
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    result = requests.get(url_basic,headers = headers).json()
    #h = httplib2.Http()
    #result = h.request(url, 'GET')[0]
    print '*****gdisconnect******'
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
        print '*****gdisconnect******'
        print response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        print '*****gdisconnect******'
        print response
        return response

#fb connect
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token


    app_id = json.loads(open('fb_client_secret.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secret.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]


    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v3.2/me"
    '''
        Due to the formatting for the result from the server token exchange we have to
        split the token first on commas and select the first index which gives us the key : value
        for the server access token then we split it on colons to pull out the actual token value
        and replace the remaining quotes with nothing so that it can be used directly in the graph
        api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v3.2/me?access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v3.2/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['picture'] = data["data"]["url"]

     #create or fetch user
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    return login_session['username']

@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    del login_session['access_token']
    del login_session['facebook_id']
    print '*****fbdisconnect******'
    print result
    return result

@app.route('/disconnect')
def disconnect():
    if login_session['provider'] == 'google':
        gdisconnect()
    else:
        fbdisconnect()
     
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['provider']


@app.route('/')
@app.route('/restaurant/')
def getAllRestaurants():
    restaurants = session.query(Restaurant).all()
    if 'username' not in login_session:
        return render_template('publicRestaurants.html',restaurants = restaurants,login_session = login_session)
    else:
        return render_template('restaurants.html',restaurants = restaurants,login_session = login_session)

@app.route('/restaurant/<int:restaurant_id>/edit/',methods=['POST','GET'])
def editRestaurant(restaurant_id):
    editRestaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'POST':
       editRestaurant.name = request.form['name']
       return redirect(url_for('getAllRestaurants'))
    else:    
        return render_template('editRestaurant.html',restaurant = editRestaurant,login_session=login_session)

@app.route('/restaurant/<int:restaurant_id>/delete/',methods = ['GET','POST'])
def deleteRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        session.delete(restaurant)
        session.commit()
        return redirect(url_for('getAllRestaurants'))
    else:    
        return render_template('deleteRestaurant.html',restaurant = restaurant,login_session=login_session)

@app.route('/restaurant/add/',methods = ['GET','POST'])
def AddRestaurant():
    if request.method == 'POST':
        newRestaurant = Restaurant(name=request.form['restaurant_name'],user_id = login_session['user_id'])
        session.add(newRestaurant)
        session.commit()
        return redirect(url_for('getAllRestaurants'))
    else:
        return render_template('createRestaurant.html')


@app.route('/restaurant/<int:restaurant_id>/')
def getAllMenuItemsForRestaurants(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    menuItems = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)
    if 'username' not in login_session:
        return render_template('publicMenu.html',restaurant = restaurant,menuItems = menuItems,login_session = login_session)
    else:
        return render_template('menuitems.html',restaurant = restaurant,menuItems = menuItems,login_session = login_session)



@app.route('/restaurant/<int:restaurant_id>/menuItem/<int:menuItem_id>/edit/',methods = ['POST','GET'])
def editMenuItem(menuItem_id,restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    menuItem = session.query(MenuItem).filter_by(id = menuItem_id).one()
    if request.method == 'POST':
        menuItem.name = request.form['name']
        menuItem.course = request.form['course']
        menuItem.price = request.form['price']
        menuItem.description = request.form['description']
        return redirect(url_for('getAllMenuItemsForRestaurants',restaurant_id = restaurant_id))
    else:    
        return render_template('editMenuItem.html',menuItem = menuItem,restaurant = restaurant,login_session=login_session)

@app.route('/restaurant/<int:restaurant_id>/menuItem/<int:menuItem_id>/delete/',methods = ['POST','GET'])
def deleteMenuItem(menuItem_id,restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    menuItem = session.query(MenuItem).filter_by(id = menuItem_id).one()
    if request.method == 'POST':
        session.delete(menuItem)
        session.commit()
        return redirect(url_for('getAllMenuItemsForRestaurants',restaurant_id = restaurant.id))
    else:    
        return render_template('deleteMenuItem.html',menuItem = menuItem,restaurant = restaurant,login_session=login_session)    

@app.route('/restaurant/<int:restaurant_id>/menuItem/add/',methods = ['POST','GET'])
def AddMenuItem(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        newMenuItem = MenuItem(name=request.form['name'],course = request.form['course'],description = request.form['description'],price = request.form['price'],restaurant_id = restaurant_id,user_id=login_session['user_id'])
        session.add(newMenuItem)
        session.commit()
        return redirect(url_for('getAllMenuItemsForRestaurants',restaurant_id = restaurant_id))
    else:    
        return render_template('createMenuItem.html',restaurant_id = restaurant_id)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0',port = 5000,threaded=False) 