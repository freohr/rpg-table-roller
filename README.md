# rolltable

A simple CLI app designed to roll on a provided random table and print out the result

## Disclaimer

I've written this on Linux using Python 3.11.2 and `venv` (the last stable version as I'm writing those lines), and it works for me. If you want to have it working on a different environment, you're welcome to fork this repo and check for yourself (except if you're trying to use Python 2; please stop)

## Usage

```
usage: rolltable [-h] [-v] [-f {list,chance,hexflower}] [-c COUNT] [-e] [-d DICE_FORMULA] [--clamp] [-s START] [-o OUTPUT] [-a] [-j JOIN] table_filepath

This program loads the random table from a configuration file and rolls a random result from it

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit

Input Options:
  table_filepath        path to random table config file
  -f {list,chance,hexflower}, --format {list,chance,hexflower}
                        Format for the table file content. Options are:
                        - 'list' [default]: contains each item as a straight simple list with comments
                        - 'chance': each item has a chance to appears in the results, usually as a percentage. Treasures tables from old-school D&D use this format.
                        - 'hexflower': the table is represented in json as a hexflower, and result navigation is done step by step. See https://goblinshenchman.wordpress.com/hex-power-flower/ for a detailled explanation
                        - 'weighted-list': in a TSV list, each item is preceded by a weight indicating the chance to be selected. Does not support custom dice formulae for now.
                        - 'template': the provided file is not a random table, but should simply be printed to the output with the inline rolls processed. Useful if you want to format rolling on multiple tables at once.

                        See the 'examples/' folder in the github repo (github.com/freohr/rpg-table-roller) for example table files of the supported formats.
  -x, --ext             Attempt to load the table using its file extension to determine the format. Valid extensions are the list of formats from the `--format` option, with dashes (-) converted to underscores (_) 

Roll Options:
  -c COUNT, --count COUNT
                        How many rolled results do you want from the table? (defaults to 1 result)
  -e, --exclusive       Each result can be rolled at most once
  -d DICE_FORMULA, --dice-formula DICE_FORMULA
                        Custom dice formula to roll on the table. Keep it simple (XdY±Z)
  --clamp               Force roll result between first and last element. No effect if not using a custom formula.

Hex-flower Options:
  -s START, --start START
                        Change the hex number that navigation starts from

Output Options:
  -o OUTPUT, --output OUTPUT
                        Text file to output the rolled results. Note: Contents will be overwritten.
  -a, --append          Append the rolled results to the output file. No effect when printing to STDOUT
  -j JOIN, --join JOIN  Join the result as a single line string in the output with the provided string. Useful when rolling multiple times on the same chance table, as the results will be aggregated for each set of rolls on the provided table.
```

Example tables are in the [`examples/`](examples/) folder in this repo.

### Inline rolling options

This program allows recursive rolling with the `[[...]]` notation, which can be used for two purposes: Inlining dice rolls in a result (to have a random number generated as part of the result), or recursively rolling on another (or on the same) table.

Dice notation, when used inline, should follow the same rules as the `-d` option of the main program, i.e. keep it as simple as `XdY±Z`.

When such a notation is encountered with a filename, the program will look up the linked table using **relative pathing** (e.g. `[[other-table]]` should be in the same directory, `[[../other-table]]` should be in the parent folder of the current table, `[[other-folder/other-table]]` should be in the `other-folder` folder located in the current folder). Those tables can link to other tables in turn, enabling you to create a full-fledged procedural generator by simply writing lists in text files.

**Important note:** Internally, `rolltable` caches the inline tables it encounters during an execution to reduce the amount of file opening and closing it does, using the table file name: This means that you should make sure that your tables have different names if they link to each other, to avoid overwriting the cached data with something unrelated.

#### Options

The inline recursive table roller can be further customized with colon options, which are as follows:

- `:e`: Force the rolled results to be _exclusive_ when the inline table is present twice or more in the same initial result. Note that this only applies for multiple inline replacements in a single result and when the inline table is either referenced more than once, or if the additional option `:c` is used to roll multiple results at once.
- `:d` followed by a number or a dice-notation string: Change the dice formula used to rolled on the inline table.
- `:cl`: Clamp the inlined results to the values present on the inline table. Same as the `--clamp` option on the command-line, it only has an effect when combined with a custom dice formula.
- `:f` followed by the name of one of the format: Specifies the list format of the inlined list. Defaults to `list`, like the program option of the same name
- `:c` followed by a number or a dice-notation string: Change the number of results rolled from 1 to many, to inline multiple results. Defaults to 1 inlined result, must be greater than or equal to 0 (but it will inline an empty string in this case)
- `:j` followed by a string: Specifies how to join the many-rolled results in the replacement string when used with `:c`. Defaults to `,`, and has no effect when used with the default `:c` value.
- `:x`: Like the option `--ext`, will attempt to determine the table format from its file extension

Those options can be combined (and the `:cl` option doesn't even do anything on its own) to further specify the behavior of the inline roller for this specific inlined result. For example, if you want one of your results to be `Roll twice on this table, rerolling duplicates`, you can have the last result (of your arbitrary 10 results for example) written as `[[this-table:e:dd9]] and [[this-table:e:dd9]]` to enable a 1-in-10 reroll on this table, selecting two exclusive results that are not the reroll.

## Contributing

As this app is currently in early development, I'm not looking for contribution or feature suggestions. If you use this and encounter a bug, you can open an issue, and I'll see what I can do.

If you still want to look around the code, I've set up a Makefile with the basic following basic commands

- `make init`: Inside your dedicated Python 3 virtualenv (or venv, or what you prefer), will install the dependencies via pip
- `make build`: Using PyInstaller, will create a contained one-file executable, because I want to provide this as-is to you and not pollute your global environment by installing dependencies
- `make install`: Rebuild the executable, then make a copy to your session local binary dir (`/home/$USER/.local/bin`), ready to be used anywhere (if you have the folder in your `$PATH`)
