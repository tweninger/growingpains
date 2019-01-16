
fights = list()
repolib = ''
user_cnt = dict()
user_first = dict()
user_last = dict()
#load fights
with open('fights.txt') as f:
    fight = list()
    fighter_x = ''
    fighter_y = ''
    pos = 0
    for line in f:
        line = line.strip()
        # repouser + ',' + lib + ',' + author + ',' + new_author + ',' + str(c) + ',' + str(t) + ',' + str(p) + ',' + str(n) + ',' + str(len(userset)) + ',' + str(commit_counter) + '\n')
        s = line.split(',')
        if len(s) != 10:
            print(line)
            continue
        new_repolib = s[0] + ',' + s[1]
        if repolib != new_repolib:
            fights.append(fight)
            repolib = new_repolib
            fight = list()
            fighter_x = s[2]
            fighter_y = s[3]
            user_cnt[fighter_x] = user_cnt.get(fighter_x, 0) + 1
            user_cnt[fighter_y] = user_cnt.get(fighter_y, 0) + 1
            ts = int(s[5])

            if fighter_x not in user_first:
                user_first[fighter_x] = ts
            else:
                user_first[fighter_x] = min(user_first[fighter_x], ts)
            if fighter_y not in user_first:
                user_first[fighter_y] = ts
            else:
                user_first[fighter_y] = min(user_first[fighter_y], ts)

            if fighter_x not in user_last:
                user_last[fighter_x] = ts
            else:
                user_last[fighter_x] = min(user_last[fighter_x], ts)
            if fighter_y not in user_last:
                user_last[fighter_y] = ts
            else:
                user_last[fighter_y] = min(user_last[fighter_y], ts)
        if len({s[2], s[3]}.intersection({fighter_x, fighter_y})) == 2:
            fight.append(s)
        if len(fights) > 1000000:
            break



#number of fights:
print('Number of fights: ', len(fights))

#number of fights by team size:
team_size_len = dict()
for fight in fights:
    if len(fight) == 0:
        continue
    team_size_len[int(fight[0][8])] = team_size_len.get(int(fight[0][8]), 0) + 1
print('Num Fights by team size: ')
for teamsize in sorted(team_size_len.keys()):
    print(teamsize, team_size_len[teamsize])

#how long are fights?
fight_len_dist = dict()
for fight in fights:
    fight_len_dist[len(fight)] = fight_len_dist.get(len(fight), 0) + 1

print('Fight Length Distribution: ')
for leng in sorted(fight_len_dist.keys()):
    print(leng, fight_len_dist[leng])


#what libs?
libs_size = dict()
for fight in fights:
    if len(fight) == 0:
        continue
    libs_size[fight[0][1]] = libs_size.get(fight[0][1], 0) + 1

print('Library Distribution: ')
sorted_by_value = sorted(libs_size.items(), key=lambda kv: kv[1], reverse=True)
for lib, size in sorted_by_value[:100]:
    print(lib, size)


#common fighters?
fighters_size = dict()
for fight in fights:
    if len(fight) == 0:
        continue
    match = '  -vs-  '.join(sorted([fight[0][2], fight[0][3]]))
    fighters_size[match] = libs_size.get(match, 0) + 1

print('Fighter Matches Distribution: ')
sorted_by_value = sorted(fighters_size.items(), key=lambda kv: kv[1], reverse=True)
for lib, size in sorted_by_value[:100]:
    print(lib, size)

#Who wins?
adopter_wins = 0
nonadopter_wins = 0
for fight in fights:
    if len(fight) == 0:
        continue
    adopter = fight[0][2]
    winner = fight[-1][3]
    if winner == adopter:
        adopter_wins += 1
    else:
        nonadopter_wins += 1

print('Adopter vs NonAdopter Wins: ', adopter_wins, nonadopter_wins)



#Who wins?
cnt_wins = 0
cnt_loses = 0
tie = 0
for fight in fights:
    if len(fight) == 0:
        continue
    adopter = fight[0][2]
    fighter_y = fight[0][3]
    winner = fight[-1][3]
    cnt_adopter = user_cnt[adopter]
    cnt_fighter_y = user_cnt[fighter_y]
    cnt_winner = ''
    if cnt_adopter == cnt_fighter_y:
        tie += 1
        continue
    if cnt_adopter > cnt_fighter_y:
        cnt_winner = adopter
    else:
        cnt_winner = fighter_y
    if winner == cnt_winner:
        cnt_wins += 1
    else:
        cnt_loses += 1

print('Experience (most commits) wins vs loses: ', cnt_wins, cnt_loses, tie)



#Who wins?
exp_wins = 0
exp_loses = 0
tie = 0
for fight in fights:
    if len(fight) == 0:
        continue
    adopter = fight[0][2]
    fighter_y = fight[0][3]
    winner = fight[-1][3]
    exp_adopter = user_first[adopter]
    exp_fighter_y = user_first[fighter_y]
    exp_winner = ''
    if exp_adopter == exp_fighter_y:
        tie += 1
        continue
    if exp_adopter > exp_fighter_y:
        exp_winner = adopter
    else:
        exp_winner = fighter_y
    if winner == exp_winner:
        exp_wins += 1
    else:
        exp_loses += 1

print('Experience(earliest account) wins vs loses: ', exp_wins, exp_loses, tie)