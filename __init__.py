from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from jira import JIRA
import re
from collections import Counter

__author__ = 'megastruktur'

LOGGER = getLogger(__name__)


class JiraSkill(MycroftSkill):
    def __init__(self):
        super(JiraSkill, self).__init__(name="JiraSkill")

    def initialize(self):

        jira_intent = IntentBuilder("JiraIntent"). \
            require("JiraKeyword").build()
        self.register_intent(jira_intent, self.handle_jira_intent)

    def handle_jira_intent(self, message):
        
        # Load data from mycroft.conf
        # JiraSkill prefix.
        jira_server = self.config.get('jira_server')
        jira_user = self.config.get('jira_user')
        jira_password = self.config.get('jira_password')
        #jira_project = self.config.get('jira_project')
        jira_project = "SEN";
        
        print jira_server
        print jira_user
        print jira_password
        
        jira_options = {'server': jira_server}
        
        authed_jira = JIRA(options=jira_options, basic_auth=(jira_user, jira_password))
        issues = authed_jira.search_issues('assignee="' + jira_user + '" and project=' + jira_project, maxResults=3)
        
        for issue in issues:
          self.speak(issue.fields.summary)
          print issue.fields.summary
          
        #projects = authed_jira.projects()
        #for v in projects:
        #   print v
        
        self.speak_dialog("jira")

    def stop(self):
        pass


def create_skill():
    return JiraSkill()
