import json
from stackoverflow_searcher import Searcher
from datetime import datetime

s = Searcher()
repolib_user = dict()
commits_dict = dict()
with open('commit_dictionary.txt', 'r') as f:
    repo = ''
    lib = ''
    user = ''
    repolib = ''
    i=0

    for line in f:
        #if i > 560000:
        #    break
        line = line.strip()
        try:
            if '__' in line:
                repo, lib = line.split(',')
                repo, user = repo.split('__')
                repolib = '__'.join([repo,lib])
                user = user[:-15]

                if repolib not in repolib_user:
                    repolib_user[repolib] = set()
                repolib_user[repolib].add(user)
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
                commits_dict[repolib].append((c,p,n,t))
        except:
            print('error', line)

so_cache = dict()
bysosize = dict()
i = 0
for repolib in commits_dict:
    i+=1
    if i %10000 == 0:
        print(i)
    lib = repolib.split('__')[1]
    ts = commits_dict[repolib][0][3]
    if not ts >0:
        continue
    try:
        ts = datetime.fromtimestamp(ts)
    except:
        print(ts)
        continue
    strts = str(ts.year) + ',' + str(ts.month)
    if lib not in so_cache:
        so_cache[lib] = dict()
    if strts not in so_cache[lib]:
        sosize = len(s.search(lib, datetime(2000, 1, 1), ts))
        so_cache[lib][strts] = sosize
    sosize = so_cache[lib][strts]

    if sosize == 0:
        sosize = 0
    if  1 <= sosize <= 10:
        sosize = 1
    if 10 < sosize <= 100:
        sosize = 10
    if 100 < sosize <= 1000:
        sosize = 100
    if 1000 < sosize:
        sosize = 1000
    if sosize not in bysosize:
        bysosize[sosize] = list()
    bysosize[sosize].append(commits_dict[repolib])


cidmean = dict()
for sosize in sorted(bysosize.keys()):
    summer = 0
    cidmean[sosize] = list()
    #commit_dist_pos = dict()
    #commit_dist_neg = dict()
    commit_dist_dif = dict()
    commits = bysosize[sosize]
    for repolib_commits in commits:
        for cid, pos, neg, _ in repolib_commits:
            summer += 1
            if cid not in commit_dist_dif:
                #commit_dist_pos[cid] = list()
                #commit_dist_neg[cid] = list()
                commit_dist_dif[cid] = 0
            #commit_dist_pos[cid].append(pos)
            #commit_dist_neg[cid].append(neg)
            commit_dist_dif[cid] += (pos - neg)

    print('SO Size: ', sosize)
    #print('Positive')
    #for cid in sorted(commit_dist_pos.keys()):
    #    print(cid, np.mean(commit_dist_pos[cid]), np.median(commit_dist_pos[cid]), np.std(commit_dist_pos[cid]),
    #          len(commit_dist_pos[cid]))
    #print('Negative')
    #for cid in sorted(commit_dist_neg.keys()):
    #    print(cid, np.mean(commit_dist_neg[cid]), np.median(commit_dist_neg[cid]), np.std(commit_dist_neg[cid]),
    #          len(commit_dist_neg[cid]))
    #print('Difference')
    #for cid in sorted(commit_dist_dif.keys()):
    #    print(cid, np.mean(commit_dist_dif[cid]), np.median(commit_dist_dif[cid]), np.std(commit_dist_dif[cid]),
    #          len(commit_dist_dif[cid]))

    summean = 0
    for cid in sorted(commit_dist_dif.keys()):
        summean += commit_dist_dif[cid]/summer
        cidmean[sosize].append(summean)


for i in range(0,100):
    print(i, end=',')
    for sosize in cidmean.keys():
        print(cidmean[sosize][i], end=',')
    print()

print('Loaded')

repos = json.load(open('github_all_repos.json', 'r'))
for repo in repos['items']:
    print(repo)
    #'watchers_count'
    #'stargazers_count'
    #'open_issues'
    #'forks'
    break

