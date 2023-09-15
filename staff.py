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

        if supervisor_records and supervisor_records[0]['svPassword'] != svPassword:
            return render_template('StaffLogin.html', login_failed=True)

        cursor.execute(fetch_student_sql, (svName,))
        student_records = cursor.fetchall()

        # Generate URLs for student files from S3
        student_records_url = {}
        object_keys = ["com_acceptance_form", "parent_ack_form", "letter_of_indemnity", "hired_evidence"]
        expiration = 3600

        for student in student_records:
            student_id = student['studId']
            urls = {}
            for key in object_keys:
                object_key = f"stud-id-{student_id}/{student[key]}"
                urls[key] = generate_presigned_url(object_key, expiration)
            student_records_url[student_id] = urls

        return render_template('StaffPage.html', supervisor=supervisor_records[0], students=student_records, urls=student_records_url)

    except Exception as e:
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
