""" starcli.layouts """

# Standard library imports
import textwrap
import math
import os
from shutil import get_terminal_size
from datetime import datetime

# Third party imports
from rich.align import Align
from rich.console import Console, render_group
from rich.rule import Rule
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich.columns import Columns
from terminalplot import plot, get_terminal_size


def shorten_count(number):
    """Shortens number"""
    if number < 1000:
        return str(number)

    number = int(number)
    new_number = math.ceil(round(number / 100.0, 1)) * 100

    if new_number % 1000 == 0:
        return str(new_number)[0] + "k"
    if new_number < 1000:
        # returns the same old integer if no changes were made
        return str(number)
    else:
        # returns a new string if the number was shortened
        return str(new_number / 1000.0) + "k"


def get_stats(repo):
    """ return formatted string of repo stats """
    stats = f"{repo['stargazers_count']} ⭐ " if repo["stargazers_count"] != "-1" else ""
    stats += f"{repo['forks_count']} ⎇ " if repo["forks_count"] != "-1" else ""
    stats += f"{repo['watchers_count']} 👀 " if repo["watchers_count"] != "-1" else ""
    return stats


def list_layout(repos):
    """ Displays repositories in list layout using rich """

    LAYOUT_WIDTH = 80

    @render_group()
    def render_repo(repo):
        """Yields renderables for a single repo."""
        yield Rule(style="bright_yellow")
        yield ""
        # Table with description and stats
        title_table = Table.grid(padding=(0, 1))
        title_table.expand = True
        stats = get_stats(repo)
        title = Text(repo["full_name"], overflow="fold")
        title.stylize(f"yellow link {repo['html_url']}")
        title_table.add_row(title, Text(stats, style="bold blue"))
        title_table.columns[1].no_wrap = True
        title_table.columns[1].justify = "right"
        yield title_table
        yield ""
        # Language and date range are added to single row
        lang_table = Table.grid(padding=(0, 1))
        lang_table.expand = True
        language_col = (
            Text(repo["language"], style="bold cyan")
            if repo["language"]
            else Text("unknown language")
        )
        date_range_col = (
            Text(repo["date_range"].replace("stars", "⭐"), style="bold cyan")
            if "date_range" in repo.keys() and repo["date_range"]
            else Text("")
        )
        lang_table.add_row(language_col, date_range_col)
        lang_table.columns[1].no_wrap = True
        lang_table.columns[1].justify = "right"
        yield lang_table
        yield ""
        # Descripion
        description = repo["description"]
        if description:
            yield Text(description.strip(), style="green")
        else:
            yield "[i green]no description"
        yield ""

    def column(renderable):
        """Constrain width and align to center to create a column."""
        return Align.center(renderable, width=LAYOUT_WIDTH, pad=False)

    console = Console()  # initialise rich
    for repo in repos:
        console.print(column(render_repo(repo)))
    console.print(column(Rule(style="bright_yellow")))


def table_layout(repos):
    """ Displays repositories in a table format using rich """

    table = Table(leading=1)

    # make the columns
    table.add_column("Name", style="bold cyan")
    table.add_column("Language", style="green")
    table.add_column("Description", style="blue")
    table.add_column("Stats", style="magenta")

    for repo in repos:

        stats = get_stats(repo)
        stats += (
            "\n" + repo["date_range"].replace("stars", "⭐")
            if "date_range" in repo.keys() and repo["date_range"]
            else ""
        )

        if not repo["language"]:  # if language is not provided
            repo["language"] = "None"  # make it a string
        if not repo["description"]:  # same here
            repo["description"] = "None"

        table.add_row(
            repo["name"],
            repo["language"],  # so that it can work here
            repo["description"],
            stats,
        )

    console = Console()
    console.print(table)


def grid_layout(repos):
    """ Displays repositories in a grid format using rich """

    max_desc_len = 90

    panels = []
    for repo in repos:

        stats = get_stats(repo)
        # '\n' added here as it would group both text and new line together
        # hence if date_range isn't present the new line will also not be displayed
        date_range_str = (
            repo["date_range"].replace("stars", "⭐") + "\n"
            if "date_range" in repo.keys() and repo["date_range"]
            else ""
        )

        if not repo["language"]:  # if language is not provided
            repo["language"] = "None"  # make it a string
        if not repo["description"]:
            repo["description"] = "None"

        name = Text(repo["name"], style="bold yellow")
        language = Text(repo["language"], style="magenta")
        description = Text(repo["description"], style="green")
        stats = Text(stats, style="blue")

        # truncate rest of the description if
        # it's more than 90 (max_desc_len) chars
        # using truncate() is better than textwrap
        # because it also takes care of asian characters
        description.truncate(max_desc_len, overflow="ellipsis")

        repo_summary = Text.assemble(
            name, "\n", stats, "\n", date_range_str, language, "\n", description,
        )
        panels.append(Panel(repo_summary, expand=True))

    console = Console()
    console.print((Columns(panels, width=30, expand=True)))

def graph_layout(star_dates):
    """
    This displays a graph of repository star gazers over time.
    """

    # I'm going to take a more basic approach for this initially
    min_date = star_dates[0]
    max_date = datetime.now().date()

    max_stars = len(star_dates)

    # Now that we have our basic dates, get our star counts
    min_stars = 0
    star_delta = max_stars - min_stars
    star_2 = min_stars + 1 * (star_delta / 3)
    star_3 = min_stars + 2 * (star_delta / 3)

    # Now we prep the table data

    # Get our terminal size
    row_count, col_count = get_terminal_size()

    # How many days are in each column?
    # Keep 3 rows and 6 columns reserved for meta data
    date_delta = (max_date - min_date) / col_count

    date_2 = min_date + 1 * (date_delta / 3)
    date_3 = min_date + 2 * (date_delta / 3)

    # This is a generator to get the numbmer of stars by each date
    star_counts = [0]
    for i in range(1, col_count):
        lower_date = min_date + (i * date_delta)
        upper_date = min_date + ((i + 1) * date_delta)

        star_arr = [x for x in star_dates if (x >= lower_date and x < upper_date)]
        print('Upper: {}\tLower: {}\tDelta: {}'.format(upper_date, lower_date, date_delta))
        print("star_arr: {}".format(star_arr))

        star_counts.append(
            len(
                star_arr
            ) + star_counts[i - 1]
        )

    # Hopefully this has built a summation of the star counts for each column
    print(star_counts)

    plot([x for x in range(0, col_count)], star_counts, row_count, col_count)
