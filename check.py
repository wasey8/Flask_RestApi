import requests
from flask import Flask,render_template,url_for,request,jsonify,abort,make_response
from bs4 import BeautifulSoup
from tqdm import tqdm
from urllib.parse import urljoin, urlparse
from googleapiclient.discovery import build
import iso8601
import os,json
from werkzeug.exceptions import HTTPException

app = Flask(__name__)

#-----------------------------------------------http response code-------------------------------------#
@app.errorhandler(HTTPException)
def handle_exception(e):
    response = e.get_response()
    response.data = json.dumps({
        "user_parameter": "parameter is missing",
        
    })
    response.content_type = "application/json"
    return response

#-------------------------------------image urls download--------------------------------------#
def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def get_all_images(url):
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    urls = []
    urls1= []
    for img in tqdm(soup.find_all("img"), "Extracting images"):
        img_url = img.attrs.get("src")
        if not img_url:
            continue
        img_url = urljoin(url, img_url)
        try:
            pos = img_url.index("?")
            img_url = img_url[:pos]
        except ValueError:
            pass
        if is_valid(img_url):
            urls.append(img_url)
            for i in urls:
                if i not in urls1:
                    urls1.append(i)

    return urls1

#-------------------------------Dribble----------------------------------------------#
@app.route("/dribbble/<dribbleuser>", methods=['GET'])
def dribbble(dribbleuser):
    r=requests.get("https://dribbble.com/{dribbleuser}".format(dribbleuser=dribbleuser))
    soup = BeautifulSoup(r.text, "html.parser")
    shots= soup.find_all("a", {"href": "/{dribbleuser}/shots".format(dribbleuser=dribbleuser)})
    collections= soup.find_all("a", {"href": "/{dribbleuser}/collections".format(dribbleuser=dribbleuser)})
    likes= soup.find_all("a", {"href": "/{dribbleuser}/likes".format(dribbleuser=dribbleuser)})

        #----------------------------ABOUT---------------------------------------------------#
    r1=requests.get("https://dribbble.com/{dribbleuser}/about".format(dribbleuser=dribbleuser))
    soup1 = BeautifulSoup(r1.text, "html.parser")
    w=[]
    for x in soup1.find_all("ul", {"class": "skills-list"}):
        for i in x.find_all('li'):
            if i is None:
                w="None"
            else:
                w.append(i.text)

    about= soup1.find_all("div", {"class": "bio"})
    residence= soup1.find_all("section", {"class": "content-section profile-info-section medium-screens-only"})

        #-------------------------------------------------------------------------------------#
    d=None
    for row in shots:
        d=row.find("span","count").text
        if d is None:
            d="Null"

    e=None
    for row in collections:
        e=row.find("span","count").text
        if e is None:
            e="Null"     
    
    f=None
    for row in likes:
        f=row.find("span","count").text
        if f is None:
            f="Null"
        
    u=None
    for x in about:
        u=x.find('p').text
        if u is None:
            u="Null"
    
    v=None
    for x in residence:
        v=x.find('span').text
        if v is None:
            v="Null"

    is_valid("https://dribbble.com/{dribbleuser}".format(dribbleuser=dribbleuser))
    a=get_all_images("https://dribbble.com/{dribbleuser}".format(dribbleuser=dribbleuser))
    a.pop(0)

    
    if r.status_code and r1.status_code == 200:
        json={
        "username":dribbleuser,
        "shots":d,
        "likes":f,
        "collections": e,
        "about":u,
        "skills":w,
        "shots_snip":a,
        }
        
        return jsonify(json)

    elif r.status_code and r1.status_code != 200:
        return jsonify ( success="failed",
            message="No user found")

    else:
        handle_exception(r)

       

#--------------------------------------Behance-----------------------------------------------#

@app.route("/behance/<behanceuser>",methods=['GET'])
def behance(behanceuser):
    r1=requests.get("https://www.behance.net/{behanceuser}/info".format(behanceuser=behanceuser)) 
    soup = BeautifulSoup(r1.text, "html.parser")
    Project= soup.find("a", {"class":"UserInfo-statValue-1_- UserInfo-disabledLink-Czm"})
    if Project is None:
        Project="None"
    else:
        Project=Project.text

    Followers= soup.find("a", {"class":"UserInfo-statValue-1_- e2e-UserInfo-statValue-followers-count"})
    if Followers is None:
        Followers="None"
    else:
        Followers=Followers.text

    About= soup.find("div", {"class":"UserInfo-bio-YNh"})
    if About is None:
        About="None"
    else:
        About=About.text

    Residence= soup.find("span", {"class":"e2e-Profile-location"})
    if Residence is None:
        Residence="None"
    else:
        Residence=Residence.text

    Following="None"
    Appreciation="None"

    for g in soup.find_all("a",{"class":"UserInfo-statValue-1_-"}):
        if g is None:
            Following="None"
        else:
            Following=g.text 
        
    for i in soup.find_all("a", {"class":"UserInfo-statValue-1_- UserInfo-disabledLink-Czm"}):
        if i is None:
            Appreciation="None"
        else:
            Appreciation=i.text
    
        
    is_valid("https://www.behance.net/{behanceuser}/projects/".format(behanceuser=behanceuser))
    snips=get_all_images("https://www.behance.net/{behanceuser}/projects/".format(behanceuser=behanceuser))

    if r1.status_code !=200:
        return jsonify(
            success="failed",
            message="No user found"
        )
    
    elif r1.status_code ==200:
        json={     
        "username":behanceuser,
        "projects_counts":Project,
        "Appreciations":Appreciation,
        "Followers": Followers,
        "Following":Following,
        "About":About,
        "Residence":Residence,
        "project_snippets_urls":snips,
        }
        return jsonify(json)
    else:
        handle_exception(r1)



#--------------------------------github--------------------------------------------------#
@app.route("/github/<githubuser>",methods=['GET'])
def github(githubuser):
    res = requests.get("https://api.github.com/users/{githubuser}".format(githubuser=githubuser), params = {"key" : "67c30d095fc1eeffd85cbd4e3288bc00b30bbcc1"})
    res1 = requests.get("https://api.github.com/users/{githubuser}/repos".format(githubuser=githubuser), params = {"key" : "67c30d095fc1eeffd85cbd4e3288bc00b30bbcc1"})
    var=res.json()
    var1=res1.json()
    Residence=var['location']
    Avatar=var['avatar_url']
    repos=var['public_repos']
    followers=var['followers']
    following=var['following']
    about=var['bio']
    url=var['html_url']
    repo_name=[]
    for i in var1:
        a=i['name']
        repo_name.append(a)
    repo_name=repo_name

    if res.status_code and res1.status_code!=200:
        return jsonify(
            success="failed",
            message="No user found"
        )

    elif res.status_code and res1.status_code ==200:
        json={  
        "username":githubuser,
        "repos_counts":repos,
        "Followers":followers,
        "Following":following,
        "About":about,
        "Residence":Residence,
        "repo_names":repo_name,
        "user_url":url,
        "avatar":Avatar
        }
        return jsonify(json)


    else:
        handle_exception(res)
        handle_exception(res1)

#-------------------------------Youtube Api-------------------------------------#

@app.route("/youtube/<chan_id>",methods=['GET'])
def youtube(chan_id):
    api_key = 'AIzaSyDQ_ocyrFiyFdJHy8CW7J7xUQ7lQ5AeCMg'
    youtube = build('youtube', 'v3', developerKey=api_key)
    request1 = youtube.channels().list(
    part='statistics',
    id=chan_id
    )
    
    response = request1.execute()
    for i in response['items']:
        a=i['statistics']
        VideoCount=a["videoCount"]
        ViewCount=a["viewCount"]
        Subscribers=a["subscriberCount"]
        
    request1 = youtube.channels().list(
    part='contentDetails',
    id=chan_id
    )

    request3 = youtube.channels().list(
    part='snippet',
    id=chan_id
    )
    
    response1=request1.execute()
    for i in response1['items']:
        a=i['contentDetails']
        b=a["relatedPlaylists"]
        c=b['uploads']
        
    request2=youtube.playlistItems().list(
        playlistId=c,
        part='snippet',
        maxResults=50
        )
        
    response2=request2.execute()
    for i in response2['items']:
        a=i['snippet']
        name=a["channelTitle"]
    f=[]
    videos=[]
    videos+=response2['items']
    for i in videos:
        a=i['snippet']['title']
        f.append(a)
    f=f

    response3=request3.execute()
    for i in response3['items']:
        a=i['snippet']
        b=a["publishedAt"]
        time=iso8601.parse_date(b)
        c=a["description"]

        if request1 is not None:
            json={
            "username":name,
            "video_count":VideoCount,
            "view_count":ViewCount,
            "Followers":Subscribers,
            "published_at":time,
            "About":c,
            "videos_titles":f,
            }
            return jsonify(json)
        else:
            handle_exception(request1)
            handle_exception(request2)
            handle_exception(request3)
            
if __name__ == "__main__":
    app.run(debug=True)
