from flaskext.mysql import MySQL


#init Mysql
mysql = MySQL()

app = Flask(__name__, static_url_path='/public')

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'thaothui'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

        #create cursor
        #cur = mysql.connect().cursor()
        cur = mysql.get_db().cursor()

        #execute query

        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s);", (name, email, username, password))
        #commit to db
        mysql.get_db().commit()
        #close db
        cur.close()