# Replication of Phylogenetic Analysis of Reticulate Software Evolution

Mar. 8, 2023

## Files

* `README.md`: this file
* `rse-image-20221028.txz`: docker image (for `amd64`)
* `rse-image-arm64-20221028.txz`: docker image (for `arm64`)
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
* _BIND9_: A family of BIND9 DNS systems


## Replication Steps

Computing distance matrices (Step 3) will take time (hours or days). We recommend configuring your container environment as follows.

* CPUs: more than 8
* Memory: more than 2G x CPUs

### 1. Importing the docker image

First of all, you need to import the docker image for `x64` (`x86_64`, `amd64`) hosts. This step may take some time.

    $ ./import_docker_image.sh rse-image-20221021.txz

If your host's architecture is `arm64`, import "`rse-image-arm64-20221028.txz`" insead of "`rse-image-20221028.txz`".


### 2. Starting a container process for the experiment

You can start a session in a new container as follows.

    $ docker run -ti --name rse -v $PWD:/mnt/work rse


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
| BIND9   | `bind9`    |

Note that you need to extract source files in archives placed at the `project` directory.
For example, a distance matrix for Emacsen (`emacs.c` only) is computed by the following.

    user@xxx:~$ cd projects
    user@xxx:~/projects$ tar Jxf emacs_c.txz
    user@xxx:~/projects$ cd ..
    user@xxx:~$ ./mkdistmat.sh emacs_c

The distance matrix will be placed at "`./work.emacs_c/infile.emacs_c.diffast.d1`".
