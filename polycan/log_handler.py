from polycan import db, input_prompt
from tqdm import tqdm
from tabulate import tabulate
import csv
import sys
import collections

known = {}
# To Do: Find the mean and variance of dT for a given pgn
def get_statistics(pgn, log):
    pass
#    return {"mean": mean, "variance": variance}

# To Do: Add a detail view for known packets
def detail_view(pgn, data):
    print(pgn)
    print(data)
    return

#This function allows the user to search all known pgns for a specific entry
def find_pgn():
    pgn = input("\nPlease enter PGN or 'q' to return to main menu: ")
    if pgn == 'q':
        return
    known = db.collection(u'known').where(u'pgn', u'==', pgn).get()
    list_known = [x for x in known]
    len_known = len(list_known)
    if len_known == 0:
        print('\nError: unknown PGN \'{}\'. Please try again.\n'.format(pgn))
        return find_pgn()
    print("\nFound %d known CAN bus IDs:" % len_known)
    for record in list_known:
        recdict = record.to_dict()
        print(u'{rid}:'.format(rid=record.id))
        print(u'\tPGN:\t{}'.format(recdict['pgn']))
        print(u'\tSource Address:\t{}'.format(recdict['source']))
        print(u'\tPriority:\t{}'.format(recdict['priority']))
        print(u'\tDescription:\t{}\n------------------'.format(recdict['description']))
    return find_pgn()

# This function gets the name of all logs in database
# It prompts the user to select one and returns the chosen name 
def prompt_log():
    while(1):
        logs = db.collection(u'logs').get()
        x = 1
        log_names = []

        print("\n0. Main Menu")
        for log in logs:
            log_names.append(log.id)
            print("{num}. {name}".format(num=x, name=log.id))
            x+=1
        if len(log_names) == 0:
            print("No logs found. Press 3 to import a log file.")
            return main_menu()
        print("")
        choice = int(input(input_prompt))
        if (choice == 0):
            return
        elif (choice > 0 and choice <= len(log_names)):
            return log_names[choice-1]
        else:
            print("Error. Enter an integer between 0 and " + str(x-1))        

#This function takes the name of the log to be filtered and allows the user to select filter options
#It queries the database with the filter configuration and displays the filtered list using show_log
def filter_log(name):
    while(1):
        choice = input("\n1. By PGN\n2. Using Log Mask\n3. Remove Filter\n4. Main menu\n\n")
        if choice == "1":
            user_pgn = input("Enter a PGN: ")
            target_log = db.collection(u'logs').document(name).collection(u'log').where(u'pgn', u'==', int(user_pgn)).order_by(u'time').get()
            return show_log(target_log, name)
        elif choice == "2":
            mask_data = prompt_log()
            mask_log = db.collection(u'logs').document(mask_data[1]).collection(u'log').order_by(u'time').get()
            target_log = db.collection(u'logs').document(name).collection(u'log').order_by(u'time').get()
            return show_log(target_log, name)
        elif choice == "3":
            target_log = db.collection(u'logs').document(name).collection(u'log').order_by(u'time').get()
        elif choice == "4":
            return
        else:
            print("Error. Enter an integer between 1 and 5\n")

#This function gets known packet data and tags all the packets in the log
#It then tabulates the data and displays to the user
#This function then allows the user to choose analysis options
def show_log(docs, name):
    data = process_log(docs, name)
    print_log(data, name)
    log_menu(data, name)
    return
    
'''
#Takes log name and returns dictionaries with all information, including description
def process_log(docs, name):
    k = db.collection(u'known').get()
    known = {}
    for entry in k:
        e = entry.to_dict()
        known[int(e['pgn'])] = e['description']
    data = []
    x = 1
    for doc in docs:
        d = doc.to_dict()
        dlist = [d['time'], d['pgn'], d['priority'], d['source'], d['destination']]
        if d['pgn'] in known:
            dlist.append(known[d['pgn']])
        else:
            dlist.append("Unknown")
        dlist.append(d['data'])
        # Add packet to data
        data.append(dlist)
    return data
'''
#Takes data as dictionary and prints using tabulate
def print_log(data):
    #Print all data using tabluate
    print("")
    print(tabulate(data, headers=["time","pgn", "prty", "src", "dest", "description", "data" ], showindex = True, tablefmt = "pipe"))
    print("")


# This function downloads a log from database and returns a list
def get_log(log_name, sort):
    log_ref = db.collection(u'logs').document(log_name).collection(u'log').order_by(sort).get()
    data = []
    for doc in log_ref:
        d = doc.to_dict()
        dlist = [d['time'], d['pgn'], d['priority'], d['source'], d['destination']]
        if d['pgn'] in known:
            dlist.append(known[d['pgn']])
        else:
            dlist.append("Unknown")
        dlist.append(d['data'])
        # Add packet to data
        data.append(dlist)
    return data

# This function is responsible for displaying logs, it calls many subfunctions
def switch_log(log_name = '', data = '', filter = 'none', filter_name = '', sort = 'time'):
    # Prompt user and get the name of desired log
    if log_name == '':
        log_name = prompt_log()
    
    # Get the data for that log
    if data == '' :
        data = get_log(log_name, sort)
        pass
    # If we are filtering by pgn
    if filter == 'pgn':
        pass

    # If we are filtering by log
    if filter == 'mask': 
        mask_data = get_log(mask_name, sort)
        #TODO: Masking Algorithm
        pass

    # Store reference to current log
    current_log = log_name
    # Display the log data
    print_log(data)
    
    return

    '''
    if (log_name in log_cache):
        print("log " + log_name + " is cached!")
    else:
        print("log " + log_name + " is not cached!")
        if (len(log_cache) > 3):
            log_cache.remove()
        log_cache.append(log_name
                   
   
   '''
# Populate list of known   
def get_known():
    known_ref = db.collection(u'known').get()
    known = {}
    for entry in known_ref:
        e = entry.to_dict()
        known[int(e['pgn'])] = e['description']
    return known

#This function allows the user to add a csv log to the database
def import_log():
    batch = db.batch()
    path = input("\nEnter file path: ")
    if len(path) <= 4:
        print("Error, Invalid File Name")
        return
    x = 0
    try:
        with open("logs/"+path, newline='') as csvfile:
            log = csv.DictReader(csvfile)
            doc_ref = db.collection(u'logs').document(path[:-4]).collection('log')
            db.collection(u'logs').document(path[:-4]).set({u'model': '5055E'})
            print("\nUploading " + path[:-4] + "...") 
            for line in tqdm(log):
                line_ref = doc_ref.document(line['time'])
                batch.set(line_ref,{ u'pgn': int(line['pgn'], 16),
                                     u'destination': int(line['destination'], 16),
                                     u'source': int(line['source'], 16),
                                     u'priority': int(line['source'], 16),
                                     u'time': float(line['time']),
                                     u'data': line['data']
                                     })
                x += 1
                if x % 500 == 0:
                    batch.commit()
            print("Uploaded", x-2, "lines.")
    except FileNotFoundError:
        print("Error. File not found.")
    
    return
known = get_known() 