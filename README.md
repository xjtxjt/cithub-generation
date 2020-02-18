# cithub-generation

This project provides a configurable template that can automatically ship standalone covering array generation tools into a docker based web application.



## Usage

### Run with embedded tools

Currently, four covering array generation tools are used as the engines of cithub-generation:

* `acts`
* `pict`
* `casa`
* `fastca`

 To deploy any of them, first pull the docker image:

```bash
docker pull waynedd/cithub-generation
```

And then run the container:

```bash
docker run -d -p [host]:6000 -e CALG=[algorithm] --cpus=2 --memory=16G --name ca-service waynedd/cithub-generation
```

where `algorithm` indicates the particular tool that provides the generation service. 



### Run with a new tool

cithub-generation uses a **configuration file** for providing the necessary information of the generation tool, as well as its usage and input/output parameters. Specifially,

* All input files and parameters should be given in `input`, except for the seed `SEED` (a random seed value will always be used in each execution). In particular, `model`, `timeout` and `repeat` are must-have parameters, and the type of each parameter can only be  `file` or `nnumber`.
* The type of `output` indicates 1) an output `file` is specified in the running command, or 2) the results can only be obtained from the `console`.
* The `bin` gives the executable binary file of the tool.
* The value of `run` gives the particular command to execute the tool, where each parameter is placed into a square brackets `[]`, and the optional part is placed into a brace `{}`. Note that each parameter here should be explicitly given in `input` (except `[SEED]`).
* The value of `get_size` gives the command to extract the size of covering array generated from the output of consoles (as we apply a strict timeout strategy, so some tools, e.g. CASA, may fail to write the best array found so far to a file when the time exceeds the budget).

Note that the current version is especially desined for packaging an exisitng command-line tool. If you wish to package an algorithm under developement, it is recommended to design and implement it as a native docker-based web service from scratch.



Here is an example of the ACTS tool's configuration file:

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
  "get_size": "grep 'Number of Tests' [console] | awk 'END {print $(NF)}'"
}
```



Once the new configuration file is ready, just build (and publish) the image, and then run the container:

```bash
docker build -t username/new-generation-service
docker push username/new-generation-service
```

