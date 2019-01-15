import json
import math

repo_numcom = dict()
i=0
repos = json.load(open('github_all_repos.json', 'r'))
for repo in repos['items']:
    w = int(repo['watchers'])
    name = repo['full_name']
    user, r = name.split('/')
    r = '__'.join([r, user])
    repo_numcom[r] = w
    del repo
    i += 1
    if i % 10000 == 0:
        print(i, 'of 250,000')

del repos

commits_dict = dict()
with open('commit_dictionary.txt', 'r') as f:
    repo = ''
    lib = ''
    user = ''
    repolib = ''
    i=0

    for line in f:
        #if i > 100000:
        #    break
        line = line.strip()
        try:
            if '__' in line:
                repo, lib = line.split(',')
                #repo, user = repo.split('__')
                repo = repo[:-15]
                repolib = '__'.join([repo,lib])


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
    try:
        repo, user, lib = repolib.split('__')
    except:
        continue
    if '__'.join([repo,user]) not in repo_numcom:
        continue
    numcom = repo_numcom['__'.join([repo,user])]
    if 0 == numcom:
        pass
    if 1 < numcom <= 1:
        pass
    if 1 < numcom <= 10:
        numcom = 10
    if 10 < numcom <= 100:
        numcom = 100
    if 100 < numcom <= 1000:
        numcom = 1000
    if 1000 < numcom:
        numcom = 10000
    if numcom not in byteamsize:
        byteamsize[numcom] = list()
    byteamsize[numcom].append(commits_dict[repolib])

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
        try:
            print(cidmean[teamsize][i], end=',')
        except:
            print(str(0), end=',')
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

