import streamlit as st
# import xlsxwriter
import pandas as pd
from io import BytesIO

output = BytesIO()


def credits(sheet_name):
    db = xcl.parse(sheet_name)
    db = db[db['Ledger Date']!= 'Total']
    db['SECTION'] = sheet_name
    db['Account Number'] = db['Account Number'].astype(str)
    db['MARKET VALUE/AMOUNT/BALANCE'] = db['Amount'].apply(lambda x: "${:,.2f}".format(x))
    # pd.concat([db,rx])
    db = db.rename(columns={
        'Amount':'Credit',
        'Ledger Date':'DATE',
        'Description':'DESCRIPTION',
        'Account Number':'ACCOUNT#',
        'Account Name': 'ACCOUNT NAME'
    })
    rx = pd.DataFrame(columns=['ULID/SERIAL NUMBER','OUR REFERENCE', 'YOUR REFERENCE', 'Debit', 'SHARES'])
    db = pd.concat([db,rx]).fillna('')
    fin_cols = ['SECTION', 'DATE', 'DESCRIPTION', 'ULID/SERIAL NUMBER', 'OUR REFERENCE', 'YOUR REFERENCE', 'Credit', 'Debit',
             'MARKET VALUE/AMOUNT/BALANCE', 'SHARES', 'ACCOUNT#', 'ACCOUNT NAME']
    return(db[fin_cols])

def debits(sheet_name):
    db = xcl.parse(sheet_name)
    db = db[db['Ledger Date']!= 'Total']
    db['SECTION'] = sheet_name
    db['Account Number'] = db['Account Number'].astype(str)
    db['MARKET VALUE/AMOUNT/BALANCE'] = db['Amount'].apply(lambda x: "${:,.2f}".format(x))
    # pd.concat([db,rx])
    db = db.rename(columns={
        'Amount':'Debit',
        'Ledger Date':'DATE',
        'Description':'DESCRIPTION',
        'Account Number':'ACCOUNT#',
        'Account Name': 'ACCOUNT NAME'
    })
    rx = pd.DataFrame(columns=['ULID/SERIAL NUMBER','OUR REFERENCE', 'YOUR REFERENCE', 'Credit', 'SHARES'])
    db = pd.concat([db,rx]).fillna('')
    fin_cols = ['SECTION', 'DATE', 'DESCRIPTION', 'ULID/SERIAL NUMBER', 'OUR REFERENCE', 'YOUR REFERENCE', 'Credit', 'Debit',
             'MARKET VALUE/AMOUNT/BALANCE', 'SHARES', 'ACCOUNT#', 'ACCOUNT NAME']
    return(db[fin_cols])

def check_paid(sheet_name):
    db = xcl.parse(sheet_name)
    db = db[~db['Check'].str.contains('Total')]
    db['SECTION'] = sheet_name
    db['Account Number'] = db['Account Number'].astype(str)
    db['MARKET VALUE/AMOUNT/BALANCE'] = db['Amount'].apply(lambda x: "${:,.2f}".format(x))
    # pd.concat([db,rx])
    db = db.rename(columns={
        'Amount':'Debit',
        'Date Paid':'DATE',
        'Check':'DESCRIPTION',
        'Account Number':'ACCOUNT#',
        'Account Name': 'ACCOUNT NAME'
    })
    rx = pd.DataFrame(columns=['ULID/SERIAL NUMBER','OUR REFERENCE', 'YOUR REFERENCE', 'Credit', 'SHARES'])
    db = pd.concat([db,rx]).fillna('')
    fin_cols = ['SECTION', 'DATE', 'DESCRIPTION', 'ULID/SERIAL NUMBER', 'OUR REFERENCE', 'YOUR REFERENCE', 'Credit', 'Debit',
             'MARKET VALUE/AMOUNT/BALANCE', 'SHARES', 'ACCOUNT#', 'ACCOUNT NAME']
    return(db[fin_cols])

def to_csv(df):
    return(df.to_csv(index=False).encode('utf-8'))

# def to_excel(df):
#     workbook = xlsxwriter.Workbook(output, {'in_memory': True})
#     worksheet = workbook.add_worksheet()

#     worksheet.write(df)
#     workbook.close()

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

if check_password():

    uploaded_file = st.sidebar.file_uploader("Choose a jpm xlsx file", accept_multiple_files=False)

    if uploaded_file is not None:
        xcl = pd.ExcelFile(uploaded_file)
        sheet_names = xcl.sheet_names

        arc = pd.DataFrame()
        for i in sheet_names:
            if i.lower() == 'deposits and credits':
                db = credits(i)
                arc = pd.concat([arc, db])
            elif i.lower() == 'withdrawals and debits':
                db = debits(i)
                arc = pd.concat([arc, db])
            elif i.lower() == 'checks paid':
                db = check_paid(i)
                arc = pd.concat([arc, db])

        credit_total = sum(arc[arc['Credit']!='']['Credit'])
        credit_total = "${:,.2f}".format(credit_total)

        debit_total = sum(arc[arc['Debit']!='']['Debit'])
        debit_total = "${:,.2f}".format(debit_total)

        col1, col2 = st.columns(2)
        col1.metric("Credit", credit_total)
        col2.metric("Debit", debit_total)

        st.download_button(
            label="Download data as CSV",
            data=to_csv(arc),
            file_name='jpm_output.csv',
            mime='csv',
        )

        st.dataframe(arc)

    else:
        st.write('Please upload JPM file')
