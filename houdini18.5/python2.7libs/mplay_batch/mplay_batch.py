"""MPlay Batch Save Utilities"""
import errno
import glob
import os
import re
import shlex
import subprocess
import sys

from distutils.spawn import find_executable

import hou


class EnvironmentVariableTypeError(TypeError):
    """Error for bad environment variable types."""

    def __init__(self, var_name, correct_type_name):
        self.message = (
            "{{{0}}} : Invalid type for env variable. Must be <{1}>".format(
                var_name, correct_type_name))
        super(EnvironmentVariableTypeError, self).__init__(self.message)

    def __str__(self):
        return self.message


class EnvironmentVariableValueError(ValueError):
    """Error for bad environment variable values."""

    def __init__(self, var_name):
        self.message = "{{{0}}} : Value out of range".format(var_name)

        super(EnvironmentVariableValueError, self).__init__(self.message)

    def __str__(self):
        return self.message


class MissingFFmpegError(EnvironmentError):
    """Error for missing ffmpeg executable"""

    def __str__(self):
        return (
            "Missing ffmpeg executable."
            "Please make sure it is installed and available "
            "on the system's PATH"
        )


class UnsupportedVideoFormatError(ValueError):
    """Error for an invalid video type."""

    def __init__(self, video_format):
        self.message = (
            "\"{0}\" is not currently supported by MPlay Batch. "
            "Supported formats include:\n{1}".format(
                video_format,
                "\n".join(Environment.valid_video_formats)
            )
        )
        super(UnsupportedVideoFormatError, self).__init__(self.message)

    def __str__(self):
        return self.message


class Environment(object):
    """Object to initialize and store information about the session."""

    # Can add more as they come up. Just a starting point.
    valid_video_formats = ["mp4", "mov"]
    if "win32" in sys.platform:
        win_formats = ["avi"]
        valid_video_formats.extend(win_formats)

    def __init__(
            self,
            ext="jpg",
            video_format="mp4",
            flipbook_dir="$JOB/flip",
            pad_sub_version=3,
            pad_seq_index=0
    ):
        self._ext = ""
        self._video_format = ""
        self._flipbook_dir = ""
        self._pad_sub_version = 3
        self._pad_seq_index = 0
        try:
            self.ext = os.environ["MPLAY_BATCH_EXTENSION"]
        except KeyError:
            self.ext = ext
        try:
            self.video_format = os.environ["MPLAY_BATCH_VIDEO_FORMAT"]
        except KeyError:
            self.video_format = video_format
        try:
            self.flipbook_dir = os.environ["MPLAY_BATCH_FLIPBOOK_DIR"]
        except KeyError:
            self.flipbook_dir = flipbook_dir
        try:
            self.pad_sub_version = os.environ["MPLAY_BATCH_PAD_SUB_VERSION"]
        except KeyError:
            self.pad_sub_version = pad_sub_version
        try:
            self.pad_seq_index = os.environ["MPLAY_BATCH_PAD_SEQ_INDEX"]
        except KeyError:
            self.pad_seq_index = pad_seq_index

        self.fps = hou.fps()

    @property
    def ext(self):
        """Image file type.

        :param extension: File extension to use when writing sequences
        :type extension: str
        """
        return self._ext

    @ext.setter
    def ext(self, extension):
        self._ext = re.sub(r"(\.?)(\w*\d*\.*)", r"\2", extension)

    @property
    def video_format(self):
        """Video format to write with ffmpeg.

        :param extension: Video format
        :type extension: str
        """
        return self._video_format

    @video_format.setter
    def video_format(self, extension):
        format_ = re.sub(r"(\.?)(\w*\d*\.*)", r"\2", extension)
        if format_ in self.valid_video_formats:
            self._video_format = format_
        else:
            raise UnsupportedVideoFormatError(format_)

    @property
    def flipbook_dir(self):
        """Validate existence of and set flipbook directory to write to.

        :param dir_: Directory to write flipbook sequences into
        :type dir_: str
        """
        return self._flipbook_dir

    @flipbook_dir.setter
    def flipbook_dir(self, dir_):
        # Replace everything surrounded by __ with a $ prefix
        dir_ = re.sub(r"__(\w+)__", r"$\1", dir_)
        dir_ = hou.expandString(dir_)
        if not os.path.exists(dir_):
            raise OSError("Flipbook directory {0} does not exist".format(dir_))
        if not os.path.isdir(dir_):
            raise ValueError("{0} is not a directory".format(dir_))
        self._flipbook_dir = dir_

    @property
    def pad_sub_version(self):
        """Set the zero-padding for the subversion suffix.

        :param padding: Number of digits to zfill
        :type padding: int
        """
        return self._pad_sub_version

    @pad_sub_version.setter
    def pad_sub_version(self, padding):
        self._pad_sub_version = self._validate_padding(
            padding, "MPLAY_BATCH_PAD_SUB_VERSION")

    @property
    def pad_seq_index(self):
        """Set the zero-padding for the individual sequence.

        :param padding: Number of digits to zfill
        :type padding: int
        """
        return self._pad_seq_index

    @pad_seq_index.setter
    def pad_seq_index(self, padding):
        self._pad_seq_index = self._validate_padding(
            padding, "MPLAY_BATCH_PAD_SEQ_INDEX")

    @staticmethod
    def _validate_padding(padding, var_name):
        try:
            padding = int(padding)
        except ValueError:
            raise EnvironmentVariableTypeError(var_name, "int")
        if padding < 0:
            raise EnvironmentVariableValueError(var_name)
        return padding

    @staticmethod
    def check_toggle_variable(var):
        """Check the state of menu toggle's variable.

        :param var: Variable to check
        :type var: str
        :return: Variable value. -1 if any undefined input
        :rtype: int
        """
        value = -1
        try:
            value = int(hou.getenv(var))
        except (ValueError, TypeError):
            value = 0
        return value


class SequenceDir(object):
    """A place to write sequences into."""

    def __init__(self, name, env):
        self._env = None
        self._name = ""
        self._dirname = ""
        self._sub_version = None

        self.env = env
        self.name = name

    @property
    def name(self):
        """Name of the sequence, typically based on $HIPNAME.

        :param new_name: What to call the sequence
        :type new_name: str
        """
        return self._name

    @name.setter
    def name(self, new_name):
        idx = new_name.rfind(".hip")
        self._name = new_name[:idx] if idx >= 0 else new_name
        self._update()

    @property
    def env(self):
        """Environment object used to create paths.

        :param new_env: Evironment settings to use for this sequence
        :type new_env: :class:`Environment`
        """
        return self._env

    @env.setter
    def env(self, new_env):
        if isinstance(new_env, Environment):
            self._env = new_env
        else:
            self._env = None
        self._update()

    @property
    def dirname(self):
        """Full path to the directory where the sequence will write."""
        return self._dirname

    @property
    def sub_version(self):
        """Sub-version number for this sequence."""
        return self._sub_version

    def _next_sub_version(self):
        """Determine the next subversion based on the sequence name."""
        regex = re.compile(r"{0}_(\d+)".format(self.name))
        dirs = [
            item for item in os.listdir(self.env.flipbook_dir)
            if os.path.isdir(os.path.join(self.env.flipbook_dir, item))
            and regex.match(item)
        ]
        next_sub_version = 0
        if dirs:
            dirs = sorted(dirs, key=lambda x: int(regex.match(x).group(1)))
            next_sub_version = int(regex.match(dirs[-1]).group(1)) + 1
        return str(next_sub_version).zfill(self.env.pad_sub_version)

    def _update(self):
        """Update internal attributes used for creating paths."""
        self._sub_version = self._next_sub_version()
        self._dirname = os.path.join(
            self.env.flipbook_dir,
            "{0}_{1}".format(self._name, self._sub_version)
        ).replace(os.sep, "/")
        if not os.path.isdir(self.dirname):
            self._create_dir()

    def _create_dir(self):
        # Only try to create once all these are valid
        if self.name and self.env and self.sub_version:
            try:
                os.makedirs(self.dirname)
            except OSError as error:
                # Fine if it exists, but raise if not
                if error.errno != errno.EEXIST:
                    raise


class Sequence(object):
    """Sequence to write to disk."""

    def __init__(self, seq_dir, index=0):
        self._seq_dir = None
        self._index = 0
        self._basename = ""
        self.seq_dir = seq_dir
        self.index = index

    @property
    def seq_dir(self):
        """Sequence location to write to.

        :param new_seq_dir: Sequence Directory instance
        :type new_seq_dir: :class:`SequenceDirectory`
        """
        return self._seq_dir

    @seq_dir.setter
    def seq_dir(self, new_seq_dir):
        if isinstance(new_seq_dir, SequenceDir):
            self._seq_dir = new_seq_dir
        else:
            self._seq_dir = None
        self._basename = self._format_basename()

    @property
    def index(self):
        """Unique index number for this sequence.

        :param new_index: Index number, starting at 0
        :type new_index: int
        """
        return self._index

    @index.setter
    def index(self, idx):
        self._index = idx
        self._basename = self._format_basename()

    @property
    def basename(self):
        """HScript-friendly basename for this sequence."""
        return self._basename

    @property
    def path(self):
        """Full path to this sequence."""
        # Avoid os.path.join to preserve escape characters on windows
        return "{0}/{1}".format(self.seq_dir.dirname, self.basename)

    @property
    def glob_pattern(self):
        """Path to this sequence with glob pattern for frame number.

        :return: Glob-patterned file name
        :rtype: str
        """
        return "{0}/{1}".format(
            self.seq_dir.dirname,
            self._format_basename(frame_symbol=r"[0-9]*")
        )

    @property
    def video_path(self):
        """Path to the video component of this sequence.

        :return: Path to the video
        :rtype: str
        """
        return "{0}/{1}_{2}_{3}.{4}".format(
            self.seq_dir.dirname,
            self.seq_dir.name,
            str(self.seq_dir.sub_version),
            str(self.index).zfill(self.seq_dir.env.pad_seq_index),
            self.seq_dir.env.video_format
        )

    def _format_basename(self, frame_symbol=r"\$\F"):
        """Format an HScript friendly basename for this sequence."""
        return r"{0}_{1}_{2}.{3}.{4}".format(
            self.seq_dir.name,
            str(self.seq_dir.sub_version),
            str(self.index).zfill(self.seq_dir.env.pad_seq_index),
            frame_symbol,
            self.seq_dir.env.ext
        )

    def __str__(self):
        return "Sequence: {0} at {1}".format(self.seq_dir.name, self.path)


class SequenceWriter(object):
    """Handles writing sequences from MPlay."""

    def __init__(self, env, video=False, keep_video_source=False):
        self.env = env
        self.video = video
        self.keep_video_source = keep_video_source
        self.location = SequenceDir(hou.hipFile.basename(), env)
        self.cmds = {"hscript": [], "ffmpeg": []}
        self.seqs = []
        if self.video:
            if not find_executable("ffmpeg"):
                raise MissingFFmpegError

    def execute(self):
        """Run through command queue."""
        # Write image sequence to disk
        for cmd in self.cmds["hscript"]:
            hou.hscript(cmd)
        # Create video using ffmpeg
        for cmd in self.cmds["ffmpeg"]:
            result = subprocess.check_call(cmd)
            if result != 0:
                raise hou.Error("Something went wrong")
        # Remove image sequence source when writing a video
        if self.video and not self.keep_video_source:
            for seq in self.seqs:
                self.remove_image_sequence(seq)

    @staticmethod
    def remove_image_sequence(seq):
        """Remove an image sequence from disk.

        :param seq: Sequence to remove
        :type seq: :class:`Sequence`
        """
        files = glob.glob(seq.glob_pattern)
        for file_ in files:
            try:
                os.remove(file_)
            except OSError:
                continue  # For now...

    def save_current(self):
        """Save the currently selected sequence to disk."""
        seq = Sequence(self.location)
        self.cmds["hscript"].append("imgsave -a {0}".format(seq.path))
        self.seqs.append(seq)
        if self.video:
            self.cmds["ffmpeg"].append(self.format_ffmpeg_cmd(seq, self.env))
        return self

    def save_all_seqs(self):
        """Save all sequences in the Sequence List to disk."""
        seqls = hou.hscript("seqls")[0].split("\n")[:-1]
        for i, seq_name in enumerate(seqls):
            seq = Sequence(self.location, index=i)
            self.cmds["hscript"].append(
                "imgsave -s {0} -a {1}".format(seq_name, seq.path))
            self.seqs.append(seq)
            if self.video:
                self.cmds["ffmpeg"].append(
                    self.format_ffmpeg_cmd(seq, self.env))
        return self

    def save_all_viewers(self):
        """Save all open viewers to disk."""
        imgviews = hou.hscript("imgviewls")
        for i, view in enumerate(imgviews):
            seq = Sequence(self.location, index=i)
            self.cmds["ffmpeg"].append(
                "imgsave -a {0} {1}".format(seq.path, view))
            self.seqs.append(seq)
        return self

    @staticmethod
    def format_ffmpeg_cmd(seq, env):
        """Format a command for ffmpeg to export video

        :param seq: Sequence to render
        :type seq: :class:`Sequence`
        :param env: Current session/env settings
        :type env: :class:`Environment`
        :return: Shlex-formatted command list
        :rtype: list
        """
        # Fix for windows being windows...
        pattern_type = "glob"
        pattern = seq.glob_pattern
        if "win32" in sys.platform:
            pattern_type = "sequence"
            pattern = pattern.replace("[0-9]*", "%d")
        ffmpeg_cmd = (
            "ffmpeg -nostdin -framerate {0} -pix_fmt yuv420p -pattern_type {1}"
            " -i \"{2}\" \"{3}\" -c:v libx264 -movflags faststart ".format(
                env.fps, pattern_type, pattern, seq.video_path)
        )
        return shlex.split(ffmpeg_cmd)


def open_flipbook_dir(env):
    """Open the flipbook directory in the OS's file browser.

    :param env: Environment object to get directory from
    :type env: :class:`Environment`
    """
    if "win32" in sys.platform:
        os.startfile(env.flipbook_dir)
    elif "darwin" in sys.platform:
        os.system("open {0}".format(env.flipbook_dir))
    elif "linux" in sys.platform:
        os.system("gio open {0}".format(env.flipbook_dir))


def main(kwargs):
    """Entry point for the MPlay Batch program.

    :param kwargs: Houdini `kwargs` dict passed from the menu
    :type kwargs: dict
    :raises RuntimeError: Invalid tool selection
    """
    # Get the flipbook directory
    env = Environment()
    tool = kwargs["toolname"]

    # Open the flipbook dir
    if tool == "open_flipbook_dir":
        open_flipbook_dir(env)
        return

    # Check video options
    # TODO: Revert back to Radio Button style when RFE is fixed.
    keep_source = Environment.check_toggle_variable(
        "MPLAY_BATCH_KEEP_VIDEO_SOURCE")
    export_video = Environment.check_toggle_variable(
        "MPLAY_BATCH_OUTPUT_VIDEO")

    # Handle menu selection
    writer = SequenceWriter(
        env,
        video=export_video,
        keep_video_source=keep_source
    )
    try:
        command = getattr(writer, tool)
    except AttributeError:
        raise RuntimeError("Not a valid tool selection")
    command().execute()
