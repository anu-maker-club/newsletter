#!/usr/bin/env python3

"""Short script to render the newsletter into HTML & text. Depends on the
Markdown and Jinja2 packages (get them with pip)."""

from htmlmin import minify
from jinja2 import Environment, FileSystemLoader
from premailer import transform

TEMPLATE_NAME = 'template.html'

# This is just some test data. Should replace with actual Markdown parsing
# later
test_issue = 7
test_preamble = """Frontiers Fortnightly will be taking a break until next semester.
Good luck with all your studies, and see you next year! (Keep an eye out for
updates on this page though, we'll still be bringing you the latest updates)"""
test_stories = [
    {
        'title': 'Student Lifehacks and DIY Projects',
        'body': 'Trying to make a Halloween prop? Try using some shapeable '
                'plastic!',
        'link': 'https://www.instamorph.com/ideas/costumes-and-props'
    },
    {
        'title': 'Security Tip',
        'body': 'Don\'t leave your cards(as in bank cards, or any cards '
                'that contain your private info and is "tapping" enabled) in '
                'your pocket if you\'re in a crowded place. And be suspicious '
                'of people approaching your pockets in general as well, even '
                'if their hands are not moving.',
        'link': 'http://example.com/something'
    },
    {
        'title': 'Cool 3D Prints!',
        'body': 'Coming soon to regular 3D printers - putting hair on 3D '
                'prints!',
        'link': 'http://example.com/3d-printing-blah'
    }
]


if __name__ == '__main__':
    env = Environment(loader=FileSystemLoader('./'))
    tmpl = env.get_template(TEMPLATE_NAME)
    rendered = tmpl.render(
        issue=test_issue, preamble=test_preamble, stories=test_stories
    )
    # XXX: For some reason this borks all of the text colours. I suspect it has
    # something to do with the way inline styles are inherited.
    transformed = transform(rendered)
    minified = minify(transformed)
    print(minified)
