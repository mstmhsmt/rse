# Replication of Phylogenetic Analysis of Reticulate Software Evolution

Mar. 23, 2023

## Files

* `README.md`: this file
* `rse-image-*.txz`: docker image (for `amd64`)
* `rse-image-arm64-*.txz`: docker image (for `arm64`)
* `import_docker_image.sh`: script for importing a docker image
* `infile.*`: distance matrices
* `argouml-variant-features_abbr.json`: correspondence between variant IDs and abbraviated features for ArgoUML-SPL
* `*.txz`: archives of source code files (also contained in the docker images)


## Description

This is a replication package of the experiments conducted for the paper "_Phylogenetic Analysis of Reticulate Software Evolution_" by Akira Mori and Masatomo Hashimoto.
The source code is available [here](https://github.com/mstmhsmt/rse).

The experiments ware conducted on the following projects.

* _Emacsen_: A family of Emacs editors
* _Marlin_: A family of Marlin 3D printer firmware
* _ArgoUML_: Variants of ArgoUML generated from 
* _ATK2_: A family of TOPPERS Automotive kernels


## Replication Steps

Computing distance matrices (Step 3) will take time (hours or days). We recommend configuring your container environment as follows.

* CPUs: more than 8
* Memory: more than 2G x CPUs


### 1. Importing the docker image

You can pull the image from Docker Hub.

    $ docker pull mhashimoto/rse

Otherwise, you need to import the docker image for `x64` (`x86_64`, `amd64`) hosts. This step may take some time.

    $ sh import_docker_image.sh rse-image-20230327.txz

If your host's architecture is `arm64`, import "`rse-image-arm64-20230327.txz`" insead of "`rse-image-20230327.txz`".


### 2. Starting a container process for the experiment

You can start a session in a new container as follows.

    $ docker run -ti --name rse -v $PWD:/mnt/work mhashimoto/rse

Note that the image name should be `rse` instead of `mhashimoto/rse`, if you imported the image manually.

### 3. Computing distance matrices

To compute a distance matrix for a project, run "`mkdistmat.sh <Project ID>`".
A project ID is assigned for each project as follows.

| Project | Project ID |
| ----    | ----       |
| Emacsen | `emacsen`  |
| Emacsen (`emacs.c` only) | `emacs_c` |
| Marlin  | `marlin`   |
| Marlin (`Marlin_main.cpp` only) | `Marlin_main_cpp` |
| ArgoUML | `argouml-variants` |
| ATK2    | `atk2_1_4_0` |

For example, a distance matrix for Emacsen (`emacs.c` only) is computed by the following.

    user@xxx:~$ ./mkdistmat.sh emacs_c

The distance matrix will be placed at "`./work.emacs_c/infile.emacs_c.diffast.d3`".

If you could make a distance matrix for ArgoUML, you will have "`./work.argouml-variants/infile.argouml-variants.diffast.d3`", where variants's labels are simple numbers.
You can convert the numbers into variant specs by the following.

    user@xxx:~$ ./get_variant_specs.py work.argouml-variants/infile.argouml-variants.diffast.d3

The result will be placed at "`./work.argouml-variants/infile.argouml-variants.diffast.d3.abbr`".


### 4. Processing distance matrices

The distance matrices can be processed by the following tools.
* [SplitsTree](https://uni-tuebingen.de/en/fakultaeten/mathematisch-naturwissenschaftliche-fakultaet/fachbereiche/informatik/lehrstuehle/algorithms-in-bioinformatics/software/splitstree/)
* [T-REX](http://www.trex.uqam.ca/index.php?action=trex&menuD=2&project=trex)
