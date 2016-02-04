# Frontiers Fortnightly email template

This repository contains a HTML email template for Frontiers Fortnightly and a
script (`render.py`) to render the template (and soon to produce a complete
email, except for the "To:" field!).

To run the script, you will first need to install its dependencies, listed in
`requirements.txt`. The easiest way to do this is using [pip and
virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/). For
instance, on Ubuntu you might do:

```
$ apt-get install python3-virtualenv
$ cd <path to this repository>
$ virtualenv env
$ source env/bin/activate
$ pip install -r requirements.txt
...some junk, possibly dependency errors which you'll need to Google to
resolve...
$ ./render.py  # Run it!
```

You might also need to install some extra packages like `lxml` for the install
to work correctly; Googling any errors that come up during `pip install` will
yield the answers you seek.

The source issues themselves are stored in Markdown format in the `issues/`
directory. Remember to follow the existing issues closely when structuring new
issues: issues should always begin with a metadata block containing an "Issue:"
key with the issue number; the issue block should be followed by a blank line,
then the preamble; stories should follow afterwards, with each story beginning
with a level-one header in the form `# <heading>` and end with a `[Learn
more](...)` URL.

To resolve possible issues with generated emails, remember to preview them in
your web browser before sending, and possibly send out some test emails to
yourself to assure yourself that email clients also render the email correctly.
