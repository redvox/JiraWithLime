import sublime, sublime_plugin
import webbrowser
import re

class OpenInBrowserCommand(sublime_plugin.TextCommand):
	def run(self, edit, issue_key=None):
		window = self.view.window()
		if not issue_key:
			region = self.view.sel()
			selection = self.view.substr(region[0])
			found = re.search(r'[a-zA-Z0-9]{4}-[0-9]{4}', selection)
			if found:
				window.run_command('open_in_browser',
			                	{'issue_key': selection})
			else:
				window.run_command('prompt_issue_key',
			                	{'callback': 'open_in_browser'})
		else:
			settings = sublime.load_settings('JiraWithLime.sublime-settings')
			if type(issue_key) != list:

				webbrowser.open(settings.get('baseURL')+"/browse/"+issue_key, 2) 
			else:
				for i in issue_key:
					print('i', i)
					webbrowser.open(settings.get('baseURL')+"/browse/"+i, 2) 

class OpenAllTestsInBrowserCommand(sublime_plugin.TextCommand):
	def run(self, edit, testValues=None):
		window = self.view.window()
		if testValues == None:
			window.run_command('test_grep', {'callback': 'open_all_tests_in_browser'})
		else:
			issue_keys = []
			for t in testValues:
				if t['key'] != '':
					issue_keys.append(t['key'])
			window.run_command('open_in_browser', {'issue_key': issue_keys})

class OpenTestCycleInBrowserCommand(sublime_plugin.TextCommand):
	pass