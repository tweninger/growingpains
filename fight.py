import json
import numpy as np

ts_user = dict()
i = 0
with open('/data/tweninge/growingpains/ts.txt', 'rb') as f:
    repouser = ''
    for line in f:
        line = line.decode('utf-8', errors='ignore').strip()
        if line.startswith('/scratch365'):
            repo = line.split('/')[-1]
            try:
                repo, user = repo.split('__')
                user = user.lower().replace(',', '')
            except:
                print(line)
                continue

            repouser = '__'.join([repo, user])
            if repouser not in ts_user:
                ts_user[repouser] = dict()
        else:
            try:
                chash, gituser, ts = line.split('\t')
                ts = int(ts)
                ts_user[repouser][ts] = gituser.lower().replace(',', '')
            except:
                print(line)
        if (i % 100000) == 0:
            print(i)
        i = i + 1


commits_dict = dict()
with open('/data/tweninge/growingpains/commit_dictionary.txt', 'r') as f, open('fights_after_cut2.txt', 'w') as fwriter:
    repo = ''
    lib = ''
    user = ''
    repolib = ''
    i=0

    author = ''
    commit_counter = 0
    flag = False
    for line in f:
        #if i > 50000:
        #    break
        line = line.strip()
        try:
            if '__' in line:
                commit_counter = 0
                repo, lib = line.encode('utf-8').split(',')
                repo, user = repo.encode('utf-8').split('__')
                user = user[:-15].encode('utf-8').lower().replace(',', '')
                repouser = '__'.join([repo,user]).encode('utf-8')
                running_p = float(0)
                running_n = float(0)
                current_totals = set()
                current_totals.add(running_p - running_n)
                if repouser not in ts_user:
                    repouser = ''
                else:
                    userset = set([ts_user[repouser][ts] for ts in ts_user[repouser]])
                    if len(userset) < 2:
                        repouser = ''
                i += 1
                if i == 50000:
                    break
                if i % 10000 == 0:
                    print(i, 'of 5,104,000')
                flag = False
                c = float(0)
                p = float(0)
                n = float(0)
                t = float(0)
            else:
                commit_counter += 1
                if repouser == '':
                    continue
                previous_p = p
                previous_n = n
                c, p, n, t = line.split(',')
                c = float(c)
                p = float(p)
                n = float(n)
                t = float(t)
                current_totals.add(running_p - running_n)
                new_author = ts_user[repouser][t].encode('utf-8')
                if author is '':
                    author = new_author
                currentauthor_commits = 0
                if (running_p - running_n != 0):
                    percent_of_peak = (running_p - running_n + p - n)/(running_p - running_n)
                    if  author is not '' and abs(percent_of_peak) <= .1 and author != new_author:
                        #fwriter.write(repouser + ',' + lib + ',' + author + ',' + new_author + ',' + str(c) + ',' + str(t) + ',' + str(p) + ',' + str(n) + ',' + str(len(userset)) + ',' + str(commit_counter) + ',' + str(running_p) + ',' + str(running_n) + ',' + str(peak) + '\n')
                        fwriter.write('\n')
                        fwriter.write(str(running_p - running_n))
                        fwriter.write(',')
                        author = new_author
                        commit_counter = 0
                        currentauthor_commits = p - n
                        flag = True
                    elif author is not '' and flag and author != new_author:
                        fwriter.write(str(currentauthor_commits))
                        fwriter.write(',')
                        currentauthor_commits = p - n
                        #fwriter.write(repouser + ',' + lib + ',' + author + ',' + new_author + ',' + str(c) + ',' + str(t) + ',' + str(p) + ',' + str(n) + ',' + str(len(userset)) + ',' + str(commit_counter) + ',' + str(running_p) + ',' + str(running_n) + ',' + str(peak) + '\n')
                        author = new_author
                        commit_counter = 0
                    elif flag:
                        currentauthor_commits = currentauthor_commits + p - n
                if repolib not in commits_dict:
                    commits_dict[repolib] = list()
                commits_dict[repolib].append((c,p,n))
                running_p = running_p + p
                running_n = running_n + n

        except:
            print('error', line)


#byteamsize = dict()
#for repolib in commits_dict:
#    repo, user = repolib.split('__')[:2]
#    repo = '__'.join([repo,user])
#    if repo not in repolib_user:
#        continue
#    teamsize = len(repolib_user[repo])
#    if teamsize in [3,4,5]:
#        teamsize = 3
#    if teamsize in [6,7,8,9]:
#        teamsize = 6
#    if teamsize >= 10:
#        teamsize = 10
#    if teamsize not in byteamsize:
#        byteamsize[teamsize] = list()
#    byteamsize[teamsize].append(commits_dict[repolib])

#cidmean = dict()
#for teamsize in sorted(byteamsize.keys()):
#    summer = 0
#cidmean[teamsize] = list()
#    #commit_dist_pos = dict()
#    #commit_dist_neg = dict()
#    commit_dist_dif = dict()
#    commits = byteamsize[teamsize]
#    for repolib_commits in commits:
#        for cid, pos, neg in repolib_commits:
#            summer += 1
#if cid not in commit_dist_dif:
#                #commit_dist_pos[cid] = list()
#                #commit_dist_neg[cid] = list()
#                commit_dist_dif[cid] = 0
#            #commit_dist_pos[cid].append(pos)
#            #commit_dist_neg[cid].append(neg)
#            commit_dist_dif[cid] += (pos - neg)

#    print('Team Size: ', teamsize)
#    #print('Positive')
#    #for cid in sorted(commit_dist_pos.keys()):
#    #    print(cid, np.mean(commit_dist_pos[cid]), np.median(commit_dist_pos[cid]), np.std(commit_dist_pos[cid]),
#    #          len(commit_dist_pos[cid]))
#    #print('Negative')
#    #for cid in sorted(commit_dist_neg.keys()):
#    #    print(cid, np.mean(commit_dist_neg[cid]), np.median(commit_dist_neg[cid]), np.std(commit_dist_neg[cid]),
#    #          len(commit_dist_neg[cid]))
#    #print('Difference')
#    #for cid in sorted(commit_dist_dif.keys()):
#    #    print(cid, np.mean(commit_dist_dif[cid]), np.median(commit_dist_dif[cid]), np.std(commit_dist_dif[cid]),
#    #          len(commit_dist_dif[cid]))

#    summean = 0
#    for cid in sorted(commit_dist_dif.keys()):
#        summean += commit_dist_dif[cid]/summer
#        cidmean[teamsize].append(summean)


#for i in range(0,100):
#    print(i, end=',')
#    for teamsize in cidmean.keys():
#        print(cidmean[teamsize][i], end=',')
#    print()

#print('Loaded')

#repos = json.load(open('github_all_repos.json', 'r'))
#for repo in repos['items']:
#    print(repo)
#    #'watchers_count'
#    #'stargazers_count'
#    #'open_issues'
#    #'forks'
#    break

