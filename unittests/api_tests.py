import unittest

from app.api import create_app

class ApiTest(unittest.TestCase):

    def setUp(self):
        self._client = create_app().test_client()

    def test_00_health(self):
        """
        test the health endpoint
        """

        response = self._client.get('/')
        self.assertEqual(200, response.status_code)

    def test_01_train(self):
        """
        test the train functionality
        """
      
        request_json = {'mode':'test'}
        r = self._client.post('/train', json=request_json)
        train_complete = r.get_json()
        self.assertEqual('success', train_complete['status'])
    
    def test_02_predict_empty(self):
        """
        ensure appropriate failure types
        """
    
        ## provide no data at all 
        r = self._client.post('/predict')
        self.assertEqual(re.sub('\n|"','',r.get_data(as_text=True)),"[]")

        ## provide improperly formatted data
        r = self._client.post('/predict', json={"key":"value"})     
        self.assertEqual(re.sub('\n|"','',r.get_data(as_text=True)),"[]")
    
    def test_03_predict(self):
        """
        test the predict functionality
        """

        query_data = {
            "country": "united_kingdom",
            "year" : "2019",
            "month": "05",
            "day": "10"
        }

        query_type = 'dict'
        request_json = {'query':query_data,'type':query_type,'mode':'test'}

        r = self._client.post('/predict', json=request_json)   
        response = literal_eval(r.get_data(as_text=True))

        for p in response['y_pred']:
            self.assertTrue(p > 0)

    def test_04_logs(self):
        """
        test the log functionality
        """

        r = requests.get('/logs')
        response = r.get_json()
        
        self.assertTrue(len(response))
