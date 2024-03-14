import os
import sqlite3
import pandas as pd
import base64
import csv
import bs4
from flask import render_template, Flask, request, redirect, url_for, send_from_directory, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user


def create_app(test_config=None):
    
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )
    users = {"*****": {"username": "******", "password": "*******"}}

    login_manager = LoginManager()
    login_manager.init_app(app)

    class User(UserMixin):
        def __init__(self, username):
            self.id = username

    @login_manager.user_loader
    def load_user(user_id):
        return User(user_id)

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    def execute_query(dbPath, query, params=()):
        conn = sqlite3.connect(dbPath)
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            result = cursor.fetchall()
            return result
        except Exception as e:
            conn.rollback()
            print("削除中にエラーが発生しました:", str(e))
        finally:
            conn.close()
        

    def get_svg_data():
        table_name = "prefSummary"
        columns = ["svg_1", "svg_2", "svg_3"]
        columns_str = ", ".join(columns)
        select_query = f"SELECT {columns_str} FROM {table_name}"
        selected_data = execute_query("flaskr/articles.db", select_query)
        svgArray = [j for i in selected_data for j in i if j != ""]
        return svgArray

    def get_pref_data():
        temp = []
        table_name = "prefSummary"
        columns = ["タイムスタンプ",
                   "都道府県名",
                    "県庁HP",
                    "都道府県名（カナ）",
                    "都道府県コード",
                    "総人口（千人）",
                    "男性総人口（千人）",
                    "女性総人口（千人）",
                    "人口性比",
                    "日本人人口（千人）",
                    "日本人男性人口（千人）",
                    "日本人女性人口（千人）",
                    "日本人人口比"]
        columns_str = ", ".join(columns)
        query = f"SELECT {columns_str} FROM {table_name};"
        data = execute_query("flaskr/articles.db", query=query)
        for row in data:
            temp.append(row)
        
        prefDataDict = {}
        for i in temp:
            prefDataDict[str(i[3])] = i
        
        temp.insert(0,columns)
        temp = pd.DataFrame(temp).T.values.tolist()
        
        return temp

    def load_articles_from_csv(csv_file):
        articles = []
        with open(csv_file, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                tags = row["タグ"].split("/")  # 複数のタグを分割
                for tag in tags:
                    articles.append(
                        {
                            "filename": row["ファイル名"],
                            "title": row["タイトル"],
                            "category": tag.strip(),  # タグの前後の空白を除去
                        }
                    )
        return articles

    def save_to_tsv(db_type, rows):
        folder_path = 'flaskr/uploaded_files/'
        os.makedirs(folder_path, exist_ok=True)
        fileName = db_type + ".tsv"
        file_path = os.path.join(folder_path, fileName)
        with open(file_path, 'w', newline='', encoding='utf-8') as tsvfile:
            writer = csv.writer(tsvfile, delimiter='\t') 
            writer.writerows(rows)
        df = pd.read_csv(file_path, sep='\t')
        conn = sqlite3.connect("flaskr/articles.db")
        df.to_sql('prefSummary', conn, if_exists='replace', index=False) 
        conn.commit()
        conn.close()
    
    #HTMLファイルからarticle_contentへ変換
    def createArticleContent(filePath):
        #bs4で定義された関数を使ってsample.htmlを読み取る
        soup = bs4.BeautifulSoup(open(filePath, encoding = 'utf-8'),'html.parser')

        #sample.htmlをコンソールに出力

        html_tag = "<html>"

        # <meta>タグを取得
        meta_tag = soup.find('meta', {'http-equiv': 'Content-Type'})


        link_tag = "<link rel='stylesheet' href='{{ url_for('static', filename='styleForNotion.css') }}'>"

        # <atricle>タグを取得
        article_tag = soup.find("article")

        # <span>タグの最後の要素を取得
        span_tag = soup.find_all("span")[-1]

        html_tag_end = "</html>"

        all = [
            str(article_tag),
            str(span_tag)
        ]
        return "\n".join(all)

    def createThumbnail(img):
        with open(img, "rb") as f:
            image_data = f.read()
        return image_data

    #article.dbにデータを追加
    def inputDBFunc(id, thumbnail_path, article_name, article_tags, article_content):
        # データベースに接続
        conn = sqlite3.connect('flaskr/articles.db')
        cursor = conn.cursor()
        try:
            # テーブルが存在しない場合は作成
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY,
                    thumbnail BLOB,
                    article_name TEXT,
                    article_tags TEXT,
                    article_content TEXT
                )
            ''')

            # 指定されたIDが存在するかチェック
            cursor.execute("SELECT id FROM articles WHERE id=?", (id,))
            existing_id = cursor.fetchone()
            

            # 画像ファイルをBLOBに変換して追加
            if thumbnail_path:
                thumbnail_blob = createThumbnail(thumbnail_path)
                if thumbnail_blob is None:
                    print("画像をBLOB形式に変換できませんでした。")
                else:
                    if existing_id:
                        cursor.execute('''
                            UPDATE articles
                            SET thumbnail=?
                            WHERE id=?
                        ''', (thumbnail_blob, id))
                    else:
                        cursor.execute('''
                            INSERT INTO articles (id, thumbnail)
                            VALUES (?, ?)
                        ''', (id, thumbnail_blob))

            cursor.execute("SELECT id FROM articles WHERE id=?", (id,))
            existing_id = cursor.fetchone()
            
            # 記事名を追加
            if article_name:
                if existing_id:
                    cursor.execute('''
                        UPDATE articles
                        SET article_name=?
                        WHERE id=?
                    ''', (article_name, id))
                else:
                    cursor.execute('''
                        INSERT INTO articles (id, article_name)
                        VALUES (?, ?)
                    ''', (id, article_name))

            cursor.execute("SELECT id FROM articles WHERE id=?", (id,))
            existing_id = cursor.fetchone()
            # 記事タグを追加
            if article_tags:
                if existing_id:
                    cursor.execute('''
                        UPDATE articles
                        SET article_tags=?
                        WHERE id=?
                    ''', (article_tags, id))
                else:
                    cursor.execute('''
                        INSERT INTO articles (id, article_tags)
                        VALUES (?, ?)
                    ''', (id, article_tags))

            cursor.execute("SELECT id FROM articles WHERE id=?", (id,))
            existing_id = cursor.fetchone()
            # 記事内容を追加
            if article_content:
                article_content_text = createArticleContent(article_content)
                if existing_id:
                    cursor.execute('''
                        UPDATE articles
                        SET article_content=?
                        WHERE id=?
                    ''', (article_content_text, id))
                else:
                    cursor.execute('''
                        INSERT INTO articles (id, article_content)
                        VALUES (?, ?)
                    ''', (id, article_content_text))

            # 変更をコミット
            conn.commit()

        except Exception as e:
            # エラーが発生した場合はロールバック
            conn.rollback()
            print("データの挿入または更新中にエラーが発生しました:", str(e))

        finally:
            # データベースとの接続をクローズ
            conn.close()


    @app.route("/")
    def map():
        articles = execute_query("flaskr/articles.db", "SELECT * FROM articles")
        articleIndex = [i[0] for i in articles]
        title = [i[2] for i in articles]
        thumbnail = [f"data:image/jpeg;base64,{base64.b64encode(i[1]).decode('utf-8')}" if i[1] else None for i in articles]
        tags = execute_query("flaskr/articles.db", "SELECT article_tags FROM articles")
        return render_template(
            "index.html",
            svgData=get_svg_data(),
            prefTable=get_pref_data(),
            articleIndex=articleIndex,
            title=title,
            thumbnail=thumbnail,
            tags=tags
        )

    @app.route("/events", methods=["GET", "POST"])
    def index():
        selected_category = request.form.get("category", "")
        categories = execute_query("flaskr/articles.db", "SELECT article_tags FROM articles")
        categories = [list(i)[0].split("/") for i in categories]
        categories = set([item for sublist in categories for item in sublist])
        result = execute_query("flaskr/articles.db", "SELECT * FROM articles")
        tags = execute_query("flaskr/articles.db", "SELECT article_tags FROM articles")
        articleIndex = [i[0] for i in result]
        title = [i[2] for i in result]
        thumbnail = [f"data:image/jpeg;base64,{base64.b64encode(i[1]).decode('utf-8')}" if i[1] else None for i in result]
        request_type = request.method
        return render_template(
            "events.html",
            articleIndex=articleIndex,
            title=title,
            tags=tags,
            thumbnail=thumbnail,
            categories=categories,
            selected_category=selected_category,
            request_type=request_type,
        )

    @app.route("/events/<string:article>")
    def notion(article):
        articleIndex = request.args.get('index')
        query = f"SELECT * FROM articles WHERE id = {int(articleIndex)}"
        dataFromDB = execute_query("flaskr/articles.db", query=query)[0]
        thumbnail = f"data:image/jpeg;base64,{base64.b64encode(dataFromDB[1]).decode('utf-8')}" if dataFromDB[1] else None
        return render_template("notion.html", articleTitle=dataFromDB[2],articleTags=dataFromDB[3],htmlContent=dataFromDB[4], articleNum=articleIndex, thumbnail=thumbnail)
            

    @app.route("/contact", methods=["GET", "POST"])
    def contact():
        if request.method == "POST":
            content_mail = request.form["mail"]
            content_text = request.form["content"]
            with open("contact.txt", "a", encoding='utf-8') as f:
                f.write(content_mail)
                f.write(",")
                f.write(content_text)
                f.write("\n")
            return render_template("request.html")
        return render_template("contact.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            if username in users and users[username]["password"] == password:
                user = User(username)
                login_user(user)
                return redirect(url_for("consoleMenu"))
            else:
                return "Invalid username or password"
        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("login"))
    
    @app.route("/consoleMenu")
    @login_required
    def consoleMenu():
        return render_template("consoleMenu.html", request_type=request.method)

    #以下の2文でアップロードしたファイルの保存先を指定
    UPLOAD_FOLDER = 'flaskr/uploaded_files/'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    @app.route("/inputDB", methods=['GET', 'POST'])
    @login_required
    def inputDB():
        db_type = request.args.get('type')
        ids = execute_query("flaskr/articles.db","SELECT id FROM articles")
        ids.insert(0, "id")

        if db_type == "prefSummary":
            dataFromDB = execute_query("flaskr/articles.db", "SELECT * FROM prefSummary")
            headers = execute_query("flaskr/articles.db","PRAGMA table_info('prefSummary')")
            headers = [header[1] for header in headers]
            dataFromDB.insert(0,headers)

        elif db_type == "articles":
            dataFromDB = execute_query("flaskr/articles.db","SELECT article_name, article_tags FROM articles")
            dataFromDB.insert(0,("記事タイトル", "タグ"))
            
            
         #   return url_for("input", db_type=db_type, row=len(dataFromDB)+1,col=len(dataFromDB[0])+1)

        return render_template("input.html", ids=ids, db_type=db_type, row =len(dataFromDB),col=len(dataFromDB[0]), data=dataFromDB)
    
    #以下では、save_to_csv()で引数にとったデータからcsvを生成し、uploaded_filesフォルダに保存
    #→save()でPOSTされたデータを取得している
    @app.route('/save', methods=['POST'])
    @login_required
    def save():
        db_type = request.args.get('type')
        data = request.form.to_dict(flat=False)
        num_rows = int(request.form['num_rows'])  # 送信された行数を取得
        num_cols = int(request.form['num_cols'])  # 送信された列数を取得
        tableHeader  = request.form.getlist('tableHeader')
        rows = [[data[f'row{i}-col{j}'][0].replace('"', '$') for j in range(1, num_cols+1)] for i in range(1, num_rows)]

        rows.insert(0,tableHeader)

        save_to_tsv(db_type, rows)
        return redirect(url_for('inputDB', type=db_type))
    
    
    @app.route('/upload', methods=['POST'])
    def upload_file():
        if 'file' not in request.files:
            return redirect(url_for("test"))
        file = request.files['file']
        if file.filename == '':
            return redirect(url_for("test"))
        if file:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for("test"))

    @app.route('/articleDetail')
    def articleDetail():
        types = request.args.get('type')
        query = f"SELECT id FROM articles;"
        dataFromDB = execute_query("flaskr/articles.db", query=query)
        dataFromDB = [int(i[0]) for i in dataFromDB]
        maxId = execute_query("flaskr/articles.db", query=query)
        maxId = [int(i[0]) for i in maxId]
        maxId = max(maxId)
        if types == "new":
            query = f"SELECT id FROM articles;"
            
            
            return render_template("articleDetail.html",articleTitle="",articleTags="", maxId=maxId+1)
        else:    
            articleNum = types.split(",")[0]
            fileName = "articles.tsv"
            tsv = []
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], fileName)
            with open(file_path, 'r', newline='', encoding='utf-8') as tsvfile:
                for i in tsvfile:
                    tsv.append(i.strip("\n").split("\t"))

            query = f"SELECT * FROM articles WHERE id = {int(articleNum)}"
            dataFromDB = execute_query("flaskr/articles.db", query=query)[0]
            thumbnail = f"data:image/jpeg;base64,{base64.b64encode(dataFromDB[1]).decode('utf-8')}" if dataFromDB[1] else None
            return render_template("articleDetail.html", articleTitle=dataFromDB[2],articleTags=dataFromDB[3],htmlContent=dataFromDB[4], articleNum=articleNum, thumbnail=thumbnail, maxId=maxId)
    
    @app.route('/saveArticleData', methods=['POST'])
    def save_article():
        if request.method == 'POST':
            id = request.form['id']  # フォームからidを取得
            thumbnail_path = request.files['inputThumbnail'].filename  # アップロードされたサムネイルのパス
            if thumbnail_path != "":
                request.files['inputThumbnail'].save(app.config['UPLOAD_FOLDER'] + "articles/" + thumbnail_path)
                thumbnail_path = app.config['UPLOAD_FOLDER'] + "articles/" + thumbnail_path
            article_name = request.form['articleName']  # 記事名を取得
            article_tags = request.form['tags']  # タグを取得
            article_content = request.files['articleHtml'].filename  # アップロードされた記事HTMLのパス
            if article_content != "":    
                request.files['articleHtml'].save(app.config['UPLOAD_FOLDER'] + "articles/" + article_content)
                article_content = app.config['UPLOAD_FOLDER'] + "articles/" + article_content
            # サムネイルパス、記事内容を指定してinputDB()を呼び出す
            inputDBFunc(id=id, thumbnail_path=thumbnail_path, article_name=article_name, article_tags=article_tags, article_content=article_content)
            
        return redirect("inputDB?type=articles")
    
    @app.route("/deleteRow")
    def deleteRow():
        articleId = request.args.get("type")
        query = f"DELETE FROM articles WHERE id={articleId}"
        execute_query("flaskr/articles.db", query=query)
        return redirect("inputDB?type=articles")
    
    @app.route('/test')
    def test():
        return render_template("test.html")

    return app
