# cithub-generation

**cithub-generation** is a configurable web service that can invoke different standalone covering array generation tools to generate covering arrays.



## Deployment & Usage

 To deploy the service, just pull the docker image, and then run the container (with specific hardware constraints):

```bash
docker pull waynedd/cithub-generation:2.0
docker run -d -p [port]:6000 --cpus=4 --memory=16G --name [service_name] waynedd/cithub-generation:2.0
```

Once the service is ready, the specific generation algorithm can be visited via an HTTP Post method:

```python
import requests

data = {
  'algorithm': 'acts', 
  'name': 'aircraft', 
  'strength': 2, 
  'model_text': open('example/models/aircraft-acts.model')
}

r = requests.post('http://127.0.0.1:[port]/generation', data=data)
print(r.json())
```

Currently, nine covering array generation tools are supported, including `acts`, `pict`, `casa`, `fastca`, `jenny`, `medici`, `tcases`, `coffee4j`, and `jcunit`. See `example/example.py` for the codes that construct input parameters (or files) for using the above tools.

**Notes**

* The service will only invoke the core generation algorithm of each tool, so that other avaiable functionalities of these tools (e.g., coverage measurement, fault diagnosis, etc.) are not supported.
* Currently, the service is only tested with model files of abstract information (that is, a specific variant of their original modelling langauge).



## Add New Tools

In order to add a new covering array generation too into the service, two modifications are required:

1. prepare a configuration file
2. write a function that extracts array sizes



#### Configuration File

`cithub-generation` uses a configuration file (in JSON format) to describe the necessary information of running each spesific tool. For example, the following code block gives the configuration file of ACTS (i.e., `configuration/acts.json`):

```json
{
  "name": "ACTS",
  "version": "3.0",
  "author": "NIST",
  "link": "https://csrc.nist.gov/Projects/automated-combinatorial-testing-for-software/downloadable-tools",
  "input": [
    {
      "name": "model",
      "type": "file"
    },
    {
      "name": "strength",
      "type": "number"
    }
  ],
  "output": {
    "name": "output",
    "type": "file"
  },
  "bin": "acts_3.0.jar",
  "run": "java -Ddoi=[strength] -Doutput=numeric -jar acts_3.0.jar [model] [output]"
}
```

Specifially,

* All input parameters of running the tool should be given in the `input` section. Typical input parameters include `model`, `constraint`, and `strength`. Note that some tools might take a `SEED`  parameter, and this parameter does not need to be explicitly described (a random seed value will always be used in each execution).
* Each tool should provide one `output` parameter, in either `file` or `stdout` type. In the former case, the tool will write the covering array generated into file; while in the latter case, the generation result can only be obtained from the stdout.

*  `bin` gives the executable binary file of the tool.
*  `run` gives the particular command to execute the tool, where each parameter is placed into a square brackets `[]`, and the optional part is placed into a brace `{}`. Note that each parameter here should be described in `input` and `output` sections (except `[SEED]`).



#### Extraction Function

Once the execution of the tool finishes,  `cithub-generation` will call the `array_size()` function of the `Extraction` class to extract the exact size of the covering array generated (see `extraction.py`). The input of this process is the `stdout` file by default, because the tool might run out of time, where no array file is produced.

For example, the following gives the extraction function of ACTS.

```python
@staticmethod
def acts(console):
  for line in console[::-1]:
    if line.startswith('Number of Tests'):
      num = line.strip().split()[-1]
      if num.isdigit():
        return int(num)
      return None
```



#### Build

After the update, build and publish the new image:

```bash
docker build -t username/cithub-generation:tag .
docker push username/cithub-generation:tag
```



Note that the current version of  `cithub-generation` is especially designed for packaging an existing command-line tool. If you wish to deploy an algorithm that is under development, it is recommended to design and implement it as a native docker-based web service.

