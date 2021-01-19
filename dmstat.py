
# %% utils
import os
from typing import List
import swagger_client as conan
import json
import requests


class VideoStat(object):

    def __init__(self, epid: str, coin: int, dm: int,
                 like: int, reply: int, view: int):
        self.epid = epid
        self.coin = coin
        self.dm = dm
        self.like = like
        self.reply = reply
        self.view = view


def get_ep_stat(ep_id: str):
    url = 'https://api.bilibili.com/pgc/season/episode/web/info?ep_id=' + ep_id

    res = requests.get(url)

    stats = json.loads(res.text)
    assert stats['code'] == 0

    x = stats['data']['stat']
    coin = int(x['coin'])
    dm = int(x['dm'])
    like = int(x['like'])
    reply = int(x['reply'])
    view = int(x['view'])

    item = VideoStat(ep_id, coin, dm, like, reply, view)
    return item


# %% api client init
conf = conan.Configuration()
conf.host = "http://localhost:3923"

client = conan.ApiClient(configuration=conf)

access_api = conan.AccessApi(api_client=client)
video_api = conan.VideosApi(api_client=client)

# login and check me()
login_model = conan.LoginModel(
    username='admin', password=os.environ['CONAN_ADMIN_PASS'])

token = access_api.login(body=login_model)
client.default_headers['Conan-LoginInfo'] = token

me = access_api.get_me()
me: conan.QUser
assert me.id is not None

# %% get all ep from conan server
videos = video_api.get_videos()
videos: List[conan.Video]

# %% get stat info

vip_videos = [p for p in videos if p.seq_id >= 942]

infos = []

for v in vip_videos:
    if not v.is_tv:
        continue
    assert v.bili_play_id.startswith('ep')

    epid = int(v.bili_play_id[2:])

    stat = get_ep_stat(str(epid))

    infos.append([v, stat])


# %% see infos

infos.sort(key=lambda x: x[1].coin, reverse=True)
for [v, t] in infos:
    v: conan.Video
    t: VideoStat
    print(v.seq_id, v.title, t.coin)

# %%
