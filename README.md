# ebuild-analyzer

Performs deep static analysis to extract information from Gentoo ebuilds.

## Features

- Extraction of optional features (optfeatures)
- Extraction of checked kernel configuration keys
- Parsing and evaluation of path conditions
- Expansion of basic variables
- User-friendly and understandable colored output
- Comprehensive unit tests

## Installation

A Python version of at least 3.11 is required in order to use the script. You must also ensure that the global portage
module is used (if creating a virtualenv use the `--system-site-packages` option).

Since this is a python script, all that is necessary is to run pip to install the script system-wide:

```commandline
pip install .
```

This will install the script along with the necessary dependencies.

## Usage

A script with the name `ebuild-analyzer` is installed after the Installation step.

Invoke the script with the `-h` flag to get a help message which explains all the possible commands and options.
Note that some commands have their own flags.

To run the analyzer against a package, invoke `ebuild-analyzer` with your desired command, for example `kernel-config`
to extract the checked kernel configuration, and with the desired package.

```commandline
ebuild-analyzer -v --ruc kernel-config net-misc/networkmanager
```

It is also possible to run the script on all the installed packages on the system using the `-a` option.

## Notes

* You may run into an ambiguous package error if there are multiple candidates for your supplied package. In this case,
  pass the package atom.

* The script will choose the best version available on the system, when specifying a package atom you may also specify a
  different version if desired.

* Note that some information is hidden to prevent cluttering the output. For example, unless the `--verbose` option is
  passed, irrelevant checked kernel configuration is hidden. A kernel configuration key is irrelevant if the path
  conditions that the check requires are unsatisfied (this means that the necessary USE flags are not set, for
  instance).

## How it works

The script finds the ebuild file which matches the given package/atom and parses it to an AST using tree-sitter after
normalizing the ebuild's contents and expanding some basic variables.

From here, the specific flow depends on the extraction, but generally speaking, the script now starts analyzing the AST
to extract the necessary nodes for the extraction.

For example, when analyzing optional features the script will look for all the AST nodes that run the `optfeature`
command. When analyzing checked kernel configurations the script will look for all the AST nodes that set the
`CONFIG_CHECK` variable and the warning/error message variables for every checked kernel config key.

After that the script will start building the path conditions necessary for the relevant nodes to be reached. This is
done statically, none of the ebuild's code is run.

Finally, the analyzed data is passed to the relevant printer to evaluate the path conditions and print the results to
the user in a (hopefully) friendly and understandable way.

## Contributing

Anyone is welcome (and I urge you) to submit bug reports, feature requests and merge requests. I will do my best to give
an answer to everything.

## Development

To play around with the code simply clone the repository.

The structure is straight-forward:

- `src/` directory contains the sources
- `tests/` directory contains the tests

To run the tests just run `pytest .`, they run very quickly and are very comprehensive.

## Limitations

As this is a new static analyzer, there are several limitations (most of which can be seen in the Issues tab).
Here is a general list of some of the limitations which I am hoping to address at some point in the future.

- Some packages use static for loops to define their optfeatures/checked kernel config keys
- Not all cases of checked kernel configuration are handled. I only check the `CONFIG_CHECK` variable but there are
  ebuilds that test kernel config keys manually using if statements or using `linux_chkconfig_present`.
