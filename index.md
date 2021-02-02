# MPlay Batch

Menu add-on for MPlay to quickly batch write sequences.

[PICS N GIFS HERE]

# Features
### Save Current Sequence

Saves the currently selected sequence to a directory.

### Save All Sequences

Saves all loaded sequences to a directory.

### Open Flipbook Directory

Launches the system's file browser and navigates to the base flipbook directory (as set by `MPLAY_BATCH_FLIPBOOK_DIR`)


By default, each sequence is saved like this:

```
{FLIPBOOK_DIR}/{HIPNAME}_{SUB_VERSION}/{HIPNAME}_{SUB_VERSION}_{SEQUENCE_INDEX}.$F.{EXT}
```

So if you're working in a hipfile called `myproj_sickexplosion_v002.hip`, and you ran _Save Current Sequence_ for the first time, it would be saved as:

```
$JOB/flip/myproj_sickexplosion_v002_000/myproj_sickexplosion_v002_000_0.$F.jpg
```

Each time you run _Save Current Sequence_, a new `SUB_VERSION` folder is created inside the `FLIPBOOK_DIR`. This helps keep subsequent writes unique.

[ PIC HERE ]

When running _Save All Sequences_, all sequences loaded in memory are written to disk inside of a single `SUB_VERSION` folder. Each sequence has a unique `SEQUENCE_INDEX` suffix appended to it. In general, they _should_ write to disk in the same order they were written, however in my testing I found that this is not guaranteed. 

[PIC HERE]



# Installation

## Quick Installation
1. Download
2. Copy the entire folder to `$HOUDINI_USER_PREF_DIR/packages`
3. Copy `mplay_batch.json` to `$HOUDINI_USER_PREF_DIR/packages`
   And you're all set!

Installation is easy using [Houdini Packages](link).

You can copy this entire folder to anywhere that packages are scanned for. Easiest is probably in you `HOUDINI_USER_PREF_DIR/packages` folder. Once you've moved it there, just copy/move the package file `mplay_batch.json` directly into `HOUDINI_USER_PREF_DIR/packages`. The package is set up by default for this configuration. 

If you'd like to keep this package somewhere else, simply modify the `MPLAY_BATCH_INSTALL_DIR` key to something else, ie `"$HOME/dev/mplay_batch` or `"C:/Users/James/houdini_tools/mplay_batch"`. Just make sure that the `mplay_batch.json` file still lives in a packages folder that Houdini will scan.


# Customization

There are a few parameters that can be customized via environment variables. The easiest place to set these would be in the package itself, though as long as they're set _somewhere_ (system variables, .bashrc, etc) they should be fine.

## Defaults:
|Environment Variable           |Default    |Description |
|-------------------------------|-----------|------------|
|`MPLAY_BATCH_FLIPBOOK_DIR`     |`$JOB/flip`| Where sequences get saved [^1]
|`MPLAY_BATCH_EXTENSION`        |`jpg`      | Image type to save
|`MPLAY_BATCH_PAD_SUB_VERSION`  |`3`        | Zero Padding to add to the "Sub-version" suffix
|`MPLAY_BATCH_PAD_SEQ_INDEX`    |`0`        | Zero Padding to add to each sequence's suffix

[^1] *This directory __must__ exist. It will not be created automatically!*

## Custom Variables, `$JOB`, `$HIP`, etc.

To use custom variables in the file pattern for `MPLAY_BATCH_FLIPBOOK_DIR`, just wrap it in `__` instead of starting with `$`.

Example:

Use `$HIP/flipbooks" as the default saving location:

`"__HIP__"/flipbooks"


## Examples

Here are some examples you can add to the `env` key in the package file:

```json
...
},
{
	"MPLAY_BATCH_FLIPBOOK_DIR": "__JOB__/renders/flipbook"
},
{
	"MPLAY_BATCH_EXTENSION": "png"
},
{
	"MPLAY_BATCH_PAD_SEQ_INDEX": "2"
},
{
	"MPLAY_BATCH_PAD_SUB_VERSION: "4"
}
```

# Notes

* Scripting for MPlay is a bit limited at the moment, as there is no HOM interface. Everything gets scripted with HScript, and there is no access to `hou.ui` when running MPlay. If this is ever addressed, I'll be sure to modify the code to be a bit sleeker, and have some more options!

* The `mplay_batch` pacakge location must be appended to `PYTHONPATH` for this plugin to be picked up by MPlay. Modifying `HOUDINI_PATH` and having a `python2.7libs` directory alond is not enough (that's why it's set explicitly in the package definition).

* The entire frame range will be written for each sequence

# Future

* Could make naming more customizable
* __Save All Viewers__ option if I can figure out why only one viewer is listed when several are open!
* Verbosity, prints, logging
