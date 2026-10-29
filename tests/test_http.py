import json
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from server import Handler

class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        cls.server.csrf = 'test-session-token'
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}'
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
    def request(self, path, payload, token=None, origin=None):
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['X-Review-Token'] = token
        if origin:
            headers['Origin'] = origin
        req = urllib.request.Request(self.base + path, data=json.dumps(payload).encode(), headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                return response.status, json.load(response)
        except urllib.error.HTTPError as error:
            return error.code, json.load(error)
    def test_missing_token_rejected(self):
        code, _ = self.request('/api/review', {'documents': [], 'question': 'capacity?'})
        self.assertEqual(code, 403)
    def test_foreign_origin_rejected(self):
        code, _ = self.request('/api/review', {'documents': [], 'question': 'capacity?'}, self.server.csrf, 'https://other.example')
        self.assertEqual(code, 403)
    def test_valid_local_request(self):
        code, data = self.request('/api/review', {'documents': [{'id':'a','title':'test','text':'Storage capacity: 10 MWh.'}], 'question':'capacity?'}, self.server.csrf, self.base)
        self.assertEqual(code, 200)
        self.assertEqual(data['status'], 'supported')
    def test_malformed_document_rejected(self):
        code, _ = self.request('/api/review', {'documents':[{'id':'x'}], 'question':'capacity?'}, self.server.csrf)
        self.assertEqual(code, 400)
    def test_unknown_endpoint_is_404(self):
        code, _ = self.request('/api/not-present', {}, self.server.csrf)
        self.assertEqual(code, 404)

if __name__ == '__main__':
    unittest.main()
