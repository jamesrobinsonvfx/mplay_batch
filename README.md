# MPlay Batch
Menu add-on for MPlay to quickly batch write sequences.

[Add some pictures and gifs and stuff] [Maybe try a gh-pages]

By default, each sequence is saved like this:

`{FLIPBOOK_DIR}/{HIPNAME}_{SUB_VERSION}/{HIPNAME}_{SUB_VERSION}_{SEQUENCE_INDEX}.$F.{EXT}`

## Some example paths:

[Add these]

# Installation
Installing is easy using [Houdini Packages](https://www.sidefx.com/docs/houdini/ref/plugins.html).

You can copy this entire folder to anywhere that packages are scanned for.
Easiest is probably in your `HOUDINI_USER_PREF_DIR/packages` folder. Once you've moved
it there, just copy/move the package file `mplay_batch.json` directly into `HOUDINI_USER_PREF_DIR/packages`.
The package is setup by default for this configuration.

If you'd like to keep this package somewhere else, simply modify the `MPLAY_BATCH_INSTALL_DIR` key to something else, ie
`"$HOME/dev/mplay_batch"` or `"C:/Users/James/houdini_tools/mplay_batch"`. Just make sure that the `mplay_batch.json` file still lives in that `packages` folder.

## Quick Installation

1. Download
2. Copy entire folder to `$HOUDINI_USER_PREF_DIR/packages`
3. Copy `mplay_batch.json` to `$HOUDINI_USER_PREF_DIR/packages`

    And you're all set!


# Customization
There are a few parameters that can be customized via environment variables. The easiest place to set these would be in the package itself, though as long as they're set _somewhere_ (system variables, .bashrc, etc) they should be fine.

## Defaults:

| Environment Variable       | Default   | Description                                      |
|----------------------------|-----------|--------------------------------------------------|
|MPLAY_BATCH_FLIPBOOK_DIR    |`$JOB/flip`| Where sequences get saved<sup>1</sup>
|MPLAY_BATCH_EXTENSION       |`jpg`      | Image type to save
|MPLAY_BATCH_PAD_SUB_VERSION |`3`        | Zero Padding to add to the "Sub-version" suffix
|MPLAY_BATCH_PAD_SEQ_INDEX   |`0`        | Zero Padding to add to each sequence's suffix

<sup>1</sup> *This directory __must__ exist. It will not be created automatically!*

## Custom Variables, $JOB, $HIP, etc.
To use custom variables in the file pattern for `MPLAY_BATCH_FLIPBOOK_DIR`, just wrap it in `__` instead of using `$`.
Example, to use `$HIP/flipbooks` as the default saving location:

`"__HIP__/flipbooks"`

## Examples
Here are some examples you can add to the `env` key in the package file.
```json
...
},
{
    "MPLAY_BATCH_FLIPBOOK_DIR": "__JOB__/renders/flipbooks"
},
{
    "MPLAY_BATCH_EXTENSION": "png"
},
{
    "MPLAY_BATCH_PAD_SEQ_INDEX": "2"
},
{
    "MPLAY_BATCH_PAD_SUB_VERSION": "4"
}
```

# Notes
* Scripting for MPlay is a bit limited at the moment, as there is no official HOM interface. Everything gets scripted with HScript, and there is no access to `hou.ui` when running MPlay.
If this is ever addressed, I'll be sure to modify the code to be a bit sleeker and have some more options!

* The `mplay_batch` package location must be appended to `PYTHONPATH` for this plugin to be picked up by MPlay. Modifying `HOUDINI_PATH` and having a `python2.7libs` directory alone is not enough (that's why it's there explicitly in the package definition).

* The entire frame range will be written for each sequence.

# Future
* Could make naming more customizable
* __Save All Viewers__ option if I can figure out why only 1 viewer is listed when several are open!
* Verbosity, prints, logging.