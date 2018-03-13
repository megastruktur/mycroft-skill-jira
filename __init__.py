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

        jira_intent = IntentBuilder("JiraKeywordIntent"). \
            require("TestKeyword").build()
        self.register_intent(jira_intent,
                             self.handle_jira_intent)

    def handle_jira_intent(self, message):
        jira_server = 'https://jira.atlassian.net'
        jira_user = '';
        jira_password = '';
        jira_options = {'server': jira_server}
        
        authed_jira = JIRA(options=jira_options, basic_auth=(jira_user, jira_password))
        issues = authed_jira.search_issues('assignee=""')
        projects = authed_jira.projects()
        for v in projects:
           print v
        
        #self.speak_dialog("test")
        self.speak("test")

    def stop(self):
        pass


def create_skill():
    return JiraSkill()
