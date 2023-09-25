# rolltable

A simple CLI app designed to roll on a provided random table and print out the result

## Disclaimer

I've wrote this on Linux using Python 3.11.2 and `venv` (the last stable version as I'm writing those lines), and it works for me. If you want to have it working on a different environment, you're welcome to fork this repo and check for yourself (except if you're trying to use Python 2; please stop)

## Usage

```
usage: rolltable [-h] [-f {list,chance}] [-c COUNT] [-e] [-d DICE_FORMULA]
                 [--clamp] [-o OUTPUT] [-a]
                 table_filepath

This program loads the random table from a configuration file and rolls a
random result from it

options:
  -h, --help            show this help message and exit

Input Options:
  table_filepath        path to random table config file
  -f {list,chance}, --format {list,chance}
                        Format for the table file content. Options are: 
                        - 'list' [default]: contains each item as a straight
                          simple list with comments
                        - 'chance': each item has a chance to appears in the results, 
                          usually as a percentage
                        See the github repo (freohr/rpg-table-roller) for example 
                        table files of the supported formats.

Roll Options:
  -c COUNT, --count COUNT
                        How many rolled results do you want from the table?
                        (defaults to 1 result)
  -e, --exclusive       Each result can be rolled at most once
  -d DICE_FORMULA, --dice-formula DICE_FORMULA
                        Custom dice formula to roll on the table. Keep it
                        simple (XdY±Z)
  --clamp               Force roll result between first and last element. No
                        effect if not using a custom formula.

Output Options:
  -o OUTPUT, --output OUTPUT
                        Text file to output the rolled results. Note: Contents
                        will be overwritten.
  -a, --append          Append the rolled results to the output file. No
                        effect when printing to STD
```

Example tables are in the [`examples/`](examples/) folder in this repo.

## Contributing

As this app is currently in early development, I'm not looking for contribution or feature suggestions. If you use this and encounter a bug, you can open an issue and I'll see what I can do.

If you still want to look around the code, I've set up a Makefile with the basic following basic commands

- `make init`: Inside your dedicated Python 3 virtualenv (or venv, or you know what you prefer), will install the dependencies via pip
- `make build`: Using PyInstaller, will create a contained one-file executable, because I want to provide this as-is to you and not pollute your global environment by installing dependencies
- `make install`: Rebuild the executable, then make a copy to your session local binary dir, ready to be used anyhwere
