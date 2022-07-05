from flask import Flask, render_template, request, redirect, url_for, flash, abort, session
import os
from flask_qrcode import QRcode
import random
import requests
import pymysql.cursors
from flask_mail import Mail, Message

app = Flask(__name__)

Con = pymysql.Connect(host="127.0.0.1", port=3307, user="root", passwd="",db='qrify')

cur = Con.cursor()

qrcode = QRcode(app)

url = "https://www.fast2sms.com/dev/bulkV2"

app.secret_key = "abdhghsb"

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=465
app.config['MAIL_USERNAME']='qrify.in@gmail.com'
app.config['MAIL_PASSWORD']='Qrify2002@'
app.config['MAIL_USE_TLS']=False
app.config['MAIL_USE_SSL']=True

mail = Mail(app)

#     return User.query.get(int(user_id))

@app.route("/", methods=["GET","POST"])
def home():
    if request.method == "POST":
        email1 = request.form["email"]
        cur.execute("INSERT INTO emails (email) VALUES (%s)", (email1,))
        Con.commit()
        return redirect(url_for('home'))
    return render_template("index.html")

name = " "

user_data = {
    "firstname":"",
    "lastname":"",
    "email":"",
    "phone":"",
    "vehicle_no":"",
    "address":""
}

car_details = {
    "first_name":"",
    "contact_no":"",
    "vehicle_no":""
}



qr_string =" "
@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        email1 = request.form["email"]
        sql = "SELECT * FROM user WHERE email='"+email1+"'"
        if cur.execute(sql):
            flash("You have already signed up with that email! LogIn instead")
            return redirect(url_for('login'))
        
        global user_data, qr_string
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        vehicle = request.form['vehicle']
        address = request.form['address']

        user_data['firstname'] = first_name
        user_data['lastname'] = last_name
        user_data['email'] = email
        user_data['phone'] = phone
        user_data['vehicle_no'] = vehicle
        user_data['address'] = address

      

        msg = Message('Hello', sender = 'qrify.in@gmail.com', recipients = [request.form['email']])
        msg.html = render_template('emailt.html')
        mail.send(msg)

        sql = "INSERT INTO user (first_name, last_name, email,password,contact,vehicle,address) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        val = (first_name,last_name,email,password,phone,vehicle,address)
        cur.execute(sql,val)
        Con.commit()
        qr_string = f"First Name: {first_name}\nLast Name: {last_name}\nEmail: {email}\nPhone: {phone}\nVehicle Number: {vehicle}"
        session['loggedin'] = True
        return redirect(url_for('dash2'))
    return render_template("signup.html", data=user_data)


@app.route("/login", methods=["GET","POST"]) 
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        sql1 = "SELECT * FROM user WHERE email='"+email+"'"
        cur.execute(sql1)
        myresult = cur.fetchone()

        if not myresult:
            flash("That email does not exist, please try again.") 
            return redirect(url_for('login'))
        elif not (myresult[4]==password):
            print(myresult[4])
            flash("Password is incorrect!")
            return redirect(url_for('login'))
        else:
            global user_data, qr_string
            user_data['firstname'] = myresult[1]
            user_data['lastname'] = myresult[2]
            user_data['email'] = myresult[3]
            user_data['phone'] = myresult[5]
            user_data['vehicle_no'] = myresult[6]
            user_data['address'] = myresult[7]
            qr_string = f"First Name: {myresult[1]} \nLast Name: {myresult[2]} \nEmail: {myresult[3]} \nPhone: {myresult[5]}\nVehicle Number: {myresult[6]}"
            session['loggedin'] = True
            session['name'] = myresult[1]
            return redirect(url_for('dash2'))
        
    return render_template("login.html")



@app.route("/dashboard-qr", methods=["GET", "POST"])
def dash2():
    if request.method == "POST":
        email = request.form["email"]
        cur.execute("INSERT INTO emails (email) VALUES (%s)", (email,))
        Con.commit()
    if 'loggedin' in session:
        return render_template("dashboard.html" , data=user_data,qr_data=qr_string)
    else:
        return redirect(url_for('login'))

@app.route("/profile", methods=["GET","POST"])
def profile():
    if request.method == "POST":
        email = request.form["email"]
        cur.execute("INSERT INTO emails (email) VALUES (%s)", (email,))
        Con.commit()
    if 'loggedin' in session:
        return render_template("profile.html", data=user_data)
    else:
        return redirect(url_for('login'))


@app.route("/logout")
def logout():
    # logout_user()
    session.clear()
    return redirect(url_for('login'))

@app.route("/forgot-password", methods=["GET","POST"])
def forget():
    if request.method == "POST":
        email = request.form['email']
        new_pwd = request.form['newpwd']
        
        # user = User.query.filter_by(email=email).first()
        sql = "SELECT * FROM user WHERE email='"+email+"'"
        cur.execute(sql)
        myresult = cur.fetchone()
        if not myresult:
            flash("That email does not exist!")
            return render_template("updatepwd.html")
        else:
            msg = Message('Hello', sender = 'qrify.in@gmail.com', recipients = [request.form['email']])
            msg.html = render_template('forgett.html')
            mail.send(msg)
            
            sql = "UPDATE user SET password='"+new_pwd+"' WHERE email='"+email+"'"
            cur.execute(sql)
            Con.commit()
            # user.password = secure_pwd
            # db.session.commit()
            # me = "qrify.in@gmail.com"
            # password = "QRify@2803"
            
            return redirect(url_for('login'))
    return render_template("updatepwd.html")

@app.route("/help", methods=["GET","POST"])
def help():
    if request.method == "POST":
        email = request.form["email"]
        message = request.form["message"]

        # newEntry = Questions(email=email, question=message)
        # db.session.add(newEntry)
        # db.session.commit()
        sql = "INSERT INTO question (email, question) VALUES (%s, %s)"
        val = (email, message)
        cur.execute(sql, val)
        Con.commit()

       
        return redirect(url_for('help'))
    return render_template("help.html")

@app.route("/contact", methods=["GET","POST"])
def contact():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        sql = "INSERT INTO contact (name,email,message) VALUES(%s, %s, %s)"
        val = (name,email,message)
        cur.execute(sql, val)
        Con.commit()
        # newEntry = ContactForm(name=name, email=email, message=message)
        # db.session.add(newEntry)
        # db.session.commit()
        msg = Message('Hello', sender = 'qrify.in@gmail.com', recipients = [request.form['email']])
        msg.html = render_template('contactt.html')
        mail.send(msg)

        return redirect(url_for('contact'))
    return render_template("contactus.html")

@app.route("/order-qr-code", methods=["GET","POST"])
def order():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        address = request.form["address"]
        vehicle = request.form["vehicle"]

        cur = Con.cursor()
        sql = "SELECT * FROM stickerorder WHERE vehicle='"+vehicle+"'"
       
        cur.execute(sql)
        myresult=cur.fetchone()
        
        if myresult:
            flash("That vehicle number is registered on our site!") 
            return redirect(url_for('order')) 
        else:
            
            sql = "INSERT INTO stickerorder (name, email, phone, vehicle, address) VALUES (%s, %s, %s, %s, %s)"
            val = (name, email, phone, vehicle, address)
            cur.execute(sql, val)
            Con.commit()
            msg = Message('Hello', sender = 'qrify.in@gmail.com', recipients = [request.form['email']])
            msg.html = render_template('ordert.html')
            mail.send(msg)
            
            return redirect(url_for('thanks'))
        
        
        return redirect(url_for('thanks'))
    return render_template("order.html")

@app.route("/t2", methods=["POST"])
def t2():
    if request.method=="POST":
        name=user_data["firstname"]
        email=user_data["email"]
        address=user_data["address"]
        phone=user_data["phone"]
        vehicle=user_data["vehicle_no"]

        msg = Message('Thanks for ordering', sender = 'qrify.in@gmail.com', recipients = [email])
        msg.html = render_template('ordert.html')
        mail.send(msg)
        
        sql = "INSERT INTO stickerorder (name, email, phone, vehicle, address) VALUES (%s, %s, %s, %s, %s)"
        val = (name, email, phone, vehicle, address)
        cur.execute(sql, val)
        Con.commit()
        
        return redirect(url_for('thanks'))

@app.route("/thanks-for-ordering", methods=["GET","POST"])
def thanks():
    if request.method == "POST":
        email2 = request.form["email"]
        cur.execute("INSERT INTO emails (email) VALUES (%s)", (email2,))
        Con.commit()
        return redirect(url_for('thanks'))
    return render_template("thanks.html")

random_otp = 0
mobile_no = ''
car_no = ''
@app.route("/mobile-number", methods=["GET","POST"])
def mobile():
    if request.method == "POST":
        global mobile_no
        mobile_no = request.form["mobile"]
        global random_otp
        random_otp = random.randint(1000, 9999)
        
        queryatring = {"authorization" : "p6vyZ2tz5FIIAG0yG8nNPk1WGIj11H6W9JInS63xpiMWOCqgH7HcIfjpD9s3",
        "route" : "v3","sender_id" : "FSTSMS","message":f"Your OTP is {random_otp}","language" : "english","numbers" :{mobile_no}}

        headers = {
            'cache-control' : 'no-cache'
        }
        response = requests.request("GET",url,headers=headers, params=queryatring)
        session['loggedin'] = True
        print(response.text)
        return redirect(url_for('check_otp'))
        
        
    return render_template("mobile.html")

@app.route("/check-your-otp-number", methods=["GET","POST"])
def check_otp():
    if request.method == "POST":
        otp_no = request.form["otp"]
        if int(otp_no) == int(random_otp):
            return redirect(url_for('car_no'))
        else:
            flash("OTP is incorrect")
            return redirect(url_for('check_otp'))
        return redirect(url_for("check_otp"))
    return render_template('check_otp.html')


@app.route("/car-number", methods=["GET","POST"])
def car_no():
    if request.method == "POST":
        global car_no
        car_no = request.form["car_no"]
        sql = "SELECT * FROM user WHERE vehicle='"+car_no+"'"
        cur.execute(sql)
        myresult = cur.fetchone()

        sql2 = "SELECT * FROM stickerorder WHERE vehicle='"+car_no+"'"
        cur.execute(sql2)
        myresult2 = cur.fetchone()

        if not (myresult or sql2):
            flash(f"No match found")
            return redirect(url_for('car_no'))
        elif myresult:
            car_details["first_name"] = myresult[1] 
            car_details["contact_no"] = myresult[5]
            car_details["vehicle_no"] = myresult[6]
            sql3 = "INSERT INTO scan (mobile, vehicle) VALUES (%s, %s)"
            val = (mobile_no, car_no)
            cur.execute(sql3, val)
            Con.commit()
            return redirect(url_for('details'))
        elif myresult2:
            car_details["first_name"] = myresult2[1]
            car_details["contact_no"] = myresult2[3]
            car_details["vehicle_no"] = myresult2[4]
            sql3 = "INSERT INTO scan (mobile, vehicle) VALUES (%s, %s)"
            val = (mobile_no, car_no)
            cur.execute(sql3, val)
            Con.commit()
            return redirect(url_for('details'))
    return render_template("car_no.html")


@app.route("/details")
def details():
    if request.method == "pOST":
        email2 = request.form["email"]
        cur.execute("INSERT INTO emails (email) VALUES (%s)", (email2,))
        Con.commit()
        return redirect(url_for('details'))
    if 'loggedin' in session:
        return render_template("details.html", details=car_details)
    else:
        return redirect(url_for('mobile'))

@app.route("/feedback", methods=["GET","POST"])
def feedback():
    if request.method=="POST":
        name = request.form["name"]
        email = request.form["email"]
        msg = request.form["message"]
        sql = "INSERT INTO feedback(name, email, message) VALUES (%s, %s, %s)"
        val = (name, email, msg)
        cur.execute(sql,val)
        Con.commit()
        return render_template("feedback.html")
    return render_template("feedback.html")

@app.route("/newslatter", methods=["POST"])
def newslatter():
    if request.method == "POST":
        email = request.form["email"]
        cur.execute("INSERT INTO emails (email) VALUES (%s)", (email,))
        Con.commit()
        return redirect(url_for('home'))


@app.route("/email")
def home2():
    msg = Message('Join our team', sender = 'qrify.in@gmail.com', recipients = ["vishveshpatel2002@gmail.com"])
    msg.html = render_template('index.html')
    mail.send(msg)
    return "send"
    
if __name__ == "__main__":
    app.run(debug=True)

