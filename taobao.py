# -*- coding:utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

keyWord = u'取暖�?
#itemPrice = u'429.00'
itemPrice = u'298.00'
#shopName = u'艾美�?
shopName = u'星月'
maxPages = 5

driver = webdriver.Ie()
driver.maximize_window()
driver.get("http://www.taobao.com")

query = driver.find_element_by_css_selector("#q")
query.send_keys(keyWord + Keys.RETURN)

def isfloat(value):
	try:
		float(value)
		return True
	except ValueError:
		return False

itemsFound = []
itemsToBrowse = []
count = 1
while(count < maxPages):
	js_scroll = '''
		document.body.scrollTop=0;
		//alert(document.body.clientHeight);
		count = document.body.scrollHeight/ 100;
		for (var i=0; i <= count+1; i++)
		{
			document.body.scrollTop = 100 * i
			//sleep(1000)
		}
		//document.body.scrollTop=0
'''
	driver.execute_script(js_scroll)
	nextBtn = None
	for btn in driver.find_elements_by_css_selector('div.page-wrap a'):
		if btn.get_attribute('title') == u'下一�?:
			print "Found nextBtn: %s" % btn.get_attribute('href')
			nextBtn = btn
	if not nextBtn:
		print "Didn't find nextBtn!!!"
		break	

	page = driver.find_element_by_css_selector("span.page-cur").text
	#import pdb;pdb.set_trace()
	if int(page) != count:
		print "Next page didn't happen,trying again!!!"
		nextBtn.click()

	for itemElement in driver.find_elements_by_css_selector("div.tb-content div.item"):
		price = itemElement.find_element_by_css_selector("div.price strong").text
		shop_name = itemElement.find_element_by_css_selector("div.seller a").text
		print "price: %s, shop_name: %s" % (price,shop_name)

		if price == itemPrice and shop_name.find(shopName) >= 0:
			itemsFound.append(itemElement)
		else:
			itemsToBrowse.append(itemElement)
	
	count = count + 1
	print "Trying next page : %d" % count
	nextBtn.click()

if len(itemsFound) == 1:
	currentItem = itemsFound[0].find_element_by_css_selector(".summary a")
	print "itemFound: %s" % currentItem.get_attribute('href')
	currentItem.click()
else:
	print "I found %d matching items in total" % len(itemsFound)
	for item in itemsFound:
		currentItem = itemsFound[0].find_element_by_css_selector(".summary a")
		print "itemFound: %s" % currentItem.get_attribute('href')

