from . import markdown2
import re

class MyMarkdownParser():

	def build_markdown(self, text):
		textArray = text.split('\n')
		textArray = self.build_tables(textArray)
		# textArray = self.build_headlines(textArray)
		text = self.build_processed_text(textArray)
		return markdown2.markdown(text)

	def build_tables(self, textArray):

		# Headline				| Headline1 | Headline2   |
		# Markline (Allignment)	| --------- | :---------: |
		# Bode 					| text      |             |

		found_headline = False
		found_allignment = False
		headlines = []
		allignment = []
		# text = text.split('\n')
		i = 0
		for line in textArray:
			isTable = re.search(r'^\|.*', line)
			if isTable:
				#content = re.findall(r'\|\s*([a-zA-Z0-9]*)\s*', l)
				content = line.split('|')
				content = content[1:] # Ignore first
				content = content[:-1] # Ignore last
				if not found_headline:
					found_headline = True
					self.headlines = content
					columns = len(content)
				elif not found_allignment:
					found_allignment = True
					allignment = []
					line = line.replace(" ", "")
					for s in content:
						if s.startswith(':') and s.endswith(':'):
							allignment.append('text-align:center;')
						elif s.startswith(':'):
							allignment.append('text-align:left;')
						elif s.endswith(':'):
							allignment.append('text-align:right;')
						else:
							allignment.append('')
					textArray[i]=''
					p = ''
					if i-2 > 0 and textArray[i-2].strip() != '':
						textArray[i-2] = '<p>'+textArray[i-2]
					else:
						p = '<p>'				

					textArray[i-1] = p+'<table style="border-collapse:collapse;"><thead><tr>'
					for h in range(len(self.headlines)):
						textArray[i-1]+='<th style="border: 1px solid #ccc; padding: 6px 13px;%s">%s</th>'%(allignment[h], self.headlines[h]) 
					textArray[i-1]+= '</tr></thead><tbody>'
				else:
					textArray[i] = '<tr>'
					for s in range(len(content)):
						textArray[i]+='<td style="background-color: #fff; border: 1px solid #ccc; padding: 6px 13px;%s">%s</td>'%(allignment[s], content[s])
					textArray[i]+= '</tr>'
			elif found_headline:
				textArray[i-1]+='</tbody></table></p>'
				found_headline = False
				found_allignment = False
				headlines = []
				allignment = []
			i=i+1
		return textArray

	def build_headlines(self, textArray):
		i=0
		for line in textArray:
			isHeadline = re.search(r'^#.*', line)
			if isHeadline:
				h = 0
				for s in line:
					if s == "#":
						h=h+1
				print("textArray", textArray)
				textArray[i] = textArray[i][h:]
				textArray[i] = "<h"+str(h)+">"+textArray[i]+"</h"+str(h)+">"
			i=i+1
		return textArray 

	def build_processed_text(self, text):
		processed_text = ''
		for line in text:
			line_w_break = line+' \n'
			processed_text+=line_w_break
		return processed_text