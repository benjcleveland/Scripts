#!/usr/bin/python

import urllib2
import urllib
import time
import hashlib 
import json
import sys

import cowboy_keys

def build_url( method ):
    
    url_dict = { 'api_key' : cowboy_keys.PUBLIC_KEY,
                'method' : method,
                'nonce' : str(time.time()),
                'timestamp' : str(int(time.time())),
                'response_type' : 'json',
    }
    
    return url_dict

def create_url_string( url_dict ):
    '''
    create a sorted url form the dictionary
    '''
    url_string = ''
    for key in sorted( url_dict.iterkeys()):
       url_string = '&'.join([url_string, '='.join([key ,urllib.quote(url_dict[key])])])
    return url_string[1:]

def create_sig( url_dict, req_type ):
    p_api_key = cowboy_keys.PRIVATE_KEY

    url_string = create_url_string(url_dict).lower()
    sig_string = '|'.join([p_api_key, req_type, url_dict['method'], url_dict['timestamp'], url_dict['nonce'],url_string])

    # create the hash
    h = hashlib.sha1( sig_string ).hexdigest()

    # save it
    url_dict['sig'] = h


def team_cowboy_test( test_string ):
    print 'test'
    
    url_dict = build_url('Test_GetRequest')

    url_dict['testParam'] = test_string
    
    # create the sig
    create_sig( url_dict, 'GET')

   # url_dict = sorted(url_dict, key=url_dict.iterkeys())
    request = create_url_string(url_dict)
    headers = {'user-agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)'}
    url = urllib2.Request('http://api.teamcowboy.com/v1/?' + request, headers=headers)
    res = urllib2.urlopen(url)
    data = res.read()
    print data


def team_cowboy_test_post( test_string ):
    print 'test'

    url_dict = build_url('Test_PostRequest')
    url_dict['testParam'] = test_string

    create_sig( url_dict, 'POST')

    request = create_url_string(url_dict)

    headers = {'user-agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)'}
    url = urllib2.Request('http://api.teamcowboy.com/v1/', data=request, headers=headers)
    res = urllib2.urlopen(url)
    data = res.read()
    print data

def team_cowboy_login( username, password ):
    print 'test'

    url_dict = build_url('Auth_GetUserToken')
    url_dict['username'] = username
    url_dict['password'] = password

    # create sig
    create_sig( url_dict, 'POST')

    request = create_url_string( url_dict )

    headers = {'user-agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)'}
    url = urllib2.Request('https://api.teamcowboy.com/v1/', data=request, headers=headers)
    res = urllib2.urlopen(url)

    data = json.loads( res.read())

    return data



def team_cowboy_get_teamid( usertoken ):

    url_dict = build_url('User_GetTeams')
    url_dict['userToken'] = usertoken 

    # create sig
    create_sig( url_dict, 'GET')

    request = create_url_string( url_dict )

    headers = {'user-agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)'}
    url = urllib2.Request('https://api.teamcowboy.com/v1/?' + request, headers=headers)
    res = urllib2.urlopen(url)

    data = json.loads( res.read())

    ids = []
    for value in data['body']:
        print 'team name', value['name']
        print 'city', value['city']
        ids.append((value['name'],value['teamId']))
    return ids 

def team_cowboy_get_team_members(usertoken,  teamid ):

    name_list = {} 

    for (name,team) in teamid:

        url_dict = build_url('Team_GetRoster')
        url_dict['userToken'] = usertoken 
        url_dict['teamId'] = team
        url_dict['userId'] = ''
        url_dict['includeInactive'] = 'False'
        url_dict['sortBy'] = ''
        url_dict['sortDirection'] = '' 

        # create sig
        create_sig( url_dict, 'GET')

        request = create_url_string( url_dict )

        headers = {'user-agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)'}
        url = urllib2.Request('https://api.teamcowboy.com/v1/?' + request, headers=headers)
        res = urllib2.urlopen(url)

        data = json.loads( res.read())

   
        print 'Team ', name
        for value in data['body']:
            print value['firstName'], value['lastName'], value['emailAddress1'], value['phone1']

        name_list[name] = data

    return name_list 

def team_cowboy_get_team_schedule( usertoken, teamids):

    for (name, team) in teamids:

        url_dict = build_url('User_GetTeamEvents')
        url_dict['userToken'] = usertoken
        url_dict['teamId'] = team
        url_dict['startDateTime'] = ''
        url_dict['endDateTime'] = ''

        create_sig( url_dict, 'GET' )

        request = create_url_string( url_dict )


        headers = {'user-agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)'}
        url = urllib2.Request('https://api.teamcowboy.com/v1/?' + request, headers=headers)
        res = urllib2.urlopen(url)

        data = json.loads( res.read())

        print name
        for value in data['body']:
            print value['oneLineDisplay']  + value['location']['name']

if __name__ == '__main__':

    # test it all out
# login
    team_cowboy_test( 'Ben is')
    team_cowboy_test_post( 'Ben is')
    # this call will fail without a user name and password
    username = raw_input('Enter username ->')
    password = raw_input('Enter password ->')
    login = team_cowboy_login(username, password)
    teamids = team_cowboy_get_teamid( login['body']['token'] )
    #names = team_cowboy_get_team_members(login['body']['token'], teamids )
    #for key in names:
    #    print names[key]

    team_cowboy_get_team_schedule( login['body']['token'], teamids ) 
