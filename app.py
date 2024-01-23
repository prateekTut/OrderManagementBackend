from flask import Flask
import flask
import json

import datetime
from datetime import date, timedelta, timezone
from flask import jsonify, request, send_file
from sqlalchemy import exists, select
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required, get_jwt, \
    unset_jwt_cookies

from flask_cors import CORS

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import aliased

app = Flask(__name__)
CORS(app)
# cors = CORS(app, resources={r"/gettutoruser/*": {"origins": "http://localhost:3000"}})

app.config["JWT_SECRET_KEY"] = "sdadwkhkln2313nklne3123"  # Change this!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)

jwt = JWTManager(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:admin''@localhost:3306/ordermodule'

# app.app_context().push()
db = SQLAlchemy(app)

class Users(db.Model):
    users_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstname = db.Column(db.String(50))
    lastname = db.Column(db.String(50))
    password = db.Column(db.String(50))
    email = db.Column(db.String(50))
    contact = db.Column(db.String(25))
    joiningDate = db.Column(db.Date)
    type = db.Column(db.String(50))


class Client(db.Model):
    client_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_name = db.Column(db.String(100))
    client_contact = db.Column(db.String(25))
    client_email = db.Column(db.String(50))
    client_status = db.Column(db.String(100))
    university = db.Column(db.String(100))
    business_name = db.Column(db.String(100))
    student_login = db.Column(db.String(100))
    student_password = db.Column(db.String(100))


class Employees(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('users.users_id'))
    firstname = db.Column(db.String(50))
    lastname = db.Column(db.String(50))
    email = db.Column(db.String(50))
    contact = db.Column(db.String(25))
    address = db.Column(db.String(255))
    dob = db.Column(db.Date)
    status = db.Column(db.String(50))
    roles = db.Column(db.String(50))
    designation = db.Column(db.String(100))

    users = db.relationship('Users', backref=db.backref('employees_foreign_key'))

class Orders(db.Model):
    __tablename__ = 'orders'
    orders_id = db.Column(db.String(50), primary_key=True)
    task_subject = db.Column(db.String(100))
    expert_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'))
    client_id = db.Column(db.Integer, db.ForeignKey('client.client_id'))
    status = db.Column(db.String(100))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    order_budget = db.Column(db.Float)
    currency = db.Column(db.String(15))
    qc_expert_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'))
    otm_id = db.Column(db.Integer, db.ForeignKey('users.users_id'))
    description = db.Column(db.String(100))
    word_count = db.Column(db.Integer)
    expert_price = db.Column(db.Integer)
    task_date = db.Column(db.Date)

    client = db.relationship('Client', backref=db.backref('orders'))
    expert = db.relationship('Employees', foreign_keys=[expert_id], backref=db.backref('orders_as_expert'))
    qc_expert = db.relationship('Employees', foreign_keys=[qc_expert_id], backref=db.backref('orders_as_qc_expert'))
    otm = db.relationship('Users', backref=db.backref('orders'))

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('users.users_id'))
    date = db.Column(db.Date)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    status = db.Column(db.String(100))
    working_hours = db.Column(db.Integer)
    users = db.relationship('Users', backref=db.backref('attendance_foreign_key'))


class Invoice(db.Model):
    __tablename__ = 'invoice'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    invoice_number = db.Column(db.String(50))
    item = db.Column(db.String(45))
    client_id = db.Column(db.Integer, db.ForeignKey('client.client_id'))
    amount = db.Column(db.Float)
    total = db.Column(db.Float)
    total_amount = db.Column(db.Float)
    discount = db.Column(db.Integer)
    invoice_date = db.Column(db.Date)
    due_date = db.Column(db.Date)
    orders_id = db.Column(db.Integer, db.ForeignKey('orders.orders_id', ondelete='SET NULL'), nullable=True)
    tax_rate = db.Column(db.Integer)
    rate = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    tax_amount = db.Column(db.Float)
    item_total = db.Column(db.Float)
    tax_type = db.Column(db.String(45))
    currency = db.Column(db.String(45))
    discountType = db.Column(db.String(45))
    sub_tax = db.Column(db.String(20))
    dis_percent = db.Column(db.Float)
    vat = db.Column(db.Float)
    cgst = db.Column(db.Float)
    sgst = db.Column(db.Float)
    igst = db.Column(db.Float)
    paid_amount = db.Column(db.Float)
    payment_date = db.Column(db.Date)
    payment_method = db.Column(db.String(50))
    attachments = db.Column(db.String(150))
    client = db.relationship('Client', backref=db.backref('invoice'))
    order = db.relationship('Orders', backref=db.backref('orders_for_invoice'))


# -------------------LOG in Module Route start -------------------__

@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.datetime.now(timezone.utc)
        target_timestamp = datetime.datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            data = response.get_json()
            if type(data) is dict:
                data["access_token"] = access_token
                response.data = json.dumps(data)
                print(response)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original respone
        return response


@app.route('/login', methods=['POST'])
def test():
    email = flask.request.form['email']
    password = flask.request.form['password']

    user = Users.query.filter_by(email=email, password=password).first()

    if user:
        access_token = create_access_token(identity=email)
        return jsonify(access_token=access_token, type=user.type, userId=user.users_id)
    else:
        return jsonify({'message': 'Invalid email or password', 'code': '400'}), 400


@app.route('/getAllInvoices', methods=['POST'])
@jwt_required()
def getAllInvoices():
    try:
        invoice_dict = {}

        # Iterate over students and their invoices
        
        get_invoices = Invoice.query.all()
        for invoice in get_invoices:
            # Store the invoice in the dictionary using the invoice number as the key
            invoice_number = invoice.invoice_number
            client_id = invoice.client_id
            client_name = Client.query.filter_by(client_id=client_id).first()
            if invoice_number not in invoice_dict:
                invoice_dict[invoice_number] = {
                    'id': invoice.id,
                    'client_id': client_id,
                    'name': client_name.client_name,
                    'invoice_number': invoice.invoice_number,
                    'amount': invoice.total,
                    'invoice_date': invoice.invoice_date.strftime('%Y-%m-%d'),
                    'due_date': invoice.due_date.strftime('%Y-%m-%d'),
                    'currency': invoice.currency,
                    'payment_date': invoice.payment_date,
                    'paid_amount': invoice.paid_amount,
                }

        # Convert the dictionary values to a list to get the unique invoices
        all_invoices = list(invoice_dict.values())
        return jsonify(all_invoices)
    except Exception as e:
        print(e)
        return {"error": str(e)}

@app.route("/")
def home():
    return "Hello, Flask!"