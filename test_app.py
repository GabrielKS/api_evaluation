# Unit tests for the app
# Note: the server must be running and its URL must be given by the COMPANYNAME_SERVER_URL environment variable for this to work

import os
import unittest
import requests

class TestApp(unittest.TestCase):
    server_url_env_name = "COMPANYNAME_SERVER_URL"
    def __init__(self, *args, **kwargs):
        # Get the server URL from an environment variable for configurability's sake
        try:
            self.server_url = os.environ[self.server_url_env_name]
        except KeyError:
            raise KeyError(f"Could not find the environment variable {self.server_url_env_name}")
        self.temp_url = self.server_url+"/temp"
        super(TestApp, self).__init__(*args, **kwargs)
    
    # Verify that we have a server URL
    def test_environ(self):
        self.assertGreater(len(self.server_url), 0)
        print(f"Testing with server URL: {self.server_url}")
    
    # Verify a connection to the root
    def test_connect_200(self):
        response = requests.get(self.server_url)
        self.assertEqual(response.status_code, 200)
    
    # Verify that POST at /temp is not Method Not Allowed
    def test_post_temp_405(self):
        response = requests.post(self.server_url+"/temp")
        self.assertNotEqual(response.status_code, 405)
    
    # Verify that GET at /errors is not Method Not Allowed
    def test_get_errors_405(self):
        response = requests.get(self.server_url+"/errors")
        self.assertNotEqual(response.status_code, 405)
    
    # Verify that DELETE at /errors is not Method Not Allowed
    def test_delete_errors_405(self):
        response = requests.delete(self.server_url+"/errors")
        self.assertNotEqual(response.status_code, 405)
    
    # Verify that POST at /temp responds correctly to badly formatted requests
    def test_post_temp_bad(self):
        tries = [
            requests.post(self.temp_url, data="not even JSON"),
            requests.post(self.temp_url, json={"bad": "key"}),
            requests.post(self.temp_url, json={"data": "not:enough:colons"}),
            requests.post(self.temp_url, json={"data": "not-an-int:1640995229697:'Temperature':58.48256793121914"}),
            requests.post(self.temp_url, json={"data": "365951380:not-an-int:'Temperature':58.48256793121914"}),
            requests.post(self.temp_url, json={"data": "365951380:1640995229697:Temperature:58.48256793121914"}),  # Temperature lacks single quotes
            requests.post(self.temp_url, json={"data": "365951380:1640995229697:'Temperature':not-a-float"})
        ]
        for response in tries:
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {"error": "bad request"})
        pass

    # Verify that POST at /temp responds correctly to undertemp requests
    def test_post_temp_undertemp(self):
        tries = [
            "365951380:1640995229697:'Temperature':58.48256793121914",
            "-123456:1640995229697:'Temperature':58.48256793121914",
            "365951380:-234567:'Temperature':58.48256793121914",
            "365951380:1640995229697:'Temperature':-100.31415",
        ]

        for data_string in tries:
            response = requests.post(self.temp_url, json={"data": data_string})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"overtemp": False})
    
    # Verify that POST at /temp responds correctly to overtemp requests
    def test_post_temp_overtemp(self):
        tries = [
            "365951380:1640995229697:'Temperature':98.48256793121914",
            "365951380:1640995229697:'Temperature':90",  # Edge case
            "-123456:1640995229697:'Temperature':108.48256793121914",
            "365951380:-234567001:'Temperature':118.48256793121914",
            "365951380:1600000000000:'Temperature':128.31415",
        ]
        device_ids = [365951380, 365951380, -123456, 365951380, 365951380]
        formatted_times = ["2022/01/01 00:00:29", "2022/01/01 00:00:29", "2022/01/01 00:00:29", "1969/12/29 06:50:32", "2020/09/13 12:26:40"]

        for data_string, device_id, formatted_time in zip(tries, device_ids, formatted_times):
            response = requests.post(self.temp_url, json={"data": data_string})
            self.assertEqual(response.status_code, 200)
            response_json = response.json()
            self.assertEqual(response_json["overtemp"], True)
            self.assertEqual(response_json["device_id"], device_id)
            self.assertEqual(response_json["formatted_time"], formatted_time)
    
if __name__ == "__main__":
    unittest.main()
