This webapp is split into three main categories:

general/
	this contains the database models and all of the memcache information.
	when extra code is developed and doesn't have a clear home it will go here
pagehandlers/
	this code has all of the page handlers which are divided up into more specific categories
blog.py
	this is the page that brings it all together and imports all of the handlers to do all of the routing

In addition to those three main categories there are the:
static/
	this contains the javascript and css
templates/
	all of the HTML page templates are here

And in addition to all that I have the imported modules which are used throughout the project.

**Special note for SimpleAuth Integration
The BaseHandler that I use for all of my handlers is in pagehandlers/basehandler.py and is called BlogHandler.  
If you can use this or make your own base handler and then just make another file in pagehandlers that implements the SimpleAuth framework by doing something like displaying the user name or email or something.
If you can do the above two along with creating a login page that actually lets the user log in that would be great.  My current login page is in pagehandlers/otherhandlers.py but that one uses the Google Federated Login

That is all I need you to do but just for your information when I do my current authentication I redirect them to the root page and then check if I have the user
in my database and if not I create an entry.  I can take care of that so don't worry about it but I just wanted to let you know of the way I currently have it set up.

Let me know if you have any further questions.