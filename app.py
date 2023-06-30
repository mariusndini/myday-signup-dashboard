import streamlit as st
import snowflake.connector
import email_validator


# CONNECT TO SNOWFLAKE  
conn = snowflake.connector.connect( user= st.secrets["user"],
                                    password= st.secrets["password"],
                                    account= st.secrets["account"],
                                    role = st.secrets["role"],
                                    warehouse = st.secrets["warehouse"],
                                    session_parameters={
                                        'QUERY_TAG': 'Streamlit',
                                    })

# function to run queries on Snowflake
def run_query(query): 
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

def check_email(e):
    try:
        validation = email_validator.validate_email(email = e)
        if(validation.domain == 'snowflake.com'):
            return True, validation.local_part
        else:
            st.markdown("**Only Valid Snowflake Accounts are Allowed.**")
            return False, ''
        
    except email_validator.EmailNotValidError as e:
        #   st.write(str(e))
          return False, ''


    

st.title('MyDay Sign-up Dashboard')

st.markdown('To access the MyDay Native Application, kindly provide your email address below.')
st.markdown('Once you\'ve submitted your email, make sure to download your credentials to login.')
st.markdown('[Access & Architecture Slides](https://docs.google.com/presentation/d/1pHYRUULcfW-DPZJ5OzfaXL9Bh-MN4V_RfMHxdmkfQac/edit?usp=sharing)')
st.text("")

st.markdown('**After** credentials are downloaded log into https://app.snowflake.com/sfsenorthamerica/snowhealth. \n\n Navtigate to the **Apps** section of Snowflake')

email_input = st.text_input(
        "Enter your Snowflake E-Mail👇",
        placeholder = "Only Valid Snowflake E-Mails Allowed Please"
    )


if st.button('GO!'):
    valid_email, local_val = check_email(email_input)
    if valid_email==True:
        # run_query( f' CALL admin.public.create_new_user(\'{email_input.upper()}\'); ' )
        num_roles_qry = run_query( f"show roles like 'NATIVE_APP_ROLE_%';" )
        num_roles = len(num_roles_qry)+1

        run_query( f"create role NATIVE_APP_ROLE_{num_roles};" )
        run_query( f"grant role HEALTH_READER to role NATIVE_APP_ROLE_{num_roles};" )

        fnameLname = local_val.replace('.','')
        run_query( f""" Create or replace user {fnameLname} 
                        EMAIL = '{email_input}'
                        PASSWORD = 'Red123!!!'
                        default_role = NATIVE_APP_ROLE_{num_roles} 
                        must_change_password = true 
                        DEFAULT_WAREHOUSE = SNOWHEALTH;""" )
        
        run_query( f"grant role NATIVE_APP_ROLE_{num_roles} to user {fnameLname};" )
        run_query( f"GRANT APPLICATION ROLE MYDAYNATIVEAPP.APP_PUBLIC TO ROLE NATIVE_APP_ROLE_{num_roles};" )

        output = f'''username:{fnameLname}
password:Red123!!!
log-in URL:https://app.snowflake.com/sfsenorthamerica/snowhealth'''

        st.markdown('**Download your log-in credentials below!** \n\n Do not exit this app without doing so. \n\n You will be asked to changed your Password after logging in.')
        st.download_button('Download Credentials', output, 'MyDayCreds.txt')
        st.markdown('log into: https://app.snowflake.com/sfsenorthamerica/snowhealth \n\n after downloading your credentials')


    else:
        st.markdown(f'''**INVALID EMAIL** \n\n Only Snowflake.com emails: {email_input} is not a Snowflake email address''')



