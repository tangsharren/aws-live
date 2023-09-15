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
        file_names = ["com_acceptance_form", "parent_ack_form", "letter_of_indemnity", "hired_evidence"]
        expiration = 3600

        for student in student_records:
            student_id = student['studId']
            urls = {}
            object_prefix = "stud-id-" + str(student_id)
            for file_name in file_names:
                object_key = f"{object_prefix}/{file_name}.pdf"
                response = s3.generate_presigned_url(
                    'get_object',
                    Params={
                        'Bucket': custombucket,
                        'Key': object_key
                    },
                    ExpiresIn=expiration
                )
                urls[file_name] = response  # Store each URL with its respective file name
            student_records_url[student_id] = urls  # Store the URLs for the student

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
