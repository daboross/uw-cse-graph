from bs4 import BeautifulSoup
import argparse
import re
import itertools


def has_name(tag):
    return tag.has_attr("name")


def load(filename) -> BeautifulSoup:
    with open(filename) as f:
        contents = f.read()

    return BeautifulSoup(contents, 'html.parser')


_course_name_regex = re.compile("[^A-Z ]([A-Z ]+ [0-9]+)")


def find_prereqs_full(filename):
    s = load(filename)
    pre_map = {}
    desc_map = {}
    for tag in s.find_all(has_name):
        name = tag["name"]
        description = tag.contents[0].contents[-3].string
        if "Intended for non-majors" in description:
            continue
        desc_map[name] = description
        first_pass_prereqs = (s.replace(" ", "").lower()
                              for s in _course_name_regex.findall(description))
        pre_map[name] = set(s for s in first_pass_prereqs if s != tag)

    # filter out courses mentioned which we don't care about
    for key in pre_map.keys():
        pre_map[key] = [x for x in pre_map[key]
                        if x in desc_map or not x.startswith("cse")]

    return pre_map, desc_map


def debug_print(pre_map, desc_map):
    for name, desc in desc_map.items():
        print("{}:\n\t{}\n\t{}".format(name, desc, pre_map[name]))


def graphviz_out(pre_map, desc_map, out_file):
    from graphviz import Digraph
    dot = Digraph(comment="CSE courses")

    for name, desc in desc_map.items():
        dot.node(name)
        # dot.node(name, desc)

    for name, prereqs in pre_map.items():
        for prereq in prereqs:
            dot.node(prereq)
            dot.edge(prereq, name)

    dot.render(out_file, view=True)


def main():
    parser = argparse.ArgumentParser(prog="cseparse.py",
                                     description="parses an HTML file \
                        downloaded from \
                        https://www.washington.edu/students/crscat/cse.html \
                        into a list of courses and tries to parse prereqs. \
                        Should do OK, but does not distinguish between 'OR' \
                        and 'AND' prereq requirements")
    parser.add_argument('--debug-print', nargs=1, metavar="FILE",
                        help="parses and prints debug output to console")
    parser.add_argument('--graphviz', nargs=2, metavar="FILE",
                        help="parses first file and outputs graphviz output \
                        into second file")

    args = parser.parse_args()
    if args.debug_print:
        pre_map, desc_map = find_prereqs_full(args.debug_print[0])
        debug_print(pre_map, desc_map)
    elif args.graphviz:
        pre_map, desc_map = find_prereqs_full(args.graphviz[0])
        graphviz_out(pre_map, desc_map, args.graphviz[1])
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
