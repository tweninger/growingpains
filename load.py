import json
import os.path
import re
import subprocess
from collections import OrderedDict


# appends repo name to fail log file for later
def log_fail(root_dir, repo_name):
    with open(root_dir + "/github_files/github_fail_clone.txt", "a") as fail_log:
        fail_log.write(repo_name + "\n")


# end log_fail

def parse_import(line):
    # remove leading character (+ or -)
    line = line[1:].strip()
    if line.endswith(','):
        line = line[:-1]
    # line = unicodedata.normalize('NFD', line).encode('ascii', 'ignore')
    # remove any trailing comments
    line = line.split("#")[0]

    # lots of sad cases
    #       import x                                -> x
    #       import x as y, z as w, ...              -> x, z
    #       from x import y as z, v as w, ...       -> x.y, x.v
    #       from x import y                         -> x.y
    #       from x import *                         -> x.*

    # first, check if entire line matches regex (the worst regex ever)
    pattern = "^\s*(from\s(([a-zA-Z]|\.|\_|\d)+)\s){0,1}import(\s(([a-zA-Z]|\.|\_|\d)+)(\sas\s(([a-zA-Z]|\.|\_|\d)+))*,)*(\s(([a-zA-Z]|\.|\_|\d)+)(\sas\s(([a-zA-Z]|\.|\_|\d)+))*)\s*$"

    # res = re.search(pattern, line)
    # if res == None:
    if re.search(pattern, line) == None:
        return [], {}

    # special-case some other things that are sneaking through
    # if any(c in line for c in ("(", "+", "=")): #, "{", "is", "in", "or", "\\", "//", "}", "'", "0", "%", "like", "2", "my", "be", "run", "``from", "``True``")):
    #       print res, line, ":", res,

    # matches pattern, tokenize
    line = line.replace(',', ' ')  # replace ',' with space to tokenize
    tokens = [x.strip() for x in line.split()]
    lib = []
    aslib = {}

    if len(tokens) == 0:
        return lib, aslib

    # if find an as, throw it and the next token out
    # from? from x import y, z -> x.y, x.z
    if tokens[0] == "from" and len(tokens) >= 4:
        base = tokens[1] + "."
        fnamebase = base.split(".")
        fnamebase = fnamebase[0]
        flag = False
        for s in tokens[3:]:
            if flag:
                flag = False
                aslib[s] = fnamebase
                lib.append(base + s)
                continue
            if s == "as":  # as? from x import y as z -> x.y
                flag = True
                continue
            lib.append(base + s)

    # import? import x, y, z
    elif tokens[0] == "import" and len(tokens) >= 2:
        flag = False
        for s in tokens[1:]:
            if flag:
                flag = False
                aslib[s] = fname
                lib.append(s)
                continue
            if s == "as":
                flag = True
                continue
            lib.append(s)
            fname = s.split(".")
            fname = fname[0]

    return lib, aslib


# checks if a file contains a valid matching import statement
def contains_import(filename):
    pattern = r"^\s*(from\s(([a-zA-Z]|\.|\_|\d)+)\s){0,1}import(\s(([a-zA-Z]|\.|\_|\d)+)(\sas\s(([a-zA-Z]|\.|\_|\d)+))*,)*(\s(([a-zA-Z]|\.|\_|\d)+)(\sas\s(([a-zA-Z]|\.|\_|\d)+))*)\s*$"
    try:
        if os.path.islink(filename) == False:
            with open(filename, 'r') as f:
                for line in f:
                    if re.search(pattern, line) != None:
                        return True  # return true if found import
    except:
        print("fail open", filename)
    return False  # no import, return false


# end contains_import

# delete files in directory, leaving only .py (and related) and files containing a matching import
# call on directory to "shrink"
# goal: remove all files from directory recursively that
#	- are not git files
#	- do not contain an import statement
#	- are not a python file (py, pyc, pyd, pyo, py3, pyw, pyx, pxd, pxi, pyi, pyz, pywz, ipynb)
def delete_files(dir):
    delete_count = 0

    # loop all files in directory
    for root, dirs, files in os.walk(dir):
        # skip the hidden directories and files (git stuff)
        files = [f for f in files if not f[0] == '.']
        dirs[:] = [d for d in dirs if not d[0] == '.']

        for file in files:
            # skip python files
            if file.lower().endswith(('.py', '.pyc', '.pyd', '.pyo', '.py3', '.pyw', '.pyx', '.pxd', '.pxi', '.pyi',
                                      '.pyz', '.pywz', '.ipynb')):
                continue

            # create complete path
            path = os.path.join(root, file)

            # skip files containing valid import statement (just to be safe)
            if contains_import(path):
                continue

            # weeded out the "good" files, delete what remains
            # print path
            try:
                # unlink for symlinks
                if os.path.islink(path):
                    os.unlink(path)
                # true delete for files
                else:
                    os.remove(path)
                delete_count += 1
            except:
                print("fail", path)
    print("deleted", delete_count, "files")


# end delete_files

def create_new_entry(dictionary, tag, time, oldtime):
    ls = dictionary[tag + " time"]
    ls.append(time)
    dictionary[tag + " time"] = ls
    dictionary[tag] = dictionary[tag] + 1
    dictionary["old time"][time] = oldtime
    return dictionary


def create_library_instances(l2, cleanlibs):
    cleanlibs.append(" " + l2 + "(")
    cleanlibs.append("." + l2 + "(")
    cleanlibs.append(" " + l2 + ".")
    cleanlibs.append("(" + l2 + ".")
    cleanlibs.append("(" + l2 + "(")
    cleanlibs.append('@' + l2 + ".")
    cleanlibs.append('@' + l2 + "(")
    return cleanlibs


# --- MAIN EXECUTION BEGINS HERE---#


# grab and save current working directory

root_dir = "./"

# create directory for commit data (if doesn't already exist)
if os.path.isdir("./dictionary_data_library2") == False:
    os.makedirs("./dictionary_data_library2")

# process each repo

f = os.listdir('repo_clones')

i = 0
for repo_name in f:

    # extract commit data if commit log file doesn't exist
    if (os.path.isfile("dictionary_data_library2/%s_dictionary.log" % (repo_name)) == False):

        print("Extracting commit data from", repo_name)
        # move to git directory
        try:
            os.chdir("./repo_clones/" + repo_name)
        except:
            print("Error with ", repo_name)
            continue
        # get list of all matching commit diffs, save to file (if not already done)
        if os.path.isfile("../dictionary_data_library2/%s_dictionary.log" % (repo_name)) == False:
            print(os.listdir())
            f = open("../../dictionary_data_library2/%s_dictionary.log" % (repo_name), "w")
            # pull all commit data, and commit contents starting with "import" or "from"
            try:
                output = subprocess.check_output(
                    'git rev-list --reverse --all | xargs git show --format="###############################################&%aE& %aN& %h& %p& %at" --unified=0  | awk "/^#####/ || /^\-+[[:blank:]]?.*?\(.*?/ || /^\++[[:blank:]]?.*?\(.*?/ ||  /^\++[[:blank:]]?.*?\..*?/ ||  /^\-+[[:blank:]]?.*?\..*?/ || /\-+[[:blank:]]*import/ || /\++[[:blank:]]*import/  || /\-+[[:blank:]]*from/ || /\++[[:blank:]]*from/"',
                    shell=False)
            except:
                output = b"""###############################################&MY_NAME@example.com& ni8mr& 873140b& & 1430897639
+++ b/README.md
+A simple blog built with Flask.
+++ b/blog.py
+# blog.py - controller
+from flask import Flask, render_template, request, session, 
+
+import sqlite3
+DATABASE = 'blog.db'
+app = Flask(__name__)
+app.config.from_object(__name__)
+def connect_db():
+    return sqlite3.connect(app.config['DATABASE'])
+@app.route('/')
+def login():
+    return render_template('login.html')
+@app.route('/main')
+def main():
+    return render_template('main.html')
+    app.run(debug=True)
+++ b/sql.py
+# sql.py - Creating a SQLite3 table and populate it with data
+import sqlite3
+with sqlite3.connect("blog.db") as conn:
+    c = conn.cursor()
+    c.execute('CREATE TABLE posts(title TEXT, post TEXT)')
+    c.execute('INSERT INTO posts VALUES("Good", "I\'m good.")')
+    c.execute('INSERT INTO posts VALUES("Well", "I\'m well.")')
+    c.execute('INSERT INTO posts VALUES("Excellent", "I\'m excellent.")')
+    c.execute('INSERT INTO posts VALUES("Okay", "I\'m okay.")')
+++ b/templates/login.html
+{% extends "template.html" %}
+    <h3>Please login to access your blog.</h3>
+++ b/templates/main.html
+{% extends "template.html" %}
+++ b/templates/template.html
###############################################&MY_NAME@example.com& ni8mr& 8fda571& 873140b& 1431343688
--- a/blog.py
+++ b/blog.py
+from functools import wraps
-@app.route('/')
+def login_required(test):
+    @wraps(test)
+    def wrap(*args, **kwargs):
+            return test(*args, **kwargs)
+            flash('You need to login first.')
+            return redirect(url_for('login'))
+@app.route('/', methods = ['GET', 'POST'])
+    if request.method == 'POST':
+        if request.form['username'] != app.config['USERNAME'] or \
+           request.form['password'] != app.config['PASSWORD']:
+            error = 'Invalid Credentials. Please try again. '
+            return redirect(url_for('main'))
+@app.route('/logout')
+def logout():
+    session.pop('logged_in',None)
+    flash('You were logged out')
+    return redirect(url_for('login'))
--- a/sql.py
+++ b/sql.py
-    c.execute('INSERT INTO posts VALUES("Excellent", "I\'m excellent.")')
-    c.execute('INSERT INTO posts VALUES("Okay", "I\'m okay.")')
--- a/templates/login.html
+++ b/templates/login.html
+            Username: <input type="text" name="username" value="{{ request.form.username }}">
+            Password: <input type="password" name="password" value="{{ request.form.password }}">
--- a/templates/main.html
+++ b/templates/main.html
--- a/templates/template.html
+++ b/templates/template.html
+            {% for message in get_flashed_messages() %}
###############################################&MY_NAME@example.com& ni8mr& eff4cb7& 8fda571& 1431610888
--- a/blog.py
+++ b/blog.py
-# blog.py - controller
-app.config.from_object(__name__)
+app.config.from_object(__name__)
-@app.route('/', methods = ['GET', 'POST'])
+@app.route('/', methods=['GET', 'POST'])
-            error = 'Invalid Credentials. Please try again. '
+            error = 'Invalid Credentials. Please try again.'
-    return render_template('login.html')
-@app.route('/logout')
-def logout():
-    session.pop('logged_in',None)
-    flash('You were logged out')
-    return redirect(url_for('login'))
+    return render_template('login.html', error=error)
-    return render_template('main.html')
+    g.db = connect_db()
+    cur = g.db.execute('select * from posts')
+    posts = [dict(title=row[0], post=row[1]) for row in cur.fetchall()]
+    g.db.close()
+    return render_template('main.html', posts=posts)
+@app.route('/add', methods=['POST'])
+def add():
+    title = request.form['title']
+    post = request.form['post']
+        flash("All fields are required. Please try again.")
+        return redirect(url_for('main'))
+        g.db = connect_db()
+        g.db.execute('insert into posts (title,post) values (?,?)',
+                     [request.form['title'],request.form['post']])
+        g.db.commit()
+        g.db.close()
+        flash('New entry was successfully posted!')
+        return redirect(url_for('main'))
+@app.route('/logout')
+def logout():
+    session.pop('logged_in', None)
+    flash('You were logged out.')
+    return redirect(url_for('login'))
--- a/sql.py
+++ b/sql.py
-# sql.py - Creating a SQLite3 table and populate it with data
-with sqlite3.connect("blog.db") as conn:
+with sqlite3.connect("blog.db") as conn:
-    c.execute('CREATE TABLE posts(title TEXT, post TEXT)')
+    c.execute('CREATE TABLE posts (title TEXT, post TEXT)')
+    c.execute('INSERT INTO posts VALUES("Excellent", "I\'m excellent.")')
+    c.execute('INSERT INTO posts VALUES("Okay", "I\'m okay.")')
+++ b/static/css/styles.css
+.container{
+  padding: 0.8em;
+.flash, .error{
+  padding: 0.5em;
--- a/templates/login.html
+++ b/templates/login.html
-            Username: <input type="text" name="username" value="{{ request.form.username }}">
-            Password: <input type="password" name="password" value="{{ request.form.password }}">
+              request.form.username }}">
+              request.form.password }}">
--- a/templates/main.html
+++ b/templates/main.html
+    <form action="{{ url_for('add') }}" method="post" class="add">
+        <strong>Title:</strong>{{p.title}}<br/>
+        <strong>Post:</strong>{{p.post}}<br/>
--- a/templates/template.html
+++ b/templates/template.html
+        <link rel="stylesheet" href="{{ url_for('static', filename='css/styles.css') }}">
###############################################&ni8mr@users.noreply.github.com& Noor Faizur Reza& 3c6e034& eff4cb7& 1431698833
--- a/templates/login.html
+++ b/templates/login.html
"""
            output = output.split(b'###############################################&')
            output_dict = {}
            output_final = {}
            parent_hash = {}
            for o in output:
                o = o.splitlines()
                try:
                    o[0] = b'#####' + o[0]
                    author, repo, h, parent, time = o[0].split(b'&')
                    parent = parent.decode('ascii', 'ignore')
                    h = h.decode('ascii', 'ignore')
                    time = time.decode('ascii', 'ignore')
                    parent = parent.strip()
                    h = h.strip()
                    parents = parent.split(' ')
                    output_dict[h] = {}
                    output_final[h] = o
                    for p in parents:
                        if p != '':
                            output_dict[h][p] = ""
                            if p in parent_hash:
                                parent_hash[p][h] = ""
                            else:
                                parent_hash[p] = {}
                                parent_hash[p][h] = ""
                except:
                    next
            alllibs = set()
            users = {}
            dictionary_reference = {}
            oldtime = 0
            real_dict = ""
            order_list = OrderedDict()
            while output_dict != {}:
                output_dict_copy = output_dict.copy()
                for h, v in output_dict_copy.items():
                    if output_dict[h] == {}:
                        next_o = h
                        output_dict.pop(h)
                        order_list[next_o] = ""
                        try:
                            for h in parent_hash[next_o]:
                                output_dict[h].pop(next_o)
                        except:
                            break
            for h, v in order_list.items():
                output = output_final[h]
                for o in output:
                    o = o.decode('ascii', 'ignore')
                    if (o[0:5] == '#####'):
                        o = o.split('&')
                        user = o[0][7:]
                        try:
                            oldtime = time
                            time = int(o[len(o) - 1])
                        except:
                            print("except:", o)
                            continue
                    elif 'import ' in o:
                        if '+' == o[0]:
                            sign = '+'
                            libs, aslib = parse_import(o)
                            cleanlibs = []
                            textlibs = []
                            for l in libs:
                                if '.' in l:
                                    l = l.split('.')
                                    for l1 in l:
                                        if (l1 != ''):
                                            toplib = l1
                                            textlibs.append(toplib)
                                            break
                                    for l2 in l:
                                        if (l2 != ''):
                                            cleanlibs = create_library_instances(l2, cleanlibs)
                                            dictionary_reference[l2] = toplib
                                else:
                                    if (l != ''):
                                        cleanlibs = create_library_instances(l, cleanlibs)
                                        if (l in aslib):
                                            dictionary_reference[l] = aslib[l]
                                            textlibs.append(aslib[l])
                                        else:
                                            dictionary_reference[l] = ""
                                            textlibs.append(l)
                            cleanlibs = set(cleanlibs)
                            alllibs = alllibs.union(cleanlibs)
                        else:
                            libs, aslib = parse_import(o)
                            cleanlibs = []
                            textlibs = []
                            sign = '-'
                            for l in libs:
                                if '.' in l:
                                    l = l.split('.')
                                    for l1 in l:
                                        if (l1 != ''):
                                            toplib = l1
                                            textlibs.append(toplib)
                                            break
                                else:
                                    if (l != ''):
                                        cleanlibs = create_library_instances(l, cleanlibs)
                                        if (l in aslib):
                                            dictionary_reference[l] = aslib[l]
                                            textlibs.append(aslib[l])
                                        else:
                                            dictionary_reference[l] = ""
                                            textlibs.append(l)
                            cleanlibs = set(cleanlibs)
                            alllibs = alllibs.union(cleanlibs)
                        for real_dict in textlibs:
                            if user not in users:
                                users[user] = {}
                            if real_dict not in users[user]:
                                users[user][real_dict] = {}
                                users[user][real_dict]['positive time'] = []
                                users[user][real_dict]['negative time'] = []
                                users[user][real_dict]['positive'] = 0
                                users[user][real_dict]['negative'] = 0
                                users[user][real_dict]['old time'] = {}
                            if (sign == '+'):
                                users[user][real_dict] = create_new_entry(users[user][real_dict], 'positive', time,
                                                                          oldtime)
                            elif (sign == '-'):
                                users[user][real_dict] = create_new_entry(users[user][real_dict], 'negative', time,
                                                                          oldtime)

                    else:
                        o.replace(" (", "(")
                        functionsused = []
                        o = o.split(' ', 1)
                        try:
                            sign = o[0][0]
                        except:
                            next
                        try:
                            o = (o[1]).strip()
                        except:
                            o = o[0]
                        o = o.strip()
                        o = ' ' + o
                        for a2 in alllibs:
                            if a2 in o:
                                a = a2[:len(a2) - 1][1:]
                                current_dict = a
                                real_dict = dictionary_reference[current_dict]
                                if (real_dict == ""):
                                    real_dict = current_dict
                                if a != '':
                                    if user not in users:
                                        users[user] = {}
                                    if real_dict not in users[user]:
                                        users[user][real_dict] = {}
                                        users[user][real_dict]['positive time'] = []
                                        users[user][real_dict]['negative time'] = []
                                        users[user][real_dict]['positive'] = 0
                                        users[user][real_dict]['negative'] = 0
                                        users[user][real_dict]['old time'] = {}
                                    if (sign == '+'):
                                        users[user][real_dict] = create_new_entry(users[user][real_dict], 'positive',
                                                                                  time, oldtime)
                                    elif (sign == '-'):
                                        users[user][real_dict] = create_new_entry(users[user][real_dict], 'negative',
                                                                                  time, oldtime)
                                break
            json.dump(users, f)
            f.close()

        # change back to repo_clones directory
        os.chdir("../../")

    # period prints
    else:
        print("Already cloned and processed", repo_name)
    if i % 100 == 0:
        print("FINISHED", i, "REPOS OUT OF ", 1)

# final print
print("Done")
