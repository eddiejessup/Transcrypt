"""
@name     Transcrypt
@package  sublime_plugin
@author   Elliot Marsden

This Sublime Text 3 plugin adds AES encryption/decryption
features to the right click context menu.

Usage: Make a selection (or not), Choose AES Encrypt or AES Decrypt
from the context menu and then enter a password
"""

import base64
import bisect
import os
import zipfile
import sys
from functools import partial

import sublime
import sublime_plugin


BASE_PATH = os.path.abspath(os.path.dirname(__file__))
CRYPTO_PATH = os.path.join(BASE_PATH, "Crypto")
IS_64BITS = sys.maxsize > 2 ** 32

# Set the zipfile path according to the platform.
if sys.platform == "darwin":
    # OS X
    ZIP_FILE_NAME = "macos.zip"
elif sys.platform in ("linux", "linux2"):
    # Linux.
    if IS_64BITS:
        ZIP_FILE_NAME = "linux64.zip"
    else:
        ZIP_FILE_NAME = "linux32.zip"
elif sys.platform == "win32":
    # Windows.
    if IS_64BITS:
        ZIP_FILE_NAME = "win64.zip"
    else:
        ZIP_FILE_NAME = "win32.zip"
ZIP_FILE_PATH = os.path.join(CRYPTO_PATH, ZIP_FILE_NAME)


AES = None


def init():
    """Load AES pre-built binaries."""
    try:
        from Transcrypt.Crypto import AES
    except ImportError:
        if os.path.isfile(ZIP_FILE_PATH):
            with zipfile.ZipFile(ZIP_FILE_PATH, "r") as f:
                f.extractall(CRYPTO_PATH)
        try:
            from Transcrypt.Crypto import AES
        except ImportError:
            raise Exception("Can't load AES")
    globals()['AES'] = AES


class BadPaddingException(Exception):
    pass


class WrongPasswordException(Exception):
    pass


C_PAD = b"\0"
KEY_SIZES = [16, 24, 32]


def normalize_key(key):
    """Pad or truncate a key to be compatible with AES encryption.

    Pad or truncate key (assumed to be bytes) as needed to be compatible
    with AES encryption.
    """
    key_len = len(key)
    # Pad
    if key_len < max(KEY_SIZES):
        next_biggest = KEY_SIZES[bisect.bisect_left(KEY_SIZES, key_len)]
        return key + (next_biggest - key_len) * C_PAD
    # Truncate
    else:
        return key[:max(KEY_SIZES)]


def decrypt_bytes(secret, s):
    """Decrypt byte string with a key.

    Decrypt byte string 's' with the AES algorithm using secret 'secret',
    removing padding as needed.
    """
    try:
        return secret.decrypt(base64.b64decode(s)).rstrip(C_PAD)
    except ValueError as e:
        raise BadPaddingException


def encrypt_bytes(secret, s):
    """Encrypt byte string with a key.

    Encrypt byte string 's' with the AES algorithm using secret 'secret',
    padded as needed.
    """
    pad_nr = AES.block_size - (len(s) % AES.block_size)
    return base64.b64encode(secret.encrypt(s + (pad_nr * C_PAD)))


def transcrypt_text(input_text, key_text, enc, encoding='utf-8'):
    secret = AES.new(normalize_key(key_text.encode(encoding)))
    crypt_bytes_func = encrypt_bytes if enc else decrypt_bytes
    output_bytes = crypt_bytes_func(secret, input_text.encode(encoding))
    try:
        return output_bytes.decode(encoding)
    except UnicodeError:
        if enc:
            raise
        else:
            raise WrongPasswordException


class SetContentsCommand(sublime_plugin.TextCommand):

    def run(self, edit, text):
        r = sublime.Region(0, self.view.size())
        self.view.replace(edit, r, text)
        self.view.end_edit(edit)


class ShowPanelMessageCommand(sublime_plugin.WindowCommand):

    def run(self, message):
        v = self.window.create_output_panel('transcrypt_error')
        v.run_command("set_contents", {"text": message})
        self.window.run_command(
            "show_panel",
            {"panel": "output.transcrypt_error"},
        )


def show_panel_message(window, message):
    window.run_command("show_panel_message", {"message": message})


def get_input(window, message, callback):
    window.show_input_panel(message, "", callback, None, None)


class TranscryptCommand(sublime_plugin.TextCommand):

    WRONG_PW_TEXT = "Error: Wrong password"
    BAD_INPUT_TEXT = ("Error: Input is not valid output of AES encryption, "
                      "sure it's been encrypted?")

    def run(self, edit, enc, password):
        # Save the document size.
        view_size = self.view.size()

        # Get selections.
        regions = self.view.sel()
        nr_regions = len(regions)
        # Select the whole document if there is no selection.
        if nr_regions <= 1 and len(self.view.substr(regions[0])) == 0:
            regions.clear()
            regions.add(sublime.Region(0, view_size))

        # For each text selection region.
        for region in regions:
            data = self.view.substr(region)
            try:
                # Encrypt or decrypt the selection.
                result = transcrypt_text(input_text=data,
                                         key_text=password,
                                         enc=enc)
            except WrongPasswordException:
                show_panel_message(self.view.window(), self.WRONG_PW_TEXT)
            except BadPaddingException:
                show_panel_message(self.view.window(), self.BAD_INPUT_TEXT)
            else:
                # Replace selection with encrypted output.
                self.view.replace(edit, region, result)
        self.view.end_edit(edit)


def transcrypt(enc, view, password):
    if view:
        view.run_command(
            "transcrypt",
            {"enc": enc, "password": password}
        )


encrypt = partial(transcrypt, True)
decrypt = partial(transcrypt, False)


class EncryptCommand(sublime_plugin.WindowCommand):

    SET_TEXT = "Set password:"
    CONFIRM_TEXT = "Confirm new password:"
    NO_MATCH_TEXT = "Error: Passwords do not match"

    def run(self, save=False):
        get_input(self.window, self.SET_TEXT,
                  partial(self.confirm_then_encrypt, save=save))

    def confirm_then_encrypt(self, password, save=False):
        def check_then_transcrypt(password_confirm):
            if password_confirm != password:
                show_panel_message(self.window, self.NO_MATCH_TEXT)
            else:
                view = self.window.active_view()
                encrypt(view=view, password=password)
                if save:
                    view.run_command('save')
        get_input(self.window, self.CONFIRM_TEXT, check_then_transcrypt)


class DecryptCommand(sublime_plugin.WindowCommand):

    ENTER_TEXT = "Enter password:"

    def run(self):
        get_input(self.window, self.ENTER_TEXT,
                  partial(decrypt, self.window.active_view()))


# Related to encrypt-on-save.

class TranscryptSaveCommand(sublime_plugin.TextCommand):

    DEFAULT = False
    ON_SAVE = 'ON_SAVE'

    @classmethod
    def on_save_is_active(cls, view):
        var = view.settings().get(cls.ON_SAVE)
        return cls.DEFAULT if var is None else var

    @property
    def is_active(self):
        return self.on_save_is_active(self.view)

    def run(self, edit):
        """Do relevant command.

        If encrypt on save is enabled, display an encryption dialog,
        encrypt, then save.
        If encrypt on save is disabled, just save.
        """

        # End edit immediately because we aren't doing any editing.
        self.view.end_edit(edit)

        if self.is_active:
            self.view.window().run_command("encrypt", {'save': True})
        else:
            self.view.run_command('save')


class ToggleEncryptOnSaveCommand(sublime_plugin.WindowCommand):

    ACTIVE_STATUS_TEXT = 'Encrypt on save'

    @property
    def active_view(self):
        return self.window.active_view()

    @property
    def is_active(self):
        return TranscryptSaveCommand.on_save_is_active(self.active_view)

    def run(self):
        view = self.active_view
        view.settings().set(TranscryptSaveCommand.ON_SAVE, not self.is_active)
        # Add status to the status bar, if active
        view.set_status(TranscryptSaveCommand.ON_SAVE,
                        self.ACTIVE_STATUS_TEXT if self.is_active else '')


def plugin_loaded():
    """Load and unzip the pre-built binary files, if needed."""
    sublime.set_timeout(init, 200)
