from flask import Flask
from datetime import datetime
import re
import threading
import requests
import hashlib
import itertools
import schedule

app = Flask(__name__)
flagsString="Solving"
lastFetched=datetime.now()

def solver():
    # with app.app_context():

        global flagsString
        global lastFetched

        url= "https://0ijq1i6sp1.execute-api.us-east-1.amazonaws.com/dev/"
        flags=[]
        
    
        # browser
        def get_browser():
            pattern = r'Mozilla\/[\d\.]+\s\(.*?\) AppleWebKit\/[\d\.]+\s\(KHTML, like Gecko\) Version\/[\d\.]+\sSafari\/[\d\.]+'

            
            print("\nFinding the first Flag")
            browserReq= requests.get(url+'browser')
            user_agent = re.search(pattern, browserReq.json()).group()
            headers = {"User-Agent": user_agent}
            flag1 = requests.get(url+'browser', headers=headers)
            if flag1.json():
                print("Found the first flag")
                flags.append(flag1.json())


        #hash
        def get_hash():
            print("\nDecrypting the MD5 hash")
            hashReq=requests.get(url+'hash')
            pattern = r"md5\(flag\+salt\):[a-f0-9]+:"
            pattern2 = r"md5\(flag\+salt\):([^:]+):"

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

            # Read words from file and compare encrypted values
            with open("list.txt", "r") as file:
                for word in file:
                    word = word.strip()  # Remove leading/trailing whitespaces
                    encrypted_word = encrypt_with_salt(word, salt)
                    if compare_encrypted_value(word, salt, encrypted_value_to_compare):
                        print("Found the second flag")
                        flags.append(word)


        # exception
        def get_exception():
            print("\nFinding the third flag")
            exceptionReq=requests.get(url+"exception?q=tqaaaaa")
            if exceptionReq.json():
                print("Third flag found")
                flags.append(exceptionReq.json())


        #stream
        def get_stream():
            tmpRes=set()
            print("\nFinding last flag")
            print("Fetching stream characters")
            for i in range(150):
                request=requests.get(url+"stream")
                
                tmpRes.add(request.json())


            print("Done fetching")
            print(tmpRes)

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
        
        schedule.every(30).minutes.do(solver)
        
    
def run_script():
    # Run the script in a separate thread
    thread = threading.Thread(target=solver)
    thread.start()
    

# @app.before_first_request
# def on_startup():
    

        


@app.route('/')
def index():
    
    def format_time_ago(dt):
        current_time = datetime.now()
        time_difference = current_time - dt

        minutes = int(time_difference.total_seconds() / 60)

        return f"{minutes} minutes ago"
    
    
    global flagsString
    global lastFetched

   
    

    yield("<b>"+ "<h3>"+ "Flags: " + flagsString + '<br>'+ "</h3>" +"</b>")
    # yield("\n")
    yield("Last Solved : "+ str(format_time_ago(lastFetched)) + '<br>')
    yield("We run the script everytime someone visit the page and update the flags!")
  
    


      
    return("done")

        


if __name__ == '__main__':
    run_script()
    app.run()