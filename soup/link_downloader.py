#!/usr/bin/python

'''
Description - This program finds and downloads all content from the links on the class syllabus i
              on the class website.  It saves the content into a folder under the current working
              directory by week.

Author - Ben Cleveland

'''
import getopt
import sys
import urllib2
from os import mkdir, path
from BeautifulSoup import BeautifulSoup

CLASS_BASE_URL = 'http://briandorsey.info/uwpython'
CLASS_URL = CLASS_BASE_URL + '/Internet_Programming_in_Python.html'

def get_html( url ):
    '''
    Download the html from the given url
    Returns html
    '''

    # pretend to be a web browser
    headers = {'user-agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)'}

    req = urllib2.Request( url, headers=headers )
    response = urllib2.urlopen( req )

    return response.read()

def get_weeks_urls( html ):
    '''
    Return a list of the urls for the week
    Also returns the name of the week
    '''

    week_name = ''
    week = html.findAll('td')
    links = []

    for table_section in week:
        # get the week name - this will be used for the directory structure
        if table_section.has_key('id'): 
            week_name = table_section['id']

        for link in table_section.findAll('a'):
            # get all the links
            if link.has_key('href') and link['href'] != '':
                # save the link and its name
                links.append( (link['href'],link.text ) )

    return week_name, links

def download_links(directory, links ):    
    '''
    Downloads all the links into the given directory
    '''
    
    print '\nDownloading files for', directory

    # check to see if the directory exists
    if path.exists( directory ) != True:
        # create the directory
        mkdir(directory)

    for (link,name) in links:
        file_extension = '.html'

        if link.lower().endswith('.pdf'):
            # add the base url if this is a pdf
           link = CLASS_BASE_URL + '/' + link 
           file_extension = '.pdf'
        elif link.lower().startswith('http') == False:
            # can't handle this link...
            print 'Do not know how to handle link,', link, name
            continue
       
        # create the filename
        filename =  directory + '/' + name.replace(' ','_').replace('/','_').lower() + file_extension
        print 'Downloading from',link, 'to', filename

        # download the data
        data = get_html( link )

        #open the file and write to the file
        file = open(filename,'w')
        file.write( data )
        file.close()

def interactive_menu( data_list ):
    '''
    Print the menu to give the user the option of what set of data
    to download
    '''
    i = 1
    print '\nWelcome to the class link downloader'
    for (week_name, urls) in data_list:
        print str(i) + ':', week_name
        i += 1
    print 'a: Download all' 
    print '0: Exit'

    return raw_input('Enter selection-> ')

def handle_user_input( data_list ):
    '''
    This function handles the user input from the interactive menu
    '''
    # call the interative menu
    while True:
        selection = interactive_menu( data_list )
        try:
            # convert to int 
            selection = int(selection)
        except:
            if selection == 'a':
                # download everything
                for week_name, urls in data_list:
                    download_links( week_name, urls)
            else:
                print 'Invalid number entered...\n'
            continue

        if selection > 0 and selection <= len(data_list):
            # download the data
            week_name, urls = data_list[selection-1]
            download_links( week_name, urls )
        elif selection == 0:
            # exit
            break
        else:
            print 'Invalid selection...\n'
    
def handle_options():
    '''
    handle commandline options
    Returns True if all the links should be downloaded
    '''

    try:
        opts, args = getopt.getopt(sys.argv[1:], "ha")
    except getopt.GetoptError, err:
        print str(err)
        sys.exit(2)

    download_all = False
    for o, a in opts:
        if o == '-a':
            download_all = True
        elif o == '-h':
            usage()
            sys.exit()
        else:
            usage()
            sys.exit()

    return download_all

def usage():
    '''
    print the program usage
    '''
    print 'link_downloader help...'
    print 'Usage: link_downloader [OPTION]'
    print '\nDownload links from the class website (', CLASS_URL, ')'
    print 'By default this program runs in interactive mode'
    print 'Options:'
    print '-a               Download all links for each week (non-interactive mode)'
    print '-h               This help message'

def main():
    '''
    main funtion for the link downloader
    '''
    data_list = []

    # handle options
    download_all = handle_options()

    # get the class webpage
    class_html = get_html( CLASS_URL )
    
    # parse the html with BeautifulSoup
    soup = BeautifulSoup( class_html )
    
    # get the first table
    table = soup.findAll('tr')
   
    for row in table:
        urls = []
        # get the weeks urls        
        week_name,urls = get_weeks_urls( row )
        if week_name != '' and urls != []:
            data_list.append((week_name,urls))
    
    if download_all:
        #download everything
        for week_name, urls in data_list:
            download_links( week_name, urls)
    else:
        # go into interative mode
       handle_user_input( data_list )


if __name__ == '__main__':
   main() 
