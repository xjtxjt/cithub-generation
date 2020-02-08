# cithub-generation

This project provides a web application that can be configured to use different algorithms to generate
covering arrays.


### Usage

```bash
docker pull waynedd/cithub-generation
docker run -itd --name ca-service waynedd/cithub-generation
```

### Organisation

1. `bin`: this directory contains the executable binaries of covering array generation tools.

2. `example`: the python script to call the service


### The Configuration File

Here is an example of the CASA tool:

```json
{
  "name": "CASA",
  "version": "1.1b",
  "author": "",
  "link": "",
  "input": [
    {
      "label": "model",
      "file": "casa.model"
    },
    {
      "label": "constraint",
      "file": "casa.constraints"
    }
  ],
  "output": {
    "file": "casa.out",
    "get_size": "sed -n 1p [output]"
  },
  "run": "casa-1.1b [model] -c [constraint] -o [output]"
}
```

