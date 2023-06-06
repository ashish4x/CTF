from flask import Flask,Response
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
import aiohttp
import re
import time
import threading
import requests
import hashlib
import itertools
import schedule

app = Flask(__name__)
scheduler = BackgroundScheduler(daemon=True)
flagsString="Solving"
lastFetched=datetime.now()
next_event=time.time()
switch=0
time_remaining=0
seconds_remaining=0
status="Not running the script"

def solver():
    
        global flagsString
        global lastFetched
        global status
        global switch
        switch=1
    # with app.app_context():
    # while True:
       
        
        status="Solving"

        url= "https://0ijq1i6sp1.execute-api.us-east-1.amazonaws.com/dev/"
        flags=[]
        
    
        # browser
        def get_browser():
            global status
            pattern = r'Mozilla\/[\d\.]+\s\(.*?\) AppleWebKit\/[\d\.]+\s\(KHTML, like Gecko\) Version\/[\d\.]+\sSafari\/[\d\.]+'
            status="Finding the first flag"
            
            print("\nFinding the first Flag")
            browserReq= requests.get(url+'browser')
            # status="got req"
            user_agent = re.search(pattern, browserReq.json()).group()
            # status="got user-agent"
            headers = {"User-Agent": user_agent}
            flag1 = requests.get(url+'browser', headers=headers)
            # status="got first flag"
            if flag1.json():
                print("Found the first flag")
                flags.append(flag1.json())
                status="got first flag"

            


        #hash
        def get_hash():
            global status
            print("\nDecrypting the MD5 hash")
            hashReq=requests.get(url+'hash')
            pattern = r"md5\(flag\+salt\):[a-f0-9]+:"
            pattern2 = r"md5\(flag\+salt\):([^:]+):"
            status="finding second flag"

            match = re.search(pattern2, hashReq.json())
            if match:
                md5 = match.group(1)


            salt = re.sub(pattern, "", hashReq.json())



            def encrypt_with_salt(word, salt):
                salted_word = word + salt
                hashed_word = hashlib.md5(salted_word.encode()).hexdigest()
                return hashed_word

            def compare_encrypted_value(word, salt, encrypted_value):
                hashed_word = encrypt_with_salt(word, salt)
                return hashed_word == encrypted_value

            # Provide the salt and encrypted value to compare against

            encrypted_value_to_compare = md5  # Example encrypted value for the word "password"
            status="decrypting md5 hash"
            # Read words from file and compare encrypted values
            with open("list.txt", "r") as file:
                for word in file:
                    word = word.strip()  # Remove leading/trailing whitespaces
                    encrypted_word = encrypt_with_salt(word, salt)
                    if compare_encrypted_value(word, salt, encrypted_value_to_compare):
                        print("Found the second flag")
                        status="found second flag"
                        flags.append(word)


        # exception
        def get_exception():
            global status
            status="finding third flag"
            print("\nFinding the third flag")
            exceptionReq=requests.get(url+"exception?q=tqaaaaa")
            if exceptionReq.json():
                print("Third flag found")
                status="found third flag"
                flags.append(exceptionReq.json())


        #stream
        def get_stream():
            global status
            tmpRes=set()
            status="finding fourth flag"
            print("\nFinding last flag")
            print("Fetching stream characters")
            status="fetching stream characters"

            def get_tasks(session):
                global status
                status="getting tasks"
                tasks=[]
                for i in range(100):
                    status="inside task loop"
                    tasks.append(asyncio.create_task(session.get(url+"stream")))
                return tasks
            
            async def get_stream_char():
                global status
                async with aiohttp.ClientSession() as session:
                    tasks=get_tasks(session)
                    responses=await asyncio.gather(*tasks)
                    for response in responses:
                       
                        res_char= await response.json()
                        try:
                            tmpRes.add(res_char)
                            status=str(res_char)
                            print(res_char)
                        except TypeError:
                            continue

                    
                        


            asyncio.run(get_stream_char())
            status="all char added"




            # for i in range(100):
            #     if(len(tmpRes)==7):
            #         print("already found all")
            #         break
            #     request=requests.get(url+"stream")
            #     status= ("Still finding the last flag | " +str(i)+" characters fetched")
            #     print(str(i))
            #     tmpRes.add(request.json())



            print("Done fetching")
            status="done fetching stream characters"
            # print(tmpRes)

            def find_dictionary_word(characters, word_list_file):
                # Generate all possible permutations of the characters
                permutations = [''.join(p) for p in itertools.permutations(characters)]
                
                # Read the words from the word list file
                with open(word_list_file, 'r') as file:
                    word_list = file.read().splitlines()
                    # print(word_list)
                
                # Iterate through the permutations and check if they exist in the word list
                
                for word in permutations:
                    # print(word)
                    if word in word_list:
                    
                        return word
                
                # If no word is found
                return None


            # Set of characters
            characters = tmpRes

            # File path of the word list
            word_list_file = 'list.txt'

            # Find a word from the characters
            result = find_dictionary_word(characters, word_list_file)

            if result:
                # print("Word found:", result)
                status="last flag found"
                print("Last flag found")
                flags.append(result)
            else:

                print("No word found.")

        get_browser()
        get_hash()
        get_exception()
        get_stream()

        flagsString = ', '.join(flags)
        lastFetched=datetime.now()
        status="script completed | all flags found"
        # time.sleep(30*60)
        # switch=0
        





    
# def run_script():
   
#     # global next_event
#     # Run the script initially
#     # schedule.every(30).minutes.do(solver)
#     # next_event = schedule.next_run()
#     while True: 
#         solver()
#         time.sleep(30 * 60)
    

    # Schedule the script to run every 30 minutes
    
    


    # Continuously run the scheduled tasks in a separate thread
    # while True:
    #     schedule.run_pending()
    

# @app.before_first_request
# def on_startup():
    

# thread = threading.Thread(target=run_script)
# thread.start()      


# def run_script():
#     global next_event
#     if not scheduler.running:
#         # solver()
#         scheduler.add_job(solver, 'interval', minutes=30,id='solver', next_run_time=datetime.now())
#         scheduler.start()
#         next_iter = scheduler.get_job('solver').next_run_time

#         datetime_str = str(next_iter)
#         datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S.%f%z")
#         next_event = datetime_obj.replace(tzinfo=None)

# run_script()
 

def run_script():
    thread = threading.Thread(target=solver)
    thread.start()  
    

@app.route('/')
def index():
   
    
    def format_time_ago(dt):
        current_time = datetime.now()
        time_difference = current_time - dt

        minutes = int(time_difference.total_seconds() / 60)

        return f"{minutes}"
    
    
    global flagsString
    global status
    global lastFetched
    global switch
    global time_remaining
    global next_event
    global seconds_remaining

    # remaining_time = next_event - time.time()

    if not scheduler.running:
        # solver()
        scheduler.add_job(run_script, 'interval', minutes=30,id='solver',next_run_time=datetime.now())
        scheduler.start()
    #     next_iter = scheduler.get_job('solver').next_run_time

    #     datetime_str = str(next_iter)
    #     datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S.%f%z")
    #     next_event = datetime_obj.replace(tzinfo=None)

    

    # current_event = datetime.now()
   
    # time_r = next_event - current_event
    # time_remaining=int(time_r.total_seconds()/60)
    # seconds_remaining = time_r.total_seconds() % 60

    

    yield("<b>"+ "<h3>"+ "Flags: " + flagsString + '<br>'+ "</h3>" +"</b>")
    # yield("\n")
    yield("Last Solved : "+ str(format_time_ago(lastFetched)) + " minutes ago"+ " try refreshing if you don't see the flags " '<br>')
    # yield("We run the script everytime someone visit the page and update the flags!"+"<br>"+"<br>")
    yield("<b>"+  "Status: "  + "</b>"+ status + " ")
    # yield(status)
  
    # if(switch==0):
    #     thread = threading.Thread(target=run_script())
    #     thread.start()
    #     return("done")
    
    # yield("<br>"+ "The script will again execute in: "+ str(int(remaining_time/60))+" minutes ")

    yield('<br>'+'<a href=https://github.com/ashish4x/CTF target="_blank">'+"Github Link"+"</a")

    
     
    return("done")






if __name__ == '__main__':
   

    app.run()
     