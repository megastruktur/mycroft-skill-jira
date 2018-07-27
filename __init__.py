from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from jira import JIRA
import re
from collections import Counter

from datetime import date
from datetime import time
from datetime import datetime
import dateutil.parser

__author__ = 'megastruktur'

LOGGER = getLogger(__name__)


class JiraSkill(MycroftSkill):

    # Init stuff.
    def __init__(self):
        
      super(JiraSkill, self).__init__(name="JiraSkill")
    
      # Settings and etc.
      self.jira_init()

    # Functionality init.
    def initialize(self):

        ### Intents.
        jira_intent = IntentBuilder("JiraIntent").require("JiraKeyword").build()
        self.register_intent(jira_intent, self.handle_jira_intent)

    def handle_jira_intent(self, message):

      message_utterance = message.data.get('utterance')
      
      if (message_utterance == "monthly report"):
          self.handle_jira_monthly_report_intent()
      elif (message_utterance == "estimates"):
          self.handle_jira_etimates_intent()


    ### ESTIMATES.
    def handle_jira_etimates_intent(self):
    
        jira_user = self.config.get('jira_user')
        jira_project = self.config.get('jira_project')
        
        #query = 'assignee="' + jira_user + '" and project=' + jira_project
        #query = 'assignee="' + jira_user + '" and project=' + jira_project + ' and sprint in openSprints() and "Story points" is empty'
        query = 'project=' + jira_project + ' and sprint in openSprints() and "Story points" is empty'

        issues = self.jira.search_issues(query, maxResults=3)
        
        for issue in issues:
        
          if issue.fields.assignee is not None:
            #print(dir(issue.fields.assignee))
            self.speak(issue.fields.assignee.displayName + ' needs to estimate ticket ' + issue.key)
            #self.speak(issue.fields.summary)
            self.speak(".")
            print(issue.key + ' ' + issue.fields.summary)
        
        self.speak_dialog("jira")

    ### MONTHLY REPORT
    def handle_jira_monthly_report_intent(self):
      
      dateFrom = date.today().replace(day=1)
      dateTo = date.today()

      self.report(dateFrom, dateTo)

    # Initialize JIRA
    def jira_init(self):
        
      # Load data from mycroft.conf
      # JiraSkill prefix.
      jira_server = self.config.get('jira_server')
      jira_user = self.config.get('jira_user')
      jira_password = self.config.get('jira_password')
      
      jira_options = {'server': jira_server}
      
      self.jira = JIRA(options=jira_options, basic_auth=(jira_user, jira_password))


    # Generate Report based on date
    def report(self, dateFrom, dateTo):

      totaltime = 0
      overtime = 0
      ticket_details_text = ""

      jira_user = self.config.get('jira_user')
      jira_project = self.config.get('jira_project')
      # Main ticket is a place where contract work is logged.
      main_ticket = "CW0650-12"

      query = 'assignee="' + jira_user + '" and worklogDate >= ' + dateFrom.isoformat()

      # Investigate: maybe there is a feature when the second param is
      #   a list of selected fields like: fields=["attachments", "worklog"] etc.
      issues = self.jira.search_issues(query, maxResults=20)

      # Iterate through found issues and filter proper values.
      for issue in issues:
          if (issue.fields.timespent != None):

              # Get the list of all worklogs for ticket.
              worklogs = self.jira.worklogs(issue.key)
              issue_time = 0

              for worklog in worklogs:
                  # Worklog Author should be me.
                  if worklog.author.name == jira_user:
                    # Worklog time should be in selected bounds.
                    #   (start of the current month - today)
                    dateTime = dateutil.parser.parse(worklog.started)
                    if (dateTime.date() > dateFrom and dateTime.date() < dateTo and worklog.timeSpent != 0.0):
                      issue_time += convert_to_seconds(worklog.timeSpent)

              if (issue.key == main_ticket):
                # print(worklog.timeSpent)
                totaltime += issue_time
              else:
                overtime += issue_time
              # Create text to show report
              ticket_details_text += issue.key + ' ' + issue.fields.summary + " " + str(issue_time / 3600) + " hours" + "\r\n"

      print(ticket_details_text)

      hours_spent = totaltime / 3600
      hours_spent_overtime = overtime / 3600
      self.speak("You have logged " + str(hours_spent) + " hours")
      self.speak("Overtime is " + str(hours_spent_overtime) + " hours")

    def stop(self):
        pass

def create_skill():
    return JiraSkill()

### HELPERS
seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 28800, "w": 144000}

def convert_to_seconds(string):

    seconds = 0
    for s in string.split():
      seconds += int(s[:-1]) * seconds_per_unit[s[-1]]
    return seconds
