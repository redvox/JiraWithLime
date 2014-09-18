from . import requests
import zipfile
import re

class Update():

	def __init__(self, path, raw_version_url, repo_url):
		self.path = path
		self.repo_url = repo_url
		self.raw_version_url = raw_version_url

	def checkForUpdate(self):
		print("Test for Update")
		f = open(self.path+'version.txt', 'r')
		self.current_Version = f.read()

		response = requests.get(self.raw_version_url+'version.txt', stream=True)
		self.online_version = response.text

		print("current_Version", self.current_Version, "online_version", self.online_version)

		if self.current_Version != self.online_version:
			print("Up-Date available.")
			return True
		else:
			print("Your version is Up-To-Date")
			return False

	def update(self):
		response = requests.get(self.repo_url+self.online_version+'.zip', stream=True)
		print("Update response", response.status_code, self.repo_url+self.online_version+'.zip')
		if response.status_code == 200:
			with open(self.path+'update.zip', 'wb') as f:
				for chunk in response.iter_content():
					f.write(chunk)

			fh = open(self.path+'update.zip', 'rb')
			z = zipfile.ZipFile(fh)
			package_name_length = len(z.namelist()[0])
			print("z.namelist()", z.namelist())
			for name in z.namelist():
				local_name = name[package_name_length:]
				directory = re.search(r'.*/$', name)
				directory_requests = re.search(r'./requests/.', name)
				print(found)
				if name != 'JiraWithLime.sublime-settings' and local_name != '' and not directory and not directory_requests:
					print('name', name)
					print('local_name', local_name)
			
					data = z.read(name)
			
					# myfile = open(self.path+local_name, "wb")
					# myfile.write(data)
					# myfile.close()
			fh.close()