# Olivettize
Render text like an Olivetti Te-318 teleprinter! But without the hearing loss!

`python3 olivettize.py file.txt` will create `file.pdf`

Olivettize will read the text file and generate 8.5x11" 600 dpi images, which are wrapped together into a PDF. The `chars` directory contains images of the printed Olivetti type. Four complete sets are used to provide a modest degree of variability. Like a physical teleprinter using continuous feed paper, Olivettize prints down the entire length of the page; however, it is exquisitely aligned such that one never prints over the peroration (future feature).

Requires python3.X and the Pillow image library.

More about the Olivetti Te-318 [http://ef1j.org/~emf/Olivetti_TE318.html]

The contents of this repository are published under the MIT license.
