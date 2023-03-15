import requests
from requests.structures import CaseInsensitiveDict

class FujiWrapper:
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
			print(result["metric_tests"][test]);passed += 1 if result["metric_tests"][test]["metric_test_status"] == "pass" else 0
		
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
			check = {};print(raw["request"]["object_identifier"]);print("************************")
			check["principle_id"] = self.__reformat_principle_id(result)
			check["category_id"] = self.__set_category(check["principle_id"])
			check["status"], check["total_passed_tests"], check["total_tests_run"] = self.__calculate_tests_and_status(result)
			check["title"] = result["metric_name"]
			check["explanation"] = self.__get_explanation(result)
			check["assessment"] = result["test_status"]
			check["score"] = result["score"]["earned"]
			check["total_score"] = result["score"]["total"]
			# check["description"] = ""
			self.output["checks"].append(check)
	

	def get_checks(self):
		return self.output["checks"]

	def get_identifier(self):
		return self.output["identifier"]
    
