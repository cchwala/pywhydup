pywhydup
========


Python WRF-Hydro setup duplicator, manipulator and SLURM runner

Usage
-----

```

dir_handler = pywhydup.SetupDirHandler(root_dir='/PATH/TO/WRF_HYDRO_ROOT_DIR/',
                                       template_dir='TEMPLATE_SETUP_DIR/')

# This would generate a new setup in the directory `setup_001`. `setup` is
# the defaults base string, and the function increments the numbers until
# the desired diretory does not yet exist.
new_setup = dir_handler.duplicate_template(t_start='2015-01-06',
                                           t_stop='2015-01-08')

# Hence, this generates the duplicated setup in the directory `setup_002`
new_setup = dir_handler.duplicate_template(t_start='2015-01-06',
                                           t_stop='2015-01-08')

# If the temporal period is not specified, all forcing files a copied. If
# desired, the name of the directory can be specified explicitly.
new_setup = dir_handler.duplicate_template(new_dir='my_new_setup')

```

Installation
------------

Clone the repo and install the dependencies. Then do a local install via `pip`

```
conda install netcdf4

pip install -e PATH_TO_CLONED_REPO
```

Requirements
------------

`netCDF4`

Licence
-------

BSD 3-Clause License


Authors
-------

`pywhydup` was written by `Christian Chwala <christian.chwala@kit.edu>`_.
