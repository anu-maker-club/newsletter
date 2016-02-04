#!/usr/bin/env python3

"""Short script to render the newsletter into HTML & text. Depends on the
packages in ``requirements.txt`` (get them with ``pip``!)."""

from bleach import clean
from bs4 import BeautifulSoup
from htmlmin import minify
from jinja2 import Environment, FileSystemLoader, Markup
from markdown import Markdown, markdown
from premailer import transform
import re

TEMPLATE_NAME = 'template.html'
ALLOWED_TAGS = [
    'em', 'pre', 'code', 'h2', 'h3', 'h1', 'h6', 'h4', 'h5', 'table', 'span',
    'ul', 'tr', 'li', 'hr', 'th', 'td', 'blockquote', 'acronym', 'dd', 'ol',
    'abbr', 'br', 'dt', 'strong', 'a', 'b', 'i', 'p', 'div', 'tt'
]

# TODO:
# 1) Fixing styles so that they apply properly when inlined.
# 2) Inlining images. CIDs look like the way to go, although data: URLs might
# be easier.
# 3) Argparse!
# 4) Text template
# 5) Roll it all together so that it produces a complete email


class ParseError(Exception):
    """Exception class for errors related to parsing of issues"""
    pass


def load_issue(md_source):
    """Reads an issue from a string-like object containing a Markdown document.
    Returns the issue number, preamble and stories.

    :param md_source: A string containing the Markdown source of the document.
    :returns: Tuple of ``(issue number, preamble, stories)``, where the issue
    number is an integer, the preamble is a Markdown string and stories is a
    list of dictionaries with keys ``title``, ``body`` and ``link``, which are
    strings which should be interpreted as Markdown, Markdown and a URL,
    respectively."""
    # Just parsing to get metadata
    parser = Markdown(extensions=['markdown.extensions.meta'])
    parser.convert(md_source)
    try:
        issue_no = int(''.join(parser.Meta['issue']))
    except (ValueError, KeyError):
        raise ParseError("No issue number present")

    # Split document according to level 1 headings (only using # style at BOL).
    # Heading group matches will be in elements 1, 3, 5, etc. (so 0, 2, 4, and
    # so on are sections)
    try:
        _, no_meta = md_source.split('\n\n', 1)
    except ValueError:
        raise ParseError('No preamble after the metadata!')
    heading_re = re.compile('\n#([^\n]+)\n')
    sections = heading_re.split(no_meta)
    if len(sections) <= 3:
        raise ParseError(
            "Need more than one section (preamble + at least one story)"
        )
    preamble = sections[0]
    if not preamble.strip():
        raise ParseError('Preamble is empty')

    # Process stories
    stories = []
    for heading_md, story in zip(sections[1::2], sections[2::2]):
        lines = story.strip().split('\n')
        if not lines:
            raise ParseError(
                'Story with heading "{}" is empty'.format(heading_md)
            )
        # This is the body of the story
        remainder = '\n'.join(lines[:-1])

        # "Learn more" link should be last line of the story. Last line is
        # stripped during processing otherwise. This is a little magic (I
        # probably should *enforce* a specific format), but whatever.
        link_line = lines[-1]
        parsed_ll = BeautifulSoup(markdown(link_line), "lxml")
        elem = parsed_ll.select_one('a[href]')
        if elem is None:
            raise ParseError(
                'Could not find "learn more" link for "{}"'.format(heading_md)
            )
        parsed_link = elem['href']

        stories.append({
            'title': heading_md,
            'body': remainder,
            'link': parsed_link
        })

    import pprint
    pprint.pprint(stories)
    pprint.pprint(sections)

    return (issue_no, preamble, stories)


def bleach_filter(value):
    """Run Bleach on the given HTML string, marking the result as safe."""
    cleaned = clean(value, tags=ALLOWED_TAGS)
    return Markup(cleaned)


def markdown_filter(value):
    """Simply Markdown-process the given string (don't mark it as safe, because
    it's not)."""
    return markdown(value)


def headermarkdown_filter(value):
    """Similar to :func:`markdown_filter`, except treats value as the inside of
    a header."""
    return markdown('#' + value).lstrip('<h1>').rstrip('</h1>')


if __name__ == '__main__':
    env = Environment(loader=FileSystemLoader('./'))
    env.filters['bleach'] = bleach_filter
    env.filters['markdown'] = markdown_filter
    env.filters['headermarkdown'] = headermarkdown_filter
    tmpl = env.get_template(TEMPLATE_NAME)
    # TODO: Pass this in as an argument with argparse
    with open('issues/issue-7.md') as fp:
        md_source = fp.read()
    issue, preamble, stories = load_issue(md_source)
    rendered = tmpl.render(
        issue=issue, preamble=preamble, stories=stories
    )
    # XXX: For some reason this borks all of the text colours. I suspect it has
    # something to do with the way inline styles are inherited.
    transformed = transform(rendered)
    minified = minify(transformed, remove_comments=True)
    print(minified)
