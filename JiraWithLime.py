import sublime, sublime_plugin
import re
from JiraWithLime.lime_connection import LimeConnection
from JiraWithLime.lime_issue import LimeIssue
from . import markdown2

class GetJiraHeadlineCommand(sublime_plugin.TextCommand):
	def run(self, edit, issue_key=None):
		window = self.view.window()
		if not issue_key:
			window.run_command('prompt_issue_key',
								{'callback': 'get_jira_headline'})
		else:
			connection = LimeConnection()
			issue = connection.get(issue_key)
			region = self.view.sel()
			line = self.view.line(region[0])
			self.view.insert(edit, line.end(), "\n@ "+issue.key+" - "+issue.name+"\n"+issue.description)

class PromptIssueKeyCommand(sublime_plugin.TextCommand):
	def run(self, edit, callback):
		window = self.view.window()
		settings = sublime.load_settings('JiraWithLime.sublime-settings')
		issue_key_hint = settings.get('project', "") + "-"
		call = lambda v: window.run_command(callback, {'issue_key': v})
		window.show_input_panel('Issue key', issue_key_hint, call, None, None)

class OpenIssueCommand(sublime_plugin.TextCommand):
	def run(self, edit, issue_key=None):
		window = self.view.window()
		if not issue_key:
			window.run_command('prompt_issue_key',
								{'callback': 'open_issue'})
		else:
			connection = LimeConnection()

			issue = connection.get(issue_key)

			TEMPLATE = (
					"{key} - {name}\n"
					"@@ Projekt: {project}\n"
					"@@ Projekt Name: {project_name}\n"
					"@@ Reporter: {reporter}\n"
					"@@ Bearbeiter: {assignee}\n"
					# "@@ Updated: {updated}\n"
					"@@ Sprint: {version}\n"
					"\n"
					"@@ Description:\n"
					"{description}\n"
					"\n"
					"@@ Text:\n"
					"{text}\n"
					)

			keywords = re.findall(r'\{([a-z_]+)\}', TEMPLATE)
			valuesMap = {}
			for key in keywords:
				valuesMap[key] = issue.getattr(key)
			text = TEMPLATE.format(**valuesMap)
			window.new_file()
			view = window.active_view()
			view.insert(edit, 0, text)

class ReplaceAllCommand(sublime_plugin.TextCommand):
	def run(self, edit, text):
		self.view.run_command('select_all')
		self.view.replace(edit, self.view.sel()[0], text)
		self.view.sel().clear()

class UpdateIssueCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		window = self.view.window()

		TEMPLATE = (
				"{key} - {name}\n"
				"@@ Projekt: {project}\n"
				"@@ Projekt Name: {project_name}\n"
				"@@ Reporter: {reporter}\n"
				"@@ Bearbeiter: {assignee}\n"
				"\n"
				"@@ Description:\n"
				"{description}\n"
				"\n"
				"@@ Text:\n"
				"{text}\n"
				)

		self.view.run_command('select_all')
		text = self.view.substr(self.view.sel()[0])
		self.view.sel().clear()

		templateRegEx = re.sub(r'\{', "(?P<", TEMPLATE)
		templateRegEx = re.sub(r'\}', ">(.|\n)*)", templateRegEx)
		templateRegEx = re.compile(templateRegEx)
		inputValues = re.match(templateRegEx, text).groupdict()
		connection = LimeConnection()

		r = connection.update(inputValues['key'], LimeIssue().mapLimeToJira(inputValues))

class NewTestsCommand(sublime_plugin.TextCommand):
	def run(self, edit, issue_key=None):
		window = self.view.window()
		if not issue_key:
			window.run_command('prompt_issue_key',
								{'callback': 'new_tests'})
		else:
			connection = LimeConnection()

			issue = connection.get(issue_key)

			TEST_HEAD_TEMPLATE = (
					"{key} - {name}\n"
					"{description}\n"
					"\n"
					"@@ Projekt: {project}\n"
					"@@ Story: {key}\n"
					"@@ Story Reporter: {reporter}\n"
					"\n"
					"@@ Version: {version}\n"
					"@@ Attribute: {attribute}\n"
					"@@ Testgruppen: {testgroup}\n"
					'@@ Komponente: {component}\n'
					'@@ Stichwörter: {lables}\n'
					'@@ Bearbeiter: {assignee}\n'
					"\n"
					)

			keywords = re.findall(r'\{([a-z_]+)\}', TEST_HEAD_TEMPLATE)
			valuesMap = {}
			for key in keywords:
				valuesMap[key] = issue.getattr(key)
			valuesMap['attribute'] = "Regressionstest, Live-Test, Automatisiert"
			valuesMap['key'] = issue_key
			settings = sublime.load_settings('JiraWithLime.sublime-settings')
			valuesMap['assignee'] = settings.get('assignee', "")
			valuesMap['component'] = settings.get('component', "")
			valuesMap['testgroup'] = settings.get('testgroup', "")
			
			text = TEST_HEAD_TEMPLATE.format(**valuesMap)

			window.new_file()
			view = window.active_view()
			view.insert(edit, 0, text)
			window.run_command('add_test_template')
			window.run_command('add_test_template')
			window.run_command('add_test_template')

class AddTestTemplateCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		window = self.view.window()
		TEST_STEP_TEMPLATE = (
				"\n@ Test:\n"
				#"@@ Key:\n"
				"@@ Beschreibung\n"
				"{beschreibung_template}"
				"\n"
				"----\n"
				"\n"
				"->\n"
				"\n"
				"----\n"
				"\n"
				"->\n"
				"\n"
				"----\n"
				)

		settings = sublime.load_settings('JiraWithLime.sublime-settings')
		valuesMap = {}
		valuesMap['beschreibung_template'] = settings.get('beschreibung_template', "")
		text = TEST_STEP_TEMPLATE.format(**valuesMap)
		self.view.insert(edit, self.view.size(), text)

class NewBugCommand(sublime_plugin.TextCommand):
	def run(self, edit, issue_key=None):
		window = self.view.window()
		BUG_HEAD_TEMPLATE = (
				'\n'
				'@@ Projekt: {project}\n'
				#'@@ Stichwörter: {lables}\n'
				'@@ Domäne: {domain}\n'
				'@@ Umgebung: {environment}\n'
				'@@ Browser: {browser}\n'
				'@@ Komponente: {component}\n'
				'@@ Bearbeiter: {assignee}\n'
				'\n'
				'@@ Version: {version}\n'
				'\n'
				'\n'
				"@ Bug:\n"
				'@@ Relates:\n'
				'@@ Blocks:\n'
				"@@ Beschreibung\n"
				#"{beschreibung_template}"
				)

		keywords = re.findall(r'\{([a-z_]+)\}', BUG_HEAD_TEMPLATE)
		valuesMap = {}
		for key in keywords:
			valuesMap[key] = ""
		valuesMap['key'] = issue_key
		settings = sublime.load_settings('JiraWithLime.sublime-settings')
		valuesMap['project'] = settings.get('project', "")
		valuesMap['component'] = settings.get('component', "")
		valuesMap['browser'] = settings.get('browser', "")
		valuesMap['environment'] = settings.get('environment', "")
		valuesMap['domain'] = settings.get('domain', "")
		valuesMap['assignee'] = settings.get('assignee', "")
		
		text = BUG_HEAD_TEMPLATE.format(**valuesMap)

		window.new_file()
		view = window.active_view()
		view.insert(edit, 0, text)

class NewStoryCommand(sublime_plugin.TextCommand):
	def run(self, edit, issue_key=None):
		window = self.view.window()
		STORY_HEAD_TEMPLATE = (
			'@@ Projekt: {project}\n'
			'\n'
			"@@ Version: {version}\n"
			'@@ Komponente: {component}\n'
			'@@ Stichwörter: {lables}\n'
			'@@ Bearbeiter: {assignee}\n'
			'@@ Epic: {epic}\n'
			'@@ Subtask-Parent:\n'
			'\n'
			'@ Story: \n'
			'@@ Kurzbeschreibung\n'
			'\n'
			'@@ Beschreibung\n'
			"{story_description_template}"
			'\n'
			'\n'
			'@ Subtask:\n'
			'@@ Kurzbeschreibung\n'
			'\n'
			'@@ Beschreibung\n'
			'\n'
			)

		keywords = re.findall(r'\{([a-z_]+)\}', STORY_HEAD_TEMPLATE)
		valuesMap = {}
		for key in keywords:
			valuesMap[key] = ""
		valuesMap['key'] = issue_key
		settings = sublime.load_settings('JiraWithLime.sublime-settings')
		valuesMap['story_description_template'] = settings.get('story_description_template', "")
		valuesMap['project'] = settings.get('project', "")
		valuesMap['lables'] = settings.get('story_lables', "")
		valuesMap['component'] = settings.get('component', "")
		valuesMap['assignee'] = settings.get('assignee', "")
		
		text = STORY_HEAD_TEMPLATE.format(**valuesMap)

		window.new_file()
		view = window.active_view()
		view.insert(edit, 0, text)
