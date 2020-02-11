# cithub-generation

This project provides a web application that can be configured to use different algorithms to generate
covering arrays.

### Usage

Pull the docker image:

```bash
docker pull waynedd/cithub-generation
```

Run the container:

```bash
docker run -d -p [host]:6000 -e CALG=[algorithm] --name ca-service waynedd/cithub-generation
```

where `algorithm` indicates the particular generation tool that provides the service.

* `acts`
* `pict`
* `casa`
* `fastca`



### Project Organisation

1. `bin`: this directory contains the executable binaries of covering array generation tools.
2. `example`: the python script to call the service




### The Configuration File

The configuration file indicates the basic information of the generation tool, as well as its usage and input/output parameters.

* All input files and parameters should be given in `input`, except for the seed `SEED` (a random seed value will always be used in each execution). In particular, `model`, `timeout` and `repeat` are must-have parameters, and the type of each parameter can only be  `file` or `nnumber`.
* The type of `output` indicates 1) an output `file` is specified in the running command, or 2) the results can only be obtained from the `console`.
* The `bin` gives the executable binary file of the tool.
* The value of `run` gives the command to execute the tool, where each parameter is placed into a square brackets `[]`, and the optional part is placed into a brace `{}`. Note that each parameter here should be explicitly given in `input` (except `[SEED]`).
* The value of `get_size` gives the command to extract the size of covering array generated.



Here is an example of the ACTS tool:

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
    },
    {
      "name": "timeout",
      "type": "number"
    },
    {
      "name": "repeat",
      "type": "number"
    }
  ],
  "output": {
    "name": "output",
    "type": "file"
  },
  "bin": "acts_3.0.jar",
  "run": "java -Ddoi=[strength] -Doutput=numeric -jar acts_3.0.jar [model] [output]",
  "get_size": ["grep", "Number of configurations", "[output]"]
}
```



