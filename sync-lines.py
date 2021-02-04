# %% import packages
from typing import List
import time
from datetime import datetime
import json
import sys
import os
import swagger_client as conan

# %% utils
import re


def parse_line(line: str):
    eps = []

    # 059-060
    m = re.findall(r'(\d+)-(\d+)', line)
    if len(m) > 0:
        x1 = int(m[0][0])
        x2 = int(m[0][1])
        assert x1 < x2
        for i in range(x1, x2+1):
            eps.append(i)
    else:
        # 123
        m = re.findall(r'(\d+)', line)
        assert len(m) == 1
        x = int(m[0])
        eps.append(x)

    return eps


# %% api client init
conf = conan.Configuration()
conf.host = "http://localhost:3923"

client = conan.ApiClient(configuration=conf)

access_api = conan.AccessApi(api_client=client)
video_api = conan.VideosApi(api_client=client)
storyline_api = conan.StoryLinesApi(api_client=client)


# login and check me()
login_model = conan.LoginModel(
    username='admin', password=os.environ['CONAN_ADMIN_PASS'])

token = access_api.login(body=login_model)
client.default_headers['Conan-LoginInfo'] = token

me = access_api.get_me()
me: conan.QUser
assert me.id is not None

# %% 推理
with open('storylines/推理.txt', 'r', encoding='utf8') as f:
    lines = f.read().splitlines(keepends=False)

line_eps = []
for line in lines:
    line_eps += parse_line(line)

line_eps = ["tv" + str(p) for p in line_eps]

# request
storyline_id = "1-deduction"
model = conan.PutStorylineModel(
    name="推理线", description="主线、酒厂线", videos=line_eps)

res: conan.IdDto = storyline_api.put_storyline(storyline_id, body=model)
print("put 推理线", res.id)

# %% 新兰
with open('storylines/新兰.txt', 'r', encoding='utf8') as f:
    lines = f.read().splitlines(keepends=False)

# get all videos from server. SSOT: Single Source of Truth

videos: List[conan.Video] = video_api.get_videos()

movies = [p for p in videos if not p.is_tv]

video_ids = []

for line in lines:
    try:
        tv_seqs = parse_line(line)
        for x in tv_seqs:
            video_ids.append("tv" + str(x))
    except(Exception):
        # movie
        v = None
        for mov in movies:
            if mov.title.endswith(line):
                v = mov
        assert v is not None
        video_ids.append(v.id)

# do requests
storyline_id = '2-love'
model = conan.PutStorylineModel(
    name='新兰线',
    description='新一和兰的感情线',
    videos=video_ids
)

res: conan.IdDto = storyline_api.put_storyline(storyline_id, body=model)
print("put 新兰线", res.id)


# %% 危命的复活
with open('storylines/危命的复活.txt', 'r', encoding='utf8') as f:
    lines = f.read().splitlines(keepends=False)

line_eps = []
for line in lines:
    line_eps += parse_line(line)

line_eps = ["tv" + str(p) for p in line_eps]

# request
storyline_id = "3-bloodtype"
model = conan.PutStorylineModel(
    name="危命的复活",
    description="《危命的复活》系列剧情，小兰的怀疑稳步推进（漫画顺序和动画发行顺序不一致，请按故事序排序）",
    videos=line_eps)

res: conan.IdDto = storyline_api.put_storyline(storyline_id, body=model)
print("put 危命的复活", res.id)


# %% bilibili 推荐 up主：@大概更喜欢纸片人
with open('storylines/bilibili-recommend-1.txt', 'r', encoding='utf8') as f:
    content = f.read()

charlist = set(list(content))
for c in list(charlist):
    if re.match(r'[\u4e00-\u9fff]|\s|\d', c) is not None:
        charlist.remove(c)

print(charlist)


def single(s_list: List):
    assert len(s_list) == 1
    return s_list[0]


items = re.findall(r'(\d+~\d+)|(\d+)', content)
items = [single([o for o in p if o !='']) for p in items]

# print(items)

def parse2(line: str):
    eps = []

    # 059~060
    m = re.findall(r'(\d+)~(\d+)', line)
    if len(m) > 0:
        x1 = int(m[0][0])
        x2 = int(m[0][1])
        assert x1 < x2
        for i in range(x1, x2+1):
            eps.append(i)
    else:
        # 123
        m = re.findall(r'(\d+)', line)
        assert len(m) == 1
        x = int(m[0])
        eps.append(x)

    return eps

line_eps = []
for line in items:
    line_eps += parse2(line)

line_eps = ["tv" + str(p) for p in line_eps]

# print(line_eps)

# request
storyline_id = "4-bili-rec1"
model = conan.PutStorylineModel(
    name="推荐1",
    description="b站up主 @大概更喜欢纸片人 的推荐，截至1034。cv7208676，BV18K4y1a7eo",
    videos=line_eps)

res: conan.IdDto = storyline_api.put_storyline(storyline_id, body=model)
print("put @大概更喜欢纸片人 的推荐", res.id)


# %%
