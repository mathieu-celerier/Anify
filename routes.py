import base64, json, requests, xmltodict, re, urllib, os, time
from flask import render_template, request, flash, Blueprint, redirect, session, current_app, url_for, abort, send_file
from flask_login import login_user, logout_user, current_user, login_required
from datetime import date
from Anify import db
from Anify.forms import LoginForm
from Anify.models import Admin, User, AnimeSong

SONG_MODE = "OP"
SONG_MATCH = {  "Uzu to Uzu":                                   "spotify:track:0XzdNOD0QRzwdsc3vKWbFq",
                "Kouga Ninpouchou":                             "spotify:track:5tDLvWHp0tc8BBDu3hZAKp",
                "Ouka Ninpouchou":                              "spotify:track:0TqNsYDUt2cYdeenoiP72a",
                "Hajimaru no wa, Sayonara":                     "spotify:track:1aUPS1Brr3nIazm9rdNEY4",
                "Hey!!!":                                       "spotify:track:21hAe7iOy3AWll8yZ80jU1",
                "Seishun Satsubatsu-ron":                       "spotify:track:0PY7EFmEa52bsJ12xSq4B5",
                "LIVE for LIFE ~Ookamitachi no Yoru~":          "spotify:track:3EAqLiujBTJ7aeix48TKEh",
                "Shoujo S":                                     "spotify:track:6TVCtahFY64cE2roIDyA7H",
                "Zannenkei Rinjinbu (Hoshi Futatsu Han)":       "spotify:track:7C06EecjfGb0kEWByZMb2w",
                "Megumeru ~cuckool mix 2007~":                  "spotify:track:4DR2J4AaNkDzAK7lmSeSv4",
                "Kakusei Heroism ~The Hero without a Name~":    "spotify:track:6hM8loMN7RREyTEZtKMqUK",
                "Tsukiakari no Michishirube":                   "spotify:track:2dJO8sudemIsWRKmdL1LTu",
                "KISS OF DEATH (Produced by HYDE) Remix ver.":  "spotify:track:0ekGJQiqn1DzeZ3w5AsBoH",
                "LAMENT ~Yagate Yorokobi wo~":                  "spotify:track:3TAHskg2l2qmRgrFWmNTyw",
                "Fairy Tail: Yakusoku no Hi":                   "spotify:track:6hUQcGznld9GAqA59o5guX",
                "Kirameku Namida wa Hoshi ni":                  "spotify:track:62ZVOt97IwjbefTTQQXtyc",
                "Sharanran feat. 96 Neko":                      "spotify:track:7hHlie5UhAJYvP0MF5WGVI",
                "Kizunairo":                                    "spotify:track:14DJrH99IB3YWe0277FmXy",
                "Love Dramatic feat. Rikka Ihara":              "spotify:track:7ItVcZD840Q8ehx3z03iwW",
                "DADDY! DADDY! DO! feat. Airi Suzuki":          "spotify:track:7tdBXBfqfXSWpMaMA8QaES",
                "masterpiece":                                  "spotify:track:59a4HxvOrQbihRRIjS1M9F"}

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    return render_template('index.html')

@main.route("/get_started")
def get_started():
    return render_template('username.html')

@main.route('/download')
def download():
    path = "datapack.zip"
    return send_file(path, as_attachment=True)

@main.route('/upload')
def uploadPage():
    return render_template('upload.html')

@main.route('/upload', methods=['POST'])
def uploadFile():
    if current_user.is_authenticated:
        if current_user.username != 'naruto':
            abort(403)
    else:
        return redirect(url_for('main.login'))
    uploaded_file = request.files['file']
    print(uploaded_file.filename)
    if uploaded_file.filename != '':
        uploaded_file.save('Anify/datapack.zip')
    return redirect(url_for('main.logout'))

@main.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.username == 'egtquzr9':
            return redirect(url_for('admin.index'))
        elif current_user.username == 'naruto':
            return redirect(url_for('main.uploadPage'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Admin.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.login'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@main.route("/logout")
def logout():
    logout_user()
    return redirect("/")

@main.route("/login_spotify", methods=['POST'])
def login_spotify():
    session["USERNAME"] = request.form['username']
    scopes = 'playlist-modify-public playlist-modify-private user-read-email user-read-private'
    return redirect("{}client_id={}&response_type=code&redirect_uri={}&scope={}".format('https://accounts.spotify.com/authorize?',
                                                                                        current_app.config['CLIENT_ID'],
                                                                                        current_app.config['REDIRECT_URL'],
                                                                                        scopes))

@main.route("/get_spotify_token")
def get_spotify_token():
    
    body = {
        "grant_type": 'authorization_code',
        "code" : str(request.args['code']),
        "redirect_uri": current_app.config['REDIRECT_URL'],
        'client_id' : current_app.config['CLIENT_ID'],
        'client_secret': current_app.config['CLIENT_SECRET']
    }
     
    # encoded = base64.b64encode(b"e6ffc669d1b64a568f6d4e624c159ee7:57122c0227a844e39d08af0a65045f33")
    # headers = {"Content-Type" : 'application/x-www-form-urlencoded', "Authorization" : "Basic {}".format(encoded)} 

    post = requests.post('https://accounts.spotify.com/api/token/', data=body)
    response = json.loads(post.text)
    auth_head = {"Authorization": "Bearer {}".format(response["access_token"])}
    session["REFRESH_TOKEN"] = response["refresh_token"]
    session["TOKEN_DATA"] = [response["access_token"], auth_head, response["scope"], response["expires_in"]]

    user_response = requests.get("https://api.spotify.com/v1/me",headers=session["TOKEN_DATA"][1]).json()
    
    print("User Anilist ID : ", session["USERNAME"])
    print("User Spotify ID : ", str(user_response["id"]))

    new_user = User(username=session["USERNAME"],access_token=response["access_token"],spotify_id=str(user_response["id"]))
    db.session.add(new_user)
    db.session.commit()

    return redirect("/load_anime")

@main.route("/load_anime")
def load_anime():
    return render_template('loaderAnime.html')

@main.route("/load_anime_list")
def load_anime_list():

    # Here we define our query as a multi-line string
    query = '''
    query ($name: String) {
        User(name: $name){
            id
            name
            statistics{
                anime{
                    count
                }
            }
        }
    }
    '''
    variables = {
        'name': session["USERNAME"],
    }

    url = 'https://graphql.anilist.co'

    # Make the HTTP Api request
    userResponse = requests.post(url, json={'query': query, 'variables': variables})

    if "errors" in userResponse.json():
        flash('Username not found please retry', 'danger')
        user_db = User.query.filter_by(username=session["USERNAME"]).first_or_404()
        db.session.delete(user_db)
        db.session.commit()
        return redirect('/')

    print(userResponse.headers['X-RateLimit-Remaining'])
    userId = int(userResponse.json()["data"]["User"]["id"])
    print(userId)
    p = 1
    animeIDs = []
    authorizedFormat = ['TV','TV_SHORT','ONA']
    status_in_def = 'COMPLETED, CURRENT'
    while 1:
        query = '''
        query ($uID: Int, $page: Int) {
            Page(page: $page){
                mediaList(userId: $uID, sort: MEDIA_TITLE_ROMAJI, status_in: [COMPLETED, CURRENT], type: ANIME){
                    media{
                        id
                        idMal
                        title{
                            romaji
                            english
                        }
                        format
                        synonyms
                    }
                }
            }
        }
        '''
        variables = {
            'uID': userId,
            'page' : p,
        }

        response = requests.post(url, json={'query': query, 'variables': variables})
        # print(json.dumps(response.json(), indent=4))

        # print(json.dumps(response.json()["data"]["Page"]["mediaList"],indent=4))

        for media in response.json()["data"]["Page"]["mediaList"]:
            animeIDs.append(media["media"]["idMal"])

        # print(animeIDs)

        if len(response.json()["data"]["Page"]["mediaList"]) == 50:
            p = p + 1
        else:
            break

    # print(animeIDs)

    print(len(animeIDs),"anime entries")

    user_db_id = User.query.filter_by(username=session["USERNAME"]).first_or_404().id

    notFound = []
    regexPos = [{'match': r'',                          'replace' : ''},
                {'match': r'\'',                        'replace' : ''},
                {'match': r' *\b(\w*season\w*)\b',      'replace' : ''},
                {'match': r' +2\b',                     'replace' : ' 2nd'},
                {'match': r' *\(tv\)',                  'replace' : ''},
                {'match': r':*',                        'replace' : ''},
                {'match': r'[()]',                      'replace' : ''}]
    for malId in animeIDs:
        url = "https://animethemes-api.herokuapp.com/api/v1/anime/" + str(malId)
        # print(animeTitle)
        response2 = requests.request("GET", url)
        # print(response2.json())
        if not (response2.json() == "Anime not found"):
            for i in range(len(response2.json()["themes"])):
                is_in_db = len(AnimeSong.query.filter_by(user_id=user_db_id).filter_by(name=response2.json()["themes"][i]["title"]).all())
                if SONG_MODE == "OP" and "OP" in response2.json()["themes"][i]["type"] and not is_in_db:
                    # print("\t",response2.json()['anime_list'][c]["themes"][i]["type"],":",response2.json()['anime_list'][c]["themes"][i]["title"])
                    new_song = AnimeSong(name=response2.json()["themes"][i]["title"], user_id=user_db_id)
                    db.session.add(new_song)
                    db.session.commit()
                elif SONG_MODE == "ED" and "ED" in response2.json()["themes"][i]["type"] and not is_in_db:
                    # print("\t",response2.json()['anime_list'][c]["themes"][i]["type"],":",response2.json()['anime_list'][c]["themes"][i]["title"])
                    new_song = AnimeSong(name=response2.json()["themes"][i]["title"], user_id=user_db_id)
                    db.session.add(new_song)
                    db.session.commit()
                elif SONG_MODE == "ALL" and not is_in_db:
                    # print("\t",response2.json()['anime_list'][c]["themes"][i]["type"],":",response2.json()['anime_list'][c]["themes"][i]["title"])
                    new_song = AnimeSong(name=response2.json()["themes"][i]["title"], user_id=user_db_id)
                    db.session.add(new_song)
                    db.session.commit()
        else:
            notFound.append(animeIDs)
        # print("OK    " if found == True else "Error ",animeTitles[t]["romaji"])

    print(len(AnimeSong.query.filter_by(user_id=user_db_id).all()),"anime's songs found :")
    # for song in song_titles:
    #     print("\t",song)

    print(len(notFound),"anime's songs couldn't be found on the database :")
    # for title in notFound:
    #     print("\t",title)

    if len(notFound) > 0:
        flash('Anime list loaded, {} anime not found.'.format(len(notFound)), 'warning')
    else:
        flash('Anime list loaded successfully.', 'success')
    return redirect('/load_playlist')

@main.route("/load_playlist")
def load_playlist():
    return render_template('loaderPlaylist.html')

@main.route("/fill_user_anify_playlist")
def fill_user_anify_playlist():
    notFound = []

    user_db = User.query.filter_by(username=session["USERNAME"]).first_or_404()

    song_list = AnimeSong.query.filter_by(user_id=user_db.id).all()

    auth_head = {"Authorization": "Bearer {}".format(user_db.access_token)}

    TRACK_IDS= []

    if len(session["TOKEN_DATA"]) == 0:
        flash('Connect with spotify before continuing', 'danger')
        AnimeSong.query.filter_by(user_id=user_db.id).delete()
        db.session.delete(user_db)
        db.session.commit()
        return redirect('/')

    if len(song_list) == 0:
        flash('No anime list loaded, please load list before continuing', 'danger')
        AnimeSong.query.filter_by(user_id=user_db.id).delete()
        db.session.delete(user_db)
        db.session.commit()
        return redirect('/')

    song_search_url = "https://api.spotify.com/v1/search?"
    for song in song_list:
        # print("'"+song+"'")
        found = False

        if song.name in SONG_MATCH:
            found = True
            TRACK_IDS.append(SONG_MATCH[song.name])

        for i in range(10):
            if found:
                break
            song_replaced = urllib.parse.quote_plus(song.name,safe="†")
            url = song_search_url+'q="{}"&type=track&limit=50&offset={}&market=FR'.format(song_replaced,i*50)

            while 1:
                response = requests.get(url,headers=auth_head)

                if response.status_code == 429:
                    time.sleep(int(response.headers['retry-after']))
                else:
                    response = response.json()
                    break

            for title in response["tracks"]["items"]:
                if found:
                    break
                if song.name == "":
                    print(title["name"])
                
                regexPos = [{'match': r'',                          'replace' : ''},
                            {'match': r'[^\x00-\x7F]+',             'replace' : ' '},
                            {'match': r' *\([^)]*\)',               'replace' : ''},
                            {'match': r' *~[^)]*~',                 'replace' : ''},
                            {'match': r'''[+-=_~*$#'",?%]+''',      'replace' : ''},
                            {'match': r' ',                        'replace' : ''}]
                songName = song.name.lower()
                titleName = title["name"].lower()
                for string1 in regexPos:
                    if found:
                        break
                    songName = re.sub(string1["match"],string1["replace"],songName)
                    for string2 in regexPos:
                        if found:
                            break
                        titleName = re.sub(string2["match"],string2["replace"],titleName)
                        if songName == titleName:
                            if not " remix " in title["name"].lower():
                                found = True
                                TRACK_IDS.append(title["uri"])
                                       
        if not found:
            notFound.append(song.name)
    print("{}/{}".format(len(notFound),len(song_list)),"songs couldn't be found :")
    # for song in notFound:
    #     print("\t",song)

    data = {'name': f'Anify {session["USERNAME"]}', 'public': 'false', 'description': 'Generated from Anify, anime list to Spotify playlist for AniList, on {}'.format(date.today().strftime("%d/%m/%Y"))}

    while 1:
        playlist_response = requests.post("https://api.spotify.com/v1/users/{}/playlists".format(user_db.spotify_id),data=json.dumps(data),headers=auth_head)

        if playlist_response.status_code == 429:
            time.sleep(int(playlist_response.headers['retry-after']))
        else:
            playlist_response = playlist_response.json()
            break

    # print(json.dumps(playlist_response,indent=4))
    ANIFY_PLAYLIST_ID = playlist_response["id"]
    print("Anify ID : ", ANIFY_PLAYLIST_ID)

    url = "https://api.spotify.com/v1/playlists/{}/tracks?uris=".format(ANIFY_PLAYLIST_ID)

    count = 0
    for uris in TRACK_IDS:
        if count == 0:
            url = url + uris
        else:
            url = url + "," + uris
        count = count + 1
        if count >= 100:
            # print(url)
            while 1:
                response = requests.post(url,headers=auth_head)

                if response.status_code == 429:
                    time.sleep(int(response.headers['retry-after']))
                else:
                    break
            count = 0
            url = "https://api.spotify.com/v1/playlists/{}/tracks?uris=".format(ANIFY_PLAYLIST_ID)
            # print(json.dumps(response.json(),indent=4))
    if count > 0:
        while 1:
            response = requests.post(url,headers=auth_head)

            if response.status_code == 429:
                time.sleep(int(response.headers['retry-after']))
            else:
                break
        # print(json.dumps(response.json(),indent=4))

    AnimeSong.query.filter_by(user_id=user_db.id).delete()
    db.session.delete(user_db)
    db.session.commit()

    if len(notFound) > 0:
        flash('Song list loaded, {} songs not found.'.format(len(notFound)),'warning')
    else:
        flash('Song list loaded successfully','success')
    
    return redirect('/')