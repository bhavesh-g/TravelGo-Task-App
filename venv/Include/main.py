from flask import Flask, render_template, request, session,redirect
import requests,json,random,pymongo,time
from bson.objectid import ObjectId

def make_connection():
    db=pymongo.MongoClient("mongodb://localhost:27017/")
    if('Travelgo' in db.database_names()):
        mydb=db['Travelgo']
        if('login' in mydb.collection_names() and 'posts' in mydb.collection_names()):
            return mydb
        else:
            if( 'posts' in mydb.collection_names() and 'login' not in mydb.collection_names()):
                random=mydb['login']
                return mydb
            elif('posts' not in mydb.collection_names() and 'random'  in mydb.collection_names()):
                custom=mydb['login']
                return mydb
            else:
                custom = mydb['posts']
                random = mydb['login']
                return mydb
    else:
        mydb=db['Travelgo']
        random=mydb['login']
        custom=mydb['posts']
        return mydb

app = Flask(__name__)
mydb=make_connection()
@app.route('/dashboard',methods=['GET','POST'])
def dashboard():
    if "email" in session:
        return render_template("dashboard.html",name=session['author'])
    else:
        return render_template("dashboard.html",message="You must be loggedin to see dashboard!")

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='GET':
        return render_template("login.html")
    else:
        query = mydb.login.find({'email': request.form['email']})
        query_list= list(query)
        print(list(query))
        if query.count()>0:
            if request.form['pass']==query_list[0]['passw'] :
                session['email']= request.form['email']
                print(query_list[0]['name'])
                session['author']= query_list[0]['name'].capitalize()
                return redirect("/dashboard", code=302)
            else:
                return "Wrong Password or email. <a href='/login'>Login</a>"
        else:
            return "Not Registered, <a href='/register'>Register here</a>."

@app.route('/register',methods=['POST','GET'])
def register():
    if (request.method =='GET'):
       return render_template("register.html")
    else:
        if(mydb.login.find({'email':request.form['email']}).count()>0):
            return "<a href='/register'>Register</a> | <a href='/login'>Login</a> | <a href='/'>Home</a><br><br>Email already exist in database."
        else:
            mydb.login.insert({
                'name': request.form['name'],
                'email': request.form['email'].lower(),
                'passw': request.form['pass']
            })
            return "Registered successfully. Goto <a href='/login'>login</a> Page to login."
@app.route('/logout',methods=['GET'])
def logout():
    session.clear()
    return redirect("/login", code=302)

@app.route('/create',methods=['POST','GET'])
def create():
    if request.method=='GET':
        #Get all post of my own.
        query=mydb.posts.find({'email':session['email']})
        post_list=list(query)
        #print(session['email'])
        if(len(post_list)>0):

            sorted_list=[]
            for each in post_list:
                elem= int(each.get('order'))
                sorted_list.append((elem,each))
            sorted_list.sort(reverse=True)
            return render_template("create.html" ,post_list=sorted_list)
        else:
            return render_template("create.html", messagey="Make your first post !!")

    else:

        content= request.form['content']
        title=request.form['title']
        ti = time.ctime()

        order=time.time()
        elem=int(time.time())
        if mydb.posts.find({'title':title}).count()>0:
            return render_template("create.html",message="Already a post with same title . See all public Posts ")
        else:
            mydb.posts.insert({
                'title':title,
                'content':content,
                'createdon': ti,
                'order':elem,
                'author':session['author'],
                'email': session['email']
            })
            return render_template("create.html",messagex= "Created successfully." )

@app.route('/edit',methods=['POST','GET'])
def edit():
    if request.method=='GET':
        #show all this user's post with edit button on each. form each.
        query = mydb.posts.find({'email': session['email']})
        post_list = list(query)
        print(session['email'])
        if (len(post_list) > 0):

            sorted_list = []
            for each in post_list:
                elem = int(each.get('order'))
                sorted_list.append((elem, each))
            sorted_list.sort(reverse=True)
            #print(sorted_list)
            return render_template("edit.html", post_list=sorted_list)
        else:
            return render_template("edit.html", message="No Post to edit yet!")

    else:

        title=request.form['title']
        content=request.form['content']
        ti = request.form['createdon_old']
        old_id= request.form['post_id']
        order=time.time()
        elem=request.form['order_old']
        new_post_data={
            'title': title,
            'content': content,
            'createdon': ti,
            'order': elem,
            'author': session['author'],
            'email': session['email'],
            'edited':1
        }

        query= mydb.posts.update_one({"_id": ObjectId(old_id)},{"$set": new_post_data})
        #print(list(query))
        return render_template("edit.html",messagex="Successfully edited.")

@app.route('/all',methods=['POST','GET'])
def all():
    query=mydb.posts.find({},{ "_id": 0 })
    post_list = list(query)

    if (len(post_list) > 0):

        sorted_list = []
        for each in post_list:
            elem = int(each.get('order'))
            sorted_list.append((elem, each))
        sorted_list.sort(reverse=True)
        # print(sorted_list)
        return render_template("all.html", post_list=sorted_list)
    else:
        return render_template("all.html", message="No Posts yet!")

@app.route('/',methods=['POST','GET'])
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.secret_key = 'anything'
    app.run(debug=True)

