from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time, os, json, tempfile

import requests
from requests.structures import CaseInsensitiveDict

class FujiWrapperv2:
	def __init__(self):
		pass
	def get_metrics(self, url):
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
		
		print(resp.json())


    
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

 
# roFAIR = FujiWrapperv2()
# roFAIR.get_metrics("https://doi.org/10.1594/PANGAEA.908011")
