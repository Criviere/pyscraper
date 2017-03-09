from selenium import webdriver
from elasticsearch import Elasticsearch
from time import sleep
import os

class TestFIUSearchPage():

	def __init__(self):
		self.driver = webdriver.Firefox()
		self.driver.get("https://pslinks.fiu.edu/psc/cslinks/EMPLOYEE/CAMP/c/COMMUNITY_ACCESS.CLASS_SEARCH.GBL&FolderPath=PORTAL_ROOT_OBJECT.HC_CLASS_SEARCH_GBL&IsFolder=false&IgnoreParamTempl=FolderPath,IsFolder")

	def search_request(self, num, pre):
		courseNumber = self.driver.find_element_by_id('SSR_CLSRCH_WRK_CATALOG_NBR$4')
		courseNumber.send_keys(num)
		prefix = self.driver.find_element_by_id('SSR_CLSRCH_WRK_SUBJECT$3')
		prefix.send_keys(pre)
		self.driver.find_element_by_id('CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH').click()

	def getCourses(self, courses, INDEX_N, TYPE_N):
		
		course = {}
		classSectionsFound = self.driver.find_element_by_xpath('//*[@id="win0divSSR_CLSRSLT_WRK_GROUPBOX1"]/table/tbody/tr[1]/td').text
		n = int(classSectionsFound.partition(' ')[0])
		i = 0
		while(i < n):
			outinfo = self.driver.find_element_by_xpath('//*[@id="win0divSSR_CLSRSLT_WRK_GROUPBOX2GP$0"]').text
			course['courseinfo'] = outinfo.replace('\n',' ')
			classnuminfo = self.driver.find_element_by_xpath('//*[@id="MTG_CLASS_NBR$' + str(i) + '"]').text
			course['classNum'] = classnuminfo.replace('\n',' ')
			outsection = self.driver.find_element_by_xpath('//*[@id="MTG_CLASSNAME$' + str(i) + '"]').text
			course['section'] = outsection.replace('\n',' ')
			daysandtimesinfo = self.driver.find_element_by_xpath('//*[@id="MTG_DAYTIME$' + str(i) + '"]').text
			course['daysAndTimes'] = daysandtimesinfo.replace('\n',' ')
			roominfo = self.driver.find_element_by_xpath('//*[@id="MTG_ROOM$' + str(i) + '"]').text
			
			course['room'] = roominfo.replace('\n',' ')
			instructorinfo = self.driver.find_element_by_xpath('//*[@id="MTG_INSTR$' + str(i) + '"]').text
			course['instructor'] = instructorinfo.replace('\n',' ')
			meetingdatesinfo = self.driver.find_element_by_xpath('//*[@id="MTG_TOPIC$' + str(i) + '"]').text
			course['meetingDates'] = meetingdatesinfo.replace('\n',' ')
			locationinfo = self.driver.find_element_by_xpath('//*[@id="DERIVED_CLSRCH_DESCR$' + str(i) + '"]').text
			course['location'] = locationinfo.replace('\n',' ')
			
			#Unique identifier of each course created within loop. Each loop
			#will create a new identifier for each unique course within a set 
			#of similar courses
			ID_FIELD = 'classNum'
			op_dict = {
				"index": {
					"_index": INDEX_N,
					"_type": TYPE_N,
					"_id": course[ID_FIELD]
				}
			}
			courses.append(op_dict) #added
			courses.append(course)
			i = i + 1
			course = {}
	
		return courses

	
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
	
	#Added parameters needed to build dict objects
	def scrapeAndModifySearch(self, courses, esindex, estypename):
			sleep(1)
			self.getCourses(courses, esindex, estypename)
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
		courses = []

		#elasticsearch host variable	
		ES_HOST = { 
			"host" : "localhost", #added
			"port" : 9200 #added
		}
		INDEX_NAME = 'cscourses' #added
		TYPE_NAME = 'somecscourse' #added


		while(i < len(courseNumList)):
			self.clearAndSearch(courseNumList[i], coursePrefixList[i])

			if(self.checkSearch() == True):
				i = i + 1
				continue
			#Added index information as parameter to build dict objects
			self.scrapeAndModifySearch(courses, INDEX_NAME, TYPE_NAME)
			i = i + 1

			if(i == len(courseNumList)):
				break

		#While loop returns a list of dict objects that will be bulk indexed
		#into a newly created index

		#create ES clinet and index
		esearch = Elasticsearch(hosts = [ES_HOST])
		
		#Replace exisiting index
		if esearch.indices.exists(INDEX_NAME):
			print "deleting %s index..." % INDEX_NAME
			res = esearch.indices.delete(index = INDEX_NAME)
			print "response: %s" % res 
		
		#Number of indices
		request_body = {
			"settings" : {
				"number_of_shards" : 1,
				"number_of_replicas" : 0
			}
		}

		#create index
		print "creating %s index..." % INDEX_NAME
		res = esearch.indices.create(index = INDEX_NAME, body = request_body)
		print "response %s" % res

		#bulk index
		print "bulk indexing..."
		res = esearch.bulk(index = INDEX_NAME, body = courses, refresh = True)

		
