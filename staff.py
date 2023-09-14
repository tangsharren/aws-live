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
table = 'staff'


#if call / then will redirect to that pg

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('StaffLogin.html')


@app.route("/staffLogin")
def companyLogin():
    return render_template('StaffLogin.html') 

@app.route("/staffPage", methods=['POST'])
def GetEmp():
    return render_template('StaffPage.html')
    
@app.route("/staffLogin", methods=['GET', 'POST'])
def staffLogin():
    svEmail = request.form['svEmail']
    svPassword = request.form['svPassword']
    status = "Pending Approval"
    
    fetch_staff_sql = "SELECT * FROM staff WHERE svEmail = %s"
    fetch_company_sql = "SELECT * FROM company WHERE status = %s"
    cursor = db_conn.cursor()

    if svEmail == "" and svPassword == "":
        return render_template('StaffLogin.html', empty_field=True)

    try:
        cursor.execute(fetch_sv_sql, (svEmail))
        records = cursor.fetchall()

        cursor.execute(fetch_student_sql, (status))
        companyRecords = cursor.fetchall()

        if records and records[0][2] != adminPassword:
            return render_template('AdminLogin.html', login_failed=True)
        else:
            return render_template('AdminPage.html', admin=records, company=companyRecords)

    except Exception as e:
        return str(e)

    finally:
        cursor.close()


@app.route("/fetchdata", methods=['POST'])
def ReadEmp():
    emp_id = request.form['emp_id']

    fetch_sql = "SELECT * FROM employee WHERE emp_id = %s"
    cursor = db_conn.cursor()
    object_key = "emp-id-" + str(emp_id) + "_image_file" + ".jpg"
    expiration = 3600

    if emp_id == "":
        return "Please enter an employee id"


    try:
        cursor.execute(fetch_sql, (emp_id))
        records = cursor.fetchall()
        try:
            response = s3.generate_presigned_url('get_object',
                                                Params={'Bucket': custombucket,
                                                        'Key': object_key},
                                                ExpiresIn=expiration)
        except ClientError as e:
            logging.error(e)



    finally:
        cursor.close()

    return render_template('GetEmpOutput.html', staff=records, url=response)
    


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
