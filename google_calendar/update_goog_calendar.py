try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
import gdata.calendar.data
import gdata.calendar.client
import gdata.acl.data
import atom
import getopt
import sys
import string
import time

import team_cowboy

email = raw_input('Enter email -> ')
password = raw_input('Enter password -> ')


# connect
client = gdata.calendar.client.CalendarClient(source='Ben-Cleveland-schedule_updater-1.0')
client.ClientLogin( email, password, client.source)


feed = client.GetCalendarEventFeed()
for i, a_calendar in zip(xrange(len(feed.entry)), feed.entry):
    print '%s, %s' %(i, a_calendar.title.text)


# get team cowboy info
username = raw_input('Enter username ->')
password = raw_input('Enter password ->')
login = team_cowboy.team_cowboy_login(username, password)
teamids = team_cowboy.team_cowboy_get_teamid( login['body']['token'] )

games = team_cowboy.team_cowboy_get_team_schedule( login['body']['token'], teamids ) 


for game in games:
    event = gdata.calendar.data.CalendarEventEntry()
    event.title = atom.data.Title(text=game['title'])
    event.content = atom.data.Content(text=game['content'])
    event.where.append(gdata.data.Where(value=game['content']))

        # Use current time for the start_time and have the event last 1 hour
    end_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z',
            time.gmtime(time.time() + 3600))
    start_time = game['starttime'].replace(' ','T')
    end_time = game['endtime'].replace(' ','T')
    print start_time
    event.when.append(gdata.data.When(start=start_time,
          end=end_time))

    new_event = client.InsertEvent(event)

