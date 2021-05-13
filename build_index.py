import os
import sys
import argparse
import itertools
import wikitextparser as wtp
import networkx as nx
from networkx.algorithms import community
from pathlib import Path

INDEX_NAME      = 'Index'
MD_EXTENSION    = '.md'

class NoteGraph:

    def __init__(self, root_dir):
        self.root_dir           = root_dir
        self.digraph            = nx.DiGraph()
        self.index              = []
        self.populate_digraph()
        self.num_indexed_notes  = 4 # changeable, I just thought it seemed good

    def node_inlinks_generator(self, min_inlinks, max_inlinks):
        """
        Yields nodes with inlinks inside the limits.
        """
        for node in self.digraph.nodes:
            inlinks = self.digraph.in_degree(node)
            if min_inlinks <= inlinks <= max_inlinks:
                yield (node, inlinks)

    def populate_digraph(self):
        self.digraph.add_nodes_from(self.notes_generator())
        self.digraph.add_edges_from(self.links_generator())
        self.digraph.remove_node(INDEX_NAME)

    def populate_index(self):
        """
        Will populate the index as a list of sections, with each section being a list of notes.
        For each section returned by the section generator, creates a subgraph and gets up to four
        of the highest ranked notes.
        Order them by section size (not number of important notes).
        """

        sections_by_num = []

        for section in self.sections_generator():
            sections_by_num.append((len(section), self.get_important_notes(section)))

        for section in sorted(sections_by_num, reverse=True):
            self.index.append(section[1])

    def get_important_notes(self, section):
        """
        Returns up to four of the highest ranked notes in a subgraph of the provided notes.
        """

        subgraph = self.digraph.subgraph(section)

        important_notes = nx.voterank(subgraph, self.num_indexed_notes)

        return important_notes

    def links_generator(self):
        """
        Yields the tuples that represent links between notes, using wikilinks
        since they're used for internal links.
        Don't count self links!
        """

        for note in self.notes_generator():
            path = os.path.join(self.root_dir, note) + MD_EXTENSION
            with open(path, 'r') as f:
                data        = f.read()
                wikilinks   = wtp.parse(data).wikilinks

                for wikilink in wikilinks:
                    if note != wikilink.title:
                        yield (note, wikilink.title)


    def notes_generator(self):
        """
        Yields the notes.
        For now, let's make notes just simple strings of their paths.
        Just get everything in the directory, assuming same level.
        """

        for root, dirs, files in os.walk(self.root_dir):
            for filename in files:
                notename = filename.replace(MD_EXTENSION, '')
                yield (notename)

    def sections_generator(self):
        """
        Yields the communities of a directed graph as sets of nodes.
        """

        graph = self.digraph.to_undirected()

        for section in community.label_propagation_communities(graph):
            print(section)
            yield section


    def print_index_to_file(self, filename):
        path = os.path.join(self.root_dir, filename)

        with open(path, 'w') as f:

            md =    '# Main Index\n\n'
            md +=   'This index is automated, any edits will be overwritten on next regeneration.\n\n'
            md +=   '---\n\n'

            for section in self.index:
                if not section:
                    continue

                section_md      = '## [[' + section[0] + ']]\n'

                if len(section) > 1:
                    section_list = section[1:]
                    for item in section_list:
                        section_md += '- [[' + item + ']]\n'

                section_md += '\n'

                md += section_md.format(section)

            f.write(md)
        f.closed


parser = argparse.ArgumentParser()
parser.add_argument("dir_path", type=Path)
p = parser.parse_args()

notes = NoteGraph(p.dir_path)
notes.populate_index()
notes.print_index_to_file(INDEX_NAME + MD_EXTENSION)
print("\nUnderlinked notes:")
for node_inlinks in notes.node_inlinks_generator(-float('inf'), 2):
    print(node_inlinks)
print("\nSufficiently linked notes:")
for node_inlinks in notes.node_inlinks_generator(3, float('inf')):
    print(node_inlinks)
