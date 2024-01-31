from pickle import BYTEARRAY8
from flask import Flask
import flask
import json

import datetime
from datetime import date, timedelta, timezone
from flask import jsonify, request, send_file,render_template,url_for,redirect
from sqlalchemy import exists, select
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required, get_jwt, \
    unset_jwt_cookies

from flask_cors import CORS, cross_origin

from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from sqlalchemy.orm import aliased
import os
from dateutil import parser

app = Flask(__name__)
CORS(app)
CORS(app, origins=['http://localhost:3000'])
CORS(app, support_credentials=True)
# cors = CORS(app, resources={r"/gettutoruser/*": {"origins": "http://localhost:3000"}})

app.config["JWT_SECRET_KEY"] = "sdadwkhkln2313nklne3123"  # Change this!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)

jwt = JWTManager(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:nizam@localhost:3306/newschema'

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

class Expense(db.Model):
    __tablename__ = 'expense'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    expense_date = db.Column(db.Date)
    expense_number = db.Column(db.String(50))
    invoice_number = db.Column(db.String(50),unique=True)
    currency = db.Column(db.String(45))
    amount = db.Column(db.Float)
    notes = db.Column(db.String(255))
    vendor = db.Column(db.String(45))
    paid_amount = db.Column(db.Float)
    due_date = db.Column(db.Date)
    attachment = db.Column(db.String(255))
    payment_date = db.Column(db.Date)
    payment_method = db.Column(db.String(45))
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




@app.route('/submitexpense', methods=['POST'])
@jwt_required()
def submit_expense():
    # expense_date = flask.request.form['expense_date']
    # expense_number = flask.request.form['expense_number']
    # invoice_number = flask.request.form['invoice_number']
    # amount = flask.request.form['amount']
    # notes = flask.request.form['notes']
    # vendor = flask.request.form['vendor']
    # currency = flask.request.form['currency']
    # attachment = flask.request.form['attachment']
    data = flask.request.get_json()

    expense_date = data.get('expense_date')
    expense_number = data.get('expense_number')
    invoice_number = data.get('invoice_number')
    amount = data.get('amount')
    notes = data.get('notes')
    vendor = data.get('vendor')
    currency = data.get('currency')
    attachment = data.get('attachment')
    print(attachment)
    expense = Expense(
            expense_date=expense_date,
            expense_number=expense_number,
            invoice_number=invoice_number,
            currency=currency,
            amount=amount,
            notes=notes,
            vendor=vendor,
            attachment=attachment
        )
    db.session.add(expense)
    db.session.commit()

    return jsonify({'message': 'Expense submitted successfully'})


@app.route('/getAllExpenses', methods=['GET'])
@cross_origin(supports_credentials=True)
@jwt_required()
def get_all_expenses():
    expenses = Expense.query.all()

    # Convert the list of expenses to a list of dictionaries
    expenses_list = [
        {
            'id': expense.id,
            'expense_date': expense.expense_date.strftime('%Y-%m-%d'),  # Convert Date to String
            'expense_number': expense.expense_number,
            'invoice_number': expense.invoice_number,
            'currency': expense.currency,
            'amount': expense.amount,
            'notes': expense.notes,
            'vendor': expense.vendor,
            'currency': expense.currency,
            'due_date':expense.due_date,
            'paid_amount':expense.paid_amount,
            'attachment':expense.attachment,
            'payment_method':expense.payment_method,
            'payment_date':expense.payment_date
        }
        for expense in expenses
    ]

    return jsonify({'expenses': expenses_list})

@app.route('/editexpense/<int:expense_id>', methods=['PUT'])
@jwt_required()
def edit_expense(expense_id):
    data = request.get_json()

    expense = Expense.query.get(expense_id)
    if not expense:
        return jsonify({'error': 'Expense not found'}), 404

    expense.expense_date = data.get('expense_date', expense.expense_date)
    expense.expense_number = data.get('expense_number', expense.expense_number)
    expense.invoice_number = data.get('invoice_number', expense.invoice_number)
    expense.amount = data.get('amount', expense.amount)
    expense.notes = data.get('notes', expense.notes)
    expense.vendor = data.get('vendor', expense.vendor)
    expense.currency = data.get('currency', expense.currency)
    expense.attachment = data.get('attachment', expense.attachment)

    db.session.commit()

    return jsonify({'message': 'Expense updated successfully'})

@app.route('/deleteexpense/<int:expense_id>', methods=['DELETE'])
@jwt_required()
def delete_expense(expense_id):
    expense = Expense.query.get(expense_id)
    if not expense:
        return jsonify({'error': 'Expense not found'}), 404

    db.session.delete(expense)
    db.session.commit()

    return jsonify({'message': 'Expense deleted successfully'})


@app.route('/update_payment/<int:expense_id>', methods=['PUT'])
@jwt_required()
def update_payment(expense_id):
    data = request.form  # Use request.form to get form data

    expense = Expense.query.get(expense_id)
    if not expense:
        return jsonify({'error': 'Expense not found'}), 404

    # Update payment-related fields
    expense.paid_amount = data.get('paid_amount', expense.paid_amount)
    
    # If 'payment_date' is provided in the form data, convert it to a datetime object
    payment_date_str = data.get('payment_date')
    if payment_date_str:
        try:
            payment_date_obj = parser.parse(payment_date_str)
            expense.payment_date = payment_date_obj.strftime('%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400

    expense.payment_method = data.get('payment_method', expense.payment_method)

    db.session.commit()

    return jsonify({'message': 'Payment information updated successfully'})



if __name__ == '__main__':
    app.run(debug=True)



@app.route("/")
def home():
    return "Hello, Flask!"