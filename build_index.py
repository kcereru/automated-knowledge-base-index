import os
import sys
import argparse
import itertools
import wikitextparser as wtp
import networkx as nx
from networkx.algorithms import community
from pathlib import Path

INDEX_NAME = 'Index.md'

class NoteGraph:

    def __init__(self, root_dir):
        self.root_dir           = root_dir
        self.digraph            = nx.DiGraph()
        self.index              = []
        self.populate_digraph()
        self.num_indexed_notes  = 4 # changeable, I just thought it seemed good

    def populate_digraph(self):
        self.digraph.add_nodes_from(self.nodes_generator())
        self.digraph.add_edges_from(self.edges_generator())

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

        print(list(subgraph.edges))

        important_notes = nx.voterank(subgraph, self.num_indexed_notes)

        return important_notes

    def edges_generator(self):
        """
        Yields the tuples that represent links between notes, using wikilinks
        since they're used for internal links.
        """

        for note in self.nodes_generator():
            path = os.path.join(self.root_dir, note)
            with open(path, 'r') as f:
                data        = f.read()
                wikilinks   = wtp.parse(data).wikilinks

                for wikilink in wikilinks:
                    if wikilink.title != INDEX_NAME:
                        yield (note, wikilink.title)


    def nodes_generator(self):
        """
        Yields the notes.
        For now, let's make notes just simple strings of their paths.
        Just get everything in the directory, assuming same level.
        """

        for root, dirs, files in os.walk(self.root_dir):
            for filename in files:
                if filename != INDEX_NAME:
                    yield (filename)

    def sections_generator(self):
        """
        Yields the communities of a directed graph as sets of nodes.
        """

        graph = self.digraph.to_undirected()

        for section in community.label_propagation_communities(graph):
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

                section_md      = '## [[' + section[0].replace(".md", "") + ']]\n'

                if len(section) > 1:
                    section_list = section[1:]
                    for item in section_list:
                        section_md += '- [[' + item.replace(".md", "") + ']]\n'

                section_md += '\n'

                md += section_md.format(section)

            f.write(md)
        f.closed


parser = argparse.ArgumentParser()
parser.add_argument("dir_path", type=Path)
p = parser.parse_args()

notes = NoteGraph(p.dir_path)
notes.populate_index()
notes.print_index_to_file(INDEX_NAME)
