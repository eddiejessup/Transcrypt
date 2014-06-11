Transcrypt Sublime Text 3 Package
=============================

### Encrypt/ Decrypt a document or selection(s) using PyCrypto


Install
-------
Installation via the [Package Control](http://wbond.net/sublime_packages/package_control) (Search for `Transcrypt`)
  
To install manually clone this project into your `Sublime Text 3/Packages` folder:

*OSX*

    git clone git://github.com/mediaupstream/SublimeText-Transcrypt.git ~/Library/Application\ Support/Sublime\ Text\ 2/Packages/Transcrypt


Usage
-----
After installation you will have:  

* Right-click menu item `Transcrypt` and `Tools > Transcrypt` with two options:  
  - `Encrypt`
  - `Decrypt`
* Default keyboard shortcuts:  
  - `⌘+K,e` on OSX or `ctrl+K,e` on Linux/Windows (Encrypt)
  - `⌘+K,d` on OSX or `ctrl+K,d` on Linux/Windows (Decrypt)

The commands work on a selection, multiple selections or if nothing is selected the whole document. Once you trigger the command you will be prompted to enter a password.


Todo
----
* Add other functionality:
  - encryption on save

Author & Contributors
----------------------
[Derek Anderson](http://twitter.com/derekanderson)  
[Isaac Muse](https://github.com/facelessuser)  
[Elliot Marsden](https://github.com/eddiejessup)  


License
-------
MIT License
