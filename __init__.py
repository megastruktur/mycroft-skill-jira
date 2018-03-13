from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from jira import JIRA
import re
from collections import Counter

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

        # Intents.
        jira_intent = IntentBuilder("JiraIntent"). \
            require("JiraKeyword").build()
        self.register_intent(jira_intent, self.handle_jira_intent)

    # Intent handler.
    def handle_jira_intent(self, message):
    
        jira_user = self.config.get('jira_user')
        jira_project = self.config.get('jira_project')
        
        issues = self.jira.search_issues('assignee="' + jira_user + '" and project=' + jira_project, maxResults=3)
        
        for issue in issues:
          self.speak(issue.fields.summary)
          self.speak(".")
          print issue.fields.summary
        
        self.speak_dialog("jira")

    # Initialize JIRA
    def jira_init(self):
        
      # Load data from mycroft.conf
      # JiraSkill prefix.
      jira_server = self.config.get('jira_server')
      jira_user = self.config.get('jira_user')
      jira_password = self.config.get('jira_password')
      
      jira_options = {'server': jira_server}
      
      self.jira = JIRA(options=jira_options, basic_auth=(jira_user, jira_password))

    def stop(self):
        pass


def create_skill():
    return JiraSkill()
