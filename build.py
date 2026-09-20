#!/usr/bin/env python3
"""Build jr2hao.dev.

Every page is published twice at the same path:

    /blog/nixos.md      the source Markdown, byte for byte
    /blog/nixos.html    the human-facing rendering

Nodes that have children are directories with an index (``/``, ``/blog/``);
leaf nodes are the file itself (``/about.html``, never ``/about/index.html``).
All generated links carry an explicit extension.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import itertools
import re
import shutil
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from string import Template

from markdown_it import MarkdownIt
from mdit_py_plugins.anchors import anchors_plugin
from mdit_py_plugins.footnote import footnote_plugin
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.style import Style
from pygments.token import (Comment, Error, Generic, Keyword, Name, Number,
                            Operator, String)
from pygments.util import ClassNotFound

FRONT_MATTER = re.compile(r"\+\+\+\n(.*?)^\+\+\+\n", re.S | re.M)

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
STATIC = ROOT / "static"
ICONS = ROOT / "icons"

SITE_TITLE = "JR2HAO"

# (label, href, icon stem in icons/) for the header nav on the front page.
HEADER_LINKS = [
    ("Bluesky", "https://bsky.app/profile/jr2hao.dev", "bluesky"),
    ("GitHub", "https://github.com/purewhite404", "github"),
    ("About me", "/about.html", "aboutme"),
]

# Sections, in the order they appear on the front page.
SECTIONS = [
    ("blog", "Recent posts", "date"),
    ("memo", "Technical notes", "title"),
]

# Site-absolute paths served by something other than this build.
# /exif-analyzer/ is a separate repository's project Pages site that inherits
# the custom domain; --check must not flag it as a dangling link.
EXTERNAL_PATHS = {"/exif-analyzer/"}

KATEX = """    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.21/dist/katex.min.css" integrity="sha384-zh0CIslj+VczCZtlzBcjt5ppRcsAmDnRem7ESsYwWwg3m/OaJ2l4x7YBZl9Kxxib" crossorigin="anonymous">
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.21/dist/katex.min.js" integrity="sha384-Rma6DA2IPUwhNxmrB/7S3Tno0YY7sFu9WSYMCuulLhIqYSGZ2gKCJWIqhBWqMQfh" crossorigin="anonymous"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.21/dist/contrib/auto-render.min.js" integrity="sha384-hCXGrW6PitJEwbkoStFjeJxv+fSOOQKOPbJxSfM6G5sWZjAyWhXiTIIAmQqnlLlh" crossorigin="anonymous"></script>
    <script>
        document.addEventListener("DOMContentLoaded", function() {
            renderMathInElement(document.body, {
              delimiters: [
                  {left: '$$', right: '$$', display: true},
                  {left: '$', right: '$', display: false},
                  {left: '\\\\(', right: '\\\\)', display: false},
                  {left: '\\\\[', right: '\\\\]', display: true}
              ],
              throwOnError : false
            });
        });
    </script>"""


# --------------------------------------------------------------------------
# Page shell
#
# string.Template rather than f-strings or .format(): the dark-mode script and
# the <noscript> style below are ported verbatim from the old Zola templates
# and are full of braces.  Neither contains a '$', so $-substitution passes
# them through untouched and the port stays diffable against the original.
# --------------------------------------------------------------------------

SHELL = Template("""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
$description    <title>$title</title>
    <link rel="stylesheet" href="/style.css?h=$csshash">
$head_extra</head>
<body>
$header
$main
    <div class="dark-mode-buttons">
        <button class="dark-mode-button" id="dark-mode-on" aria-label="dark mode toggle" title="Dark mode">$dark_icon</button>
        <button class="dark-mode-button" id="dark-mode-off" aria-label="light mode toggle" title="Light mode">$light_icon</button>
    </div>
    <script>
        const cls = document.querySelector("html").classList;
        const sessionTheme = sessionStorage.getItem("theme");

        function setDark() {
            cls.add("dark-mode");
            cls.remove("light-mode");
            sessionStorage.setItem("theme", "dark");
        }
        function setLight() {
            cls.add("light-mode");
            cls.remove("dark-mode");
            sessionStorage.setItem("theme", "light");
        }

        if (sessionTheme === "dark") {
            setDark();
        } else if (sessionTheme === "light") {
            setLight();
        } else if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
            setDark();
        }

        document.getElementById("dark-mode-on").addEventListener("click", function(e) {
            setDark();
        });
        document.getElementById("dark-mode-off").addEventListener("click", function(e) {
            setLight();
        });
    </script>
    <noscript>
        <style>
            .dark-mode-buttons {
                display: none;
            }
        </style>
    </noscript>
    <footer>
            <small>
                2025 jr2hao all rights reserved
            </small>
    </footer>
</body>
</html>
""")

BACK_HEADER = """<header class="space">
    <a href="javascript:history.back();">&LeftArrow; Back</a>
</header>"""


def icon(stem: str, attrs: str) -> str:
    """Inline an icons/*.svg. Inlining rather than <img src> keeps every page
    to a single request, and lets the artwork follow currentColor."""
    svg = ICONS.joinpath(stem + ".svg").read_text(encoding="utf-8").strip()
    assert svg.startswith("<svg"), stem
    return f"<svg {attrs} " + svg[len("<svg "):]


def front_header() -> str:
    links = "\n".join(
        f'            <a href="{href}">{label}'
        + icon(stem, 'class="icons" aria-hidden="true"') + "</a>"
        for label, href, stem in HEADER_LINKS
    )
    return (f'    <header class="space">\n'
            f'        <h1>{SITE_TITLE}</h1>\n'
            f'        <nav class="header-links">\n{links}\n'
            f'        </nav>\n'
            f'    </header>')


# --------------------------------------------------------------------------
# Markdown
# --------------------------------------------------------------------------

class Base16OceanDark(Style):
    """The syntect theme Zola was configured with, as a Pygments style."""

    background_color = "#2b303b"
    styles = {
        Comment:            "#65737e",
        Comment.Preproc:    "#b48ead",
        Keyword:            "#b48ead",
        Keyword.Type:       "#ebcb8b",
        Operator:           "#96b5b4",
        Name:               "#c0c5ce",
        Name.Attribute:     "#ebcb8b",
        Name.Builtin:       "#bf616a",
        Name.Class:         "#ebcb8b",
        Name.Constant:      "#d08770",
        Name.Decorator:     "#96b5b4",
        Name.Entity:        "#96b5b4",
        Name.Exception:     "#bf616a",
        Name.Function:      "#8fa1b3",
        Name.Tag:           "#bf616a",
        Name.Variable:      "#bf616a",
        Number:             "#d08770",
        String:             "#a3be8c",
        String.Escape:      "#96b5b4",
        String.Interpol:    "#96b5b4",
        Generic.Deleted:    "#bf616a",
        Generic.Inserted:   "#a3be8c",
        Error:              "#bf616a",
    }


FORMATTER = HtmlFormatter(style=Base16OceanDark, nowrap=True, noclasses=True)
# Info strings seen so far that are prose, not a language (see content/blog/nixos.md).
_unknown_langs: set[str] = set()


def render_fence(self, tokens, idx, options, env):
    """Mirror Zola's shape: inline base16-ocean-dark, no highlighting when the
    info string is not a language we know."""
    token = tokens[idx]
    info = token.info.strip()
    lang = info.split()[0] if info else ""
    body = None
    if lang:
        try:
            body = highlight(token.content, get_lexer_by_name(lang), FORMATTER)
        except ClassNotFound:
            _unknown_langs.add(info)
    if body is None:
        body = html.escape(token.content, quote=False)
    attrs = ""
    if info:
        attrs = f' class="language-{html.escape(info)}" data-lang="{html.escape(info)}"'
    return ('<pre style="background-color:#2b303b;color:#c0c5ce;">'
            f'<code{attrs}>{body}</code></pre>\n')


def render_link_open(self, tokens, idx, options, env):
    """Internal links are authored as .md; the HTML tree links to .html."""
    token = tokens[idx]
    href = token.attrGet("href")
    if href and href.endswith(".md") and "://" not in href:
        token.attrSet("href", href[:-3] + ".html")
    return self.renderToken(tokens, idx, options, env)


def slug(text: str) -> str:
    """Heading id. Unicode is kept as-is; browsers percent-encode it in links."""
    return re.sub(r"[^\w-]+", "-", text.strip().lower()).strip("-")


md = (MarkdownIt("commonmark", {"html": True})   # <sub> in headings needs html
      .enable("table")
      .enable("strikethrough")
      .use(footnote_plugin)
      .use(anchors_plugin, max_level=3, slug_func=slug))
md.add_render_rule("fence", render_fence)
md.add_render_rule("link_open", render_link_open)


# --------------------------------------------------------------------------
# Content model
# --------------------------------------------------------------------------

@dataclass
class Page:
    src: Path
    section: str          # "" for the root, else "blog" / "memo"
    stem: str             # "index" for a section index, else the slug
    meta: dict
    body: str
    raw: str
    children: list["Page"] = field(default_factory=list)

    @property
    def out(self) -> str:
        """Output path without extension, relative to the site root."""
        return f"{self.section}/{self.stem}" if self.section else self.stem

    @property
    def href_html(self) -> str:
        if self.stem == "index":
            return f"/{self.section}/" if self.section else "/"
        return f"/{self.out}.html"

    @property
    def href_md(self) -> str:
        return f"/{self.out}.md"

    @property
    def title(self) -> str:
        return self.meta.get("title", SITE_TITLE)

    @property
    def date(self):
        return self.meta.get("date")

    @property
    def genre(self) -> str | None:
        return self.meta.get("extra", {}).get("genre")


def parse(src: Path) -> Page:
    raw = src.read_text(encoding="utf-8")
    m = FRONT_MATTER.match(raw)
    if not m:
        sys.exit(f"{src}: missing or unterminated +++ front matter")
    fm, body = m.group(1), raw[m.end():]
    section = src.parent.name if src.parent != CONTENT else ""
    stem = src.stem
    return Page(src, section, stem, tomllib.loads(fm), body.lstrip("\n"), raw)


def load() -> tuple[Page, dict[str, Page]]:
    root = parse(CONTENT / "index.md")
    indexes: dict[str, Page] = {}
    for name, _, sort_key in SECTIONS:
        index = parse(CONTENT / name / "index.md")
        pages = [parse(p) for p in sorted((CONTENT / name).glob("*.md"))
                 if p.stem != "index"]
        if sort_key == "date":
            pages.sort(key=lambda p: p.date, reverse=True)
        else:
            pages.sort(key=lambda p: p.title.lower())
        index.children = pages
        indexes[name] = index
    root.children = [parse(p) for p in sorted(CONTENT.glob("*.md"))
                     if p.stem != "index"]
    return root, indexes


def group(index: Page) -> list[tuple[str, list[Page]]]:
    """Group a section index's pages for display, preserving page order."""
    if index.section == "blog":
        return [(str(year), list(g)) for year, g
                in itertools.groupby(index.children, key=lambda p: p.date.year)]
    groups: dict[str, list[Page]] = {}
    for page in index.children:
        groups.setdefault(page.genre, []).append(page)
    return list(groups.items())


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

def page_shell(*, title, main, header, description=None, math=False, csshash):
    desc = ""
    if description:
        desc = f'    <meta name="description" content="{html.escape(description)}">\n'
    return SHELL.substitute(
        title=html.escape(title),
        description=desc,
        head_extra=(KATEX + "\n") if math else "",
        dark_icon=icon("dark_mode", 'aria-hidden="true"'),
        light_icon=icon("light_mode", 'aria-hidden="true"'),
        header=header,
        main=main,
        csshash=csshash,
    )


def list_html(groups) -> str:
    out = []
    for heading, pages in groups:
        items = "\n".join(
            f'            <li><a href="{p.href_html}">{html.escape(p.title)}</a></li>'
            for p in pages
        )
        out.append(f"        <h2>{html.escape(heading)}</h2>\n"
                   f"        <ul>\n{items}\n        </ul>")
    return "\n".join(out)


def list_md(groups) -> str:
    out = []
    for heading, pages in groups:
        items = "\n".join(f"- [{p.title}]({p.href_md})" for p in pages)
        out.append(f"## {heading}\n\n{items}")
    return "\n\n".join(out)


def dateline(page: Page) -> str:
    if not page.date:
        return ""
    line = f"created at {page.date:%Y/%m/%d}"
    if page.meta.get("updated"):
        line += f", updated at {page.meta['updated']:%Y/%m/%d}"
    return f'    <p class="secondary small">\n        {line}\n    </p>\n'


def render_page_html(page: Page, csshash: str) -> str:
    main = ("<main>\n"
            f"    <h1>{html.escape(page.title)}</h1>\n"
            f"{dateline(page)}"
            '    <div class="space"></div>\n'
            f"{md.render(page.body)}"
            "</main>")
    return page_shell(title=f"{SITE_TITLE} | {page.title}", main=main,
                      header=BACK_HEADER, description=page.meta.get("description"),
                      math=page.meta.get("math", False), csshash=csshash)


def render_section_html(index: Page, csshash: str) -> str:
    body = md.render(index.body) if index.body.strip() else ""
    main = ("<main>\n"
            f"    <h1>{html.escape(index.title)}</h1>\n"
            f"{body}"
            f"{list_html(group(index))}\n"
            "</main>")
    return page_shell(title=f"{SITE_TITLE} | {index.title}", main=main,
                      header=BACK_HEADER, math=index.meta.get("math", False),
                      csshash=csshash)


def render_home_html(root: Page, indexes: dict[str, Page], csshash: str) -> str:
    parts = ["    <main>", md.render(root.body).rstrip()]
    for name, label, _ in SECTIONS:
        index = indexes[name]
        parts.append("\n" + list_html([(label, index.children[:20])]) + "\n"
                     f'        <p><a href="{index.href_html}">View all</a></p>')
    parts.append("    </main>")
    return page_shell(title=SITE_TITLE, main="\n".join(parts),
                      header=front_header(), math=root.meta.get("math", False),
                      csshash=csshash)


def render_home_md(root: Page, indexes: dict[str, Page]) -> str:
    parts = [root.raw.rstrip()]
    for name, label, _ in SECTIONS:
        index = indexes[name]
        parts.append(list_md([(label, index.children[:20])])
                     + f"\n\n[View all]({index.href_md})")
    return "\n\n".join(parts) + "\n"


def render_section_md(index: Page) -> str:
    return index.raw.rstrip() + "\n\n" + list_md(group(index)) + "\n"


def render_404(csshash: str) -> str:
    main = ("<main>\n"
            "    <h1>Page Not Found (404)</h1>\n"
            "    <p>The page you were looking for could not be found.</p>\n"
            "</main>")
    return page_shell(title=f"{SITE_TITLE} | Page Not Found", main=main,
                      header=BACK_HEADER, csshash=csshash)


# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------

def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build(out: Path) -> None:
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(STATIC, out)

    csshash = hashlib.sha256((STATIC / "style.css").read_bytes()).hexdigest()[:20]
    root, indexes = load()

    write(out / "index.html", render_home_html(root, indexes, csshash))
    write(out / "index.md", render_home_md(root, indexes))
    for index in indexes.values():
        write(out / f"{index.out}.html", render_section_html(index, csshash))
        write(out / f"{index.out}.md", render_section_md(index))
    for page in root.children + [p for i in indexes.values() for p in i.children]:
        write(out / f"{page.out}.html", render_page_html(page, csshash))
        write(out / f"{page.out}.md", page.raw)

    write(out / "404.html", render_404(csshash))
    write(out / "robots.txt", "User-agent: *\nAllow: /\n")
    write(out / ".nojekyll", "")


# --------------------------------------------------------------------------
# --check
# --------------------------------------------------------------------------

SLUG = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*\Z")


def check(out: Path) -> int:
    problems: list[str] = []

    for src in sorted(CONTENT.rglob("*.md")):
        stem = src.stem
        if stem != "index" and not SLUG.fullmatch(stem):
            problems.append(f"{src}: filename is not a slug "
                            f"(expected {stem.lower().replace('_', '-')})")
        page = parse(src)
        if src != CONTENT / "index.md" and "title" not in page.meta:
            problems.append(f"{src}: missing title")
        if src.parent.name == "memo" and stem != "index" and not page.genre:
            problems.append(f"{src}: missing extra.genre")
        if src.parent.name == "blog" and stem != "index" and not page.date:
            problems.append(f"{src}: missing date")

    for lang in sorted(_unknown_langs):
        problems.append(f"unknown code fence language: ```{lang}")

    for f in sorted(out.rglob("*.html")):
        for target in re.findall(r'(?:href|src)="([^"]+)"', f.read_text("utf-8")):
            if not target.startswith("/") or target in EXTERNAL_PATHS:
                continue
            target = target.split("?")[0].split("#")[0]
            dest = out / target.lstrip("/")
            if target.endswith("/"):
                dest = dest / "index.html"
            if not dest.exists():
                problems.append(f"{f.relative_to(out)}: dangling link {target}")

    for p in sorted(set(problems)):
        print(f"error: {p}", file=sys.stderr)
    return 1 if problems else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default="_site", type=Path)
    ap.add_argument("--check", action="store_true",
                    help="fail on slug, front matter, fence and link problems")
    args = ap.parse_args()

    build(args.out)
    return 1 if args.check and check(args.out) else 0


if __name__ == "__main__":
    sys.exit(main())
