# MPlay Batch
Menu add-on for MPlay to quickly batch write sequences.

For more info, see the [MPlay Batch GitHub Page](https://jamesrobinsonvfx.github.io/mplay_batch/)

## Quick Installation

### Option 1: Using Git

1. Navigate to where you want to put the package (probably `$HOUDINI_USER_PREF_DIR/packages`)
2. From a bash or git-bash shell, run `git clone https://github.com/jamesrobinsonvfx/mplay_batch.git`
3. Copy `mplay_batch/mplay_batch.json` to the same `packages` directory. (again, probably `$HOUDINI_USER_PREF_DIR/packages`)

### Option 2: Download Zip
1. Download the latest [.zip](https://github.com/jamesrobinsonvfx/mplay_batch/releases/latest/download/mplay_batch.zip) or [.tar.gz](https://github.com/jamesrobinsonvfx/mplay_batch/releases/latest/download/mplay_batch.tar.gz) from the [Releases Page](https://github.com/jamesrobinsonvfx/mplay_batch/releases/latest)
2. Extract the contents to `$HOUDINI_USER_PREF_DIR/packages/mplay_batch`
3. Copy `mplay_batch/mplay_batch.json` to `$HOUDINI_USER_PREF_DIR/packages`

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
