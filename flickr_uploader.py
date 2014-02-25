#!/usr/bin/python
import sys
try:
    import flickr_api
except:
    print ('please, install flickr_api: https://github.com/alexis-mignon/python-flickr-api/')
import argparse
import re
    

parser = argparse.ArgumentParser(description='Upload photos to the user\'s photostream.')
subparsers = parser.add_subparsers()

parser_init=subparsers.add_parser('init', help='set to init mode')
parser_init.set_defaults(mode='init')

parser_upload=subparsers.add_parser('upload',help='set to upload mode')
parser_upload.add_argument('-AC','--access-handler',required=True,default='access_handler',help='Path to flickr''s app write handler')
parser_upload.add_argument('-P','--photos',required=True,help='Path of uploading photos',nargs='*')
parser_upload.set_defaults(mode='upload')

parser_info=subparsers.add_parser('info',help='set to info mode')
parser_info.add_argument('-U','--username',required=True, help='Flickr''s user\'s username')
parser_info.set_defaults(mode='info')

def generate_handler():
    """Generates flickr api handler if it does not exist. Saves handler to file with inputed filename"""
    
    print ('To use this script, you must grant read and modify permissions to it by generating special access handler.\nLet\'s do it')
    print ('Fisrt step is to go to your flickr\'s profile and open AppGarden.\nIf you are logged in, you can use this url -> http://www.flickr.com/services/apps/')
    print ('You need to get an api key. When you get api key and secret, tell it to the application ')
    my_api_key=raw_input('My api key: ')
    my_secret=raw_input('My secret: ')
    perms=raw_input('Permissions: read, write (includes read), delete (includes write): ')
    
    try:
        flickr_api.set_keys(api_key = my_api_key, api_secret = my_secret)
    except:
        print ('Somth goes wrong with your keys. Try again')
    
    def check_perms(perms):
        """Checks permissions for correct input"""
        
        if (perms=='read' or perms=='write' or perms=='delete'):
            pass        
        else:
            print ('please, re-enter permissions. you can choose "read" or "write" or "delete" option')
            perms=raw_input('Enter permissions: ')
            perms=check_perms(perms)
        return perms

    perms=check_perms(perms)
    #generate handler
    access_handler = flickr_api.auth.AuthHandler()
    url = access_handler.get_authorization_url(perms)
    print ('Please, open url: %s and get auth code'%url)
    auth_code=raw_input('Pleas, enter auth code. It is in <oauth_verifier> tag:')
    access_handler.set_verifier(auth_code)
    flickr_api.set_auth_handler(access_handler)
    filename=raw_input('Enter filename to store your access handler. it is needed by scrypt to get access to your account:')
    access_handler.save(filename)



def print_info(username):
    """Function, that outputs userinfo """
    
    try:
        user=flickr_api.Person.findByUserName(username)
        print ('Username:\' %s\' and user ID: \'%s\' '%(user.username,user.id))
        #flickr_api.set_auth_handler(access_handler)
        photos = user.getPublicPhotos()
        print ('Total photos: %s\nPages:%s'%(photos.info.total,photos.info.pages))
        print (user.id)
        return (user.id)
    except:
        print ('Someone, you or me, fucked up with username or connection')
        return ('snafu')

def upload(path):
    """Function, that uploads photos """
    
    urls={} 
    faild_files=[]
    for i in range(len(path)):
        try:
            upload_result=flickr_api.upload(photo_file =path[i])
            urls[upload_result.title]=flickr_api.Photo.getPageUrl(upload_result)
        except:
            faild_files.append(path[i]) 
    return urls,faild_files

def output_urls(urls,faild_files):
    """Function, that outputs upload results e.g. uploaded photo title and url """
    
    if (urls):
        print ('seems, that we successfully uploaded some photos, and here are results:')
        for key in urls:
            print ('photo title: %s URL: %s'%(key,urls[key]))
        if (faild_files):
            print ('There are some files, that we couldn\'t upload: ')
            for i in range(len(faild_files)):
                print (faild_files[i])
    else:
        print ('We really try to upload, but we faild')
        urls={}
        faild_files=[]
    
    return (urls,faild_files)



#executable part

if __name__ == "__main__":
    args= parser.parse_args()
    mode=args.mode

    if (mode=='init'):
        generate_handler()
    else:
        if (mode=='info'):
            username=args.username
            print_info(username)
        else:
            access_handler=args.access_handler
            flickr_api.set_auth_handler(access_handler)
            path=args.photos
            urls,faild_files=upload(path)
            output_urls(urls,faild_files)

            


