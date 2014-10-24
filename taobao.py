# -*- coding:utf-8 -*-

from time import sleep
import selenium 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
import selenium.common.exceptions
from time import sleep
from random import random,randint
from selenium.webdriver.common.action_chains import ActionChains

import sys     
if sys.getdefaultencoding != 'utf-8': 
	reload(sys) 
	sys.setdefaultencoding('utf-8')

keyWord = u'取暖器'
itemPrice = u'138.00'
shopName = u'英蓝电器'
maxPages = 3
usedBrowser = u'PhantomJS'

def scrollWindow(to='bottom',steps=5):
	print "scrolling!" 
	# import pdb;pdb.set_trace()
	if to == 'bottom':
		for x in xrange(1,steps+1):
			# js = "window.scrollTo(0, (( document.body.scrollHeight - document.body.clientHeight ) / %d ) * %d); " % (steps, x)
			js = "window.scrollTo(0, (( document.body.scrollHeight) / %d ) * %d); " % (steps, x)
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

print "Started!"

if usedBrowser == u'Firefox':
	firefoxProfile =  FirefoxProfile()    
	firefoxProfile.set_preference("browser.privatebrowsing.autostart", True)
	browser = selenium.webdriver.Firefox(firefoxProfile)
	browser.maximize_window()
elif usedBrowser == u'Ie':
	browser = selenium.webdriver.Ie()
elif usedBrowser == u'Chrome':
	#browser = selenium.webdriver.Chrome(chrome_options = '--start-maximized')
	browser = selenium.webdriver.Chrome()
elif usedBrowser == u'PhantomJS':
	browser = selenium.webdriver.PhantomJS()
	
browser.implicitly_wait(1)
browser.set_page_load_timeout(30)

try:
	browser.get('http://www.taobao.com')
except selenium.common.exceptions.TimeoutException as e:
	print "Exception: ",e
	browser.quit()

currentLocation = browser.current_url
while(True):
	queries = browser.find_elements_by_css_selector("#q")
	if len(queries) == 0:
		sleep(1)
	else:
		query = queries[0]
		query.send_keys(keyWord + Keys.RETURN)
		break

# import pdb;pdb.set_trace()

while(True):
	if browser.current_url == currentLocation:
		print "Loading in progress..."
		sleep(1)
	else:
		currentLocation = browser.current_url
		break

itemsFound = { }
itemsToBrowse = { }
count = 1
while(True):
# 	js_scroll = '''
# 	// body...
# 	document.body.scrollTop=0;
# 	// alert("clientHeight is :" + document.body.clientHeight + ", scrollHeight is :" + document.body.scrollHeight);
# 	count = document.body.scrollHeight / 100;
# 	for (var i=0; i <= count; i++)
# 	{
# 		document.body.scrollTop = 100 * i
# 		//sleep(1000)
# 	}
# '''
# 	browser.execute_script(js_scroll)


	# sorts = browser.find_elements_by_partial_link_text(u'综合排序')
	# if len(sorts) == 0:
	# 	print "Search failed!!!"
	# 	browser.quit()

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
	for selector in ('li.next a','a[title="下一页"]'):
		print "Trying to locate nextBtn with: %s!" % selector
		nextBtns = browser.find_elements_by_css_selector(selector)
		if len(nextBtns) != 0:
			nextBtn = nextBtns[0]
			print "nextBtn is :%s" % nextBtn.get_attribute('href')
			break

	if not nextBtn:
		print "Didn't find nextBtn!!!"
		browser.quit()

	browser.save_screenshot("snapshot_%d.png" % count)

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
					itemsFound[item.id] = 
				else:
					itemsToBrowse.append(itemElement)
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

print "Items found : %d" % len(itemsFound)
print "Bye!"