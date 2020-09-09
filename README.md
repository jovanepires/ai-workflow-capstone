# IBM AI Enterprise Workflow Capstone
Files for the IBM AI Enterprise Workflow Capstone project. 

## Files
  
```
├───app
│   ├───api
│   ├───data_ingestion
│   ├───logger
│   ├───model
│   ├───notebooks
├───cs-production
├───cs-train
├───deploy
│   ├───notebooks
│   └───webserver
├───logs
├───reports
├───solution-guidance
└───unittests
```

## Testing 

Running all tests

```
python -m unittest unittests/*.py
```
  
Running Logger tests

```
python -m unittest unittests/logger_tests.py
```
  
Running Model tests

```
python -m unittest unittests/model_tests.py
```
  
Running API tests

```
python -m unittest unittests/api_tests.py
```

## Building
  
```
$ docker-compose build
```

## Running
  
All tests and the entire application is bundled on a docker container. When you run this command, all tests run before the API instance starts.
  
```
$ docker-compose up
```

## API
  
- Health check 

```
# request
GET /
```
```
# response
{"status":"success"}
```
    
- Train 

```
# request
POST /train
{
  "mode": "test" // toggle between a test version and a production verion of training
}
```
```
# response
{"status":"success"}
```
  
- Predict 

```
# request
POST /predict
{
	"mode": "prod",
	"type": "dict",
	"query": {
		"country": "united_kingdom",
		"year" : "2019",
		"month": "05",
		"day": "10"
	}
}
```
```
# response
[
  {
    "y_pred": 176255.3608,
    "y_proba": null
  }
]
```
- Logs 

```
# request
GET /logs
```
```
# response
[
  "general-app.data_ingestion.data_repository-2020-9.log",
  "unittests-unittests.logger_tests-2020-9.log",
]
```

```
# request
GET /logs/<filename>
```
```
# response
[
   {
      "unique_id":"a0192b07-b53d-4a3c-aa6e-208ec0803f92",
      "timestamp":1599545067.559771,
      "msg":"It's Alive"
   },
   {
      "unique_id":"33ae77c1-aec2-459e-a892-119011a310e0",
      "timestamp":1599545067.5681574,
      "msg":"It's Alive"
   },
   {
      "unique_id":"e7dc936b-a4c1-45e5-b3b4-0136dd5e305a",
      "timestamp":1599545109.4987247,
      "msg":"It's Alive"
   },
   {
      "unique_id":"83aecf57-2dfd-4f99-82cd-a8d0d090e318",
      "timestamp":1599545109.5114288,
      "msg":"It's Alive"
   },
   {
      "unique_id":"b6117e14-5699-429d-a43d-3711f808f788",
      "timestamp":1599545355.9656255,
      "msg":"It's Alive"
   },
   {
      "unique_id":"d5a3aa5b-1fea-4517-ae68-6453f038589e",
      "timestamp":1599545355.972197,
      "msg":"It's Alive"
   }
]
```