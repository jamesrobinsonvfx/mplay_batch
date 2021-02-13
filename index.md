---
vimeo_id: 508260914
---
# MPlay Batch

Menu add-on for MPlay to quickly batch write sequences.

![MPlay Batch Menu](assets/images/menu.png)

{% include vimeo_player.html id=page.vimeo_id %}

## Quick Installation ##

1. Download and extract into `mplay_batch`
2. Copy the entire `mplay_batch` folder to `$HOUDINI_USER_PREF_DIR/packages`
3. Copy `mplay_batch.json` to `$HOUDINI_USER_PREF_DIR/packages`

![Installation Filesystem Example](assets/images/installation_example.png)

And you're all set!

# Overview #
- [MPlay Batch](#mplay-batch)
	- [Quick Installation](#quick-installation)
- [Overview](#overview)
- [Features](#features)
	- [Save Current Sequence](#save-current-sequence)
	- [Save All Sequences](#save-all-sequences)
	- [Open Flipbook Directory](#open-flipbook-directory)
	- [Example: Naming](#example-naming)
- [Installation](#installation)
- [Customization](#customization)
	- [Defaults](#defaults)
	- [Custom Variables, `$JOB`, `$HIP`, etc.](#custom-variables-job-hip-etc)
		- [Example: Use a built-in Houdini Variable](#example-use-a-built-in-houdini-variable)
		- [Example: Editing the Package File](#example-editing-the-package-file)
- [Notes](#notes)
- [Future](#future)


MPlay (the built-in tool for reviewing flipbooks) comes with a really useful
feature for reviewing sequences, called the __Sequence List__. If you're not
familiar, if you click the filmstrip icon ![Filmstrip
Icon](assets/images/filmstrip_icon.png) instead of hitting <kbd>esc</kbd> or the
little red x, MPlay will start writing a new sequence to memory, while keeping
the previous one available for viewing and comparison.

![Sequence List Only Demo](assets/images/sequence_list_only.mp4)

However, if you want to save the sequences out, it can be a little tedious doing
them one by one! That's where __MPlay Batch__ comes in.


Read more about the [Sequence
List here](https://www.sidefx.com/docs/houdini/mplay/mplay_sequence_dialog.html).


# Features #
## Save Current Sequence ##

Saves the currently selected sequence to a directory.

![Save Current Sequence](assets/images/save_current_repeat.gif)

## Save All Sequences ##

Saves all loaded sequences to a directory.

![Save All Sequences](assets/images/save_all.gif)

## Open Flipbook Directory ##

Launches the system's file browser and navigates to the base flipbook directory (as set by `MPLAY_BATCH_FLIPBOOK_DIR`)

![Open Flipbook Directory](assets/images/open_flipbook_dir.gif)

By default, each sequence is saved like this:

```
{FLIPBOOK_DIR}/{HIPNAME}_{SUB_VERSION}/{HIPNAME}_{SUB_VERSION}_{SEQ_INDEX}.$F.{EXT}
```

![Naming Breakdown](assets/images/name_breakdown.png)

## Example: Naming ##

So if you're working in a hipfile called `myproj_sickexplosion_v002.hip`, and you ran _Save Current Sequence_ for the first time, it would be saved as:

```
$JOB/flip/myproj_sickexplosion_v002_000/myproj_sickexplosion_v002_000_0.$F.jpg
```

Each time you run _Save Current Sequence_, a new `SUB_VERSION` folder is created inside the `FLIPBOOK_DIR`. This helps keep subsequent writes unique.

![New Sub-Version Directory](assets/images/new_sub_version.png)

When running _Save All Sequences_, all sequences loaded in memory are written to disk inside of a single `SUB_VERSION` folder. Each sequence has a unique `SEQUENCE_INDEX` suffix appended to it. In general, they _should_ write to disk in the same order they were written, however this is not guaranteed.

![Multiple Sequence Save Result](assets/images/multi_sequence_scroll.png)



# Installation #

Installation is easy using [Houdini Packages](https://www.sidefx.com/docs/houdini/ref/plugins.html).

You can copy this entire folder to anywhere that packages are scanned for. Easiest is probably in your `HOUDINI_USER_PREF_DIR/packages` folder. Once you've moved it there, just copy/move the package file `mplay_batch.json` directly into `HOUDINI_USER_PREF_DIR/packages`. The package is set up by default for this configuration.

If you'd like to keep this package somewhere else, simply modify the `MPLAY_BATCH_INSTALL_DIR` key to something else, ie `"$HOME/dev/mplay_batch"` or `"C:/Users/James/houdini_tools/mplay_batch"`. Just make sure that the `mplay_batch.json` file still lives in a packages folder that Houdini will scan.

[Back to top](#overview)

# Customization #

There are a few parameters that can be customized via environment variables. The easiest place to set these would be in the package itself, though as long as they're set _somewhere_ (system variables, .bashrc, etc) they should be fine.

## Defaults ##

| Environment Variable          | Default     | Description                                     |
| ----------------------------- | ----------- | ----------------------------------------------- |
| `MPLAY_BATCH_FLIPBOOK_DIR`    | `$JOB/flip` | Where sequences get saved<sup>1</sup>           |
| `MPLAY_BATCH_EXTENSION`       | `jpg`       | Image type to save                              |
| `MPLAY_BATCH_PAD_SUB_VERSION` | `3`         | Zero Padding to add to the "Sub-version" suffix |
| `MPLAY_BATCH_PAD_SEQ_INDEX`   | `0`         | Zero Padding to add to each sequence's suffix   |

<sup>1</sup> *This directory __must__ exist. It will not be created
automatically!* `$JOB/flip` is the default naming when creating a project using
Houdini's built-in `File > New Project` dialog.

## Custom Variables, `$JOB`, `$HIP`, etc. ##

To use custom variables in the file pattern for `MPLAY_BATCH_FLIPBOOK_DIR`, just wrap it in `__` instead of starting with `$`.

### Example: Use a built-in Houdini Variable ###

Use `$HIP/flipbooks` as the default saving location:

`"__HIP__/flipbooks"`


### Example: Editing the Package File ###

Here are some examples you can add to the `env` key in the package file:

```json
{
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
	"MPLAY_BATCH_PAD_SUB_VERSION": "4"
}
```

[Back to top](#overview)

# Notes #

* Scripting for MPlay is a bit limited at the moment, as there is no HOM interface. Everything gets scripted with HScript, and there is no access to `hou.ui` when running MPlay. If this is ever addressed, I'll be sure to modify the code to be a bit sleeker, and have some more options!

* The `mplay_batch` package location must be appended to `PYTHONPATH` for this plugin to be picked up by MPlay. Modifying `HOUDINI_PATH` and having a `python2.7libs` directory alone is not enough (that's why it's set explicitly in the package definition).

* The entire frame range will be written for each sequence

[Back to top](#overview)

# Future #

* Could make naming more customizable
* __Save All Viewers__ option if I can figure out why only one viewer is listed when several are open!
* Verbosity, prints, logging
* See if adding a PySide dialog works

[Back to top](#overview)
