# -*- coding:utf-8 -*-
import selenium 
import selenium.common.exceptions
import tornado.ioloop
import tornado.web
import os.path
import sys     

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from time import sleep
from random import random,randint
from selenium.webdriver.common.action_chains import ActionChains
from tornado.options import define, options

if sys.getdefaultencoding != 'utf-8': 
	reload(sys) 
	sys.setdefaultencoding('utf-8')

define("port", default="8080", help="Server Port")

PreferredBrowser = u"PhantomJS"
maxPages = 5
TaskQueue = []

def scrollWindow(to='bottom',steps=5):
	print "scrolling!" 
	# import pdb;pdb.set_trace()
	if to == 'bottom':
		for x in xrange(1,steps+1):
			# js = "window.scrollTo(0, (( document.body.scrollHeight - document.body.clientHeight ) / %d ) * %d); " % (steps, x)
			js = u"window.scrollTo(0, (( document.body.scrollHeight) / %d ) * %d); " % (steps, x)
			print "#%d times scroll:%s" % (x,js)
			browser.execute_script(js)
			sleep (randint(1,3))

	elif to == 'middle':
		for x in xrange(1,steps / 2 + 1):
			# js = "window.scrollTo(0, (( document.body.scrollHeight - document.body.clientHeight ) /  %d) * %d); " % (steps, x)
			js = "window.scrollTo(0, (( document.body.scrollHeight )  /  %d) * %d); " % (steps, x)
			browser.execute_script(js)
			sleep (randint(1,3))
	else:
		browser.execute_script('window.scrollTo(0, 0);')
	print "scrolling done!"

class BuyItem:
	'''Every Item for buyer to check'''
	selectors = {
		'address' : (['.pic a'],'href'),
		'pic' : (['.pic img'],'src'),
		'price' : (['.price strong'],'innerHTML'),
		'title' : (['.summary a','.title a'],'text'),
		'shop_name' : (['.seller a','.shop a'],'href'),
		'shop_loc' : (['.row .loc','.row .location'],'innerHTML')
	}
	
	def select(self,webelement, key):
		method = BuyItem.selectors[key][1]
		for selector in BuyItem.selectors[key][0]:
			values = webelement.find_elements_by_css_selector(selector)
			if len(values) != 0:
				value = values[0]
				index = BuyItem.selectors[key][0].index(selector)
				if index != 0:
					print "Switching selectors for %s" % key
					BuyItem.selectors[key][0][index] = BuyItem.selectors[key][0][0]
					BuyItem.selectors[key][0][0] = selector
				# print value.get_attribute('outerHTML')
				if method == 'text':
					return value.text
				else:
					return value.get_attribute(method)
		return None

	def __init__(self,webelement):

		self.webelement = webelement	
		self.address = self.select(webelement,'address')
		self.pic = self.select(webelement,'pic')
		self.price = self.select(webelement,'price')
		self.title = self.select(webelement,'title')
		self.shop_name = self.select(webelement,'shop_name')
		self.shop_address = self.select(webelement,'shop_name')
		self.shop_loc = self.select(webelement,'shop_loc')

		# self.address = webelement.find_element_by_css_selector('.pic a').get_attribute('href')
		# self.pic = webelement.find_element_by_css_selector('.pic img').get_attribute('src')
		# self.price = webelement.find_element_by_css_selector('.price strong').text
		# for selector in ('.summary a','.title a'):
		# 	titles = webelement.find_elements_by_css_selector(selector)
		# 	if len(titles) != 0:
		# 		self.title = titles[0].text
		# 		break

		# for selector in ('.seller a','.shop a'):
		# 	shopnames = webelement.find_elements_by_css_selector(selector)
		# 	if len(shopnames) != 0:
		# 		self.shop_name = shopnames[0].text
		# 		self.shop_address = shopnames[0].get_attribute('href')
		# 		break

		# for selector in ('.row .loc','.row .location'):
		# 	shoplocs = webelement.find_elements_by_css_selector(selector)
		# 	if len(shoplocs) != 0:
		# 		self.shop_loc = shoplocs[0].text
		# 		break

	def __str__(self):
		# print "shop_loc: %s, title: %s" % (self.shop_loc, self.title)
		str = u"\n".join([ "%s = %s" % (k,v) for k,v in vars(self).items() if k != 'webelement'])
		# import pdb;pdb.set_trace()
		return str

	def isfloat(self,value):
		try:
			float(value)
			return True
		except ValueError:
			return False

	def match(self, **kwargs):
		for k,v in kwargs.items():
			value = getattr(self,k,None)
			if not value:
				return False
			if self.isfloat(v):
				if float(v) != float(value):
					return False
			else:
				if value.find(v) < 0:
					return False

		return True

class BrowserTask(object):
	"""Automated task within Browser"""

	taskStatus = {
		1: u'信息填充,等待扫描',
		2: u'扫描完成，等待目标确认',
		3: u'目标确认，等待浏览',
		4: u'浏览完成，等待付款(已结束)',
		5: u'任务取消'
	}

	def __init__(self, keyword, shopname, browser = None, login = None, password = None, **kwargs):
		self.scan_info = {}
		self.scan_info['keyword'] = keyword
		self.scan_info['shopname'] = shopname
		for k,v in kwargs.items():
			self.scan_info[k] = v

		if not browser:
			self.browser = PreferredBrowser

		self.login = { "username": login, "password": password }
		self.driver = None #lazy init
		self.isLogged = False #lazy init
		self.status = 1

	def login(self):
		if not self.driver:
			# self.driver = getattr(webdriver,self.browser)()
			usedBrowser = self.browser

			if usedBrowser == u'Firefox':
				firefoxProfile =  FirefoxProfile()    
				firefoxProfile.set_preference("self.driver.privatebrowsing.autostart", True)
				self.driver = selenium.webdriver.Firefox(firefoxProfile)
				self.driver.maximize_window()
			elif usedBrowser == u'Ie':
				self.driver = selenium.webdriver.Ie()
			elif usedBrowser == u'Chrome':
				#self.driver = selenium.webdriver.Chrome(chrome_options = '--start-maximized')
				self.driver = selenium.webdriver.Chrome()
			elif usedBrowser == u'PhantomJS':
				self.driver = selenium.webdriver.PhantomJS()
				
			self.driver.implicitly_wait(1)
			self.driver.set_page_load_timeout(30)

			self.driver.maximize_window()

			try:
				self.driver.get('http://www.taobao.com')
			except selenium.common.exceptions.TimeoutException as e:
				print "Exception: ",e
				self.driver.quit()

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

		self.itemsFound = {}
		self.itemsToBrowse = {}

		currentLocation = self.driver.current_url
		while(True):
			queries = self.driver.find_elements_by_css_selector("#q")
			if len(queries) == 0:
				sleep(1)
			else:
				query = queries[0]
				query.send_keys(keyWord + Keys.RETURN)
				break

		while(True):
			if self.driver.current_url == currentLocation:
				print "Loading in progress..."
				sleep(1)
			else:
				currentLocation = self.driver.current_url
				break

		browser = self.driver
		count = 1
		while(True):
			scrollWindow()
			rightPage = 0
			while(not rightPage):
				page = None
				for selector in ("span.page-cur","li.active span.num"):
					pages = browser.find_elements_by_css_selector(selector)
					if len(pages) == 1:
						page = pages[0].text
						break
				#import pdb;pdb.set_trace(find_element_by_partial_link_text)
				if page and int(page) == count:
					rightPage = 1	
				else:
					print "waiting for loading to complete..."
					sleep(1)

			nextBtn = None
			for selector in ('li.next a', u'a[title="下一页"]'):
				print "Trying to locate nextBtn with: %s!" % selector
				nextBtns = browser.find_elements_by_css_selector(selector)
				if len(nextBtns) != 0:
					nextBtn = nextBtns[0]
					print "nextBtn is :%s" % nextBtn.get_attribute('href')
					break

			if not nextBtn:
				print "Didn't find nextBtn!!!"
				browser.quit()

			# browser.save_screenshot("snapshot_%d.png" % count)
			self.itemsToBrowse[count] = []

			cnt = 1
			for selector in ('div.tb-content div.item', 'div.m-itemlist div.item'):
				itemElements = browser.find_elements_by_css_selector(selector)
				if len(itemElements) != 0:
					print "Trying to browse %d items..." % len(itemElements)
					# itemElements = []
					for itemElement in itemElements:
						print "item #%d " % cnt
						cnt = cnt + 1
						item = BuyItem(itemElement)
						#import pdb;pdb.set_trace()
						#print "price: %s, shop_name: %s" % (item.price,item.shop_name)
						print item

						if item.match(price = itemPrice, shop_name = shopName):
							itemsFound[item.id] = (item, count)
						else:
							self.itemsToBrowse[count].append(itemElement)
					break

			if count >= maxPages:
				break

			print "Current selectors: ", BuyItem.selectors

			count = count + 1
			print "Trying next page : %d" % count
			# nextBtn.click()
			ac = ActionChains(browser)
			ac.click_and_hold(nextBtn).perform()
			ac.release(nextBtn).perform()
			while (True):
				if currentLocation == browser.current_url:
					print "Loading in progress..."
					sleep(1)
				else:
					currentLocation = browser.current_url
					break

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
		pass

application = tornado.web.Application([(r"/", MainHandler),
		(r"/tasks/",TaskHandler) ],
		template_path =  os.path.join(os.path.dirname(__file__), "templates"),
		static_path = os.path.join(os.path.dirname(__file__), "static") 
	)

if __name__ == "__main__":
	tornado.options.parse_command_line()
	application.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()
