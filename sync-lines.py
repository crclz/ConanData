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
    name="推理线", description="aka主线、酒厂线", videos=line_eps)

res: conan.IdDto = storyline_api.put_storyline(storyline_id, body=model)
print("put 推理线", res.id)

# %%
