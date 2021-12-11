# Lempire Search

## :book: Introduction

After a nice conference made by [Palenath](https://github.com/megadose) @ Barbhack 2021 in Toulon , I decided to make a tool to exploit [Lampyre](https://lampyre.io/)'s API using a python3 script.

But why ?

To use Lampyre, you need to create an account. And with that account you can only make 4 free requests. In addition, each account must be verified via a link received by email.

This tool was not meant to be published but apparently several people have asked for it, so here it is

## :question: How to install

1. Clone the project

````bash
git clone https://github.com/0xSysR3ll/lempire-search
````

2. Install the required dependencies

```bash
cd lempire-search
pip3 install -r requirements.txt
```

3. Make a symbolic link

```bash
sudo ln -s lempire-search.py /usr/bin/lempire-search
sudo chmod +x /usr/bin/lempire-search
```

4. Enjoy 😀

```bash
❯ python3 lempire-search.py -h


 (                                                             
 )\ ) (                                                     )  
(()/( )\ (    )        (  (     (         (    ) (       ( /(  
 /(_)|(_))\  (    `  ) )\ )(   ))\   (   ))\( /( )(   (  )\()) 
(_))   /((_) )\  '/(/(((_|()\ /((_)  )\ /((_)(_)|()\  )\((_)\  
| |   (_)) _((_))((_)_\(_)((_|_))   ((_|_))((_)_ ((_)((_) |(_) 
| |__ / -_) '  \() '_ \) | '_/ -_)  (_-< -_) _` | '_/ _|| ' \  
|____|\___|_|_|_|| .__/|_|_| \___|  /__|___\__,_|_| \__||_||_| 
                 |_| 

L'empire search is a tool to exploit lampyre.io's database to find infos about people.
This version only includes free results (for now).
Be aware that its use is limited to 30 requests/day. You will have to use a vpn for more.

Current version : alpha 0.5

usage: lempire-search.py [-h] [-v] -t QUERY_TYPE -q QUERY

L'empire search is a tool to exploit lampyre.io's database to find infos about people.

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         Show program's version number and exit.
  -t QUERY_TYPE, --query-type QUERY_TYPE
                        Type of the query. Availables choices : email, phone
  -q QUERY, --query QUERY
                        e-mail: john.doe@mail.com; phone: Be sure to respect the international format
```



PS : I am not much of a developper, more like a DevOps. So if you have any idea/recommandation or issue to report, please feel free to contact me or make a PR.

