# -*- coding:utf-8 -*-

import tornado.ioloop
import tornado.web
import os.path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep

PreferredBrowser = "PhantomJS"
maxPages = 5
TaskQueue = []

class BrowserTask(object):
	"""Automated task within Browser"""

	taskStatus = {
		1: u'信息填充,等待扫描',
		2: u'扫描完成，等待目标确认'，
		3：u'目标确认，等待浏览'，
		4：u'浏览完成，等待付款(已结束)',
		5: u'任务取消'
	}
	def __init__(self, keyword, shopname, browser = None, login = None, password = None, **kwargs):
		self.scan_info = {}
		self.scan_info['keyword'] = keyword
		self.scan_info['shopname'] = shopname
		for k,v = kwargs.item():
			self.scan_info[k] = v

		if not browser:
			self.browser = PreferredBrowser

		self.login = { "username": login, "password": password }
		self.driver = None #lazy init
		self.isLogged = False #lazy init
		self.status = 1

	def login(self):
		if not self.driver:
			self.driver = getattr(webdriver,self.browser)()
			self.driver.maximize_window()
			self.driver.get("http://www.taobao.com")
			# just make sure all javascript init work has completed
			self.driver.execute_script('window.scrollTo(0,document.body.scrollHight)')

		if not self.isLogged:

			if self.login['username'] and self.login['password']:
				login = self.driver.find_element_by_css_selector('a.h')
				login.click()
				username = self.driver.find_element_by_css_selector('input[type="text"]')
				username.send_keys(self.login['username'])
				safeLogin = self.driver.find_element_by_css_selector('input[type="checkbox"]')
				import pdb;pdb.set_trace()
				if safeLogin.get_attribute('checked'):
					safeLogin.click()

				password = self.driver.find_element_by_css_selector('input[type="password"]')
				password.send_keys(self.login['password'])

				submit = driver.find_element_by_css_selector('button[type="submit"]')
				submit.click()
				driver.find_element_by_css_selector('li.tmsg') #confirm login

		self.isLogged = True

	def scan(self):
		if not self.isLogged:
			self.login()

		current_url = self.driver.current_url
		query = driver.find_element_by_css_selector("#q")
		query.send_keys(self.scan_info['keyword'] + Keys.RETURN)

		while(True):
			if self.driver.current_url == current_url:
				sleep(1)
			else:
				break

		self.status = 2

	def identify(self,id):
		self.status = 3

	def browse(self):
		self.status = 4

	def cancel(self):
		self.status = 5

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')


class TaskHandler(tornado.web.RequestHandler):
    def get(self):
    	''' get task infromation'''

    def post(self):
    	''' cancel a task '''


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')

application = tornado.web.Application(
	handlers = [
    	(r"/", MainHandler),
    	(r"/tasks/",TaskHandler)
    	(r"/cancel/",CancelTaskHandler)
    	(r"/scan/",ScanHandler),
    	(r"/browse/",BrowseHandler) ],
    settings = {
    	"template_path": os.path.join(os.path.dirname(__file__), ”templates”),
    	"static_path":os.path.join(os.path.dirname(__file__), ”static”) }
)

if __name__ == "__main__":
    application.listen(80)
    tornado.ioloop.IOLoop.instance().start()
