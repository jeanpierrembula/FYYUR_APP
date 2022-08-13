#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
	Flask, 
	render_template, 
	request, 
	Response, 
	flash, 
	redirect, 
	url_for,
	jsonify
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy.sql import text
from datetime import date, datetime
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TERMINÉ: connect to a local postgresql database
migrate = Migrate(app= app, db= db) #je connecte l'application à une base de donnée local

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    city = db.Column(db.String(120), nullable = False)
    state = db.Column(db.String(120), nullable = False)
    address = db.Column(db.String(120), nullable = False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TERMINÉ: implement any missing fields, as a database migration using Flask-Migrate
    seeking_description = db.Column(db.String())
    seeking_talent = db.Column(db.Boolean, nullable = False)
    website = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable = False)
    shows = db.relationship('show', backref ='venues')

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    city = db.Column(db.String(120), nullable = False)
    state = db.Column(db.String(120), nullable = False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable = False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TERMINÉ: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable = False)
    seeking_description = db.Column(db.String())
    shows = db.relationship('show', backref ='artists')

# TERMINÉ Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key = True)
    start_date = db.Column(db.DateTime, nullable = False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id',ondelete="SET NULL",onupdate="cascade"))
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id',ondelete="SET NULL", onupdate="cascade"))

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
@app.route('/home')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TERMINÉ: replace with real venues data.
  #       num_upcoming_shows should be aggreq_get_artated based on number of upcoming shows per venue.
  try:
    VillesEtat = Venue.query.with_entities(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
    venues = [] 
    Donnee_lieux = []
    
    for city_state in VillesEtat:
      ville_etat_shows_dictt = {} 
      ville_etat_shows_dictt['city'] = city_state[0]
      ville_etat_shows_dictt['state'] = city_state[1]
      Donnee_lieux.append(ville_etat_shows_dictt)      
      try:
        lieu = Venue.query.with_entities(Venue.id, Venue.name).filter(Venue.city == city_state[0] , Venue.state == city_state[1]).all()
      except:
        lieu = []
    
      venues.append(lieu)
    
    for i,v in zip(range(len(venues)),venues):
      list_lieux = [] 
      for each in v:
        ville_etat_shows_dictt = {}
        try:
          ville_etat_shows_dictt['num_upcoming_shows'] = show.query.filter(show.venue_id == each[0], show.start_date > date.now()).count()
        except:
          ville_etat_shows_dictt['num_upcoming_shows'] = 0
        ville_etat_shows_dictt['id'] = each[0]
        ville_etat_shows_dictt['name'] = each[1]
        list_lieux.append(ville_etat_shows_dictt)
      Donnee_lieux[i]['venues'] = list_lieux  
        
    return render_template('pages/venues.html', areas=Donnee_lieux)
  except Exception as e:
      print(e)
      flash('something went wrong!')
      return redirect('/')

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TERMINÉ: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  req_get = '%'+request.form.get('search_term')+'%'
  req_venues = Venue.query.with_entities(Venue.id,Venue.name).filter(Venue.name.ilike(req_get)).all()
  data = []
  for ven in req_venues:
    shows_dict = {}
    shows_dict['id'] = ven[0]
    shows_dict['name'] = ven[1]
    data.append(shows_dict)
  response = {
    'count':len(req_venues),
    'data': data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TERMINÉ: replace with real venue data from the venues table, using venue_id
  try:
    venue_data = Venue.query.get(venue_id)

    shows = show.query.with_entities(Venue, Artist.id, Artist.name, Artist.image_link, show.start_date).join(Venue).join(Artist).filter(Venue.id == venue_id).all()
    past_shows = list(filter(lambda x: x.start_date < datetime.now(), shows))
    upcoming_shows = list(filter(lambda x: x.start_date >= datetime.now(), shows))
    
    def show_artist(showObj):
      art_shows_dicttion = {}
      art_shows_dicttion['artist_id'] = showObj.id
      art_shows_dicttion['artist_name'] = showObj.name
      art_shows_dicttion['artist_image_link'] = showObj.image_link
      art_shows_dicttion['start_date'] = showObj.start_date.strftime("%Y-%m-%d %H:%M:%S")
      return art_shows_dicttion
    past_shows = list(map(lambda x: show_artist(x), past_shows))
    upcoming_shows = list(map(lambda x: show_artist(x), upcoming_shows))
    data={
      "id":venue_data.id,
      "name":venue_data.name,
      "genres": venue_data.genres.split(','),
      "address": venue_data.address,
      "city": venue_data.city,
      "state": venue_data.state,
      "phone": venue_data.phone,
      "website": venue_data.website,
      "facebook_link": venue_data.facebook_link,
      "seeking_talent": venue_data.seeking_talent,
      "seeking_description": venue_data.seeking_description,
      "image_link": venue_data.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows)
    }
    return render_template('pages/show_venue.html', venue=data)
  except Exception as e:
    print(e)
    return redirect('/venues')
 

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TERMINÉ: insert form data as a new Venue record in the db, instead
  # TERMINÉ : modify data to be the data object returned from db insertion
  form = VenueForm(request.form)
  if form.validate_on_submit():
    try:
      object_lieu = Venue()
      if form.image_link.data == '':
        form.image_link.data = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSrbEwKOiJdjiddcv71U5-4QuJIz_PmdxWCiQ&usqp=CAU'
      
      form.populate_obj(object_lieu)
      object_lieu.genres = ', '.join(form.genres.data)
      db.session.add(object_lieu)
      db.session.commit()
      # TERMINÉ: on unsuccessful db insert, flash an error instead.
      # on successful db insert, flash success
      flash('Venue ' + object_lieu.name + '  A été listé avec succès !')
    except:
      print(sys.exc_info())
      db.session.rollback()
      flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
    finally:
      db.session.close()
    return redirect('/venues')
  else:
    for key in form.errors:
      flash(key +" : "+' '.join(form.errors[key]))
    return render_template('forms/new_venue.html', form=VenueForm())

  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TERMINÉ: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  print(venue_id)
  try:
    Venue.query.filter_by(id = venue_id).delete()
    db.session.commit()
    db.session.close()
    flash('The Venue was deleted successfully!.')
    return jsonify({'success': True}) 
  except Exception as e:
    print(e)
    db.session.rollback()
    flash('An error occurred. could not delete the venue.')
    db.session.close()
    return jsonify({'success': False}) 

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TERMINÉ: replace with real data returned from querying the database
  req_query_artist = Artist.query.with_entities(Artist.id, Artist.name).all()
  data = []
  for arts in req_query_artist:
    art_shows_dictt = {}
    art_shows_dictt['id'] = arts[0]
    art_shows_dictt['name'] = arts[1]
    data.append(art_shows_dictt)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TERMINÉ: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  req_get_art = '%'+request.form.get('search_term')+'%'
  req_artists = Artist.query.with_entities(Artist.id,Artist.name).filter(Artist.name.ilike(req_get_art)).all()
  data = []
  for art in req_artists:
      shows_dict = {}
      shows_dict['id'] = art[0]
      shows_dict['name'] = art[1]
      data.append(shows_dict)
  response = {
    'count':len(req_artists),
    'data': data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TERMINÉ: replace with real artist data from the artist table, using artist_id
  try:
    artist_data = Artist.query.get(artist_id)
   
    shows = show.query.with_entities(Artist, Venue.id, Venue.name, Venue.image_link, show.start_date).join(Venue).join(Artist).filter(Artist.id == artist_id).all()
    past_shows = list(filter(lambda x: x.start_date < datetime.now(), shows))
    upcoming_shows = list(filter(lambda x: x.start_date >= datetime.now(), shows))
    
    def show_artist(showObj):
      art_shows_dicttion = {}
      art_shows_dicttion['venue_id'] = showObj.id
      art_shows_dicttion['venue_name'] = showObj.name
      art_shows_dicttion['venue_image_link'] = showObj.image_link
      art_shows_dicttion['start_date'] = showObj.start_date.strftime("%Y-%m-%d %H:%M:%S")
      return art_shows_dicttion
    past_shows = list(map(lambda x: show_artist(x), past_shows))
    upcoming_shows = list(map(lambda x: show_artist(x), upcoming_shows))
    data={
      "id": artist_data.id,
      "name":artist_data.name,
      "genres": artist_data.genres.split(','),
      "city": artist_data.city,
      "state": artist_data.state,
      "phone": artist_data.phone,
      "website": artist_data.website,
      "facebook_link": artist_data.facebook_link,
      "seeking_talent": artist_data.seeking_venue,
      "seeking_description": artist_data.seeking_description,
      "image_link": artist_data.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows)
    }
    return render_template('pages/show_artist.html', artist=data)
  except :
    print(sys.exc_info())
    return redirect('/artists')

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  data = Artist.query.get(artist_id)
  try:
    artist_data={
      "id": data.id,
      "name": data.name,
      "genres": data.genres.split(','),
      "city": data.city,
      "state": data.state,
      "phone": data.phone,
      "website": data.website,
      "facebook_link": data.facebook_link,
      "seeking_venue": data.seeking_venue,
      "seeking_description": data.seeking_description,
      "image_link": data.image_link
    }
    form.genres.data = artist_data['genres']
    return render_template('forms/edit_artist.html', form=form, artist = artist_data)
  # TODO: populate form with fields from artist with ID <artist_id>
  except :
    print(sys.exc_info())
    return redirect('/artists/'+str(artist_id))


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TERMINÉ: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  if form.validate_on_submit():
    try:
      
      if form.image_link.data == '':
        form.image_link.data = 'https://cdn.pixabay.com/photo/2018/04/18/18/56/user-3331257__340.png'
      object_artite = Artist.query.get(artist_id)
          
      object_artite.name = form.name.data
      object_artite.city = form.city.data
      object_artite.state = form.state.data
      object_artite.phone = form.phone.data
      object_artite.genres = ', '.join(form.genres.data)
      object_artite.facebook_link = form.facebook_link.data
      object_artite.website = form.website.data
      object_artite.seeking_description = form.seeking_description.data
      object_artite.seeking_venue = form.seeking_venue.data
      object_artite.image_link = form.image_link.data
      db.session.commit()
      flash('Artist ' + object_artite.name + '  A été listé avec succès !')
    except:
      print(sys.exc_info())
      db.session.rollback()
      flash('An error occurred. Artist ' + form.name.data + ' could not be edited.')
    finally:
      db.session.close()
      return redirect('/artists/'+str(artist_id))
  else:
    for key in form.errors:
      flash(key +" : "+' '.join(form.errors[key]))
    return redirect('/artists/'+str(artist_id)+'/edit')

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  # TERMINÉ: populate form with values from venue with ID <venue_id>
  data = Venue.query.get(venue_id).__shows_dictt__
  try:
    venue_data={
      "id": data['id'],
      "name": data['name'],
      "genres": data['genres'].replace(", ", ",").split(','),
      "city": data['city'],
      "state": data['state'],
      "address": data['address'],
      "phone": data['phone'],
      "website": data['website'],
      "facebook_link": data['facebook_link'],
      "seeking_talent": data['seeking_talent'],
      "seeking_description": data['seeking_description'],
      "image_link": data['image_link']
    }
    form.genres.data = venue_data['genres']
    return render_template('forms/edit_venue.html', form=form, venue = venue_data)
  except :
    print(sys.exc_info())
    return redirect('/venues/'+str(venue_id))
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TERMINÉ: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  if form.validate_on_submit():
    try:
      if form.image_link.data == '':
        form.image_link.data = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSrbEwKOiJdjiddcv71U5-4QuJIz_PmdxWCiQ&usqp=CAU'
      object_lieu = Venue.query.get(venue_id)
          
      object_lieu.name = form.name.data
      object_lieu.city = form.city.data
      object_lieu.state = form.state.data
      object_lieu.phone = form.phone.data
      object_lieu.address = form.address.data
      object_lieu.genres = ', '.join(form.genres.data)
      object_lieu.facebook_link = form.facebook_link.data
      object_lieu.website = form.website.data
      object_lieu.seeking_description = form.seeking_description.data
      object_lieu.seeking_talent = form.seeking_talent.data
      object_lieu.image_link = form.image_link.data
      db.session.commit()
      flash('Venue ' + object_lieu.name + '  A été listé avec succès !')
    except:
      print(sys.exc_info())
      db.session.rollback()
      flash('Une erreur s\'est produite. Lieu ' + form.name.data + ' n\'a pas pu être modifié.')
    finally:
      db.session.close()
    return redirect('/venues/'+str(venue_id))     
  else:
    for key in form.errors:
      flash(key +" : "+' '.join(form.errors[key]))
    return redirect('/venues/'+str(venue_id)+'/edit')

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TERMINÉ: insert form data as a new Venue record in the db, instead
  # TERMINÉ: modify data to be the data object returned from db insertion

  form = ArtistForm(request.form)
  if form.validate_on_submit():
    try:
      artist_obj = Artist()
      if form.image_link.data == '':
          form.image_link.data = 'https://cdn.pixabay.com/photo/2018/04/18/18/56/user-3331257__340.png'
      form.populate_obj(artist_obj)
      artist_obj.genres = ', '.join(form.genres.data)
      db.session.add(artist_obj)
      db.session.commit()
      # on successful db insert, flash success
      # TERMINÉ: on unsuccessful db insert, flash an error instead.
      flash('Artist ' + artist_obj.name + '  A été listé avec succès !')
    except:
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
    finally:
      db.session.close()
    return redirect('/artists')
  else:
    for key in form.errors:
      flash(key +" : "+' '.join(form.errors[key]))
    return render_template('forms/new_artist.html', form=ArtistForm())


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TERMINÉ: replace with real venues data.
  try:
      shows = show.query.with_entities(Venue.id, Venue.name, Artist.id, Artist.name, Artist.image_link, show.start_date).join(Venue).join(Artist).all()
  except:
    print(sys.exc_info())
    shows = []
  data = []
  for each in shows:
    shows_dict = {}
    shows_dict['venue_id'] = each[0]
    shows_dict['venue_name'] = each[1]
    shows_dict['artist_id'] = each[2]
    shows_dict['artist_name'] = each[3]
    shows_dict['artist_image_link'] = each[4]
    shows_dict['start_date'] = each[5].strftime("%Y-%m-%d %H:%M:%S")
    data.append(shows_dict)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TERMINÉ: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)
  if form.validate_on_submit():
    try:
      object_show = show()
      form.populate_obj(object_show)
      db.session.add(object_show)
      db.session.commit()
      flash('Le spectacle  A été listé avec succès !')
      return redirect('/')
    except :
      print(sys.exc_info())
      flash('Une erreur s\'est produite. Le spectacle n\'a pas pu être listé, vérifiez que le lieu et l\'artiste existent !')
      db.session.rollback()
      db.session.close()
      return redirect('/shows/create')
  else:
    for key in form.errors:
      flash(key +" : "+' '.join(form.errors[key]))
    return render_template('forms/new_show.html', form=ShowForm())

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
