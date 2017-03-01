from selenium import webdriver
from time import sleep
import json
import os

class TestFIUSearchPage():
	
	def __init__(self):
		self.driver = webdriver.PhantomJS()
		self.driver.get("https://pslinks.fiu.edu/psc/cslinks/EMPLOYEE/CAMP/c/COMMUNITY_ACCESS.CLASS_SEARCH.GBL&FolderPath=PORTAL_ROOT_OBJECT.HC_CLASS_SEARCH_GBL&IsFolder=false&IgnoreParamTempl=FolderPath,IsFolder")

	def search_request(self, num, pre):
		courseNumber = self.driver.find_element_by_id('SSR_CLSRCH_WRK_CATALOG_NBR$4')
		courseNumber.send_keys(num)
		prefix = self.driver.find_element_by_id('SSR_CLSRCH_WRK_SUBJECT$3')
		prefix.send_keys(pre)
		self.driver.find_element_by_id('CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH').click()
	

	def getCourses(self):
		course = {}
		classSectionsFound = self.driver.find_element_by_xpath('//*[@id="win0divSSR_CLSRSLT_WRK_GROUPBOX1"]/table/tbody/tr[1]/td').text
		self.driver.implicitly_wait(1) #PhantomJS could not find element. Added to allow headless browser time to acquire.
		n = int(classSectionsFound.partition(' ')[0])
		i = 0
		while(i < n):
			outinfo = self.driver.find_element_by_xpath('//*[@id="win0divSSR_CLSRSLT_WRK_GROUPBOX2GP$0"]').text
			course['courseinfo'] = outinfo.replace('\n','')
			classnuminfo = self.driver.find_element_by_xpath('//*[@id="MTG_CLASS_NBR$' + str(i) + '"]').text
			course['classNum'] = classnuminfo.replace('\n','')
			outsection = self.driver.find_element_by_xpath('//*[@id="MTG_CLASSNAME$' + str(i) + '"]').text
			course['section'] = outsection.replace('\n','')
			daysandtimesinfo = self.driver.find_element_by_xpath('//*[@id="MTG_DAYTIME$' + str(i) + '"]').text
			course['daysAndTimes'] = daysandtimesinfo.replace('\n','')
			roominfo = self.driver.find_element_by_xpath('//*[@id="MTG_ROOM$' + str(i) + '"]').text
			course['room'] = roominfo.replace('\n','')
			instructorinfo = self.driver.find_element_by_xpath('//*[@id="MTG_INSTR$' + str(i) + '"]').text
			course['instructor'] = instructorinfo.replace('\n','')
			meetingdatesinfo = self.driver.find_element_by_xpath('//*[@id="MTG_TOPIC$' + str(i) + '"]').text
			course['meetingDates'] = meetingdatesinfo.replace('\n','')
			locationinfo = self.driver.find_element_by_xpath('//*[@id="DERIVED_CLSRCH_DESCR$' + str(i) + '"]').text
			course['location'] = locationinfo.replace('\n','')
			
			self.writeJson(course) #calling method with each course object
			#courses.append(course) removed appending to list
			i = i + 1
			course = {}	
		#return 

	#No longer passing list as parameter. Pass individual course object. Appending to file in this location, instead of appending to list.
	def writeJson(self, aCourse):
		with open('data.json', 'a') as outfile:
			json.dump(aCourse, outfile, sort_keys=True, indent=4)

	def modifySearch(self):
			self.driver.find_element_by_id('CLASS_SRCH_WRK2_SSR_PB_MODIFY').click()

	def clearSearch(self):
			self.driver.find_element_by_id('CLASS_SRCH_WRK2_SSR_PB_CLEAR').click()

	def checkSearch(self):
		if(len(self.driver.find_elements_by_id('DERIVED_CLSMSG_ERROR_TEXT')) > 0):
			return True

	def clearAndSearch(self, num, pre):
			sleep(1)
			self.clearSearch()
			sleep(1)
			self.search_request(num, pre)
			sleep(1)

	#def scrapeAndModifySearch(self, courses):
        def scrapeAndModifySearch(self):
			sleep(1)
			#self.getCourses(courses) removed parameter passed to method
			self.getCourses()
			sleep(1)
			self.modifySearch()
			sleep(1)

	def writeToCourseNumList(self):
		with open('courseNumList.txt') as f:
			courseNums = f.readlines()
		couseNums = [x.strip('\n') for x in courseNums]
		return courseNums

	def writeToCoursePrefixList(self):
		with open('coursePrefixList.txt') as f:
			coursePres = f.readlines()
		coursePres = [x.strip('\n') for x in coursePres]
		return coursePres

	def scrape(self):
		i = 0
		courseNumList = self.writeToCourseNumList()
		coursePrefixList = self.writeToCoursePrefixList()
		open('data.json','w').close()#Erase json at start of script. 		

		while(i < len(courseNumList)):
			self.clearAndSearch(courseNumList[i], coursePrefixList[i])

			if(self.checkSearch() == True):
				i = i + 1
				continue

			#self.scrapeAndModifySearch(courses) removed passing list parameter
			self.scrapeAndModifySearch()
			i = i + 1

			if(i == len(courseNumList)):
				break
		#self.writeJson(courses) removed write to list

