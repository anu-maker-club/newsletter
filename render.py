#!/usr/bin/env python3

"""Short script to render the newsletter into HTML & text. Depends on the
packages in ``requirements.txt`` (get them with ``pip``!)."""

from argparse import ArgumentParser, FileType
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


def get_template(name):
    """Get a template with the given filename from the local directory."""
    env = Environment(loader=FileSystemLoader('./'))
    env.filters['bleach'] = bleach_filter
    env.filters['markdown'] = markdown_filter
    env.filters['headermarkdown'] = headermarkdown_filter
    return env.get_template(TEMPLATE_NAME)


def generate_html(md_source, template_name):
    """Produce the HTML necessary for an email, without inlining images."""
    tmpl = get_template(template_name)
    issue, preamble, stories = load_issue(md_source)
    rendered = tmpl.render(
        issue=issue, preamble=preamble, stories=stories
    )
    # XXX: For some reason this borks all of the text colours. I suspect it has
    # something to do with the way inline styles are inherited.
    transformed = transform(rendered)
    # We transform-minify-transform so that the minifier can see the styles
    # inlined by the transformer and the transformer can ensure that the
    # minifier's output is email-compatible
    minified = transform(minify(transformed, remove_comments=True))
    return minified


def do_genhtml(args):
    """Execute the ``genhtml`` subcommand."""
    md_source = args.source.read()
    minified = generate_html(md_source, TEMPLATE_NAME)
    args.dest.write(minified)


def do_genmime(args):
    """Execute the ``genmime`` subcommand. Unlike ``genhtml``, this command
    inlines images (which ``genhtml`` can't do becaus ``cid`` embedding is not,
    AFAIK, usable outside of email clients, but ``genhtml`` is most useful for
    previewing emails in browsers!)."""
    pass


parser = ArgumentParser(
    description="Render a Frontiers Fortnightly newsletter into HTML (for "
    "browser preview) or a multipart email."
)
subparsers = parser.add_subparsers(dest='command')
subparsers.required = True
parser.add_argument(
    'source', type=FileType('r'), help='markdown source for the newsletter'
)
parser.add_argument(
    '--dest', type=FileType('w', encoding='UTF-8'), default='-',
    help='destination for any output (default stdout)'
)

preview_parser = subparsers.add_parser(
    "genhtml", help="generate HTML for browser preview",
    description="Generate HTML for browser preview."
)
preview_parser.set_defaults(func=do_genhtml)

email_parser = subparsers.add_parser(
    "genmime", help="generate a complete MIME email",
    description="Generate a complete MIME email."
)
email_parser.set_defaults(func=do_genmime)


if __name__ == '__main__':
    args = parser.parse_args()
    args.func(args)
