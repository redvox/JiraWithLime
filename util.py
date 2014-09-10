import sublime, sublime_plugin
from JiraWithLime.lime_connection import LimeConnection

class Util():
	@staticmethod
	def findVersionId(projectID, name): #10905
		versionId = -1
		connection = LimeConnection()
		response, data = connection.getAllVersionsOfProject(projectID)
		for v in data['unreleasedVersions']:
			if v['label'] == name:
				versionId = v['value']
				break
		for v in data['releasedVersions']:
			if v['label'] == name:
				versionId = v['value']
				break
		if versionId == -1:
			sublime.error_message("Could not find Version "+name)
			raise Exception("Could not find Version")
		return versionId