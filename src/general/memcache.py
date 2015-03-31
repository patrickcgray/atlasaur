#this document has all of my memcache

#these are my general imports to make it function
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext import ndb
import logging
from operator import attrgetter

#these are my imports from my other projects
from dbmodels import Post
from dbmodels import Record
from dbmodels import Location
from dbmodels import LocationUpdate
from dbmodels import User
from dbmodels import Comment
from dbmodels import RecordComment
from dbmodels import Group
from dbmodels import GroupComment
from dbmodels import Vote


def main_cache(update = False):
    key = 'main'
    posts = memcache.get(key) 
    if posts is None or update:
        logging.error('DB QUERY')
        posts = db.GqlQuery("select * from Post order by created desc limit 50")
        posts = list(posts)
        memcache.set(key, posts)
    #need to decide how I want to implement this
    return posts

#this is the memcache for the top 20 ranked Posts of Exployre
def ranked_cache(update = False):
    key = 'ranked'
    posts = memcache.get(key)
    if posts is None or update:
        logging.error('DB QUERY')
        posts = db.GqlQuery("select * from Post order by ranking desc limit 25")
        posts = list(posts)
        memcache.set(key, posts)
    #need to decide how I want to implement this
    return posts

def daily_ranked_cache(update = False):
    key = 'dailyranked'
    posts = memcache.get(key)
    if posts is None or update:
        logging.error('DB QUERY')
        posts = db.GqlQuery("select * from Post order by created desc limit 10")
        #this sorts by the ranking category
        posts = sorted(posts, key=attrgetter('ranking'), reverse=True)
        posts = list(posts)
        memcache.set(key, posts)
    return posts

def admin_cache(update = False):
    key = 'admin_posts'
    posts = memcache.get(key)
    if posts is None or update:
        logging.error('DB QUERY')
        admin = "admin"
        posts = db.GqlQuery("select * from Post where sport=:1 order by created desc limit 3", admin)
        #this sorts by the ranking category
        posts = list(posts)
        memcache.set(key, posts)
    return posts

#this is what shows up on the User's profile pages.
def profile_cache(user_id, update = False):
    key=str(user_id)+"_personalpost"
    posts = memcache.get(key)
    logging.error('accessing profile')
    logging.error(posts)
    if posts is None or update:
        logging.error('DB QUERY')
        posts = db.GqlQuery("select * from Post where user_id=:1 order by created desc limit 20", int(user_id))
        posts = list(posts)
        logging.error(posts)
        memcache.set(key, posts)
    return posts

def profile_record_cache(user_id, update = False):
    key=str(user_id)+"_personalrecord"
    records = memcache.get(key)
    logging.error('accessing profile')
    logging.error(records)
    if records is None or update:
        logging.error('DB QUERY')
        records = Record.query(Record.user_id == user_id).order(-Record.created)
        records = list(records)
        logging.error(records)
        memcache.set(key, records)
    return records

def profile_todo_cache(user_id, update = False):
    key=str(user_id)+"_personaltodo"
    todolist = memcache.get(key)
    logging.error('accessing profile')
    logging.error(todolist)
    if todolist is None or update:
        logging.error('DB QUERY')
        user = User.get_by_id(int(user_id))
        todolist = user.todolist
        todolist = list(todolist)
        logging.error(todolist)
        memcache.set(key, todolist)
    return todolist

#this is not correct and needs to be fixed to do the main page
def record_cache(update = False):
    key="records"
    records = memcache.get(key)
    if records is None or update:
        logging.error('DB QUERY')
        records =  Record.query().order(-Record.created).fetch(200)
        records = list(records)
        memcache.set(key, records)
    return records

def recent_record_cache(update = False):
    key="recent_records"
    records = memcache.get(key)
    if records is None or update:
        logging.error('DB QUERY')
        records =  Record.query().order(-Record.created).fetch(10)
        records = sorted(records, key=attrgetter('exceptional'), reverse=True)
        records = list(records)
        memcache.set(key, records)
    return records

def ranked_location_cache(update = False):
    key="locations_ranked"
    locations = memcache.get(key)
    if locations is None or update:
        logging.error('DB QUERY')
        locations =  Location.query().order(-Location.rating).fetch(10)
        locations = list(locations)
        memcache.set(key, locations)
    return locations

def location_cache(update = False):
    key="locations"
    locations = memcache.get(key)
    if locations is None or update:
        logging.error('DB QUERY')
        locations = Location.query().order(-Location.created).fetch(500)
        locations = list(locations)
        memcache.set(key, locations)
    return locations

#this is the location page memcache to display its LocationUpdates
def location_update_cache(location_id, update = False):
    key=location_id+"locations"
    updates = memcache.get(key)
    if updates is None or update:
        logging.error('DB QUERY')
        updates = LocationUpdate.query(LocationUpdate.location_id == location_id).order(-LocationUpdate.created).fetch(10)
        updates = list(updates)
        memcache.set(key, updates)
    return updates

#this is the records for each Location page
def location_page_record_cache(keyid, update = False):
    key=str(keyid)+"_location_page_record"
    logging.error('individual record cache')
    logging.error(keyid)
    record = memcache.get(key)
    if record is None or update:
        logging.error('DB QUERY')
        record = Record.get_by_id(int(keyid))
        memcache.set(key, record)
    return record

#this is the memcache for each individual page.  don't forget you can't use post = list(post) here b/c there is only one object
def individual_record_cache(keyid, update = False):
    key=str(keyid)+"_record"
    logging.error('individual record cache')
    logging.error(keyid)
    record = memcache.get(key)
    if record is None or update:
        logging.error('DB QUERY')
        record = Record.get_by_id(int(keyid))
        memcache.set(key, record)
    return record

def individual_location_cache(keyid, update = False):
    key=str(keyid)+"_location"
    logging.error('individual location cache')
    logging.error(keyid)
    location = memcache.get(key)
    if location is None or update:
        logging.error('DB QUERY')
        location = Location.get_by_id(int(keyid))
        memcache.set(key, location)
    return location

#this is the memcache of top Exployre users ranked by their prestige
def exployrer_cache(update = False):
    key = 'exployrers'
    users = memcache.get(key)
    if users is None or update:
        logging.error('DB QUERY')
        qry = User.query().order(-User.created, User.name)
        users = qry.fetch(10)
        users = list(users)
        memcache.set(key, users)
    return users

#this is the memcache of comments for each post
def comment_cache(postid, update = False):
        key = str("comment_" + postid)
        comments = memcache.get(key)
        if comments is None or update:
                logging.error("DB QUERY")
                comments = Comment.query(Comment.postid == postid).order(Comment.created).fetch(50)
                comments = list(comments)
                memcache.set(key, comments)
        return comments

def record_comment_cache(keyid, update = False):
        key = str("record_comment_" + keyid)
        comments = memcache.get(key)
        if comments is None or update:
                logging.error("DB QUERY")
                comments = RecordComment.query(RecordComment.keyid == keyid).order(RecordComment.created).fetch(50)
                comments = list(comments)
                memcache.set(key, comments)
        return comments

def group_cache(update=False):
    key = 'groups'
    groups = memcache.get(key)
    if groups is None or update:
        logging.error('DB QUERY')
        qry = Group.query(Group.public == True).order(-Group.created)
        groups = qry.fetch(200)
        groups = list(groups)
        memcache.set(key, groups)
    return groups

def group_record_cache(group_id, update = False):
        key = "group_records" + str(group_id)
        records = memcache.get(key)
        if records is None or update:
                logging.error("DB QUERY")
                records = Record.query(Record.groups == int(group_id)).order(-Record.created).fetch(50)
                records = list(records)
                memcache.set(key, records)
        return records
    
def group_member_cache(group_id, update = False):
        key = "group_members" + str(group_id)
        members = memcache.get(key)
        if members is None or update:
                logging.error("DB QUERY")
                members = User.query(User.groups == int(group_id)).fetch(50)
                members = list(members)
                memcache.set(key, members)
        return members
    
def group_comment_cache(group_id, update = False):
    key=str(group_id)+"group_comments"
    comments = memcache.get(key)
    if comments is None or update:
        logging.error('DB QUERY')
        comments = GroupComment.query(GroupComment.group_id == int(group_id)).order(-GroupComment.created).fetch(10)
        comments = list(comments)
        memcache.set(key, comments)
    return comments