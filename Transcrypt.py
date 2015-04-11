'''
@name     Transcrypt
@package  sublime_plugin
@author   Elliot Marsden

This Sublime Text 3 plugin adds AES encryption/decryption
features to the right click context menu.

Usage: Make a selection (or not), Choose AES Encrypt or AES Decrypt
from the context menu and then enter a password

'''

import sublime
import sublime_plugin
import base64
import bisect
import os
from sys import platform as _platform
from sys import maxsize as _maxsize
import sys


BASE_PATH = os.path.abspath(os.path.dirname(__file__))
CRYPTO_PATH = os.path.join(BASE_PATH, "Crypto")

is_python3 = sys.version_info[0] > 2

AES = None


def get_zipfile_path():
    '''
    Return the zipfile path according to the platform.
    '''
    if _platform == "darwin":
        # OS X
        zip_fname = "macos.zip"
    elif _platform == "linux" or _platform == "linux2":
        # linux
        is_64bits = _maxsize > 2 ** 32
        if is_64bits:
            zip_fname = "linux64.zip"
        else:
            zip_fname = "linux32.zip"
    elif _platform == "win32":
        # Windows
        is_64bits = _maxsize > 2 ** 32
        if is_64bits:
            zip_fname = "win64.zip"
        else:
            zip_fname = "win32.zip"
    return os.path.join(CRYPTO_PATH, zip_fname)


def init():
    '''
    Load AES pre-built binaries.
    '''
    import zipfile
    try:
        from Transcrypt.Crypto import AES
    except ImportError:
        ZIP_FILE_PATH = get_zipfile_path()
        if os.path.isfile(ZIP_FILE_PATH):
            with zipfile.ZipFile(ZIP_FILE_PATH, "r") as f:
                f.extractall(CRYPTO_PATH)
        try:
            from Transcrypt.Crypto import AES
        except ImportError:
            raise Exception("Can not load AES, return")
            return
    globals()['AES'] = AES


class BadPaddingException(Exception):
    pass


class WrongPasswordException(Exception):
    pass


class TranscryptSaveCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        '''
        If encrypt on save is enabled, save just displays an encryption
        dialog, encrypts, then saves.
        If encrypt on save is disabled, just call normal save.
        '''
        def on_done(password):
            self.view.run_command(
                "transcrypt", {"enc": True, "password": password})
            self.view.run_command('save')

        # End edit immediately because we aren't doing any editing
        self.view.end_edit(edit)

        if self.view.settings().get('ON_SAVE'):
            message = "Create a Password:"
            self.view.window().show_input_panel(
                message, "", on_done, None, None)
        else:
            self.view.run_command('save')


class TranscryptToggleOnSaveCommand(sublime_plugin.WindowCommand):

    def run(self):
        view = self.window.active_view()
        on_save = view.settings().get('ON_SAVE')
        # This works even if setting not set: since 'not None == True'
        on_save = not on_save
        on_save_status = 'Encrypt on save' if on_save else ''
        view.settings().set('ON_SAVE', on_save)
        view.set_status('ON_SAVE', on_save_status)

    def is_checked(self):
        return bool(self.window.active_view().settings().get('ON_SAVE'))


class TranscryptPasswordCommand(sublime_plugin.WindowCommand):

    def run(self, enc):
        self.enc = enc
        message = "Create a Password:" if enc else "Enter Password:"
        self.window.show_input_panel(message, "", self.on_done, None, None)

    def on_done(self, password):
        try:
            if self.window.active_view():
                self.window.active_view().run_command(
                    "transcrypt", {"enc": self.enc, "password": password})
        except ValueError:
            pass


def panel(window, message):
    p = window.get_output_panel('transcrypt_error')
    p.run_command("transcrypt_message", {"message": message})
    p.show(p.size())
    window.run_command("show_panel", {"panel": "output.transcrypt_error"})


def key_round(key_b):
    '''
    Pad or truncate key_b (assumed to be bytes) as needed to be compatible
    with AES encryption: of length 16, 24 or 32.
    '''
    key_len = len(key_b)
    key_sizes = [16, 24, 32]
    # Pad
    if key_len < max(key_sizes):
        next_biggest = key_sizes[bisect.bisect_left(key_sizes, key_len)]
        return key_b + (next_biggest - key_len) * b'\0'
    # Truncate
    else:
        return key_b[:max(key_sizes)]


def crypt(key_text, input_text, enc):
    '''
    Encrypt ('enc' == True) or decrypt ('enc' == False) unicode string
    'input_text' using AES algorithm using unicode string 'key_text'
    as the encryption key (padded or truncated as needed).
    '''
    key_b = key_text.encode('utf-8')
    key_b_round = key_round(key_b)
    secret = AES.new(key_b_round)
    input_b = input_text.encode('utf-8')

    if enc:
        undershoot = len(input_b) % AES.block_size
        input_b_pad = input_b + (AES.block_size - undershoot) * b'\0'
        output_b = base64.b64encode(secret.encrypt(input_b_pad))
        output_text = output_b.decode('utf-8')
    else:
        try:
            output_b_pad = secret.decrypt(base64.b64decode(input_b))
        except ValueError:
            raise BadPaddingException
        output_b = output_b_pad.rstrip(b"\0")
        try:
            output_text = output_b.decode('utf-8')
        except UnicodeError:
            raise WrongPasswordException

    return output_text


class TranscryptCommand(sublime_plugin.TextCommand):

    def run(self, edit, enc, password):
        # Save the document size
        view_size = self.view.size()
        # Get selections
        regions = self.view.sel()
        num = len(regions)
        x = len(self.view.substr(regions[0]))
        # Select the whole document if there is no user selection
        if num <= 1 and x == 0:
            regions.clear()
            regions.add(sublime.Region(0, view_size))

        # For each text selection region
        for region in regions:
            data = self.view.substr(region)
            # Encrypt or decrypt selection
            try:
                result = crypt(password, data, enc)
            except WrongPasswordException:
                panel(self.view.window(), "Error: Wrong password")
                result = ''
            except BadPaddingException:
                panel(self.view.window(),
                      "Error: Input is not valid output of AES encryption, "
                      "sure it's been encrypted?")
                result = ''

            if result:
                # Replace selection with encrypted output
                self.view.replace(edit, region, result)
        self.view.end_edit(edit)


def plugin_loaded():
    '''
    Load and unzip the pre-built binary files, if needed.
    '''
    sublime.set_timeout(init, 200)

##################
# Init plugin
if not is_python3:
    init()
