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
from Transcrypt.Crypto import AES


class AesCryptCommand(sublime_plugin.WindowCommand):

    def run(self, enc):
        self.enc = enc
        message = "Create a Password:" if enc else "Enter Password:"
        self.window.show_input_panel(message, "", self.on_done, None, None)
        pass

    def on_done(self, password):
        try:
            if self.window.active_view():
                self.window.active_view().run_command(
                    "transcrypt", {"enc": self.enc, "password": password})
        except ValueError:
            pass


class TranscryptMessageCommand(sublime_plugin.TextCommand):

    def run(self, edit, message):
        self.view.insert(edit, self.view.size(), message)


def panel(window, message):
    p = window.get_output_panel('transcrypt_error')
    p.run_command("transcrypt_message", {"message": message})
    p.show(p.size())
    window.run_command("show_panel", {"panel": "output.transcrypt_error"})


def key_round(key_b):
    key_len = len(key_b)
    key_sizes = [16, 24, 32]
    # Pad
    if key_len < max(key_sizes):
        next_biggest = key_sizes[bisect.bisect_left(key_sizes, key_len)]
        return key_b + (next_biggest - key_len) * b'\0'
    # Truncate
    else:
        return key_b[:max(key_sizes)]


def encrypt(key, clear_text):
    key_b = key.encode('utf-8')
    key_b_round = key_round(key_b)
    secret = AES.new(key_b_round)
    clear_text_b = clear_text.encode('utf-8')
    undershoot = len(clear_text_b) % AES.block_size
    tag_string = clear_text_b + (AES.block_size - undershoot) * b'\0'
    cipher_text = base64.b64encode(secret.encrypt(tag_string))
    return cipher_text.decode('utf-8')


def decrypt(key, cipher_text):
    key_b = key.encode('utf-8')
    key_b_round = key_round(key_b)
    secret = AES.new(key_b_round)
    cipher_text_bytes = cipher_text.encode('utf-8')
    raw_decrypted = secret.decrypt(base64.b64decode(cipher_text_bytes))
    clear_val = raw_decrypted.rstrip(b"\0")
    return clear_val.decode('utf-8')


def transcrypt(view, enc, password, data):
    if enc:
        result = encrypt(password, data)
    else:
        try:
            result = decrypt(password, data)
        except UnicodeError:
            panel(view.window(),
                  "Error: Output is not valid Unicode, wrong password?")
        except ValueError:
            panel(view.window(),
                  "Error: Input is not valid output of AES encryption, sure it's been encrypted?")
    return result


class TranscryptCommand(sublime_plugin.TextCommand):

    def run(self, edit, enc, password):
        # save the document size
        view_size = self.view.size()
        # get selections
        regions = self.view.sel()
        num = len(regions)
        x = len(self.view.substr(regions[0]))
        # select the whole document if there is no user selection
        if num <= 1 and x == 0:
            regions.clear()
            regions.add(sublime.Region(0, view_size))

        # encrypt / decrypt selections
        for region in regions:
            data = self.view.substr(region)
            results = transcrypt(self.view, enc, password, data)
            if results:
                self.view.replace(edit, region, results)
