import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
import cv2
import os
import matplotlib.pyplot as plt
import re
import psycopg2

# -------------CONNECTING WITH POSTGRES SQL DATABASE-------------#
conn=psycopg2.connect(host = "localhost",
                      user = "postgres",
                      password = "Kavidhina@5566",
                      port = 5432,
                      database = "bizcardx")
mycursor = conn.cursor()
conn.commit()

# -----------INITIALIZING THE EasyOCR READER----------------#
reader = easyocr.Reader(['en'])    

#page congiguration
st.set_page_config(page_title= "BizCardX",
                   page_icon= 'random',
                   layout= "wide",)
st.markdown("<h1 style='text-align: center; color: blue;'>BizCardX</h1>", unsafe_allow_html=True)

#=========hide the streamlit main and footer
hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)   

#application background
def app_bg():
    st.markdown(""" <style>.stApp {{
                        background: url("https://cdn.wallpapersafari.com/7/90/BFUQb1.jpg");
                        background-size: cover}}
                     </style>""",unsafe_allow_html=True)
app_bg()



#-------------------------- TABLE CREATION------------------#
mycursor.execute('''CREATE TABLE IF NOT EXISTS card_details
                   (id SERIAL PRIMARY KEY,
                    company_name TEXT,
                    card_holder TEXT,
                    designation TEXT,
                    mobile_number VARCHAR(50),
                    email TEXT,
                    website TEXT,
                    area TEXT,
                    city TEXT,
                    state TEXT,
                    pin_code VARCHAR(10),
                    image BYTEA
                    )''')
conn.commit()

#-------------- CREATING OPTION MENU----------------------#
selected = option_menu(None, ["\U0001F3E0 Home", "\U0001F4E5 Upload & Extract", "\U0001F5D1 Modify or Delete"], 
icons=["\U0001F3E0 Home", "\U0001F4E5", "\U0001F5D1"],
default_index=0,
orientation="horizontal",
styles={"nav-link": {"font-size": "25px", "text-align": "center", "margin": "0px", "--hover-color": "orange", "transition": "color 0.3s ease, background-color 0.3s ease"},
        "icon": {"font-size": "25px"},
        "container": {"max-width": "6000px", "padding": "10px"},
        "nav-link-selected": {"background-color": "green", "color": "white"},
        "nav-link-0": {"icon": "fa-home", "background-color": "#4285F4", "color": "white", "padding-left": "15px"}})

#*********************HOME MENU***********************#
if selected == "\U0001F3E0 Home":
        col1, col2 = st.columns([3,2])
        with col2:
            st.video(r"C:\Users\arjun\Downloads\Untitled video - Made with Clipchamp.mp4")
        with col1:    
            st.subheader(":orange[About the App:] In this streamlit web app you can upload an image of a business card and extract relevant information from it using easyOCR. You can view, modify or delete the extracted data in this app. This app would also allow users to save the extracted information into a database along with the uploaded business card image. The database would be able to store multiple entries, each with its own business card image and extracted information.")
            st.subheader(":orange[Technologies Used:] EasyOCR, Python, SQL, Streamlit")
            st.subheader(":orange[Contact Details:]")
        st.subheader((":orange[>>Linkedin page:] https://www.linkedin.com/in/kaviyarasan-e-906826180/"))
        st.subheader((":orange[>>Github repository:]  https://github.com/kaviyarasanEaswaran/Phonepe-Pulse-Data-Visualization-and-Exploration-/tree/63adabe2d10d7faa4fc4f1ed7fde5899f9e95c98"))

    
    
# ------------------UPLOAD AND EXTRACT MENU------------------#
if selected == "\U0001F4E5 Upload & Extract":
    tab1,tab2 = st.tabs(["Predefined Text","Undefined text"])
    with tab1:
        #st.image(Image.open(r"D:\Data Science\BizCardX Extracting Business Card Data with OCR\Creative Modern Business Card\2.png"))
        uploaded_card = st.file_uploader("upload here",label_visibility="collapsed",type=["png","jpeg","jpg"])
     
        if uploaded_card is not None:
            def save_card(uploaded_card):
                with open(os.path.join(r"D:\Data Science\BizCardX Extracting Business Card Data with OCR\Uploaded_cards", uploaded_card.name), "wb") as f:
                    f.write(uploaded_card.getbuffer())
            save_card(uploaded_card)
            
            def image_preview(image,res): 
                for (bbox, text, prob) in res: 
                  # ....Data detection....#
                    (tl, tr, br, bl) = bbox
                    tl = (int(tl[0]), int(tl[1]))
                    tr = (int(tr[0]), int(tr[1]))
                    br = (int(br[0]), int(br[1]))
                    bl = (int(bl[0]), int(bl[1]))
                    cv2.rectangle(image, tl, br, (0, 255, 0), 2)
                    #cv2.putText(image, text, (tl[0], tl[1] - 10),
                    #cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                plt.rcParams['figure.figsize'] = (15,15)
                plt.axis('off')
                plt.imshow(image)
            
            # .....DISPLAY THE UPLOADED CARD.....#
            col1,col2 = st.columns(2,gap="large")
            with col1:
                st.markdown("#     ")
                st.markdown("#     ")
                st.markdown("### You have uploaded the card")
                st.image(uploaded_card)
            
        
                #..... DISPLAYING THE CARD WITH HIGHLIGHTS....#
                with col2:
                    st.markdown("#     ")
                    st.markdown("#     ")
                    with st.spinner("Please wait processing image..."):
                        st.set_option('deprecation.showPyplotGlobalUse', False)
                        #saved_img = os.getcwd()+ "\\" + "uploaded_cards"+ "\\"+ uploaded_card.name
                        saved_img = r"D:\Data Science\BizCardX Extracting Business Card Data with OCR\Uploaded_cards\\" + uploaded_card.name
                        image = cv2.imread(saved_img)
                        res = reader.readtext(saved_img)
                        st.markdown("### Image Processed and Data Extracted")
                        st.pyplot(image_preview(image,res))  
                    
                 
    
            saved_img = r"D:\Data Science\BizCardX Extracting Business Card Data with OCR\Uploaded_cards\\" + uploaded_card.name
    
            result = reader.readtext(saved_img,detail = 0,paragraph=False)
            
            
    
            # CONVERTING IMAGE TO BINARY TO UPLOAD TO SQL DATABASE
            def img_to_binary(file):
                # Convert image data to binary format
                with open(file, 'rb') as file:
                    binaryData = file.read()
                return binaryData
                
            data = {"company_name" : [],
                "card_holder" : [],
                "designation" : [],
                "mobile_number" :[],
                "email" : [],
                "website" : [],
                "area" : [],
                "city" : [],
                "state" : [],
                "pin_code" : [],
                "image" : img_to_binary(saved_img)
               }
            
            def get_data(res):
                 for index, i in enumerate(res):
                    # To get CARD HOLDER NAME
                    if index == 0:
                        data["card_holder"].append(i)
                    # To get DESIGNATION
                    elif index == 1:
                        data["designation"].append(i)
                    # To get WEBSITE_URL
                    if "www " in i.lower() or "www." in i.lower():
                           data["website"].append(i)
                    elif "WWW" in i:
                           data["website"].append(res[4] + "." + res[5])
                    # To get EMAIL ID
                    elif "@" in i:
                           data["email"].append(i)
                    # To get MOBILE NUMBER
                    elif "-" in i:
                         data["mobile_number"].append(i)
                    if len(data["mobile_number"]) == 2:
                         data["mobile_number"] = [" & ".join(data["mobile_number"])]
                    # To get COMPANY NAME 
                    elif index == len(res) - 1:
                        data["company_name"].append(i)
                        if len(data["company_name"][0])<5:
                            data["company_name"][0] = (f'{res[-4]} '+ res[-2])
                        elif len(data["company_name"][0]) == 8 and i == 'digitals':
                           data["company_name"][0] = (f'{res[-3]} '+res[-1])
                        elif len(data["company_name"][0])==8 :
                           data["company_name"][0] = (f'{res[-2]} '+res[-1])
                        elif len(data["company_name"][0])<=10:
                           data["company_name"][0] = (f'{res[-3]} '+res[-1])    
                    # To get AREA
                    if re.findall('^[0-9].+, [a-zA-Z]+', i):
                        data["area"].append((i.split(',')[0]))
                    elif re.findall('[0-9] [a-zA-Z]+', i):
                        data["area"].append(i+ 'St')
                    # To get CITY NAME
                    match1 = re.findall('.+St , ([a-zA-Z]+).+', i)
                    match2 = re.findall('.+St,, ([a-zA-Z]+).+', i)
                    match3 = re.findall('^[E].*', i)
                    if match1:
                        data["city"].append(match1[0])
                    elif match2:
                        data["city"].append(match2[0])
                    elif match3:
                        data["city"].append(match3[0])
                    # To get STATE
                    state_match = re.findall('[a-zA-Z]{9} +[0-9]', i)
                    if state_match:
                        data["state"].append(i[:9])
                    elif re.findall('^[0-9].+, ([a-zA-Z]+);', i):
                        data["state"].append(i.split()[-1])
                    if len(data["state"]) == 2:
                        data["state"].pop(0)
                    # To get PINCODE
                    if len(i) >= 6 and i.isdigit():
                        data["pin_code"].append(i)
                    elif re.findall('[a-zA-Z]{9} +[0-9]', i):
                        data["pin_code"].append(i[10:])
                               
            get_data(result)
          
            cola,colb = st.columns([3,1])
            with cola:
                #FUNCTION TO CREATE DATAFRAME
                def create_df(data):
                    df = pd.DataFrame(data)
                    return df
                df = create_df(data)
                st.success("### Data Extracted Successfully!!!")
                st.write(df)
            
                try:
                    if st.button("Upload to Database"):
                     name=data["card_holder"][0]
                     query =f"select * from card_details where card_holder= '{name}'"
                     mycursor.execute(query)
                     result = mycursor.fetchall()
                     z=result[0][2]
                     if name == z :
                         st.warning("Duplicate card Details, Data Already Exists in Database")
                    else:
                         pass
                except:
                    for i,row in df.iterrows():
                        #here %S means string values 
                        sql = """
                                INSERT INTO card_details (company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code,image)
                                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                                """
                        mycursor.execute(sql, tuple(row))
                        # the connection is not auto committed by default, so we must commit to save our changes
                        conn.commit()
                    st.success("#### Successfully uploaded to database!!!")

            with colb:
                with st.expander("Details",expanded=True):
                    data1 = [value[0] for  value in data.values()]
                    st.write('')
                    st.write('###### :green[Company_Name] :', data1[0])
                    st.write('###### :green[Card_Holder ] :', data1[1])
                    st.write('###### :green[Designation]  :', data1[2])
                    st.write('###### :green[Contact]      :', data['mobile_number'][0])
                    st.write('###### :green[Email id]     :', data1[4])
                    st.write('###### :green[URL]          :', data['website'][0])
                    st.write('###### :green[Address]      :', data1[6])
                    st.write('###### :green[City]         :', data1[7])
                    st.write('###### :green[State]        :', data1[8])
                    st.write('###### :green[Pincode]      :', data1[9])
                    
          
    with tab2:
        uploaded_card = st.file_uploader("Upload here",label_visibility="collapsed",type=["png","jpeg","jpg"])
        if uploaded_card is not None:
            def save_card(uploaded_card):
                with open(os.path.join(r"D:\Data Science\BizCardX Extracting Business Card Data with OCR\Uploaded_cards", uploaded_card.name), "wb") as f:
                    f.write(uploaded_card.getbuffer())
            save_card(uploaded_card)
            
            def image_preview(image,res): 
                for (bbox, text, prob) in res: 
                  # ....Data detection....#
                    (tl, tr, br, bl) = bbox
                    tl = (int(tl[0]), int(tl[1]))
                    tr = (int(tr[0]), int(tr[1]))
                    br = (int(br[0]), int(br[1]))
                    bl = (int(bl[0]), int(bl[1]))
                    cv2.rectangle(image, tl, br, (0, 255, 0), 2)
                    #cv2.putText(image, text, (tl[0], tl[1] - 10),
                    #cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                plt.rcParams['figure.figsize'] = (15,15)
                plt.axis('off')
                plt.imshow(image)
            
            # .....DISPLAY THE UPLOADED CARD.....#
            col1,col2 = st.columns(2,gap="large")
            with col1:
                st.markdown("#     ")
                st.markdown("#     ")
                st.markdown("### You have uploaded the card")
                st.image(uploaded_card)
            
        
                #..... DISPLAYING THE CARD WITH HIGHLIGHTS....#
                with col2:
                    st.markdown("#     ")
                    st.markdown("#     ")
                    with st.spinner("Please wait processing image..."):
                        st.set_option('deprecation.showPyplotGlobalUse', False)
                        #saved_img = os.getcwd()+ "\\" + "uploaded_cards"+ "\\"+ uploaded_card.name
                        saved_img = r"D:\Data Science\BizCardX Extracting Business Card Data with OCR\Uploaded_cards\\" + uploaded_card.name
                        image = cv2.imread(saved_img)
                        res = reader.readtext(saved_img)
                        st.markdown("### Image Processed and Data Extracted")
                        st.pyplot(image_preview(image,res))  
                    
                 
    
            saved_img = r"D:\Data Science\BizCardX Extracting Business Card Data with OCR\Uploaded_cards\\" + uploaded_card.name
    
            result = reader.readtext(saved_img,detail = 0,paragraph=True)
            
            with st.expander("Details",expanded=True):
                st.write('###### :green[Extracted Text]         :', result)
            


# ------------------------MODIFY MENU--------------------#
if selected == "\U0001F5D1 Modify or Delete":
    col1,col2,col3 = st.columns([3,3,2])
    st.title("Alter the data here")
    column1,column2 = st.columns(2,gap="large")
    try:
        with column1:
            decription = ['company_name','card_holder','designation','mobile_number','email','website','area','city','state','pin_code']
            dropdown = st.selectbox("Select the Description",decription)
            #st.image(Image.open(r"D:\Data Science\BizCardX Extracting Business Card Data with OCR\Uploaded_cards\modifyrightimg.jpeg"))
            mycursor.execute(f"SELECT {dropdown} FROM card_details")
            result = mycursor.fetchall()
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]
            selected_card = st.selectbox(f"### Select the :green[**{dropdown}'s**]", list(business_cards.keys()))
            st.markdown("#### Update or modify any data below")
            mycursor.execute(f"select company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code from card_details WHERE '{selected_card}'=%s",
                            (selected_card,))
            result = mycursor.fetchone()
            
            # DISPLAYING ALL THE INFORMATIONS
            st.markdown(
                """
                <style>
                input[type="text"] {
                    color: green;
                }
                input[type="text"][data-bk-color="yellow"] {
                    color: yellow;
                }
                </style>
                """,
                unsafe_allow_html=True,
            )
            # Create the text input fields and set their values
            company_name = st.text_input("Company_Name", result[0])
            card_holder = st.text_input("Card_Holder", result[1])
            designation = st.text_input("Designation", result[2])
            mobile_number = st.text_input("Mobile_Number", result[3])
            email = st.text_input("Email", result[4])
            website = st.text_input("Website", result[5])
            area = st.text_input("Area", result[6])
            city = st.text_input("City", result[7])
            state = st.text_input("State", result[8])
            pin_code = st.text_input("Pin_Code", result[9])

            if st.button("Commit changes to DB"):
                # Update the information for the selected business card in the database
                mycursor.execute(f"""UPDATE card_details SET company_name=%s,card_holder=%s,designation=%s,mobile_number=%s,email=%s,website=%s,area=%s,city=%s,state=%s,pin_code=%s
                                    WHERE {dropdown}=%s""", (company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code,selected_card))
                conn.commit()
                st.success("Information updated in database successfully.")
            if st.button("view updated data"):
                mycursor.execute("select company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code from card_details")
                updated_df = pd.DataFrame(mycursor.fetchall(),columns=["Company_Name","Card_Holder","Designation","Mobile_Number","Email","Website","Area","City","State","Pin_Code"])
                st.write(updated_df)

        with column2:
            st.title("Delete the data here")
            decription1 = ['company_name','card_holder','designation','mobile_number','email','website','area','city','state','pin_code']
            dropdown = st.selectbox("Select the description",decription)
            #st.image(Image.open(r"D:\Data Science\BizCardX Extracting Business Card Data with OCR\Uploaded_cards\modifyrightimg.jpeg"))
            mycursor.execute(f"SELECT {dropdown} FROM card_details")
            result = mycursor.fetchall()  
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]
            selected_card = st.selectbox(f"Select a {dropdown}  to Delete", list(business_cards.keys()))
            st.write(f"### You have selected :green[**{selected_card} {dropdown}**]to delete")
            st.write("#### Proceed to delete this card_details?")

            if st.button("DELETE"):
                mycursor.execute(f"DELETE FROM card_details WHERE {dropdown} = %s", (selected_card,))
                conn.commit()
                st.success("Business card information deleted from database.")
            if st.button("View updated data"):
                mycursor.execute("select company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code from card_details")
                updated_df = pd.DataFrame(mycursor.fetchall(),columns=["Company_Name","Card_Holder","Designation","Mobile_Number","Email","Website","Area","City","State","Pin_Code"])
                st.write(updated_df)
    except :
        st.warning("There is no data available in the database")
    
            















    
     
   