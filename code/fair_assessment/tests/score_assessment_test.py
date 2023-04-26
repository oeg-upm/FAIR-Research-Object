import unittest
import requests
import time

class TestFUJIAssessment(unittest.TestCase):

    def test_score(self):

        url = "http://fairos.linkeddata.es/api/jobs/a32362cd-4109-4416-89ca-442329ee810a"
        r = requests.get(url)
        response = r.json()
        status = response['status']
        while (status == "RUNNING"):
            time.sleep(1000)
            r = requests.get(url)
            response = r.json()
            status = response['status']
        print("Status:"+str(status))
        url = "http://fairos.linkeddata.es/api/assessment/a32362cd-4109-4416-89ca-442329ee810a"
        r = requests.get(url)
        components = r.json()['components']

        checks = components[0]['checks']
        self.assertEqual(checks[0]['principle_id'], "F1.1")
        self.assertEqual(checks[0]['status'], "pass")
        self.assertEqual(checks[1]['principle_id'], "F1.2")
        self.assertEqual(checks[1]['status'], "pass")
        self.assertEqual(checks[2]['principle_id'], "F2.1")
        self.assertEqual(checks[2]['status'], "pass")
        self.assertEqual(checks[3]['principle_id'], "F3.1")
        self.assertEqual(checks[3]['status'], "fail")
        self.assertEqual(checks[4]['principle_id'], "F4.1")
        self.assertEqual(checks[4]['status'], "pass")
        self.assertEqual(checks[5]['principle_id'], "A1.1")
        self.assertEqual(checks[5]['status'], "pass")
        self.assertEqual(checks[6]['principle_id'], "I1.1")
        self.assertEqual(checks[6]['status'], "pass")
        self.assertEqual(checks[7]['principle_id'], "I1.2")
        self.assertEqual(checks[7]['status'], "pass")
        self.assertEqual(checks[8]['principle_id'], "I3.1")
        self.assertEqual(checks[8]['status'], "pass")
        self.assertEqual(checks[9]['principle_id'], "A1.1")
        self.assertEqual(checks[9]['status'], "pass")
        self.assertEqual(checks[10]['principle_id'], "R1.1")
        self.assertEqual(checks[10]['status'], "fail")
        self.assertEqual(checks[11]['principle_id'], "R1.1.1")
        self.assertEqual(checks[11]['status'], "pass")
        self.assertEqual(checks[12]['principle_id'], "R1.2.1")
        self.assertEqual(checks[12]['status'], "pass")
        self.assertEqual(checks[13]['principle_id'], "R1.3.1")
        self.assertEqual(checks[13]['status'], "pass")
        self.assertEqual(checks[14]['principle_id'], "R1.3.2")
        self.assertEqual(checks[14]['status'], "fail")
        self.assertEqual(checks[15]['principle_id'], "A1.3")
        self.assertEqual(checks[15]['status'], "fail")
        self.assertEqual(checks[16]['principle_id'], "A1.2")
        self.assertEqual(checks[16]['status'], "pass")

        score = components[0]['score']

        findable = score['Findable']
        self.assertEqual(findable['tests_passed'],4)
        self.assertEqual(findable['total_tests'],5)
        self.assertEqual(findable['score'],3.5)
        self.assertEqual(findable['total_score'],7)

        accessible = score['Accessible']
        self.assertEqual(accessible['tests_passed'],2)
        self.assertEqual(accessible['total_tests'],3)
        self.assertEqual(accessible['score'],1.5)
        self.assertEqual(accessible['total_score'],3)

        interoperable = score['Interoperable']
        self.assertEqual(interoperable['tests_passed'],3)
        self.assertEqual(interoperable['total_tests'],3)
        self.assertEqual(interoperable['score'],3)
        self.assertEqual(interoperable['total_score'],4)

        reusable = score['Reusable']
        self.assertEqual(reusable['tests_passed'],3)
        self.assertEqual(reusable['total_tests'],5)
        self.assertEqual(reusable['score'],3)
        self.assertEqual(reusable['total_score'],10)

if __name__ == '__main__':
    unittest.main()

        
