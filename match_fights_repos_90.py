import pandas as pd

f90fights = pd.read_csv('fights2.txt', usecols=[0], header=None, names=['Repo'])

f90fights = f90fights.groupby('Repo').last()

f90fights = pd.DataFrame(data=f90fights, columns=['Repo2']).reset_index()
f90fights.columns = ['Repo', 'Size']
f90fights = f90fights.drop(['Size'], axis=1)
teamsize = pd.read_csv('repo_by_teamsize.txt', header=None, names=['Repo', 'Team Size'])
f90fights_team = teamsize.merge(f90fights, on='Repo', how='inner')


f90fights_teamsize = f90fights_team.groupby('Team Size').agg(['count'])
normal_teamsize = teamsize.groupby('Team Size').agg(['count'])

f90teamsize_groups = f90fights_teamsize.merge(normal_teamsize, on='Team Size', how='inner')
f90teamsize_groups.columns = ['Number of Teams at Size', 'Number of Repos at Size']
f90teamsize_groups['Result'] = f90teamsize_groups['Number of Teams at Size']/f90teamsize_groups['Number of Repos at Size']
f90teamsize_gropus = f90teamsize_groups.drop(['Number of Repos at Size', 'Number of Teams at Size'], axis=1)
f90teamsize_groups.to_csv('90_fight_percentages.txt')


    
