# %% all imports
from typing import List
import csv
import time
from datetime import datetime
import json
import sys
import os
import swagger_client as conan

# %% api client init
conf = conan.Configuration()
conf.host = "http://localhost:3923"

client = conan.ApiClient(configuration=conf)

access_api = conan.AccessApi(api_client=client)
video_api = conan.VideosApi(api_client=client)


# login and check me()
login_model = conan.LoginModel(
    username='admin', password=os.environ['CONAN_ADMIN_PASS'])

token = access_api.api_access_login_post(body=login_model)
client.default_headers['Conan-LoginInfo'] = token

me = access_api.api_access_me_get()
me: conan.QUser
assert me.id is not None


# %% util functions

def datetime_to_unix_sec(d: datetime):
    return int(time.mktime(d.timetuple()))


class Video(object):
    def __init__(self, id: str, is_tv: bool,
                 title: str, seq_id: int, pub: int,
                 bili_play_id: str):
        self.id = id
        self.is_tv = is_tv
        self.title = title
        self.seq_id = seq_id
        self.pub = pub
        self.bili_play_id = bili_play_id


# %% load tvs
tvdata = json.load(open('./tv-with-time.json', 'r', encoding='utf8'))

videos_1 = []

for tv in tvdata:
    pub = tv['pub']
    pub = datetime.strptime(pub, '%Y/%m/%d')
    pub = datetime_to_unix_sec(pub)

    seq_id = tv['tvid']
    id = f"tv{seq_id}"

    v = Video(id, True, tv['title'], seq_id, pub, tv['playId'])
    videos_1.append(v)

for v in videos_1[:2]:
    print(v.__dict__)
print("tv", len(videos_1))

# %% load movies
videos_2 = []

reader = csv.reader(open('./movie.csv', 'r', encoding='utf8'))
lines = list(reader)
lines = lines[1:]

for line in lines:
    seq_id, title, pub = line
    seq_id = int(seq_id)
    pub = datetime.strptime(pub, '%Y年%m月%d日')
    pub = datetime_to_unix_sec(pub)

    id = f"m{seq_id}"

    v = Video(id, False, title, seq_id, pub, None)
    videos_2.append(v)


for v in videos_2[:2]:
    print(v.__dict__)

print("movie", len(videos_2))

# %% generate diff report


def dto_convert(v: conan.Video):
    assert isinstance(v, conan.Video)
    return Video(v.id, v.is_tv, v.title, v.seq_id, v.publish, v.bili_play_id)


# fetch video list
old_videos = video_api.api_videos_get()
old_videos = [dto_convert(p) for p in old_videos]

# compare video list
videos = videos_1 + videos_2

new_d = {p.id: p for p in videos}
old_d = {p.id: p for p in old_videos}

new_keys = set(new_d.keys())
old_keys = set(old_d.keys())

# +
k_add = list(new_keys - old_keys)
k_add.sort()
videos_add = [new_d[p] for p in k_add]

# -
k_rm = list(old_keys - new_keys)
k_rm.sort()
videos_rm = [old_d[p] for p in k_rm]

# M
k_prob_mod = list(new_keys.intersection(old_keys))
k_prob_mod.sort()
videos_mod = [[old_d[p], new_d[p]] for p in k_prob_mod]

# if same, do not midify
videos_mod = [[v1, v2]
              for [v1, v2] in videos_mod if str(v1.__dict__) != str(v2.__dict__)]

unchange_count = len(k_prob_mod) - len(videos_mod)

# generate report
with open('migration-report.txt', 'w', encoding='utf8') as f:

    # +
    f.write(f"Add: {len(videos_add)}\n\n")
    for v in videos_add:
        f.write(str(v.__dict__)+"\n")
    f.write('---------------------------------\n\n')

    # -
    f.write(f"Remove: {len(videos_rm)}\n\n")
    for v in videos_rm:
        f.write(str(v.__dict__))
    f.write('---------------------------------\n\n')

    # M
    f.write(f"Modify: {len(videos_mod)}\n\n")
    for [v1, v2] in videos_mod:
        f.write("old: " + str(v1.__dict__) + "\n")
        f.write("new: " + str(v2.__dict__) + "\n")
    f.write('---------------------------------\n\n')

    f.write(f"unchange: {unchange_count}\n")
    f.write('---------------------------------\n\n')


# %% do requests after checking the migration report

assert len(videos_rm) == 0  # removing causes cascade business operations

# +
for v in videos_add:
    model = conan.PutVideoModel(
        title=v.title, is_tv=v.is_tv, seq_id=v.seq_id,
        publish=v.pub, bili_play_id=v.bili_play_id)

    res: conan.IdDto = video_api.api_videos_id_put(v.id, body=model)
    assert res.id is not None
    print(res.id)

# M
for [_, v] in videos_mod:
    model = conan.PutVideoModel(
        title=v.title, is_tv=v.is_tv, seq_id=v.seq_id,
        publish=v.pub, bili_play_id=v.bili_play_id)
    res: conan.IdDto = video_api.api_videos_id_put(v.id, body=model)
    assert res.id is not None
    print(res.id)

print("migration end")

# %%
