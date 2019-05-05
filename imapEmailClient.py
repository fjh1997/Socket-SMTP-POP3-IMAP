import socket, ssl, base64, sys, time, math

print "Connecting.."

username = ""
password = ""

# Choose a mail server (e.g. Google mail server) and call it mailserver

mailserver = ('imap.163.com', 143)

# Create socket called clientSocket and establish a TCP connection with mailserver

#Fill in start  

#sslSocket = ssl.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM),

#ssl_version = ssl.PROTOCOL_SSLv23)
sslSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sslSocket.connect(mailserver)

recv = sslSocket.recv(1024)

if recv.find('OK Gimap ready for requests from') != -1:
    print "Connected.\n"
else:
    print "Problem connecting.\n"

#################################
#Done connecting
#################################


#################################
#Global Variables
#################################
currentFolder = "None" #Stores the currently selected mail box


#################################
#imap Methods
#################################
def imap_login():#login

    print("Login information:")
    username = "a@163.com"
    password = "password"
    
    
    print("Attempting to login.\n")
    
    sslSocket.send('A001 LOGIN ' + username + ' ' + password + '\r\n')

    recv = sslSocket.recv(1024)
    
    if recv.find("completed") != -1:
        print "Successfully logged in to: " + username + "\n"
        return 1
    else:
        print "Login failed!\n"
        return -1
#List
def imap_list(dir = "", type = "*"):#return list of mailboxes with optional parameters to change what is listed
    sslSocket.send('A101 List ' + "\"\"" +' '+ type + '\r\n')
    recv = recv_all()
    return recv
#Search
def imap_search(x):
    sslSocket.send('A201 SEARCH ' + x + '\r\n')
    recv = recv_all()
    return recv
#Examine
def imap_examine(x):
    sslSocket.send('A900 EXAMINE "' + x + '"\r\n')
    recv = sslSocket.recv(1024)
    return recv
#Fetch
def imap_fetch(x):
    sslSocket.send('A301 FETCH ' + x + '\r\n')
    recv = recv_all()
    return recv
#Create
def imap_create(x):
    sslSocket.send('A401 CREATE "' + x + '"\r\n')
    recv = sslSocket.recv(1024)
    return recv
#Delete
def imap_delete(x):
    print 'A501 DELETE "' + x + '"\r\n'
    sslSocket.send('A501 DELETE "' + x + '"\r\n')
    recv = sslSocket.recv(1024)
    print recv
    return recv
#UID Copy
def imap_uid_copy(x):
    sslSocket.send('A300 COPY "' + x + '"\r\n')
    recv = recv_all()
    return recv
#UID Fetch
def imap_uid_fetch(x):
    sslSocket.send('A999 UID FETCH ' + x + '\r\n')
    recv = recv_all()
    return recv
#UID Store
def imap_uid_store(x):
    print 'A003 UID STORE ' + x + '\r\n'
    sslSocket.send('A003 UID STORE ' + x + '\r\n')
    recv = sslSocket.recv(1024)
    print recv
    return recv
#UID Search
def imap_uid_search(x):
    sslSocket.send('A999 UID SEARCH ' + x + '\r\n')
    recv = recv_all()
    return recv
#Expunge
def imap_expunge():
    sslSocket.send('A202 EXPUNGE\r\n')
    recv = sslSocket.recv(1024)
    print recv
#Select
def imap_select(x):
    sslSocket.send('A142 SELECT "' + x + '"\r\n')
    recv = recv_all()
    return recv

#################################
#Extra Methods
#################################
#Receive using a timeout
def recv_all(timeout = 2):#can either pass a different timeout or use the default set in the parameter
    global sslSocket
    #set the socket to non-blocking
    sslSocket.setblocking(0)
    #array of the data received
    data_str = ''
    #time this method started
    begin = time.time()
     
    #loop till the timeout has passed
    while True:
        #If some data was receive and it passed the timeout, then stop
        if data_str and time.time()-begin > timeout:
            break
        #If no data has been retrieved and it has passed the timeout by 2, then there is probably nothing to get, so stop 
        elif time.time()-begin > timeout*2:
            break
        #try and get the data using a try/except to catch errors with getting data from the server
        try:
            data = sslSocket.recv(1024)
            if data: #if there is some data that was received then store that data
                data_str += data
                begin=time.time()#reset the begin time so that it doesn't timeout while still getting data
            else:
                time.sleep(0.1)#give a slight pause before trying to read again
        except:
            pass #just let it reloop if there was an error thrown
    #set the socket back to blocking since only this method is designed for non=blocking
    sslSocket.setblocking(1)
    return data_str

#Returns a list containing the mailbox names
#The parameter is the string returned from the imap_list command
def get_mailbox_list_array(mailbox_string):
    temp_list = mailbox_string.split('\r\n')#Split the returned string by the new line indicators
    del temp_list[len(temp_list)-1]#The last element is an empty string, so it isn't needed
    
    mail_list = []#Will hold the list of mailbox names to be returned
    for x in temp_list:
        if x.find('/" "') != -1 and x.find('\Noselect') == -1 and x.find('[Gmail]/All Mail') == -1:#The line has a mail box (AND) doesn't contain the /Noselect flag  (And)  isn't the all mail folder
            pos = x.find('/" "')+4
            mail_list.append(x[pos:-1]) #Store the substring of the line containing the mailbox name 
    return mail_list
    
#Print the mailbox names in a list
def print_mailboxes_list(mailbox_list):
    print ""
    print "---------------------------------"
    print "Mail Boxes:"
    
    index = 0
    while index < len(mailbox_list):
        print str(index) + ":" + mailbox_list[index]
        index = index + 1
    
    print "---------------------------------"
    
#Print the mailbox names in a list with additional information
def print_mailboxes_list_with_info(mailbox_list, info):
    print ""
    print "---------------------------------"
    print "Mail Boxes:"
    
    index = 0
    while index < len(mailbox_list):
        print str(index) + ":" + mailbox_list[index] + "  " + info[index]
        index = index + 1
    
    print "---------------------------------"
    
#Print the email list in the format    (box number or uid number): Subject: This is the email subject
def print_mail_list_with_subject(nums, subs, start = 1, end = -1):#nums = the numbers of the emails, subs = the subjects of the emails
    if end == -1:#If the point to stop printing in the list wasn't specified in the params, set it to the end of the list
        end = len(subs)
        
    while start <= len(nums) and start <= end:#Print the specified elements of the lists
        print str(nums[start-1]) + ": " + str(subs[start-1])
        start += 1

#Get how many emails each mailbox contains
def get_mailboxes_info_array(mail_list):
    mail_info_list = [] #Holds the list of info for the emails
    for x in mail_list:
        recv = imap_examine(x)
        tmp = recv.split(" ")
        
        amtExist = 'N/A'
        amtRecent = 'N/A'
        try:
            amtExist = tmp[17]
            amtRecent = tmp[19]
        except:
            pass
        
        mail_info_list.append('(Emails: ' + amtExist + '  Recent: ' + amtRecent + ')')#Add the formated string to the list
    return mail_info_list

#Return a string of the numbers returned from the search command
def get_mail_numbers_from_search(recv):
    pos1 = recv.find('SEARCH')+7
    pos2 = recv.find('\r')
    r = recv[pos1:pos2]
    tmp = r.split(' ')
    temp_list = []
    for t in tmp:
        try:
            temp_list.append(int(t))
        except:
            pass
    return temp_list

#Return the text of the email body
def format_email_body(recv):
    first = 0
    last = len(recv)-1
    
    if recv.find('}') != -1:#Find the first }
        first = recv.find('}') + 3
    
    for index in reversed(range(len(recv))): #Loop from the end til it find the A
        if recv[index] == 'A':
            last = index - 5
            break
    return recv[first:last]

#Return true if the mail box has child boxes
def has_children(strg, mailbox_list):
    for s in mailbox_list:
        if s.find(strg) != -1 and strg != s:
            return True
    return False
    
def delete_all_children_with_child(strg, mailbox_list):
    for s in mailbox_list:
        if s.find(strg) != -1:
            imap_delete(s)

def filter_list_of_subjects(l):
    li = []
    if l.find('\nSubject: ') != -1:
        tmp = l.find('\nSubject: ')
        l = l[tmp:]
        while l.find('\nSubject: ') != -1:
            pos1 = l.find('\nSubject: ')+1
            pos2 = l.find('\r')
            new = l[pos1:pos2]
            if new != '':
                li.append(new)
            l = l[pos2+1:]
    return li

def email_is_read(mail_type, ch):#0 == norm  #1 == UID
    recv = ''
    if mail_type == 0:
        recv = imap_search(str(ch) + ' SEEN')
    else:
        recv = imap_uid_search(str(ch) + ' SEEN')
    
    pos1 = recv.find('SEARCH')+7
    pos2 = recv.find('\r')
    r = recv[pos1:pos2]
    if r != '':
        return True
    else:
        return False


#################################
#Mail Client Methods
#################################
def view_mailboxes():
    mailbox_string = imap_list()
    mail_list = get_mailbox_list_array(mailbox_string)
    mailboxes_info = get_mailboxes_info_array(mail_list)
    print_mailboxes_list_with_info(mail_list, mailboxes_info)
    

def examine_mailbox():
    global currentFolder
    mailbox_string = imap_list()
    mail_list = get_mailbox_list_array(mailbox_string)
    mailboxes_info = get_mailboxes_info_array(mail_list)
    print_mailboxes_list_with_info(mail_list, mailboxes_info)
    
    choice = raw_input("Which mail box do you want to open: ")
    
    try:
        if int(choice) < len(mail_list):
            currentFolder = mail_list[int(choice)]
            print "\nSelected " + currentFolder
        else:
            print "\nNot a valid mail box."
    except:
        print "\nNot a valid mail box."


def get_mail_boxnum():
    get_mail(0)

def get_mail_uid():
    get_mail(1)
    
def get_mail(mail_type):#0 == search  #1 == UID search
    imap_select(currentFolder)
    email_list_length = 10
    
    
    if mail_type == 0:
        recv = imap_search('ALL')
    else:
        recv = imap_uid_search('ALL')
    
    mail_nums = get_mail_numbers_from_search(recv)
    
    string_list = ''
    for x in range(len(mail_nums)):
        string_list += str(mail_nums[x]) + ','
    if string_list:
        string_list = string_list[:-1]
    if mail_type == 0:
        subject_list = imap_fetch(string_list + " BODY[HEADER.FIELDS (SUBJECT)]")
    else:
        subject_list = imap_uid_fetch(string_list + " BODY[HEADER.FIELDS (SUBJECT)]")
    mailboxes_info = filter_list_of_subjects(subject_list)
    max_pages = int(len(mail_nums)/email_list_length)
    if (len(mail_nums)%email_list_length) > 0:
        max_pages += 1
    current_page = 0
    again = 1
    while again == 1:
        again = 1
        
        start = current_page * email_list_length + 1
        end = start + email_list_length - 1 
        
        if len(mail_nums) > 0:
            print '\n-------------------------------\nEmails~    Page: ' + str(current_page+1) + '/' + str(max_pages)
            print_mail_list_with_subject(mail_nums, mailboxes_info, start, end)
            
            print "\nTo view more mail type, NEXT or PREV"
            choice = raw_input("Which email do you want to open? ")
            if choice == 'NEXT' or choice == 'next':
                again = 1
                if current_page < max_pages-1:
                    current_page+=1
            elif choice == 'PREV' or choice == 'prev':
                again = 1
                if current_page > 0:
                    current_page-=1
            else:
                again = 0
        else:
            print "Mail box is empty."
            again = 0
        
    if len(mail_nums) > 0:
        try:
            ch = int(choice)
            if mail_type == 0:
                recv_body = imap_fetch(str(ch) + " BODY[1]")
                recv_header = imap_fetch(str(ch) + " BODY[HEADER.FIELDS (DATE SUBJECT FROM TO)]")
                recv_uid = imap_fetch(str(ch) + " (UID)")
            else:
                recv_body = imap_uid_fetch(str(ch) + " BODY[1]")
                recv_header = imap_uid_fetch(str(ch) + " BODY[HEADER.FIELDS (DATE SUBJECT FROM TO)]")
                recv_uid = imap_uid_fetch(str(ch) + " (UID)")
            print "\n==============================================================================="
            pos = recv_uid.find('(UID')+5
            pos2 = recv_uid.find(')')
            msg_uid = recv_uid[pos:pos2]
            print "Email UID: " + msg_uid
            pos = recv_header.find("Date: ")
            pos2 = recv_header.find('OK Success\r\n')-11
            print recv_header[pos:pos2]
            print "--------------------------------------------------------------------"
            print format_email_body(recv_body)
            print "===============================================================================\n"
            email_read = email_is_read(mail_type, ch)#0 == norm  #1 == UID     #false = unread   true = read
            print email_read 
            if email_read:
                print "\nMark as unread = 1,   Delete = 2,   Leave as is = 3"
                choice = raw_input("Choice: ")
                if choice == "1":
                     #mark as unread
                    recv = imap_uid_store(msg_uid + ' -FLAGS (\seen)')
                elif choice == "2":
                     #delete
                    recv = imap_uid_store(msg_uid + ' +FLAGS (\deleted)')
                    print recv
                    imap_expunge()
                    
            else:
                print "\nMark as read = 1,   Delete = 2,   Leave as is = 3"
                choice = raw_input("Choice: ")
                if choice == "1":
                     #mark as read
                    recv = imap_uid_store(msg_uid + ' +FLAGS (\seen)')
                elif choice == "2":
                     #delete
                    recv = imap_uid_store(msg_uid + ' +FLAGS (\deleted)')
                    print recv
                    imap_expunge()
        except:
            print "Email not available."

def create_dir():
    name = raw_input("\nName of new mailbox to create:")
    recv = imap_create(name)
    if recv.find("OK Success") != -1:
        print "Created " + name + "!"
    else:
        print "Failed to create."

def delete_dir():
    mailbox_string = imap_list("/", "*")
    mail_list = get_mailbox_list_array(mailbox_string)
    print_mailboxes_list(mail_list)
    
    choice = raw_input("Enter the number for the box to delete: ")
    try:
        ch_num = int(choice)
        if ch_num > len(mail_list):
            cmd = "No Box available"
        else:
            name = mail_list[ch_num]
            if has_children(name, mail_list):
                decision = raw_input("Are you sure you want to delete " + name + " and all children.(1=yes, 2=no)")
                if decision == "1":
                    delete_all_children_with_child(name, mail_list)
                    cmd = "all"
                else:
                    cmd = ""
            else:
                cmd = name
    except:
        cmd = ""

    print "Checking: " + cmd
    if cmd == "":
        print "\nNo Box chosen"
    if cmd == "all":
        print "Deleted"
    else:
        imap_delete(cmd)
        if recv.find("OK Success") != -1:
            print "Deleted " + name + "!"
        else:
            print "Failed to delete."

def search_mail_search():
    search_mail(0)

def search_mail_uid_search():
    search_mail(1)

def search_mail(search_type):#0 == search  #1 == UID search
    imap_examine(currentFolder)
    options = ["All", "Unread", "Old", "Drafts", "Text", "Date"]
    print "\n------------------------------"
    print "Search by:"
    inc = 0
    while inc < len(options):
        print str(inc) + ":" + options[inc]
        inc = inc + 1
    print "------------------------------"
    
        
    choice = raw_input("Choice: ")
    cmd = ""
    #all
    if choice == "0":
        cmd = 'ALL'
    #unread
    elif choice == "1":
        cmd = 'UNSEEN'
    #old
    elif choice == "2":
        cmd = 'OLD'
    #drafts
    elif choice == "3":
        cmd = 'DRAFT'
    #text
    elif choice == "4":
        search_text = raw_input("Search for text: ")
        cmd = 'TEXT "' + search_text + '"'
    #date
    elif choice == "5":
        when_ch = raw_input("(Before date = 1)(On date = 2)(Since date = 3):")
        date_ch = raw_input("Date(dd-mm-yyyy)(ex. 1-Sep-2013):")
        date_opt = "ON"
        if when_ch == "1":
            date_opt = "BEFORE"
        elif when_ch == "2":
            date_opt = "ON"
        elif when_ch == "3":
            date_opt = "SINCE"
            
        cmd = date_opt + ' ' + date_ch
    
    if search_type == 0:
        recv = imap_search(cmd)        
    else:
        recv = imap_uid_search(cmd)
    
    mail_nums = get_mail_numbers_from_search(recv)
    if len(mail_nums) > 0:
        string_list = ''
        for x in range(len(mail_nums)):
            string_list += str(mail_nums[x]) + ','
        if string_list:
            string_list = string_list[:-1]
        if search_type == 0:
            subject_list = imap_fetch(string_list + " BODY[HEADER.FIELDS (SUBJECT)]")
        else:
            subject_list = imap_uid_fetch(string_list + " BODY[HEADER.FIELDS (SUBJECT)]")
        mailboxes_info = filter_list_of_subjects(subject_list)
        print_mail_list_with_subject(mail_nums, mailboxes_info)
    else:
        print "Mail box is empty."

def copy_mail():
    imap_examine(currentFolder)
    recv = imap_uid_search('ALL')
    
    mail_nums = get_mail_numbers_from_search(recv)
    if len(mail_nums) > 0:
        print '\n-------------------------------\nEmails:'
        string_list = ''
        for x in range(len(mail_nums)):
            string_list += str(mail_nums[x]) + ','
        if string_list:
            string_list = string_list[:-1]
        subject_list = imap_uid_fetch(string_list + " BODY[HEADER.FIELDS (SUBJECT)]")
        mailboxes_info = filter_list_of_subjects(subject_list)
        print_mail_list_with_subject(mail_nums, mailboxes_info)
    else:
        print "Mail box is empty."
    
    choice = raw_input('\nWhich email do you want to copy: ')
    choice_dest = raw_input('To which folder: ')
    
    try: 
        if len(mail_nums)+2 > int(choice) and int(choice) > 0:
            print imap_uid_copy(choice + ' ' + choice_dest)
        else:
            print "Not a valid email."
    except:
        print "Invalid input."
    
def testing():
    imap_expunge()

    
#Done running
def close_mail():
    sslSocket.close() #close the socket
    print "Done."

#Main Method
def main():
    log_success = imap_login()
    if log_success == -1:
        close_mail()
        return 0
    
    choice = ""
    #The main loop
    while choice != "0":
        print "\n"
        print "---------------------------------------------"
        print "-- Currently Selected Mailbox: " + currentFolder
        print "---------------------------------------------"
        print "What would you like to do? (0 to quit.)"
        print "1: View all mail boxes"
        print "2: Examine a mail box"
        print "3: Search selected mail box"
        print "4: Search using message unique id" 
        print "5: Get mail from selected mail box"
        print "6: Get mail from selected mail box using unique id"
        print "7: Create a mail box"
        print "8: Delete a mail box"
        print "9: Copy email from selected mail box to another"
        
        choice = raw_input("Choice: ")
        
        if choice == "1":
            view_mailboxes()
        elif choice == "2":
            examine_mailbox()
        elif choice == "3":
            if currentFolder == "None":
                print "\nNo mail box selected."
            else:
                search_mail_search()
        elif choice == "4":
            if currentFolder == "None":
                print "\nNo mail box selected."
            else:
                search_mail_uid_search()
        elif choice == "5":
            if currentFolder == "None":
                print "\nNo mail box selected."
            else:
                get_mail_boxnum()
        elif choice == "6":
            if currentFolder == "None":
                print "\nNo mail box selected."
            else:
                get_mail_uid()
        elif choice == "7":
            create_dir()
        elif choice == "8":
            delete_dir()
        elif choice == "9":
            copy_mail()
        elif choice == "10":
            testing()
        
        if choice == "0":
            close_mail()
        




if __name__ == '__main__':
    main()
