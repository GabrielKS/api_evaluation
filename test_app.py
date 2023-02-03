# Unit tests for the app
# Note: the server must be running and its URL must be given by the EVAL_SERVER_URL environment variable for this to work

import os
import unittest
import requests

class TestApp(unittest.TestCase):
    # Name of the environment variable we get the server URL from
    server_url_env_name = "EVAL_SERVER_URL"
    # Several ways to POST incorrectly to /temp, to be used in multiple tests
    bad_posts = [  # Format: things that we can pass to requests.post as **kwargs
        {"data": "not even JSON"},
        {"json": {"bad": "key"}},
        {"json": {"data": "not:enough:colons"}},
        {"json": {"data": "not-an-int:1640995229697:'Temperature':58.48256793121914"}},
        {"json": {"data": "365951380:not-an-int:'Temperature':58.48256793121914"}},
        {"json": {"data": "365951380:1640995229697:Temperature:58.48256793121914"}},  # Temperature lacks single quotes
        {"json": {"data": "365951380:1640995229697:'Temperature':not-a-float"}}
    ]

    def __init__(self, *args, **kwargs):
        # Get the server URL from an environment variable for configurability's sake
        try:
            self.server_url = os.environ[self.server_url_env_name]
        except KeyError:
            raise KeyError(f"Could not find the environment variable {self.server_url_env_name}")
        self.temp_url = self.server_url+"/temp"
        super(type(self), self).__init__(*args, **kwargs)
    
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
        for bad_post in self.bad_posts:
            response = requests.post(self.temp_url, **bad_post)
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
    
    # Helper function to DELETE the /errors
    def delete_errors(self):
        return requests.delete(self.server_url+"/errors")

    # Helper function to GET the /errors and assert that the response is formatted correctly
    def get_errors(self):
        response_json = requests.get(self.server_url+"/errors").json()
        self.assertEqual(list(response_json.keys()), ["errors"])
        return requests.get(self.server_url+"/errors").json()["errors"]

    # Verify that GET /errors and DELETE /errors display the correct behavior
    def test_errors_correctness(self):
        for n in range(len(self.bad_posts)):  # Run the test for errors buffers of varying lengths
            self.delete_errors()
            error_log = []
            for bad_post in self.bad_posts[:n]:
                body = requests.post(self.temp_url, **bad_post).request.body
                if isinstance(body, bytes): body = body.decode("utf-8")
                error_log.append(body)
            self.assertEqual(self.get_errors(), error_log)

if __name__ == "__main__":
    unittest.main()
