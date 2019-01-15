import numpy as np

pos = dict()
neg = dict()


def parse(lines):
    c = 0
    for line in lines:
        sp = line.strip().split(', ')
        if not (len(sp) > 1 and len(sp) < 4):
            print(line)
        if sp[1].endswith('(+)'):
            p = int(sp[1].split(' ')[0])
            pos[c].append(p)
            if len(sp) == 3 and sp[2].endswith('(-)'):
                n = int(sp[2].split(' ')[0])
                neg[c].append(n)
            else:
                neg[c].append(0)
        elif sp[1].endswith('(-)'):
            pos[c].append(0)
            n = int(sp[1].split(' ')[0])
            neg[c].append(n)
        else:
            pass
            #print(line)

        c += 1

repo = 0
loadlines = list()
with open('graph.txt') as f:
    c = 0
    for line in f:
        if c not in pos:
            pos[c] = list()
        if c not in neg:
            neg[c] = list()

        if ' changed, ' in line:
            loadlines.append(line)
            c += 1
        else:
            try:
                parse(reversed(loadlines))
            except:
                pass
            loadlines = list()
            c = 0

            if repo % 1000 == 0:
                print(repo)
            repo += 1

for i in pos.keys():
    if len(pos[i]) == 0:
        continue
    if i > 100:
        break
    mean = np.mean(pos[i])
    med = np.median(pos[i])
    s = np.sum(pos[i])
    std = np.std(pos[i])
    q1 = np.quantile(pos[i], .25)
    q3 = np.quantile(pos[i], .75)
    cnt = len(pos[i])

    print(str( (i, mean, med, s, std, q1, q3, cnt ) ) )

for i in pos.keys():
    if len(neg[i]) == 0:
        continue
    if i > 100:
        break
    mean = np.mean(neg[i])
    med = np.median(neg[i])
    s = np.sum(neg[i])
    std = np.std(neg[i])
    q1 = np.quantile(neg[i], .25)
    q3 = np.quantile(neg[i], .75)
    cnt = len(neg[i])

    print(str( (i, mean, med, s, std, q1, q3, cnt ) ) )