# Usage of cithub-generation

Currently, `cithub-generation` supports nine covering array generation tools: 

| Tool     | Algorithm Implemented | Source                                                       | Test Model Format |
| -------- | --------------------- | ------------------------------------------------------------ | ----------------- |
| ACTS     | Greedy (IPO)          | [link](https://csrc.nist.gov/Projects/automated-combinatorial-testing-for-software/downloadable-tools) | ACTS              |
| PICT     | Greedy                | [link](https://github.com/microsoft/pict)                    | PICT              |
| CASA     | Simulated Annealing   | [link](http://cse.unl.edu/~citportal/)                       | CASA              |
| FastCA   | Tabu Search           | [link](https://github.com/jkunlin/fastca)                    | CASA              |
| Jenny    | Greedy                | [link](https://burtleburtle.net/bob/math/jenny.html)         | Jenny             |
| medici   | Greedy (BDD)          | [link](https://github.com/garganti/medici)                   | CASA              |
| Tcases   | Greedy                | [link](https://github.com/Cornutum/tcases)                   | Tcases            |
| JCUnit   | Greedy                | [link](https://github.com/dakusui/jcunit)                    | ACTS              |
| coffee4j | Greedy                | [link](https://coffee4j.github.io)                           | ACTS              |



#### Input and output parameters of the `/generation` API

##### Input Parameters

Form data

* `algorithm`: (*string, mandatory*) name of the generation algorithm

* `model`: (*string, mandatory*) name of the test model
* `strength`: (*int, mandatory*) coverage strength (the execution of some tools does not rely on this value, but it is still required for this API)

* `timeout`: (*int*) execution time budget, default = 100
* `repeat`: (*int*) number of repetitions, default = 1
* `model_text`: (*string*) the plain text of test model file
* `constraint_text`: (*string*) the plain text of constraint file

File data

* `model`: the object of model file
* `constraint`: the object of constraint file

The service will first look for `model_text` and `constraint_text`, and use the content provided to create their respective files (almost all tools take model files as the input). If such content is not provided, the service will look for the file data and upload necessary model files. Note that some tools require only a model text/file, while some others require two texts/files (in particular, the CASA format). 



##### Output Parameters

Once the generation process terminates, the service will return the results in JSON format, like:

```
{
	'result': {
		'best': {
			'size': 8,
			'time': 0,
			'array': 'tmp/casa-aircraft-2-way-WUX7.array', 
			'stdout': 'tmp/casa-aircraft-2-way-WUX7.stdout' 
		}, 
    'size': [8, 8, 9, 8, 10]
    'time': [0, 0, 1, 0, 0]
	}
}
```

Here, `size` and `time` (list of numbers) give array sizes and time costs (in seconds) observed in each execution, and the `best` field indicates the smallest array size obtained. The array and stdout files of this best result are given in the `array` and `stdout` field,  and can be downloaded via an HTTP GET method (e.g., from `http://127.0.0.1:5000/tmp/casa-aircraft-2-way-WUX7.array`)



#### The use of existing tools

`cithub-generation` directly uses the executable binaries of the above tools (except for `jcunit` and `coffee4j`), without any modification, to construct the required covering arrays. While for `jcunit` and `coffee4j`, they are designed as extensions of JUnit testing framework. So an additional Java program is developed as the executable binary, which will read the test model of ACTS format (abstract format only), and call the core generation algorithm of `jcunit`, or `coffee4j`, to construct the covering array.

The directory of executable binaries (can be customised using the `C_BIN` environment variable):

* `bin`: compiled and tested in CentOS 7 system (default)
* `bin-mac`: compiled and tested in MacOS 11 system



#### Support of Original Modelling Language

Here, the test model that only describes the number of parameters and sizes of parameter value domains is referred to as an **abstract test model** (such a test model is enough for evaluating the performance of covering array generation algorithms, see `models` for examples). By contrast, the test model that describes the concrete names of parameters and values are referred to as a **concrete test model** (see `models_origin` for examples).

* The tools supporting both abstract and concrete test models:
  * `acts`: should be written in plain text. The output array format can be specified by `array_format` (`numeric` by default; other options include `nist` and `csv`).
  * `pict`: should be written in plain text.
  * `tcases`: should be written in JSON format.

* The tools supporting abstract test models only:
  * `casa`, `fastca`, and `medici`: by definition of CASA format. Especially, `fastca` will only report the minimum array sizes, without yielding the covering array.
  * `jenny`: by definition of Jenny format.
  * `jcunit` and `coffee4j`: these two tools require a specific variant of ACTS format, which uses abstract information to describe parameters and values (e.g., `p0(int):0,1`), and uses forbidden tuples to describe constraints (e.g., `p11!= 1 || p12!= 0`).