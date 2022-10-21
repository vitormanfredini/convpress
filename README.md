# ConvPress

## File compression software using convolutions and a genetic algorithm

This is a project I'm doing to study Python.
It's slow and not recomended for any type of production use.

---

To install, first create a virtual environment:

`virtualenv venv_convpress`

and activate it:

`source venv_convpress/bin/activate`

Install dependencies:

`pip install -r requirements.txt`

---

To compress a file:

`./convpress.py data/original-file.txt data/compressed-file.cp`

To uncompress a file:

`./deconvpress.py data/compressed-file.cp data/uncompressed-file.txt`

---

To see all parameters that you can pass to the compressing program:

`./convpress.py -h`

---

You can recompress a file that has already been compressed and it will make it even smaller, though less and less until it can't compress it further.

---

Tests:

`python -m unittest`
