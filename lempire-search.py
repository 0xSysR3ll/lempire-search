# -*- coding: utf-8 -*-
from requests.sessions import Session
from termcolor import colored
import requests as req
from bs4 import BeautifulSoup as bs4
import time
import random
from json.decoder import JSONDecodeError
import json
import os
import re
import argparse

path = os.getcwd()


def y(string):
    return colored(string, 'yellow')


def g(string):
    return colored(string, 'green')


def r(string):
    return colored(string, 'red')


class Lampyre:

    def __init__(self, email, password) -> None:
        self.email = email
        self.password = password

        """
        Create a new account on Lampyre.io \n
        """

        ##              Registering part                ##

        url = "https://lampyre.io/api/1.6/accounts"

        data = '{"email": "'+email+'", "password": "'+password+'"}'
        headers = {
            'Content-Type': 'application/json',
        }
        s = req.Session()
        # Registration consists in a simple post request which returns a 201 http code
        register = s.post(url=url,
                          headers=headers, data=data).status_code
        if register == 201:
            pass
        else:
            raise exit(
                r(f"Could not register an account on Lampyre. Error code : {register}"))
        pass

        ##              Account validation part                 ##

    def validate(self, confirmation_link):
        confirmation_api = "https://lampyre.io/api/1.6/confirm"
        email = self.email

        token = confirmation_link.split("/")[-1].strip()
        headers = {"Content-type": "application/json"}
        validate = req.put(url=confirmation_api+'/'+token,
                           headers=headers)  # Validate with PUT request
        if validate.status_code == 201 and email in validate.json()["email"]:
            # If the account is validated, the response is 200 OK => json {"email", email}
            pass
        else:
            raise exit(
                r(f"Error while retriving the response : {validate.status_code}"))

        ##                  Login part                      ##

    def login(email, password) -> Session:
        """
        Returns an http session object after login to Lampyre's api.
        > lampyre = Lampyre(email, password)
        > lampyre = lampyre.login()
        > cookies = lampyre.cookies.get_dict()
        """

        data = '{"login": "'+email+'", "password": "'+password+'"}'
        headers = {"Content-type": "application/json"}
        login_api = "https://account.lampyre.io/api/1.6/login"
        s = req.Session()
        log = s.post(url=login_api, data=data,
                     headers=headers, allow_redirects=True)
        if log.status_code == 201:
            pass
        else:
            raise exit(
                r(f"Error while retriving the response : {log.status_code}"))
        return s

        ##                  Activation key                      ##

    def activation_key(self, s):
        license_api = "https://account.lampyre.io/api/1.6/subscriptions?type=license&limit=10"
        r = s.get(
            url=license_api)
        if r.status_code == 200:
            activation_key = r.json(
            )['subscriptions'][0]['license_keys'][0].strip()
        else:
            activation_key = 'None'
        return activation_key

        ##              Delete account key                      ##

    def delete(self, s):
        account_api = "https://lampyre.io/api/1.6/accounts"
        headers = {'Content-type': 'application/json'}

        s.delete(account_api, headers=headers)

        ##                  Query part                          ##
    def query(s, query_type, query):
        # Function to use Lampyre api to request infos
        query_start = time.time()
        query_api = "https://account.lampyre.io/api/1.6/find"
        headers = {'Content-type': 'application/json'}
        query = {str(query_type): str(query)}
        query_uuid = ""

        try:
            query_uuid = s.get(
                query_api, params=query, headers=headers).json()['request_uuid']
        except:
            query_uuid = "None"
            #print(f"{y('INFO : ')} 4 request/day limit exceeded. Need to create a new account.")
            # The request on the api generated a query_uuid which will be used to refresh content
        if query_uuid != "None":
            json_results = s.get(query_api+'/'+query_uuid).json()
            # ['status'] indicates the status of the request
            # 1 - the request is in progress
            # 2 - the request is fulfilled
            # 3 - the request is failed
            while json_results['status'] == 1:
                json_results = s.get(query_api+'/'+query_uuid).json()
                #soup = bs4(json_results, features='html_parser')

                if json_results['status'] == 3:
                    raise exit(r(f"No result found for {query} !"))
            query_end = time.time()
            print(
                f"[{g('+')}] Results found in {round(query_end - query_start, 2)} s !")
        else:
            pass

        return json_results


class Mohmal:
    """
    Class to use the temporary mail provider Mohmal.

    > inbox = Mohmal() \n
    > email = inbox.email \n
    > message = inbox.read() \n
    => Disclaimer : It is only set up for this program.
    """

    def __init__(self) -> None:
        inbox = "https://www.mohmal.com/fr/inbox"
        email = ""

        # Generate the temporary mail :
        session = req.Session()
        page = session.get(url=inbox).content.decode('utf-8')
        soup = bs4(page, features='html.parser')
        mail_search = soup.findAll(
            'div', {'data-clipboard-target': '#email .email', })
        for result in mail_search:
            try:
                email = result.get('data-email')
            except:
                pass
        if email == "":
            raise exit(
                r("Couldn't get new temporary mail. Maybe because of the 30 mailbox/day/ip"))

        self.email = email
        self.inbox = session

    def read(self):
        inbox_url = "https://www.mohmal.com/fr/inbox"
        refresh_rul = "https://www.mohmal.com/fr/refresh"
        read_url = "https://www.mohmal.com/fr/message/{0}"

        session = self.inbox
        # Refresh the page
        time.sleep(2)
        session.get(refresh_rul)

        # Get new content of page
        content = session.get(url=inbox_url).content.decode('utf-8')
        soup = bs4(content, features='html.parser')
        inbox_search = soup.findAll('table', {'id': 'inbox-table'})
        # Get message ID
        for message in inbox_search:
            if 'data-msg-id' in str(message):
                # print(message)
                message_id = str(message).split(
                    'data-msg-id=')[1].split('"')[1].strip()
            else:
                return None
        # Get content of the message
        try:
            message = session.get(url=read_url.format(
                message_id)).content.decode('utf-8')
        except:
            return None
        return message


def update_buffer(values: dict):
    buffer_file = "buffer.json"
    try:
        buffer = open(os.path.join(path, buffer_file))
        buffer_data = json.loads(buffer.read())
        buffer.close()
    except JSONDecodeError as e:
        buffer.close()
        raise exit(r(e))
    buffer = open(os.path.join(path, buffer_file), "w+")
    for key in values.keys():
        buffer_data[key] = values[key]
    json.dump(buffer_data, buffer)
    buffer.close()


def new_password():
    # Just a simple function to generate a random password.
    # N.B : Lampyre doesn't seem to like some special characters...
    password = ''
    pwd_chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for _ in range(8):
        password += ''.join(pwd_chars[int(random.random()
                            * len(pwd_chars))].strip())
    return password


def new_credentials():
    ##              Account registration                     ##

    print(f"[{g('+')}] Requesting for a temporary mailbox")
    inbox = Mohmal()  # Requesting for a new temp mailbox
    email = inbox.email
    print(f"[{g('+')}] Generating a random password")
    password = new_password()  # Generating a random password
    print(f"[{g('+')}] Registering a new account on Lampyre.io")
    lampyre = Lampyre(email, password)
    print(f"[{g('+')}] Validating the account")
    confirmation_email = inbox.read()
    confirmation_link = str(confirmation_email).split('href=')[
        1].split('"')[1].strip()
    lampyre.validate(confirmation_link)
    s = Lampyre.login(email, password)

    ##              Getting the activation key              ##

    activation_key = lampyre.activation_key(s)

    return email, password, activation_key, lampyre


def nice_display(json_data, target):
    ## Function to display the json values into a beautiful html page :) ##

    import webbrowser
    import string

    # Wasn't quite easy
    results = json_data['result']
    html = f"""<!DOCTYPE html>
    <html>
    <head>
    <title>Results for {target}</title>
    """+"""
    <!-- <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-KyZXEAg3QhqLMpG8r+8fhAXLRk2vvoC2f3B09zVXn8CA5QIVfZOJ3BCsw2P0p/We" crossorigin="anonymous">-->
    <!-- <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-KyZXEAg3QhqLMpG8r+8fhAXLRk2vvoC2f3B09zVXn8CA5QIVfZOJ3BCsw2P0p/We" crossorigin="anonymous">-->
    <meta charset="utf-8">
    <style>@import 'https://fonts.googleapis.com/css?family=Open+Sans';ul{list-style:none;}ul li.found::before{content:'✅';display:inline-block;margin-right:0.2rem;}ul li.notavailable::before{content:'❌';}*{-webkit-box-sizing:border-box;box-sizing:border-box;}body{font-family:'Open Sans', sans-serif;line-height:1.75em;font-size:16px;background-color:#222;color:#aaa;}.simple-container{max-width:675px;margin:0 auto;padding-top:70px;padding-bottom:20px;}.simple-print{fill:white;stroke:white;}.simple-print svg{height:100%;}.simple-close{color:white;border-color:white;}.simple-ext-info{border-top:1px solid #aaa;}p{font-size:16px;}h1{font-size:30px;line-height:34px;}h2{font-size:20px;line-height:25px;}h3{font-size:16px;line-height:27px;padding-top:15px;padding-bottom:15px;border-bottom:1px solid #D8D8D8;border-top:1px solid #D8D8D8;}hr{height:1px;background-color:#d8d8d8;border:none;width:100%;margin:0px;}a[href]{color:#1e8ad6;}a[href]:hover{color:#3ba0e6;}img{max-width:100%;}li{line-height:1.5em;}aside,[class *= 'sidebar'],[id *= 'sidebar']{max-width:90%;margin:0 auto;border:1px solid lightgrey;padding:5px 15px;}@media (min-width:1921px){body{font-size:18px;}}</style>
    </head>
    """
    header = f'<div class="simple-container"><center><h1> Results for {target} </h1> </center><br/>'
    body = '<body>'
    body += header

    for _ in range(len(results)):
        source = "<h2>"+results[_]['source'].replace('"', '')+'</h2><ul>'
        body += source
        data = results[_]['data']
        for sub in data:
            for key in sub.keys():
                key = str(key)
                value = str(sub[key])
                for car in ['[', ']', '\'', '{', '}']:
                    value = value.replace(car, '')
                if 'XX' in value:
                    value = value.replace('X', '•')
                elif 'http' in value:
                    value = f'<a href="{value}">{value}</a>'
                if '•' in value:
                    body += '<li class="notavailable">'+key+': '+value+'</li>'
                else:
                    body += '<li class="found">'+key+': '+value+'</li>'

        body += '</ul>'
    body += '</div></body>'
    html += body + '</html>'
    soup = bs4(html, features='html.parser')
    html = soup.prettify()
    cars = string.digits
    random_num = ''.join(random.choice(cars) for i in range(10))

    time.sleep(5)
    if not os.path.isdir(f'{path}/results'):
        os.mkdir(f'{path}/results')

    with open(f'{path}/results/result-{random_num}.html', 'w+', encoding='utf-8') as html_file:
        html_file.write(html)
        html_file.flush()
        html_file.close()

    url = f'file:///{path}/results/result-{random_num}.html'
    print(g("\nYour browser will now open with the results :)"))
    webbrowser.open(url, new=2)  # open page in browser (new tab)


path = os.getcwd()
buffer_file = "buffer.json"
version = "alpha 0.5"
banner = r(f'''

 (                                                             
 )\ ) (                                                     )  
(()/( )\ (    )        (  (     (         (    ) (       ( /(  
 /(_)|(_))\  (    `  ) )\ )(   ))\   (   ))\( /( )(   (  )\()) 
(_))   /((_) )\  '/(/(((_|()\ /((_)  )\ /((_)(_)|()\  )\((_)\  
| |   (_)) _((_))((_)_\(_)((_|_))   ((_|_))((_)_ ((_)((_) |(_) 
| |__ / -_) '  \() '_ \) | '_/ -_)  (_-< -_) _` | '_/ _|| ' \  
|____|\___|_|_|_|| .__/|_|_| \___|  /__|___\__,_|_| \__||_||_| 
                 |_| 
''')+'''
L'empire search is a tool to exploit lampyre.io's API to find infos about people.
This version only includes free results (for now).
Be aware that its use is limited to 30 requests/day. You will have to use a vpn for more.
'''


def main():

    print(banner)
    print(f"Current version : {version}\n")

    parser = argparse.ArgumentParser(prog='lempire-search.py',
                                     description='''L'empire search is a tool to exploit lampyre.io's database to find infos about people.''')
    parser.add_argument('-v', '--version', action='version',
                        version=f"L'empire seach tool, version {version}", help="Show program's version number and exit.")
    parser.add_argument('-t', '--query-type', required=True,
                        help='Type of the query. Availables choices : email, phone', type=str)
    parser.add_argument('-q', '--query', required=True,
                        help='e-mail: john.doe@mail.com; \nphone: Be sure to respect the international format', type=str)
    args = parser.parse_args()
    query = args.query
    query_type = args.query_type

    ##                  Filtering queries                    ##

    query_types = ['email', 'phone']
    regex_query_type = re.compile(
        r"\+(9[976]\d|8[987530]\d|6[987]\d|5[90]\d|42\d|3[875]\d|2[98654321]\d|9[8543210]|8[6421]|6[6543210]|5[87654321]|4[987654310]|3[9643210]|2[70]|7|1)\d{1,14}$")
    if query_type not in query_types:
        raise exit(
            r('This script only supports `email` and `phone` as query types'))
    if query_type == 'phone' and not regex_query_type.match(query):
        raise exit(
            r('Phone number should be in the international format, starting with + and a country code (e.g. +12345678900)'))

    ##              Trying to read local buffer                 ##
    if not os.path.isfile('buffer.json'):
        print(f'{y("INFO")} : Buffer file not present. Creating it... ')
        with open('buffer.json', 'w') as buf:
            buf.write('{}')
            buf.close()

    print(f"\n[{g('+')}] Retriving informations from buffer")
    buffer = open(os.path.join(path, buffer_file), 'r')
    buffer_data = json.loads(buffer.read())
    buffer.close()

    if len(buffer_data) < 4 or int(buffer_data["queries"]) >= 4:
        print(f"\n{y('INFO')} : Either the buffer is corrupted or the maximum number of queries is exceeded. I need to generate a new Lampyre account.\n")
        email, password, activation_key, lampyre = new_credentials()
        queries = "0"
        print(f"[{g('+')}] Updating the buffer")

        ##              Buffer update                           ##

        update_buffer({"email": email, "password": password,
                      "queries": queries, "activation_key": activation_key})
        buffer = open(os.path.join(path, buffer_file), 'r')
        buffer_data = json.loads(buffer.read())
        buffer.close()

    email = buffer_data['email']
    password = buffer_data['password']
    queries = buffer_data['queries']
    activation_key = buffer_data['activation_key']

    print(f"\n[?] {y('Account details')}\n")
    print(f"{g('•')} login : {email}")
    print(f"{g('•')} password : {password}")
    print(f"{g('•')} activation key : {activation_key}")
    print(f"\n[?] {y('Details of the query')}\n")
    print(f"{g('•')} Type : {query_type}")
    print(f"{g('•')} Query : {query}\n")

    lampyre = Lampyre.login(email, password)  # Log-in with the lampyre account
    json_results = Lampyre.query(lampyre, query_type, query)  # Sending request
    queries = int(buffer_data['queries'])
    queries += 1
    update_buffer({"queries": str(queries)})  # Updating queries number

    time.sleep(5)
    if not os.path.isdir(f'{path}/results'):
        os.mkdir(f'{path}/results')
    nice_display(json_results, query)


if __name__ == '__main__':
    main()
