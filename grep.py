import sublime, sublime_plugin
import re

class TestGrepCommand(sublime_plugin.TextCommand):
	def run(self, edit, callback):
		window = self.view.window()

		self.view.run_command('select_all')
		text = self.view.substr(self.view.sel()[0])
		self.view.sel().clear()
		lineCollection = list(iter(text.splitlines()))

		self.testValues = []
		self.testNr = -1
		self.stepNr = -1
		self.lineNr = 0

		self.project = ""
		self.assignee = ""
		self.attributes = []
		self.testgroups = []
		self.components = []
		self.labels = []
		self.story = ""
		self.version = ""
		self.description = ""
		self.domain = ""
		self.environment = ""
		self.browser = ""
		self.links = []

		self.resetFlags()
		for line in lineCollection:
			self.lineNr = self.lineNr+1

			found = re.search(r'^@@ Projekt:(.+)', line)
			if found:
				self.project = self.stripSpaces(found.group(1))
				continue
			
			found = re.search(r'^@@ Attribute:(.*)', line)
			if found:
				self.attributes = self.splitAndStrip(found)
				continue
			
			found = re.search(r'^@@ Testgruppen:(.*)', line)
			if found:
				self.testgroups = self.splitAndStrip(found)
				continue
			
			found = re.search(r'^@@ Komponente:(.*)', line)
			if found:
				self.components = self.splitAndStrip(found)
				continue
			
			found = re.search(r'^@@ Stichwörter:(.*)', line)
			if found:
				self.labels = self.splitAndStrip(found)
				continue

			found = re.search(r'^@@ Bearbeiter:(.*)', line)
			if found:
				print("Bearbeiter", line)
				self.assignee = self.stripSpaces(found.group(1))
				continue
			
			found = re.search(r'^@@ Story:(.+)', line)
			if found:
				self.story = self.stripSpaces(found.group(1))
				continue
			
			found = re.search(r'^@@ Version:(.+)', line)
			if found:
				self.version = self.stripSpaces(found.group(1))
				continue
			
			found = re.search(r'^@ Test:(.*)', line)
			if found:
				print("Found", "Test", "in Line", self.lineNr, line)
				self.newTest()
				self.addValue('name', found.group(1))
				self.testValues[self.testNr]['links'].append(['tests', self.story])
				self.testValues[self.testNr]['type'] = "Test"
				self.resetFlags()
				continue			

			found = re.search(r'^@ Bug:(.*)', line)
			if found:
				print("Found", "Bug", "in Line", self.lineNr, line)
				self.newTest()
				self.addValue('name', found.group(1))
				self.testValues[self.testNr]['type'] = "Bug"
				self.resetFlags()
				continue

			found = re.search(r'^@@ Domäne:(.*)', line)
			if found:
				self.domain = self.stripSpaces(found.group(1))
				self.resetFlags()
				continue

			found = re.search(r'^@@ Umgebung:(.*)', line)
			if found:
				self.environment = self.stripSpaces(found.group(1))
				self.resetFlags()
				continue

			found = re.search(r'^@@ Browser:(.*)', line)
			if found:
				self.browser = self.stripSpaces(found.group(1))
				self.resetFlags()
				continue				

			found = re.search(r'^@@ Key:(.*)', line)  
			if found:
				self.testValues[self.testNr]['key'] = self.stripSpaces(found.group(1))
				self.testValues[self.testNr]['keyLineNr'] = self.lineNr
				self.resetFlags()
				continue

			found = re.search(r'^@@ Blocks:(.*)', line)  
			if found:
				#self.links.append(['Blocks', self.stripSpaces(found.group(1))])
				self.testValues[self.testNr]['links'].append(['Blocks', self.stripSpaces(found.group(1))])
				self.resetFlags()
				continue			

			found = re.search(r'^@@ Relates:(.*)', line)  
			if found:
				#self.links.append(['Relates', self.stripSpaces(found.group(1))])
				self.testValues[self.testNr]['links'].append(['Relates', self.stripSpaces(found.group(1))])
				self.resetFlags()
				continue

			found = re.search(r'^@@ Beschreibung:*(.*)', line) #  
			if found:
				print("Found", "Beschreibung", "in Line", self.lineNr)
				self.description = found.group(1)
				self.testValues[self.testNr]['description'] = ""
				self.addValue('description', found.group(1))
				self.resetFlags()
				self.description_flag = True
				continue

			found = re.search(r'^----$', line)
			if found:
				self.newStep()
				self.resetFlags()
				self.step_flag = True
				continue

			found = re.search(r'(.*)->(.*)', line)
			if found and self.step_flag:
				self.addValue('steps', found.group(1))
				self.addValue('result', found.group(2))
				self.resetFlags()
				self.result_flag = True
				continue

			if self.description_flag:
				self.addValue('description', line)
				self.description += '  \n'
				self.description += line
				continue
			if self.step_flag:
				self.addValue('steps', line)
				continue
			if self.result_flag:
				self.addValue('result', line)
				continue
			if self.data_flag:
				self.addValue('data', line)
				continue

		window.run_command(callback, {'testValues': self.testValues})

	def newTest(self):
		self.testNr = self.testNr+1
		self.stepNr = -1
		self.testValues.append({
				'project' : self.project,
				'assignee' : self.assignee,
				'attributes' : self.attributes,
				'testgroups' : self.testgroups,
				'components' : self.components,
				'labels' : self.labels,
				'story' : self.story,
				'version' : self.version,
				'name' : "",
				'description' : self.description,
				'steps' : [],
				'result' : [],
				'data' : [],
				'testLineNr' : self.lineNr,
				'keyLineNr' : -1,
				'key' : '',
				'type' : '',
				'domain' : self.domain,
				'environment' : self.environment,
				'browser' : self.browser,
				'links' : []
				})

	def newStep(self):
		print("Add New Test Step")
		self.stepNr = self.stepNr+1
		self.testValues[self.testNr]['steps'].append("")
		self.testValues[self.testNr]['result'].append("")
		self.testValues[self.testNr]['data'].append("")

	def addValue(self, vtype, value):
		print("Add Value", "vtype", vtype, "value", value)
		value = self.stripSpaces(value)
		if type(self.testValues[self.testNr][vtype]) == list:
			if self.testValues[self.testNr][vtype][self.stepNr] != '':
				self.testValues[self.testNr][vtype][self.stepNr] += '  \n'
			self.testValues[self.testNr][vtype][self.stepNr] += value
		else:
			if self.testValues[self.testNr][vtype] != '':
				self.testValues[self.testNr][vtype] += '  \n'
			self.testValues[self.testNr][vtype] += value

	def resetFlags(self):
		self.test_flag = False
		self.key_flag = False
		self.description_flag = False
		self.step_flag = False
		self.result_flag = False
		self.data_flag = False

	def stripSpaces(self, value):
		while len(value) > 0 and (value[0] == ' ' or value[0] == '\t' or value[0] == '\n'):
			value = value[1:]
		while len(value) > 0 and (value[-1] == ' ' or value[-1] == '\t' or value[-1] == '\n'):
			value = value[:-1]
		return value

	def splitAndStrip(self, matchObj):
		vals = matchObj.group(1).split(',')
		for i in range(len(vals)):
			vals[i] = self.stripSpaces(vals[i])
		return vals