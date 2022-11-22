from flask import Flask,render_template,request, jsonify,flash,redirect,session, url_for
from sqlalchemy.sql.expression import func
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, migrate
from flask_security import UserMixin
from werkzeug.security import check_password_hash,generate_password_hash
from datetime import date, datetime

from email_validator import validate_email, EmailNotValidError

from random import randint

app = Flask(__name__)
app.secret_key = 'asdfgghjkhklghjk'
app.debug = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

class profile(db.Model):
    first_name = db.Column(db.String(200),unique=False, nullable=False)
    email = db.Column(db.String(200),primary_key=True)
    password = db.Column(db.String(200), unique=False, nullable=False)
    mobile_no = db.Column(db.String(10), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class bus(db.Model):
    bus_number = db.Column(db.Integer,primary_key=True,nullable=False)
    bus_name = db.Column(db.String(150))
    start_point = db.Column(db.String(150), unique=False, nullable=False)
    end_point = db.Column(db.String(150), nullable=False)
    fare_of1_seat= db.Column(db.Integer, nullable=False)
    dateTime= db.Column(db.DateTime, nullable=False)
    routes=db.Column(db.String(1500), nullable=False)
    

class wallet(db.Model):
    Username=db.Column(db.String(200),primary_key=True, nullable=False)
    Amount=db.Column(db.Integer, nullable=False)

class bookingHistory(db.Model):
    username=db.Column(db.String(200),nullable=False)
    bus_number=db.Column(db.Integer,nullable=False)
    bookigId=db.Column(db.Integer,primary_key=True)
    source=db.Column(db.String(200),nullable=False)
    destination=db.Column(db.String(200),nullable=False)
    dateTime= db.Column(db.DateTime, nullable=False)

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)


def camelize(str):
    ans1 = str.title()
    ans2 = ans1.translate({ord(' '): None})
    return ans2


@app.route('/test',methods=['GET','POST'])
def test():
    pass

@app.route('/view',methods=['GET','POST'])
def view():
    if request.method=='POST':
        Uid=request.form.get('Username')
        bus_number=request.form.get('busN')
        booking_Id=request.form.get('bookingId')
        bus_name=bus.query.filter_by(bus_number=bus_number).first().bus_name
        bus_dateTime=bus.query.filter_by(bus_number=bus_number).first().dateTime
        adding=bus.query.filter_by(bus_number=bus_number).first().fare_of1_seat  #fare
        p=profile.query.filter_by(email=Uid).first()    
        Source=request.form.get('start_point')
        Destination=request.form.get('end_point')
        return render_template('ticket.html',email=Uid,bus_number=bus_number,fare=adding,profile=p,Source=Source,Destination=Destination,bus_name=bus_name,booking_Id=booking_Id,dateTime=bus_dateTime)

@app.route('/', methods = ['GET', 'POST'])
def login():
    message=""
    if request.method=='POST':
        email=request.form.get('email'),
        password=request.form.get('password')
        p=profile.query.filter_by(email=email[0]).first()
        pw=wallet.query.filter_by(Username=email[0]).first()
        print(p.password)
        print(p.check_password(password))
        if p!=None and p.check_password(password):
            return  render_template('userProfile.html',wallet=pw,profile=p)
        message="Enter right credential"
    return render_template('login.html',message=message)

@app.route('/home',methods=['GET','POST'])
def home():
    if request.method=='POST':
        email=request.form.get('email')
        print(email)
        p=profile.query.filter_by(email=email).first()
        pw=wallet.query.filter_by(Username=email).first()
        return  render_template('userProfile.html',wallet=pw,profile=p)



    

@app.route('/adminhome', methods = ['GET', 'POST'])
def adminhome():      
    if request.method=='POST':
        print(request.form.get('Datetime'))
        year = int(request.form.get('year'))
        month = int(request.form.get('month'))
        day = int(request.form.get('day'))
        d = date(year, month, day)
        hours = int(request.form.get('hours'))
        minutes = int(request.form.get('minutes'))
        dt = datetime(year, month, day, hours, minutes)
        b=bus(
            bus_number=request.form['Bnumber'],
            bus_name=request.form['Bname'],
            start_point ="",
            end_point="",
            fare_of1_seat = request.form['fare'],
            dateTime=dt,
            routes= request.form['routes']
            )
        
        db.session.add(b)
        db.session.commit()
    return render_template('adminhome.html')

@app.route('/addbalance', methods = ['GET', 'POST'])
def addbalance():
    return render_template('addmoney.html',accountholder=request.form.get('email'),currentamount=request.form.get('currentAmount'))

@app.route('/makePayment', methods = ['GET', 'POST'])
def makePayment():
    if request.method=='POST':
        return render_template('makePayment.html',accountholder=request.form.get('accountholder'),currentamount=request.form.get('currentAmount'),fare=request.form.get('Fare'),BusId=request.form.get('BusId'),Source=request.form.get('Source'),Destination=request.form.get('Destination'))

#money deduction helper
@app.route('/deductbalancehelper', methods = ['GET', 'POST'])
def deductbalancehelper():
    message=""
    if request.method=='POST':
        accountHolder=request.form.get('accountholder')
        password=request.form.get('password')
        
        currentamount=request.form.get('currentAmount')
        fare=request.form.get('fare')
        pw=wallet.query.filter_by(Username=accountHolder).first()
        busTime=bus.query.filter_by(bus_number=request.form.get('BusId')).first().dateTime
        p=profile.query.filter_by(email=accountHolder).first()
        print(p.password)
        print(p.check_password(password))
        if p!=None and p.check_password(password):
            if int(currentamount)-int(fare)<0:
                message="you do not have sufficient balance"
            else:
                db.session.delete(pw)
                db.session.commit()
                booking = bookingHistory(
                username=accountHolder,
                bus_number=request.form.get('BusId'),
                bookigId=random_with_N_digits(5),
                source=request.form.get('Source'),
                destination=request.form.get('Destination'),
                dateTime=busTime
                )
                db.session.add(booking)
                db.session.commit()
                walletp=wallet(
                Username=accountHolder,
                Amount=int(currentamount)-int(fare))
                db.session.add(walletp)
                db.session.commit()
                pwUpdated=wallet.query.filter_by(Username=accountHolder).first()
                bookings=bookingHistory.query.filter_by( username=accountHolder)      
                return  render_template('userProfile.html',wallet=pwUpdated,profile=p,bookings=bookings,message="You have Booked your Bus")
        else:
            message="you have entered wrong amount or password"
        p=profile.query.filter_by(email=accountHolder).first()
        pw=wallet.query.filter_by(Username=accountHolder).first()     
        return  render_template('userProfile.html',wallet=pw,profile=p,message=message)

    
#Wallet money adding
@app.route('/addbalancehelper', methods = ['GET', 'POST'])
def addbalancehelper():
    message=""
    if request.method=='POST':
        accountHolder=request.form.get('accountholder')
        password=request.form.get('password')
        Cnumber=request.form.get('formCardNumber')
        year=int(request.form.get('year'))
        month=int(request.form.get('month'))
        print(month)
        dt = datetime(year, month,31,23,59)
        current_Datetime=datetime.now()
        
        if Cnumber.isdigit() and len(Cnumber)==16 and dt>=current_Datetime:
            currentamount=request.form.get('currentAmount')
            adding=request.form.get('adding')
            pw=wallet.query.filter_by(Username=accountHolder).first()

            p=profile.query.filter_by(email=accountHolder).first()
            print(p.password)
            print(p.check_password(password))
            if p.check_password(password) and int(adding)>=0 :
                db.session.delete(pw)
                db.session.commit()
                walletp=wallet(
                Username=accountHolder,
                Amount=int(currentamount)+int(adding))
                db.session.add(walletp)
                db.session.commit()
                pwUpdated=wallet.query.filter_by(Username=accountHolder).first()
                bookings=bookingHistory.query.filter_by( username=accountHolder)    
                message="Added Money"
                return  render_template('userProfile.html',wallet=pwUpdated,profile=p,bookings=bookings,message=message)
        message="you have entered wrong amount or password or Your Card haS Expired, We cannot add Money"
    p=profile.query.filter_by(email=accountHolder).first()
    pw=wallet.query.filter_by(Username=accountHolder).first()     
    return  render_template('userProfile.html',wallet=pw,profile=p,message=message)


@app.route('/<string:id>/search',methods = ['GET','POST'])
def search(id):
    if request.method=='POST':
        source=request.form['Source']
        destination=request.form['Destination']
        source=camelize(source)
        destination=camelize(destination)
        print(destination)
        print(source)
        p=bus.query.all()
        current_Datetime=datetime.now()
        Bus_available=[]
        idl=id.split('12kfNinABSLDSFKGL,mjnmkmkssfu5678FDFKMGJfkednjfgjndfjngfDsYbH')
        id=idl[0]+idl[1]+"@gmail.com"
        print(id)
        m="Sorry for inconvience,Currently no bus available on this route.We will update the buses for this route very soon."
        for i in p:
            routes_list =i.routes.split(',')
            if (source in routes_list) and (destination in routes_list) and i.dateTime>current_Datetime:
                sourceIndex=routes_list.index(source)
                destinationIndex=routes_list.index(destination)
                if (sourceIndex<destinationIndex):
                    busDict={
                        "bus_number":i.bus_number,
                        "bus_name":i.bus_name,
                        "start_point":source,
                        "end_point":destination,
                        "fare_of1_seat":((i.fare_of1_seat)+(334)*(destinationIndex-sourceIndex)),
                        "dateTime":i.dateTime,
                        "busRoutes":i.routes
                    }
                    Bus_available.append(busDict)
                    m="Happy Journey"
        print(Bus_available)
        return render_template('table.html',buses=Bus_available,id=id,message=m)
    return render_template('search.html')

@app.route('/bookingHistory',methods = ['GET','POST'])
def bookinghistory():
    if request.method=='POST':
        Uid=request.form.get('Id')
        bookings=bookingHistory.query.filter_by( username=Uid)
        
        current_Datetime=datetime.now()
        return render_template('seebookingstable.html',bookingHistory=bookings,id=Uid,currentDT=current_Datetime)

@app.route('/cancelit',methods = ['GET','POST'])
def cancel():
    if request.method=='POST':
        Uid=request.form.get('Username')
        bookp=bookingHistory.query.filter_by(bookigId=request.form.get('bookingId')).first()
        #wallet money back
        
        currentamount=wallet.query.filter_by(Username=Uid).first().Amount
        bus_number=request.form.get('busN')
        adding=bus.query.filter_by(bus_number=bus_number).first().fare_of1_seat  #fare
        
        pw=wallet.query.filter_by(Username=Uid).first()
        db.session.delete(pw)
        db.session.commit()
        walletp=wallet(
            Username=Uid,
            Amount=int(currentamount)+int(adding))
        
        db.session.add(walletp)
        db.session.commit()

        db.session.delete(bookp)
        db.session.commit()

        p=profile.query.filter_by(email=Uid).first()
        pw=wallet.query.filter_by(Username=Uid).first()     
       
        message="Your Bus Has been cancelled and Your money have refunded"
        
        return render_template('userProfile.html',wallet=pw,profile=p,message=message)
    


@app.route('/bookit',methods = ['GET','POST'])
def bookit():
    pw=wallet.query.filter_by(Username=request.form.get('Id')).first()
    return  render_template('confirmBooking.html',profileemail=request.form.get('Id'),Bid=request.form.get('busN'), s=request.form.get('start_point'),d=request.form.get('end_point'),walletAmount=pw.Amount,fare=request.form.get('fare'))


@app.route('/editDetailhelper', methods = ['GET', 'POST'])
def editdetailrender():
    if request.method=='POST':
        p= profile.query.filter_by(email=request.form.get('email')).first()
        return render_template('editDetail.html',profile=p)
@app.route('/editDetail', methods = ['GET', 'POST'])
def editdetail():
    if request.method=='POST':
        print('POST')
        passwordOld=request.form.get('Current_password')
        email=str(request.form.get('email'))
        print(email)
        p= profile.query.filter_by(email=email).first()
        first_name=profile.query.filter_by(email=email).first().first_name
        mobileNo=profile.query.filter_by(email=email).first().mobile_no
        print(p.password)
        print(p.check_password( passwordOld))
        pw=wallet.query.filter_by(Username=email).first()
        passwordNew=request.form.get('password')
        print(passwordNew[0])
        if len(passwordNew)<8:
            return render_template('editDetail.html',message="please Enter the password length of Atleast length 8")
        if p.check_password(passwordOld):
            db.session.delete(p)
            db.session.commit()
            p=profile(
                first_name=str(first_name),
                email=email,
                password=generate_password_hash(passwordNew),
                mobile_no=str(mobileNo)
                )
            db.session.add(p)
            db.session.commit()
            return  render_template('userProfile.html',wallet=pw,profile=p,message='You Have Changed Your Password')
        return  render_template('userProfile.html',wallet=pw,profile=p,message='You have Entered wrong Password, we cannot change your password')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        print('POST')
        
             
        firstName=request.form.get('first_name')
        email=request.form.get('email'),
        password=request.form.get('password'),
        mobile_no=request.form.get('Mnumber')
        if len(password[0])<8:
            return render_template('register.html',message="please Enter the password length of Atleast length 8")
        if len(str(mobile_no))!=10:
            return render_template('register.html',message="please Enter correct Mobile Number")

        p=profile(
            first_name=str(firstName),
            email=str(email[0]),
            password=generate_password_hash(password[0]),
            mobile_no=str(mobile_no)
            )
        walletp=wallet(
            Username=request.form['email'],
            Amount=0
            )
        db.session.add(p)
        db.session.add(walletp)
        db.session.commit()
        return redirect('/')
    return render_template('register.html',message="")

    
if __name__ == '__main__':
	app.run()
