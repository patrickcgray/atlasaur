#this file has everything to do with locations and their functionality

#external imports
from google.appengine.api import images
import string

from geopy import geocoders 
from geopy import distance
from geopy import point

from operator import attrgetter


#internal imports
from basehandler import BlogHandler
from general.dbmodels import User
from general.dbmodels import Location
from general.dbmodels import LocationUpdate
from general.dbmodels import Record
from general.dbmodels import Group
from general.memcache import record_cache
from general.memcache import individual_location_cache
from general.memcache import location_cache
from general.memcache import individual_record_cache
from general.memcache import exployrer_cache
from general.memcache import location_update_cache
from general.memcache import group_record_cache

#this lets the user add a new location and adds a record db entry at the same time
class NewLocation(BlogHandler):
    def get(self):
        if self.get_user():
            user = self.get_user()            
            groups = None
            if user['groups']:
                groups = []
                for group in user['groups']:
                    groups.append(Group.get_by_id(int(group)))
            
            self.render('newlocation.html', user = user, groups=groups)
        else:
            self.render('pleaselogin.html')
    def post(self):
        location_description = self.request.get('location_description')
        location_name = self.request.get('location_name')
        location_address = self.request.get('location_address')
        GPSlocation = self.request.get('GPSlocation')
        locationtype = self.request.get('locationtype')
        whatdidyoudo = self.request.get('whatdidyoudo')
        title = self.request.get('title')
        postsport = self.request.get('postsport')
        rating = self.request.get('rating')
        howwasit = self.request.get('howwasit')
        equipment = self.request.get('equipment')
        difficulty = self.request.get('difficulty')
        group_tag = self.request.get('group_tag')
        tags = self.request.get('tags')
        website = self.request.get('website')
        
        user = self.get_user()
            
        submitter = user['username']
        user_id = user['model_id']
        
        location_name = str(location_name)
        location_name = location_name.replace(' ', '25fdsa67ggggsd5')
        location_name = ''.join(e for e in location_name if e.isalnum())
        location_name = location_name.replace('25fdsa67ggggsd5', '-')
        
        title = str(title)
        title = title.replace(' ', '25fdsa67ggggsd5')
        title = ''.join(e for e in title if e.isalnum())
        title = title.replace('25fdsa67ggggsd5', '-')
                
        if location_description and location_address and location_name and whatdidyoudo and submitter and user_id and title and postsport and rating and howwasit:
            if not equipment:
                equipment = None
            if not website:
                website = None
                
            error = None
            
            g = geocoders.GoogleV3()
                #to catch an error where there is no corresponding location
            try:
                #to catch an error where there are multiple returned locations
                try:
                    place, (lat, lng) = g.geocode(location_address)
                    place, searched_location = g.geocode(location_address)
                except ValueError:
                    geocodespot = g.geocode(location_address, exactly_one=False)
                    place, (lat, lng) = geocodespot[0]
                    place, searched_location = geocodespot[0]
                GPSlocation = "("+str(lat)+", "+str(lng)+")"
                Long = lng
                Lat = lat
                

            #this is straight from the docs:  http://code.google.com/p/geopy/wiki/Exceptions and happens when there is no location that matches
            except geocoders.google.GQueryError:
                error = "We cannot find " + location_address +"... try to be a little more specific or search a nearby location."
            
            if error:          
                self.render('newlocation.html', user = user, location_address=location_address, location_description=location_description, location_name=location_name, equipment=equipment,
                         whatdidyoudo=whatdidyoudo, howwasit=howwasit, group_tag=group_tag, tags=tags, website=website,  submitter=submitter, user_id=user_id, title=title, GPSlocation = GPSlocation, locationtype = locationtype, error=error)
            
            if not difficulty:
                difficulty = None
            else:
                difficulty = int(difficulty)
            
            location_db = Location(
                    description=location_description,
                    user_id=user_id, 
                    website = website,
                    Long = Long,
                    Lat = Lat,
                    title=location_name,
                    recordRefs = [],
                    updateRefs = [],
                    rating=float(0.0),
                    ratingCount=int(0),
                    GPSlocation = str(GPSlocation),
                    todoCount = 0,
                    locationtype = locationtype)
            location_db.put()
            
            location_id=location_db.key.id()
            
            record_db = Record(
                    whatdidyoudo=whatdidyoudo,
                    submitter=submitter,
                    user_id=user_id, 
                    title=title,
                    GPSlocation = GPSlocation,
                    location_id = int(location_id),
                    location_title = location_db.title,
                    postsport = postsport,
                    rating = int(rating),
                    howwasit = howwasit,
                    equipment = equipment,
                    difficulty = difficulty,
                    exceptional = 0,
                    informative = 0,
                    entertaining = 0,
                    groups = []
                    )
            if group_tag != "choose" and group_tag:
                record_db.groups.append(int(group_tag))
                group = Group.get_by_id(int(group_tag))
                record_db.group_names.append(group.name)  
            if tags:
                record_db.tags = tags.split(', ')
            else:
                record_db.tags = []
            record_db.put()
            
            keyid=str(record_db.key.id())
                        
            location_db.ratingCount = location_db.ratingCount + 1
            location_db.rating = float((location_db.rating * (location_db.ratingCount-1) + float(rating))/location_db.ratingCount)
            location_db.recordRefs.append(int(keyid))
            location_db.postsport.append(postsport)
            
            location_db.put()
            
            user_db_qry = User.query(User.theid == user['theid'])
            user_db_list = user_db_qry.fetch(1)
            currentregistereduser = user_db_list[0]
            
            currentregistereduser.prestige = currentregistereduser.prestige + 4
            currentregistereduser.put()
            
            #for some reason user.groups isn't json seralizible 
#            currentregistereduser.created = None
#            currentregistereduser.last_modified = None
#            currentregistereduser.avatar = None
#            self.session['_current_user'] = currentregistereduser.to_dict()

            exployrer_cache(True)
            individual_location_cache(str(location_id), True)
            individual_record_cache(keyid, True)
            record_cache(True)
            location_cache(True)
            if group_tag != "choose" and group_tag:
                group = Group.get_by_id(int(group_tag))
                group.recordCount = group.recordCount + 1
                group.put()
                group_record_cache(group_tag, True)
            
                                    
            self.redirect('/record/%s/%s' % (keyid, title))
                    
        else:
            location_description = self.request.get('location_description')
            location_name = self.request.get('location_name')
            location_address = self.request.get('location_address')
            GPSlocation = self.request.get('GPSlocation')
            locationtype = self.request.get('locationtype')
            whatdidyoudo = self.request.get('whatdidyoudo')
            title = self.request.get('title')
            postsport = self.request.get('postsport')
            rating = self.request.get('rating')
            howwasit = self.request.get('howwasit')
            equipment = self.request.get('equipment')
            difficulty = self.request.get('difficulty')
            group_tag = self.request.get('group_tag')
            tags = self.request.get('tags')
            website = self.request.get('website')
            
            
            error = "Hey Chief you'll need to fill out every field along with a location."                    
            self.render('newlocation.html', user = user, location_description=location_description, location_name=location_name, equipment=equipment,
                         whatdidyoudo=whatdidyoudo, howwasit=howwasit, location_address=location_address, group_tag=group_tag, tags=tags, website=website,  submitter=submitter, user_id=user_id, title=title, GPSlocation = GPSlocation, locationtype = locationtype, error=error)
                   
#this is the location permalink
class LocationPage(BlogHandler):
    def get(self, keyid, title):
        location = individual_location_cache(keyid)
        records = []
        if location.recordRefs != []:
            for ref in location.recordRefs:
                records.append(Record.get_by_id(ref))
        updates = location_update_cache(keyid)
        photos = []
        for record in records:
            if record.blobRefs:
                photos.append(images.get_serving_url(record.blobRefs[0], size=None, crop=False, secure_url=None))
        
        user = self.get_user()
        self.render("locationpermalink.html", user=user, records=records, updates=updates, location=location, photos=photos)
        
    def post(self, keyid, title):
        #if the user posted an update
        content = self.request.get('content')
        user = self.get_user()
        
        if content:                
            submitter = user['username']
            user_id = user['model_id']
            
            u = LocationUpdate(content = content, submitter = submitter, location_id=keyid, user_id = user_id)
            u.put()
            location_update_cache(keyid, True)
            
            self.redirect('/location/%s/%s' % (keyid, title))
        
        #if the user is adding a new Record
        description = self.request.get('description')
        title = self.request.get('title')
        GPSlocation = self.request.get('GPSlocation')
        postsport = self.request.get('postsport')
        rating = self.request.get('rating')
        location_id = self.request.get('location_id')
        location_title = self.request.get('location_title')
        
        #some of the imported GPS coordinated had a strange character in them
        filter(lambda x: x in string.printable, GPSlocation)
            
        submitter = user['username']
        user_id = user['model_id']
        
        title = str(title)
        title = title.replace(' ', '25fdsa67ggggsd5')
        title = ''.join(e for e in title if e.isalnum())
        title = title.replace('25fdsa67ggggsd5', '-')
                
        if description and submitter and user_id and title and GPSlocation and location_id and location_title and postsport and rating:
            record_db = Record(
                    description=description,
                    submitter=submitter,
                    user_id=user_id, 
                    title=title,
                    GPSlocation = GPSlocation,
                    location_id = int(location_id),
                    location_title = location_title,
                    postsport = postsport,
                    rating = int(rating)
                    )
            record_db.put()
            
            keyid=str(record_db.key.id())
            
            location = Location.get_by_id(int(location_id))
            
            location.ratingCount = location.ratingCount + 1
            location.rating = float((location.rating * (location.ratingCount-1) + float(rating))/location.ratingCount)
            location.recordRefs.append(int(keyid))
            location.postsport.append(postsport)
            
            location.put()
            
            user_db_qry = User.query(User.theid == user['theid'])
            user_db_list = user_db_qry.fetch(1)
            currentregistereduser = user_db_list[0]
            
            try:
                currentregistereduser.todolist.remove(int(location_id))
            except ValueError:
                location_id=location_id
            
            currentregistereduser.prestige = currentregistereduser.prestige + 4
            currentregistereduser.put()
            
            currentregistereduser.created = None
            currentregistereduser.last_modified = None
            currentregistereduser.avatar = None
            self.session['_current_user'] = currentregistereduser.to_dict()

            exployrer_cache(True)
            individual_location_cache(location_id, True)
            individual_record_cache(keyid, True)
            record_cache(True)
            
            
            self.redirect('/record/%s/%s' % (keyid, title))
                    
        else:
            description = self.request.get('description')
            title = self.request.get('title')
            GPSlocation = self.request.get('GPSlocation')
            postsport = self.request.get('postsport')
            rating = self.request.get('rating')
            
            location = individual_location_cache(keyid)
            records = []
            if location.recordRefs != []:
                for ref in location.recordRefs:
                    records.append(Record.get_by_id(ref))                
            photos = []
            for record in records:
                if record.blobRefs:
                    photos.append(images.get_serving_url(record.blobRefs[0], size=None, crop=False, secure_url=None))
            
            error = "Hey Chief you'll need to fill out every field along with a location."                    
            self.render('locationpermalink.html', user = user, description=description, location=location, photos=photos,
                        submitter=submitter, user_id=user_id, title=title, GPSlocation = GPSlocation, postsport = postsport, rating = rating, error=error)
            
#displays all of the locations on a map this is the Find tab        
class Map(BlogHandler):
    def get(self):        
        postsport = self.request.get('postsport')
        rating = self.request.get('rating')
        inputlocation = self.request.get("location")
        radius = self.request.get("radius")
        
        user = self.get_user()
        
        GPSlocation = None
        error = None
        locations_to_render = None
        locations = []
        search = False

        
        if postsport or rating or inputlocation:
            
            if postsport != "choose" and rating:
                locations = Location.query().filter(Location.postsport == str(postsport)).order(-Location.rating).fetch(100)
            elif postsport != "choose":
                locations = Location.query().filter(Location.postsport == str(postsport)).order(-Location.rating).fetch(100)
            elif rating:
                locations = Location.query().filter(Location.rating >= float(rating)).order(-Location.rating).fetch(100)
            else:
                locations = location_cache()
            
            if inputlocation:        
                g = geocoders.GoogleV3()
                searched_location = None
                #to catch an error where there is no corresponding location
                try:
                    #to catch an error where there are multiple returned locations
                    try:
                        place, (lat, lng) = g.geocode(inputlocation)
                        place, searched_location = g.geocode(inputlocation)
                    except ValueError:
                        geocodespot = g.geocode(inputlocation, exactly_one=False)
                        place, (lat, lng) = geocodespot[0]
                        place, searched_location = geocodespot[0]
                    GPSlocation = "("+str(lat)+", "+str(lng)+")"
                    
                    new_locations = []                   
                    for location in locations:
                        distance.distance = distance.GreatCircleDistance
                        location_distance = distance.distance(searched_location, point.Point(location.Lat, location.Long)).miles
                        #make this 20 a variable that the user can set and have it be 10, 25, 50, 100, 200
                        if location_distance < int(radius):
                            new_locations.append(location)
                    locations = new_locations
                    search=True
                    locations_to_render = sorted(locations, key=attrgetter('rating'), reverse=True)
                    locations_to_render = locations_to_render[:10]
                #this is straight from the docs:  http://code.google.com/p/geopy/wiki/Exceptions and happens when there is no location that matches
                except geocoders.google.GQueryError:
                    error = "We cannot find " + inputlocation +"... try to be a little more specific or search a nearby location."
                    search=False  
                    
                    self.render('map.html', error=error, user = user)
        else:
            locations = location_cache()
        
        self.render('map.html', locations=locations, radius=radius, centerlocation=GPSlocation, error=error, locations_to_render=locations_to_render, search=search, user = user)

class RecentLocations(BlogHandler):
    def get(self):
        locations = location_cache()
        user = self.get_user()
        
        self.render("recentlocations.html", locations=locations, user=user)
        
class IncorrectLocation(BlogHandler):
    def get(self, location_id, title):              
        location = Location.get_by_id(int(location_id))
        if location:
            if location.incorrect_location:
                location.incorrect_location = location.incorrect_location + 1
            else:
                location.incorrect_location = 1
            location.put()
        
        self.redirect("/location/%s/%s" % (location_id, title))
        
class ListIncorrectLocations(BlogHandler):
    def get(self):
        user = self.get_user()
        if user:
            if user['admin']:
                locations = Location.query(Location.incorrect_location > 0).fetch(200)          
                self.render("listincorrectlocations.html", locations=locations, user=user)
            else:
                self.redirect('/noaccess')
        else:
            self.redirect('/noaccess')


class ModifyLocation(BlogHandler):
    def get(self, location_id, title):              
        user = self.get_user()
        if user:
            if user['admin']:
                location = Location.get_by_id(int(location_id))
                self.render("modifylocation.html", location=location, user=user)
        else:
            self.redirect('/noaccess')
    def post(self, keyid, title):
        location_address = self.request.get('location_address')
                
        user = self.get_user()
            
        submitter = user['username']
        user_id = user['model_id']
        
        GPSlocation = None
        error = None
                
        if location_address:
            
            g = geocoders.GoogleV3()
            location = Location.get_by_id(int(keyid))
            
            #to catch an error where there is no corresponding location
            try:
                #to catch an error where there are multiple returned locations
                try:
                    place, (lat, lng) = g.geocode(location_address)
                    place, searched_location = g.geocode(location_address)
                except ValueError:
                    geocodespot = g.geocode(location_address, exactly_one=False)
                    place, (lat, lng) = geocodespot[0]
                    place, searched_location = geocodespot[0]
                GPSlocation = "("+str(lat)+", "+str(lng)+")"
                Long = lng
                Lat = lat
                

            #this is straight from the docs:  http://code.google.com/p/geopy/wiki/Exceptions and happens when there is no location that matches
            except geocoders.google.GQueryError:
                error = "We cannot find " + location_address +"... try to be a little more specific or search a nearby location."
            
            if error:          
                self.render('modifylocation.html', user = user, error=error, location=location) 
                            
            location.Long = Long
            location.Lat = Lat
            location.GPSlocation = str(GPSlocation)
            location.incorrect_location = 0
            location.put()
            
            for recordRef in location.recordRefs:
                record = Record.get_by_id(recordRef)
                record.GPSlocation = str(GPSlocation)
                record.put()
                individual_record_cache(record.key.id(), True)


            individual_location_cache(str(keyid), True)
            record_cache(True)
            location_cache(True)
                        
            self.redirect('/modifylocation/%s/%s' % (keyid, title))
                    
        else:            
            user = self.get_user()
            
            error = "There is no location address..."                    
            self.render('modifylocation.html', user = user, error=error, location=location) 
                   
        