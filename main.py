import mysql.connector
from flask import Flask, request, render_template, redirect
import time
from datetime import datetime
datetime.today().strftime('%Y-%m-%d')


try :
    conn = mysql.connector.connect(
            host = "localhost",
            username = "bankadmin",
            password = "bankadmin",
            database = "bankingsystem",
    )

    curr = conn.cursor()

    print('Connection to DB has been established')
except:
    print('Connection to the DB has failed')


app = Flask('__name__')


# Login Page

@app.route("/")
def login():
    return render_template('login.html', valid='')

# Invalid Login

@app.route("/", methods = ['POST','GET'])
def loginverify():


    if request.method == 'POST':
        accno = request.form["accno"]
        password = request.form["password"]
        try : 
            curr.execute('select passwordCheck(%s,%s)', [int(accno), password])
            validity = curr.fetchone()
            if validity[0] == 1:
                return redirect('/' + str(accno))
            else:
                return render_template('login.html', valid = 'Please re-check the credentials')
        except :
            return render_template('login.html', valid = 'Invalid Input')


# User Details

@app.route('/<int:accno>')
def userdetails(accno):
    curr.execute('select balance, min_balance from balance_details where accno = %s', [int(accno)])
    bldetails = curr.fetchone()
    curr.execute('select * from transactions where sender_accno = %s', [int(accno)])
    transactions = curr.fetchall()
    curr.execute('select * from investments where accno = %s', [int(accno)])
    investments = curr.fetchall()
    curr.execute('select * from loans where accno = %s', [int(accno)])
    loans = curr.fetchall()
    curr.execute('select name from accounts where accno = %s', [int(accno)])
    name = curr.fetchone()
    print(bldetails)

    return render_template('userdetails.html', bldetails = bldetails, transactions=transactions, investments=investments, loans=loans,accno=accno, name = name[0])

# Transaction Menu

@app.route('/<int:accno>transact')
def transactPage(accno):
    return render_template('transact.html', accno=accno)


# Transaction Routing

@app.route('/<int:accno>transact', methods=['POST'])
def transact(accno):
    if request.method == 'POST':
        raccno = request.form["raccno"]
        amount = request.form["amount"]
        date = datetime.today().strftime('%Y-%m-%d')

        try:
            curr.execute('insert into transactions values(null,%s,%s,%s,%s,null)', [int(accno), int(raccno),int(amount),date])
            curr.execute('commit')
        except mysql.connector.Error as err:
            print(err)

        return redirect('/' + str(accno))


# Opening Investment

@app.route('/<int:accno>openinvestment')
def investmentpage(accno):
    return render_template('investment.html', accno = accno, status = '')

@app.route('/<int:accno>openinvestment', methods=['POST'])
def investmentopen(accno):
    if request.method == 'POST':
        amount = request.form["amount"]
        mdate = request.form["mdate"]
        cdate = datetime.today().strftime('%Y-%m-%d')

        try :
            curr.execute('select openInvestment(%s,%s,%s,%s)', [accno,int(amount),mdate,cdate])
            if curr.fetchone()[0] == 0:
                print('You do not have sufficient funds to do so')
                return render_template('investment.html', accno = accno, status = 'You do not have sufficient funds in your account to make the investment')
            else:
                curr.execute('commit')
                return redirect('/' + str(accno))
        except mysql.connector.Error as err:
            print(err)
    
    return 'hello'


# Closing Investment
@app.route('/<int:accno>+<int:investmentid>investment', methods = ['POST'])
def closeinvestment(accno, investmentid):
    if request.method == 'POST':
        curr.execute('delete from investments where investment_id = %s', [investmentid])
        curr.execute('commit')
        return redirect('/' + str(accno))

# Closing Loan
@app.route('/<int:accno>+<int:loanid>loan', methods=['POST'])
def repayLoan(accno, loanid):
    if request.method == 'POST':
        try:
            curr.execute('select repayLoan(%s,%s)', [accno, loanid])
            if curr.fetchone()[0] == 0:
                print('You do not have sufficient funds to do so')
            else:
                curr.execute('commit')
                return redirect('/' + str(accno))
        except mysql.connector.Error as err:
            print(err)

    return 'hello'

#New Loan

@app.route('/<int:accno>loan')
def loan(accno):
    return render_template('loan.html', accno=accno)

#Submit Loan
@app.route('/<int:accno>loan', methods=["POST"])
def loansanction(accno):
    amount = request.form["lamount"]
    rdate = request.form["rdate"]
    cdate = datetime.today().strftime('%Y-%m-%d')

    try:
        curr.execute('insert into loans values(null,%s,%s,null,%s,%s,null,null)', [accno, int(amount),cdate,rdate])
        curr.execute('commit')
        # redirect('/' + str(accno))

    except mysql.connector.Error as err:
        print(err)

    return redirect('/' + str(accno))


if __name__ == '__main__':
    app.run(debug=True)
    curr.close()
    conn.close()