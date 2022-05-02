from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time, os, json, tempfile

import requests
from requests.structures import CaseInsensitiveDict

class FujiWrapperv2:
	def __init__(self, url):
		fuji_api = "http://localhost:1071/fuji/api/v1/evaluate"
		headers = CaseInsensitiveDict()
		headers["accept"] = "application/json"
		headers["Authorization"] = "Basic bWFydmVsOndvbmRlcndvbWFu"
		headers["Content-Type"] = "application/json"

		data = ('{'
      			'"metadata_service_endpoint": "http://ws.pangaea.de/oai/provider",'
				'"metadata_service_type": "oai_pmh",'
    			f'"object_identifier": \"{url}\",'
    			'"test_debug": true,'
       			'"use_datacite": true'
				"}")
  

		resp = requests.post(fuji_api, headers=headers, data=data)
		self.raw_output = resp.json()
		self.output = {}
		self.__unify_output()

	def __reformat_principle_id(self, result):
		"""
  		In Fuji output the principle identifier is something like FsF-F1-01D
		This function refactor that into a stardard representation like F1.1
		"""
		principle = result["metric_identifier"]
		# remove FSF-
		principle = principle.replace("FsF-", "")
		# remove M or D 
		principle = principle.replace("M", "")
		principle = principle.replace("D", "")
		# remove the 0 from 0X
		principle = principle.replace("0", "")
  		# use . instead of -
		principle = principle.replace("-", ".")
		return principle

	def __set_category(self, principle):
		char = principle[0]
		if   char == 'F':
			return "Findable"
		elif char == 'A':
			return "Accessible"
		elif char == 'I':
			return "Interoperable"
		else:
			return "Reusable"
   		
	def __calculate_tests_and_status(self, result):
		tests = result["metric_tests"]
		passed, total = 0, len(tests)
		for test in tests:
			passed += 1 if result["metric_tests"][test]["metric_test_status"] == "pass" else 0
		return "ok" if passed == total else "error", passed, total
  
	def __get_explanation(self, result):
		tests = result["metric_tests"]
		output = []
		for test in tests:
			output.append(f"{result['metric_tests'][test]['metric_test_status'].upper()}: {result['metric_tests'][test]['metric_test_name']}")
		return output

	def __unify_output(self):
		raw = self.raw_output
		self.output["identifier"] = raw["request"]["object_identifier"]
		self.output["checks"] = []
  
		for result in raw["results"]:
			check = {}
			check["principle_id"] = self.__reformat_principle_id(result)
			check["category_id"] = self.__set_category(check["principle_id"])
			check["status"], check["total_passed_tests"], check["total_tests_run"] = self.__calculate_tests_and_status(result)
			check["title"] = result["metric_name"]
			check["explanation"] = self.__get_explanation(result)
			# check["description"] = ""
			self.output["checks"].append(check)
	

	def get_checks(self):
		return self.output["checks"]

	def get_identifier(self):
		return self.output["identifier"]
    
	
    
class FujiWrapper:

	def __init__(self):
		self.driver = self.__setupDriver()

	def __setupDriver(self):
		chrome_options = webdriver.ChromeOptions()

		chrome_options.add_argument("--disable-extensions")
		chrome_options.add_argument("--disable-gpu")
		chrome_options.add_argument("--no-sandbox") # linux only
		# chrome_options.add_argument("--headless")
		chrome_options.add_argument("--start-maximized")
		prefs = {"download.default_directory": tempfile.gettempdir()}
		chrome_options.add_experimental_option("prefs", prefs)

		# Provide the path of chromedriver present on your system.
		driver = webdriver.Chrome(executable_path=r"C:/chromedriver.exe",
								  chrome_options=chrome_options)
		# driver.minimize_window()
		return driver

	# method to get the downloaded file name
	def __getDownLoadedFileName(self):
		# navigate to chrome downloads
		self.driver.get('chrome://downloads')
		# return the file name
		name = self.driver.execute_script("return document.querySelector('downloads-manager').shadowRoot.querySelector('#downloadsList downloads-item').shadowRoot.querySelector('div#content  #file-link').text")
		#print("The file downloaded is: ", name)
		return name


	def __parseJSON(self, filename):
		with open(filename) as json_file:
			data = json.load(json_file)
			os.remove(filename)
			return data

	def get_metric(self, url):
		# Enter f-uji page
		self.driver.get('https://www.f-uji.net/index.php?action=test')

		# fill the url
		element = self.driver.find_element(by=By.ID, value="pid")
		element.send_keys(url)

		# click the button
		self.driver.find_element(by=By.NAME, value="runtest").click()

		# wait and download the JSON
		try:
			WebDriverWait(self.driver, 30).until(
				EC.presence_of_element_located((By.NAME, "downloadtest"))
			)
			# download the JSON
			self.driver.get('https://www.f-uji.net/export.php')
			time.sleep(3)

			# get the file name
			file_name = self.__getDownLoadedFileName()
			full_path = tempfile.gettempdir() + "/" + file_name
			#print("The full path is", full_path)

			data = self.__parseJSON(full_path)

			return data
		except:
			print("An exception occurred")
			return None

		finally:
			self.driver.quit()

 
roFAIR = FujiWrapperv2("https://doi.org/10.1594/PANGAEA.908011")

