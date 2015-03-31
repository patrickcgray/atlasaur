from google.appengine.api import users
from basehandler import BlogHandler


import secrets

class Tester(BlogHandler):
    def get(self):
        logout = users.create_logout_url(self.request.uri) 
        user = users.get_current_user()
        self.render("working.html", user=user, logout=logout)
        
class SimpleAuthLogin(BlogHandler):
    def get(self):
        self.render("sa_login.html", logged_in = self.logged_in)        
        
class SimpleAuthProfile(BlogHandler):
    def get(self):
    	if not self.logged_in:
            self.redirect("/sa_login")
        else:
    		self.render("sa_profile.html", user_id = self.session['_user_id'], user=self.session['_current_user'], data = pretty_dict(self.session['data']))         

def pretty_dict(dictionary, ident_level = 0):
    retString = ""
    for key, value in dictionary.iteritems():
        line_beggining = "    " * ident_level + '{"' + key + '":'
        line_end = "    " * ident_level + "}<br>"
        if isinstance(value, dict):
            retString += line_beggining + "<br>" + pretty_dict(value, ident_level + 1) + "<br>" + line_end
        else:
            try:
                retString += line_beggining + value + "}"
            except:
                retString += line_beggining + str(value) + "}<br>"
    return retString
            
def print_dict(dictionary, ident = '', braces=1):
    """ Recursively prints nested dictionaries."""

    for key, value in dictionary.iteritems():
        if isinstance(value, dict):
            print '%s%s%s%s' %(ident,braces*'[',key,braces*']') 
            print_dict(value, ident+'  ', braces+1)
        else:
            print ident+'%s = %s' %(key, value)            