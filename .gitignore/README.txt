Where is flask run/ app.run supposed to be
set FLASK_APP=
initdb
python -m

How to I recover just the event_id, is my many to many function even right. It has to map user to events and events to user. I think my backref is wrong
backref would be used to see all of the attendees

Would placing a link to cancel an event be possible in the table, how would I be able to differentiate the events and the events the user is hosting
place the cancel link with the event, attend link or cancel link, display on every event, only visible to the people that see it. Check in either templates or controller
check permission in template, or check it in the controller and pass result to the template

Where do you list out the events, is that in layout or homepage and how do i do that.
should only be on the homepage, use the recitation example. Make a table

app.route am i allowed to have 2 variables
/homepage/<user>/<event>