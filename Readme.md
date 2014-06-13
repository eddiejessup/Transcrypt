Transcrypt Sublime Text 3 Package
=================================
Encrypt and decrypt a document or selection(s) using PyCrypto using AES.

Install
-------
### Package Control
- See [here](http://wbond.net/sublime_packages/package_control) for instructions on installation of Package Control
- In Sublime Text, search for package 'Transcrypt'

### Manual
Clone this repository into `Sublime Text 3/Packages` using OS-appropriate location:

OSX:

    git clone git://github.com/eddiejessup/SublimeText-Transcrypt.git ~/Library/Application\ Support/Sublime\ Text\ 3/Packages/Transcrypt

Windows:

    git clone git://github.com/eddiejessup/SublimeText-Transcrypt.git "%APPDATA%\Sublime Text 3\Packages\Transcrypt"

Usage
-----
Access commands via:

- Right-click menu item `Transcrypt`
- Menu item `Tools -> Transcrypt`
- Default keyboard shortcuts:
  - Encrypt: `⌘+K, e` (OSX) or `ctrl+K, e` (Linux and Windows)
  - Decrypt: `⌘+K, d` (OSX) or `ctrl+K, d` (Linux and Windows)
  - Toggle 'encrypt on save' mode: `⌘+k, ⌘+e` (OSX) or `ctrl+k, ctrl+e` (Linux and Windows)

The commands work on a selection, multiple selections or if nothing is selected, the whole document. Once you trigger the command you will be prompted to enter a password.

### 'Encrypt on save'

If this mode is enabled, the default save shortcut (`⌘+s` in OSX or `ctrl+s` in Linux and Windows) instead opens a password encryption prompt, and only if a password is entered is the document encrypted and saved. If the encryption is cancelled, the file is not saved. This should help to prevent accidentally saving your private file in plaintext.

The mode is toggled on a per-file basis, and should persist as long as the file is open.

When the mode is enabled for a file, 'Encrypt on save' will appear in the status bar (lower left) when viewing that file.

Notes:

- The menu entry for `save` is not changed, so normal saving can still be done if required (or you can simply disable the mode).
- If you've changed the default key binding for `save` to something else, this won't be remapped automatically (though it can of course be changed manually)
- This feature is experimental, use at your own risk!

Requirements
------------
Due to containing C extension modules pre-compiled for Python 3.3, only Sublime Text 3 is supported.

Conflicts
------
Because this is essentially a fork of [Crypto](https://github.com/mediaupstream/SublimeText-Crypto), it uses the same default key bindings. They should otherwise happily coexist, so if you want to use both for some reason, change the key bindings of one.

About
-----
Based on [Crypto](https://github.com/mediaupstream/SublimeText-Crypto) by [Derek Anderson](https://github.com/mediaupstream) and [Richard Mitchell's fork](https://github.com/mitchellrj/pycrypto) of [PyCrypto](https://github.com/dlitz/pycrypto).

Identical interface to Crypto, but supporting much larger text selections by avoiding the subprocess interface.

Author & Contributors
---------------------
- [Elliot Marsden](https://github.com/eddiejessup)
- [Derek Anderson](http://twitter.com/derekanderson)
- [Isaac Muse](https://github.com/facelessuser)
- [Richard Mitchell](https://github.com/mitchellrj)
- [Dwayne Litzenberger](https://github.com/dlitz)

License
-------
MIT License
