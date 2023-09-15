from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'supervisor'


#if call / then will redirect to that pg

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('Home.html')

@app.route("/svLogin", methods=['POST'])
def svLogin():
    svEmail = request.form['svEmail']
    svPassword = request.form['svPassword']

    fetch_supervisor_sql = "SELECT * FROM supervisor WHERE svEmail = %s"
    fetch_student_sql = "SELECT * FROM student WHERE uniSupervisor = %s"
    
    cursor = db_conn.cursor()

    try:
        if not svEmail or not svPassword:
            return render_template('StaffLogin.html', empty_field=True)

        cursor.execute(fetch_supervisor_sql, (svEmail,))
        supervisor_records = cursor.fetchall()

        if not supervisor_records:
            return render_template('StaffLogin.html', login_failed=True)

        if supervisor_records and supervisor_records[0]['svPassword'] != svPassword:  # Use column name 'svPassword'
            return render_template('StaffLogin.html', login_failed=True)

        cursor.execute(fetch_student_sql, (svName,))  # Change 'svEmail' to 'svName'
        student_records = cursor.fetchall()

        # Pass both supervisor and student records to the StaffPage template
        return render_template('StaffPage.html', supervisor=supervisor_records[0], students=student_records)

    except Exception as e:
        # Log the error or return a user-friendly error message
        app.logger.error(str(e))
        return "An error occurred."

    finally:
        cursor.close()


@app.route("/toSvLogin")
def toSvLogin():
    return render_template('StaffLogin.html') 

@app.route("/toCompanyLogin")
def toCompanyLogin():
    return render_template('CompanyLogin.html') 

@app.route("/toCompanyRegister")
def toCompanyRegister():
    return render_template('CompanyRegister.html') 

@app.route("/companyLogin", methods=['GET', 'POST'])
def companyLogin():
    companyEmail = request.form['companyEmail']
    companyPassword = request.form['companyPassword']
    status = "Approved"

    fetch_company_sql = "SELECT * FROM company WHERE companyEmail = %s"
    cursor = db_conn.cursor()

    if companyEmail == "" and companyPassword == "":
        return render_template('CompanyLogin.html', empty_field=True)

    try:
        cursor.execute(fetch_company_sql, (companyEmail,))
        records = cursor.fetchall()

        if not records:
            return render_template('CompanyLogin.html', login_failed=True)
        if records[0][7] != companyPassword:
            return render_template('CompanyLogin.html', login_failed=True)
        elif records[0][8] != status:
            return render_template('CompanyLogin.html', inactive_acc=True)
        else:
            return render_template('CompanyPage.html', company=records)

    except Exception as e:
        return str(e)

    finally:
        cursor.close()



@app.route("/Login", methods=['GET', 'POST'])
def companyLogin():
    companyEmail = request.form['companyEmail']
    companyPassword = request.form['companyPassword']
    status = "Approved"

    fetch_company_sql = "SELECT * FROM company WHERE companyEmail = %s"
    cursor = db_conn.cursor()

    if companyEmail == "" and companyPassword == "":
        return render_template('CompanyLogin.html', empty_field=True)

    try:
        cursor.execute(fetch_company_sql, (companyEmail,))
        records = cursor.fetchall()

        if not records:
            return render_template('CompanyLogin.html', login_failed=True)
        if records[0][7] != companyPassword:
            return render_template('CompanyLogin.html', login_failed=True)
        elif records[0][8] != status:
            return render_template('CompanyLogin.html', inactive_acc=True)
        else:
            return render_template('CompanyPage.html', company=records)

    except Exception as e:
        return str(e)

    finally:
        cursor.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
