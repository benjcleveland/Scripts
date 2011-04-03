#!/usr/bin/python

import urllib2
import urllib
import time
import hashlib 
import sys

import cowboy_keys

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        from django.utils import simplejson as json


class TeamCowboyApi:

    def __init__( self, use_gae=False ):
        '''
        initialize the class
        '''
        self.use_gae = use_gae
        if self.use_gae:
            # import urlfetch
            from google.appengine.api import urlfetch


    def build_url(self, method ):

        url_dict = { 'api_key' : cowboy_keys.PUBLIC_KEY,
                'method' : method,
                'nonce' : str(time.time()),
                'timestamp' : str(int(time.time())),
                'response_type' : 'json',
                }

        return url_dict

    def url_request(self, url_args, data='', m='get' ):
        '''
        depending on how the class was created, it will use urlfetch (Google app engine) or urllib2
        '''
        headers = {'user-agent': ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)')}
        result = '' 
        if self.use_gae:

            method = { 'post':urlfetch.POST,
                    'get':urlfetch.GET,
                    }
            fetch_result = urlfetch.fetch(url=(url_args), payload=(data), headers=headers, method= method.get(m,urlfetch.GET))
            result = fetch_result.content

        else:
            # don't use urlfetch
            if m == 'get':
                url = urllib2.Request(url_args, headers=headers)
            elif m =='post':
                url = urllib2.Request(url_args,data, headers=headers)

            res = urllib2.urlopen(url)
            result = res.read()

        return result

    def create_url_string(self, url_dict ):
        '''
        create a sorted url form the dictionary
        '''
        url_string = ''
        for key in sorted( url_dict.iterkeys()):
            url_string = '&'.join([url_string, '='.join([key ,urllib.quote(url_dict[key])])])
        return url_string[1:]

    def create_sig(self, url_dict, req_type ):
        p_api_key = cowboy_keys.PRIVATE_KEY

        url_string = self.create_url_string(url_dict).lower()
        sig_string = '|'.join([p_api_key, req_type, url_dict['method'], url_dict['timestamp'], url_dict['nonce'],url_string])

        # create the hash
        h = hashlib.sha1( sig_string ).hexdigest()

        # save it
        url_dict['sig'] = h

    def team_cowboy_test(self, test_string ):

        url_dict = self.build_url('Test_GetRequest')

        url_dict['testParam'] = test_string


        # create the sig
        self.create_sig( url_dict, 'GET')

       # url_dict = sorted(url_dict, key=url_dict.iterkeys())
        request = self.create_url_string(url_dict)

        '''
        headers = {'user-agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)'}
        url = urllib2.Request('http://api.teamcowboy.com/v1/?' + request, headers=headers)
        res = urllib2.urlopen(url)
        '''
        url = 'http://api.teamcowboy.com/v1/?' + request
        res = self.url_request(url)
        #data = res.read()
        #print data
        print res


    def team_cowboy_test_post(self, test_string ):

        url_dict = self.build_url('Test_PostRequest')
        url_dict['testParam'] = test_string

        self.create_sig( url_dict, 'POST')

        request = self.create_url_string(url_dict)

        headers = {'user-agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)'}
        '''
        url = urllib2.Request('http://api.teamcowboy.com/v1/', data=request, headers=headers)
        res = urllib2.urlopen(url)
        '''
        #data = res.read()
        #print data

        url = 'http://api.teamcowboy.com/v1/?' 
        res = self.url_request(url, data=request, m='post')
        print res

    def team_cowboy_login(self, username, password ):

        url_dict = self.build_url('Auth_GetUserToken')
        url_dict['username'] = username
        url_dict['password'] = password

        # create sig
        self.create_sig( url_dict, 'POST')

        request = self.create_url_string( url_dict )

        '''
        headers = {'user-agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)'}
        url = urllib2.Request('https://api.teamcowboy.com/v1/', data=request, headers=headers)
        res = urllib2.urlopen(url)
        '''
        url = str('https://api.teamcowboy.com/v1/?')
        res = self.url_request(url, data=request, m='post')
        #data = json.loads( res.read())
        data = json.loads( res)
        return data 



    def team_cowboy_get_teamid(self, usertoken ):

        url_dict = self.build_url('User_GetTeams')
        url_dict['userToken'] = usertoken 

        # create sig
        self.create_sig( url_dict, 'GET')

        request = self.create_url_string( url_dict )

        ''' 
        headers = {'user-agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)'}
        url = urllib2.Request('https://api.teamcowboy.com/v1/?' + request, headers=headers)
        res = urllib2.urlopen(url)
        '''
        url = 'http://api.teamcowboy.com/v1/?' + request
        res = self.url_request(url)

        #data = json.loads( res.read())
        data = json.loads( res)

        ids = []
        for value in data['body']:
            #print 'team name', value['name']
            #print 'city', value['city']
            ids.append((value['name'],value['teamId']))
        return ids 

    def team_cowboy_get_team_members(self,usertoken,  teamid ):

        name_list = [] 

        for (name,team) in teamid:

            url_dict = self.build_url('Team_GetRoster')
            url_dict['userToken'] = usertoken 
            url_dict['teamId'] = team
            url_dict['userId'] = ''
            url_dict['includeInactive'] = 'False'
            url_dict['sortBy'] = ''
            url_dict['sortDirection'] = '' 

            # create sig
            self.create_sig( url_dict, 'GET')

            request = self.create_url_string( url_dict )

            '''
            headers = {'user-agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)'}
            url = urllib2.Request('https://api.teamcowboy.com/v1/?' + request, headers=headers)
            res = urllib2.urlopen(url)
            '''

            url = 'http://api.teamcowboy.com/v1/?' + request
            res = self.url_request(url)
    
            #data = json.loads( res.read())
            data = json.loads( res)


            #print 'Team ', name
            #for value in data['body']:
                #print value['firstName'], value['lastName'], value['emailAddress1'], value['phone1']

            #name_list[name] = data
            data['teamname'] = name
            name_list.append(data)

        return name_list 

    def team_cowboy_get_team_schedule(self, usertoken, teamids):

        ret = []

        for (name, team) in teamids:

            url_dict = self.build_url('User_GetTeamEvents')
            url_dict['userToken'] = usertoken
            url_dict['teamId'] = team
            url_dict['startDateTime'] = ''
            url_dict['endDateTime'] = ''

            self.create_sig( url_dict, 'GET' )
    
            request = self.create_url_string( url_dict )


            headers = {'user-agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)'}
            url = urllib2.Request('https://api.teamcowboy.com/v1/?' + request, headers=headers)
            res = urllib2.urlopen(url)

            data = json.loads( res.read())

            print name
            for value in data['body']:
                print value['oneLineDisplay']  + value['location']['name'] + value['dateTimeInfo']['startDateTimeLocal']

                ret.append({ 'title': value['oneLineDisplay'], 'content': value['location']['name'], 'starttime':value['dateTimeInfo']['startDateTimeLocal'], 'endtime':value['dateTimeInfo']['endDateTimeLocal'] })

        return ret
if __name__ == '__main__':

    # test it all out
    tc_api = TeamCowboyApi()
# login
    tc_api.team_cowboy_test( 'Ben is')
    tc_api.team_cowboy_test_post( 'Ben is')
    # this call will fail without a user name and password
    username = raw_input('Enter username ->')
    password = raw_input('Enter password ->')
    login = tc_api.team_cowboy_login(username, password)
    teamids = tc_api.team_cowboy_get_teamid( login['body']['token'] )
    #names = team_cowboy_get_team_members(login['body']['token'], teamids )
    #for key in names:
    #    print names[key]

    tc_api.team_cowboy_get_team_schedule( login['body']['token'], teamids ) 
