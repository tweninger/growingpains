import json
import numpy as np

repolib_user = dict()
i = 0
with open('/data/tweninge/growingpains/ts.txt', 'rb') as f:
    repouser = ''
    for line in f:
        line = line.decode('utf-8', errors='ignore').strip()
        try:
            if line.startswith('/scratch365'):
                repo = line.split('/')[-1]
                try:
                    repo, user = repo.split('__')
                except:
                    print(line)
                    continue

                repouser = '__'.join([repo, user])
                if repouser not in repolib_user:
                    repolib_user[repouser] = set()
            else:
                chash, gituser, ts = line.split('\t')
                repolib_user[repouser].add(gituser.lower())
        except:
            print("error:", line)
        if (i % 100000) == 0:
            print(i)
        i = i + 1

commits_dict = dict()
with open('/data/tweninge/growingpains/commit_dictionary.txt', 'r') as f:
    repo = ''
    lib = ''
    user = ''
    repolib = ''
    i=0

    for line in f:
        line = line.strip()
        try:
            if '__' in line:
                repo, lib = line.split(',')
                repo, user = repo.split('__')
                user = user[:-15]
                repolib = '__'.join([repo,user,lib])


                i += 1
                if i % 10000 == 0:
                    print(i, 'of 5,104,000')
            else:
                c, p, n, t = line.split(',')
                c = int(c)
                if c > 100:
                    continue
                p = int(p)
                n = int(n)
                t = int(t)
                if repolib not in commits_dict:
                    commits_dict[repolib] = list()
                commits_dict[repolib].append((c,p,n))
        except:
            print('error', line)

byteamsize = dict()
repos_used = dict()
j = 0
with open('repo_by_teamsize.txt', 'w') as f:
    for repolib in commits_dict:
        repo, user = repolib.split('__')[:2]
        repo = '__'.join([repo,user])
        if repo not in repolib_user:
            continue
        teamsize = len(repolib_user[repo])
        f.write(str(repo))
        f.write(',')
        f.write(str(teamsize))
        f.write('\n')
        if (j % 100000) == 0:
            print(j)
        j = j + 1
