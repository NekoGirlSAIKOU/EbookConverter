# Ebook Converter
This is an app to convert ebook format.
This app uses gryf's ebook-converter, which is based 
on calibre, to convert ebooks. 

The ebook-converter is modified and based on
35c34c3b45d8ee41c1e9dbabe86c1484cd074472 because
its newest source code seems broken.

# Input formats
Not tested.
Currently, following formats are supported:

- Microsoft Word 2007 and up (``docx``)(**may not work**)
- EPUB, both v2 and v3 (``epub``)(**work**)
- Pure text files (``txt``)(**work**)
- Mobipocket (``mobi``)(**work**)
- Kindle (``azw3``, ``azw4``, …)
- Hyper Text Markup Language (``html``)(**work**)

Note, that old Microsoft doc format is not supported.
Some settings related to these formats may 
not work. Report an issue if you find something 
not working.

# Output formats
Currently, following formats are supported:

- EPUB v2 (``epub``)(**work**)
- Mobipocket (``mobi``)(**work**)
- Microsoft Word (``docx``)(**work**)
- Text (``txt``)(**work**)

Note, some settings related to these formats may 
not work. Report an issue if you find something 
not working.

# Build
Install required packages:
```shell
sudo apt install zlib1g-dev libssl-dev libffi-dev \
 libltdl-dev autoconf automake zip cmake pkg-config \
 libxml2-dev 
pip install cython
pip install buildozer
```
Build:
```shell
buildozer android debug
```
