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
- LibreOffice (``odt``)
- Pure text files (``txt``)
- Several PalmOS (``pdb``) readers support:

  - Plucker
  - Adobe Reader for PalmOS
  - eReader various formats
  - Weasel Reader
  - Haodoo Reader

- Rich Text Format (``rtf``)
- Mobipocket (``mobi``)
- Kindle (``azw3``, ``azw4``, …)
- FictionBook (``fb2``)
- Hyper Text Markup Language (``html``)
- Adobe Portable Document Format (``pdf``)
- Broadband eBooks (shortened as BBeB) (``lrf``)

Note, that old Microsoft doc format is not supported.

# Output formats
Not tested.
Currently, following formats are supported:

- Broadband eBooks (shortened as BBeB) (``lrf``)
- EPUB v2 (``epub``)
- Mobipocket (``mobi``)(**work**)
- Microsoft Word (``docx``)
- zipped HTML file with additional assets, like images (``htmlz``)
- Text (``txt``)

# Build
Install required packages for buildozer:
```shell
sudo apt install zlib1g-dev libssl-dev libffi-dev \
 libltdl-dev autoconf automake zip cmake pkg-config
pip install cython
```
Install buildozer:
```shell
pip install buildozer
```
Build:
```shell
buildozer android debug deploy run
```
