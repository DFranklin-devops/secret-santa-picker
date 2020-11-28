import json
import random as rnd
import pyinputplus as pyip
import smtplib
import os
from json import JSONEncoder
#
# input data format:
# a person is identified by Name, Email, Spouse
# demo-names.json is a dictionary that includes an array of Participants
# in this code though, we are adding a new field, "Picked" to indicate who they chose for secret santa
# So we are embellishing a person/participant by adding a new field, and we'll write that file
# We will also email the person who they've picked

# picker must be Participant type
# who can the picker pick? Not themselves or their spouse, but anyone else unclaimed
def valid_choices(picker):
    return [p for p in out_people if picker.Name != p.Name and
                                     picker.Name != p.Spouse and
                                     p.PickedBy == ""]

# Notify each participant individually who they picked
def send_email_notifications(people):
    smtp_obj = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_obj.ehlo()
    smtp_obj.starttls()
    sender_email = os.environ['AUTO_EMAIL']
    sender_pass = os.environ['AUTO_PASS']
    if sender_email == None or sender_pass == None:
        sender_email = input("Please enter the sending email address:")
        sender_pass = input("Please enter the sending email password:")
    smtp_obj.login(sender_email,sender_pass)
    for person in people:
        message = ("Subject: {} - your Secret Santa pick\nYou selected {} for this "
                    "year's Secret Santa. Merry Christmas and happy shopping!").format(person.Name, person.Picked)
        message += "\nLove,\nSanta's Automated Helper"
        smtp_obj.sendmail(sender_email, "jazzrunnerdave@gmail.com", message)
    smtp_obj.quit()


class Participant(object):
    def __init__(self, dict):
        for key in dict:
            setattr(self, key, dict[key])
#        self.Picked = ""
#        self.PickedBy = ""
        setattr(self, "Picked", "")
        setattr(self, "PickedBy", "")

with open('demo-names.json') as f:
    data = json.load(f)

# Set up
in_people = data['Participants']
out_people = [] # to add the Picked and PickedBy attributes
for person in in_people:
    out_people.append( Participant(person) )

# Since a person can't pick themselves, and they can't pick their spouse,
# there are many choices where we get to the end of the list and the last
# one or two people have no options.
# We may have to rewind one or two people and even then we're not guaraneed
# a re-selection (even with a newly reduced list) will work
# So brute force: loop until we get valid configuration
all_set = False
while not all_set:
    count = 0
    # randomly set the picking order
    rnd.shuffle(out_people)
    # Ask people to pick names
    for part in out_people:
        print(part.Name + " - it is your time to choose")
        legal_options = valid_choices(part)
        if not legal_options:
            print("\n\nWe need to start over, no legal options available")
            for x in out_people:
                x.Picked, x.PickedBy = "", ""
        else:
            count+=1
            optnum = len(legal_options)
            i = pyip.inputNum("Please pick a number 1 through {}: ".format(
                               optnum),min=1,max=optnum)
            part.Picked = legal_options[i-1].Name
            legal_options[i-1].PickedBy = part.Name
            if count == len(out_people):
                all_set = True

# dump the picks just in case something gets lost
with open('secret-santa.json','w') as f:
    json.dump([ob.__dict__ for ob in out_people], f)

choice = pyip.inputYesNo("Do you want to send individual email notifications?")
if choice == 'yes':
    send_email_notifications(out_people)
