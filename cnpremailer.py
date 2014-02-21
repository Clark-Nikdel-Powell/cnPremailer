import sublime
import sublime_plugin
import urllib.parse
import urllib.request
import json
import threading
import time


class CnpremailerCommand(sublime_plugin.TextCommand):

	def run(self, edit):

		startThread = threading.Thread(target=self.begWork, args=(edit,))
		startThread.start()
		

	def begWork(self, edit):

		print('[' + time.strftime('%X') + '] Starting process...')
		print('[' + time.strftime('%X') + '] Loading data from document...')
		regions = self.getRegions()
		clipboard = ''
		for line in regions:
			clipboard += str(self.view.substr(line))

		print('[' + time.strftime('%X') + '] Getting settings for request...')
		url = 'http://premailer.dialect.ca/api/0.1/documents'
		values = {
			'html' : clipboard,
			'preserve_styles' : 0
		}

		print('[' + time.strftime('%X') + '] Sending request to Premailer...')
		try:
			urlrequest = self.urlreq(url,values,"json")
		except:
			print('[' + time.strftime('%X') + '] No response received. An error has occurred.')
			self.exit(0)

		print('[' + time.strftime('%X') + '] Response received...')
		if urlrequest:

			print('[' + time.strftime('%X') + '] Getting code...')
			try:
				docurl = urlrequest['documents']['html']
				docrequest = self.urlreq(docurl,0,'raw')
			except:
				print('[' + time.strftime('%X') + '] Could not start process. An error has occurred.')
				self.exit(0)

			print('[' + time.strftime('%X') + '] Code recieved...')
			if docrequest:
				print('[' + time.strftime('%X') + '] Loading data...')
				commentline = '<!-- GENERATED FROM PREMAILER.DIALECT.CA !-->'
				sublime.set_clipboard(commentline + '\n' + docrequest)
				print('[' + time.strftime('%X') + '] Data loaded into clipboard successfully.')
			else:
				print('[' + time.strftime('%X') + '] No data was returned to load into the clipboard.')

		else:
			print('[' + time.strftime('%X') + '] No response received from server.')


	def getRegions(self):
		content = sublime.Region(0, self.view.size())
		self.view.add_regions('all', [content], 'string')
		regions = self.view.get_regions('all')
		self.view.erase_regions('all')
		return regions


	def urlreq(self, url, values, action):

		if values:
			data = urllib.parse.urlencode(values)
			data = data.encode('UTF-8')
			req = urllib.request.Request(url, data)
			response = urllib.request.urlopen(req)
		else:
			response = urllib.request.urlopen(url)

		pagereturned = response.read().decode('UTF-8')

		if action=="json":
			jsonData = json.loads(pagereturned)
			return jsonData
		else:
			return pagereturned

class CheckUrlPanel(sublime_plugin.WindowCommand):

	def quick_panel(self, messages, flags):
		self.window.show_quick_panel(messages, None, flags)