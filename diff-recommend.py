# %% imports

from typing import List
import swagger_client as conan
import utils

# %% parse recommend
with open('recommend/zhihu-1.txt', 'r', encoding='utf8') as f:
    lines = f.read().splitlines(keepends=False)

import re

recommend_eps = []

for line in lines:
    if len(line) == 0:
        continue

    m = re.findall(r'^(\d+)', line)
    epid = int(m[0])
    recommend_eps.append(epid)

for x in recommend_eps:
    print(x)

# %% login


api = utils.Api()


api.login('chr001', 'DetectiveChr231223')

# %% get my eps
views = api.users_api.get_my_video_views()


views: List[conan.VideoView]

viewed_ids = [int(p.video_id[2:])
              for p in views if p.video_id.startswith('tv')]

# %% diff

recom_set = set(recommend_eps)
view_set = set(viewed_ids)

diff_eps = list(recom_set - view_set)
diff_eps.sort()

print(diff_eps)

# %%
