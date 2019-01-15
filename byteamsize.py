import json
import numpy as np

repolib_user = dict()
with open('Ats.txt', 'rb') as f:
    repouser = ''
    for line in f:
        line = line.decode('utf-8', errors='ignore').strip()
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


commits_dict = dict()
with open('commit_dictionary.txt', 'r') as f:
    repo = ''
    lib = ''
    user = ''
    repolib = ''
    i=0

    for line in f:
        if i > 50000:
            break
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
for repolib in commits_dict:
    repo, user = repolib.split('__')[:2]
    repo = '__'.join([repo,user])
    if repo not in repolib_user:
        continue
    teamsize = len(repolib_user[repo])
    if teamsize in [3,4,5]:
        teamsize = 3
    if teamsize in [6,7,8,9]:
        teamsize = 6
    if teamsize >= 10:
        teamsize = 10
    if teamsize not in byteamsize:
        byteamsize[teamsize] = list()
    byteamsize[teamsize].append(commits_dict[repolib])

cidmean = dict()
for teamsize in sorted(byteamsize.keys()):
    summer = 0
    cidmean[teamsize] = list()
    #commit_dist_pos = dict()
    #commit_dist_neg = dict()
    commit_dist_dif = dict()
    commits = byteamsize[teamsize]
    for repolib_commits in commits:
        for cid, pos, neg in repolib_commits:
            summer += 1
            if cid not in commit_dist_dif:
                #commit_dist_pos[cid] = list()
                #commit_dist_neg[cid] = list()
                commit_dist_dif[cid] = 0
            #commit_dist_pos[cid].append(pos)
            #commit_dist_neg[cid].append(neg)
            commit_dist_dif[cid] += (pos - neg)

    print('Team Size: ', teamsize)
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
        cidmean[teamsize].append(summean)


for i in range(0,100):
    print(i, end=',')
    for teamsize in cidmean.keys():
        print(cidmean[teamsize][i], end=',')
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

