# cithub-generation

**cithub-generation** is a configurable web service that can invoke different standalone covering array generation tools to generate covering arrays.



## Deployment & Usage

 To deploy the service, first pull the docker image, and then run the container (with specific hardware constraints):

```bash
docker pull waynedd/cithub-generation:1.7
```

```bash
docker run -d -p [port]:5000 --cpus=2 --memory=16G --name [service_name] waynedd/cithub-generation:1.8
```

Once the service is ready, the specific generation service can be visited via an HTTP Post method:

```python
import requests

data = {'algorithm': 'acts', 'timeout': 60, 'repeat': 5, 'strength': 2}
files = {'model': 'example/files/grep-acts.model'}

r = requests.post('http://127.0.0.1:[port]/generation', data=data, files=files)
print(r.json())
```

Currently, seven covering array generation tools are supported:

* `acts`
* `pict`
* `casa`
* `fastca`
* `jenny`
* `medici`
* `tcases`

See `example/example.py` for the codes that use each of the above tools to generate covering arrays. The test model (and constraint) files can be found in  `example/files`. 



## Add New Tools

In order to add a new covering array generation too into the service, just 1) prepare a configuration file, and 2) write a function that extracts array sizes.

#### Configuration File

`cithub-generation` uses a configuration file (in JSON format) to describe the necessary information of running each spesific tool. For example, the following code block gives the configuration file of ACTS (`configuration/acts.json`):

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

* All input parameters of running the tool should be given in the `input` section. Typical input parameters include `model`, `constraint`, and `strength`. Note that some tools can take a `SEED`  parameter, and this parameter does not need to be explicitly described (a random seed value will always be used in each execution).
* Each tool typically has one `output` parameter. Its type indicates 1) a `file` is specified in the running command, or 2) the results can only be obtained from the `console` (stdout).
*  `bin` gives the executable binary file of the tool.
*  `run` gives the particular command to execute the tool, where each parameter is placed into a square brackets `[]`, and the optional part is placed into a brace `{}`. Note that each parameter here should be described in `input` and `output` sections (except `[SEED]`).
* *Optional*:  `clean` gives the additional command that should be executed after the execution of the tool (e.g., killing some processes forked by the tool). See `configuration/tcases.json` for example.



#### Extraction Function

Once the execution of the tool finishes,  `cithub-generation` will call the `array_size()` function of the `Extraction` class to extract the exact size of the covering array generated (see `extraction.py`). It is recommended to extract the size from the `console` file generated (stdout), because the tool might run out of time, where no array file is produced.

For example, the following gives the extraction function of ACTS.

```python
@staticmethod
  def acts(console):
    for line in console:
      if line.startswith('Number of Tests	:'):
        number = int(line.strip().split()[-1])
        return number
    return None
```



#### Build

After the updating, just rebuild (and publish) the new image, and run the container.

```bash
docker build -t username/cithub-generation:1.x .
docker push username/cithub-generation:1.x
```



#### Additional Notes

The current version of `cithub-generation` is especially designed for packaging an existing command-line tool. If you wish to package an algorithm under development, it is recommended to design and implement it as a native docker-based web service.

