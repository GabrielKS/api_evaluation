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
        super(TestApp, self).__init__(*args, **kwargs)
    
    # Verify that we have a server URL
    def test_environ(self):
        self.assertGreater(len(self.server_url), 0)
        print(f"Testing with server URL: {self.server_url}")
    
    # Verify a connection to the root
    def test_connect_ok(self):
        r = requests.get(self.server_url)
        self.assertEqual(r.status_code, 200)
    
    # Verify that POST at /temp is OK
    def test_post_temp_ok(self):
        r = requests.post(self.server_url+"/temp")
        self.assertEqual(r.status_code, 200)
    
    # Verify that GET at /errors is OK
    def test_get_errors_ok(self):
        r = requests.get(self.server_url+"/errors")
        self.assertEqual(r.status_code, 200)
    
    # Verify that DELETE at /errors is OK
    def test_delete_errors_ok(self):
        r = requests.delete(self.server_url+"/errors")
        self.assertEqual(r.status_code, 200)
    
if __name__ == "__main__":
    unittest.main()
