import json
from stackoverflow_searcher import Searcher
from datetime import datetime

s = Searcher()
repolib_user = dict()
commits_dict = dict()

pipy = set()
with open('pypi.html', 'r') as f:
    for line in f:
        line = line.strip()
        if line.startswith('<a '):
            lib = line.split('<')[1].split('>')[1]
            pipy.add(lib.strip().lower())


builtin = set()
with open('builtin.html', 'r') as f:
    for line in f:
        line = line.strip()
        if '<code class="xref">' in line:
            lib = line.split('<code class="xref">')[1].split('<')[0]
            builtin.add(lib.strip().lower())

with open('commit_dictionary.txt', 'r') as f:
    repo = ''
    lib = ''
    user = ''
    repolib = ''
    i=0

    for line in f:
        #if i > 50000:
        #    break
        line = line.strip()
        try:
            if '__' in line:
                repo, lib = line.split(',')
                repo, user = repo.split('__')
                #repolib = '__'.join([repo,lib])
                user = user[:-15]

                if lib not in repolib_user:
                    repolib_user[lib] = set()
                repolib_user[lib].add(user)
                i += 1
                if i % 10000 == 0:
                    print(i, 'of 5,104,000')
        except:
            print('error', line)

so_cache = dict()
bysosize = dict()
i = 0
for lib in repolib_user.keys():
    i+=1
    if i %10000 == 0:
        print(i)

    sosize = len(s.search(lib, datetime(2000, 1, 1), datetime(2019, 1, 1)))
    users = len(repolib_user[lib])
    p = 0
    if lib.strip().lower() in builtin:
        p=1
    elif lib.strip().lower() in pipy:
        p=2
    if sosize == 0 or users == 0:
        continue
    print(sosize, users, p, lib)
