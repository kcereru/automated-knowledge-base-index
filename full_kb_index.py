import os
import sys
import argparse
import wikitextparser as wtp
import networkx as nx
from networkx.algorithms import community
from pathlib import Path
import pprint

FOLDERS_TO_INDEX = ['Concepts', 'Fiction'] 

INDEX_NAME      = 'Index'
MD_EXTENSION    = '.md'

class NoteGraph:

    def __init__(self, root_dir):
        self.root_dir           = root_dir
        self.digraph            = nx.DiGraph()
        self.notes_and_paths    = {}
        self.populate_digraph()

    def populate_digraph(self):
        self.digraph.add_nodes_from(self.notepaths_generator())
        self.digraph.add_edges_from(self.links_generator())

    def links_generator(self):
        """
        Yields the tuples that represent links between notes, using wikilinks
        since they're used for internal links.
        Don't count self links, but permit links to notes that might not exist.
        That means we can immediately take advantage of multiple notes linking 
        the topic they're on without requiring a note on the topic itself.
        """

        for path in self.notepaths_generator():
            with open(path, 'r') as f:
                data        = f.read()
                wikilinks   = wtp.parse(data).wikilinks

                for wikilink in wikilinks:
                    linked_note_path = self.infer_note_path(wikilink.title)
                    if path != linked_note_path:
                        yield (path, linked_note_path)


    def infer_note_path(self, note):
        if note in self.notes_and_paths:
            return self.notes_and_paths[note]
        else:
            return os.path.join(self.root_dir, 'Concepts', note) + MD_EXTENSION


    def notepaths_generator(self):
        """
        Yields the paths of notes.
        Get md files in the folders to read, recursively
        """

        for folder in FOLDERS_TO_INDEX:
            for root, dirs, files in os.walk(os.path.join(self.root_dir, folder)):
                for filename in files:
                    notename = filename.replace(MD_EXTENSION, '')
                    notepath = os.path.join(root, filename)
                    if notepath.endswith('.md'):
                        self.notes_and_paths[notename] = notepath
                        yield (notepath)


    def generate_full_index(self):
        """
        Given a directory, create an index consisting only of files within it
        The way we're going to do this is create a dict of header => contents dict,
        where each contents dict is also header => contents or header => [items].
        """

        # so to start, we'll just use the main graph. 

        index = self.get_communities_with_headers(self.digraph)

        # now with a subgraph of each of these communities, we'll want to do the same.

        # for each key/value in index, create a subgraph of the values
        # then replace the value at key with the return value

        for header, nodes in index.items():
            subgraph        = self.digraph.subgraph(nodes)
            communities     = self.get_communities_with_headers(subgraph)
            index[header]   = communities

        # TODO: manage continuing this until it's no longer viable

        return index


    def get_communities_with_headers(self, digraph):
        """
        Given a digraph, find its communities, with one node as header
        """

        header_to_communities = { 'Other': set() }

        graph = digraph.to_undirected()
        for c in community.greedy_modularity_communities(graph):
            community_graph = digraph.subgraph(c)
            header = self.get_header_node(community_graph) 
            if header:
                header_to_communities[header] = self.remove_header(c, header)
            else:
                header_to_communities['Other'].update(c)

        return header_to_communities


    def filter_dict(self, index, directory):
        """
        Given an index dictionary, filter out any non header
        items not in the provided directory.
        That way we can then order the dict or reshuffle around empty lists.
        TODO
        """

        raise NotImplementedError


    def remove_header(self, nodes, header):
        node_set = set(nodes)
        node_set.remove(header)

        return node_set


    def get_header_node(self, graph):
        ranks = nx.pagerank(graph)
        filtered_ranks = { key:value for (key,value) in ranks.items() if key.startswith(os.path.join(self.root_dir, 'Concepts'))}
        if (len(filtered_ranks) > 2):
            return max(filtered_ranks, key=filtered_ranks.get)
        else:
            return None
    

parser = argparse.ArgumentParser()
parser.add_argument("dir_path", type=Path)
p = parser.parse_args()

notes = NoteGraph(p.dir_path)

pp = pprint.PrettyPrinter(indent=2)
index = pp.pprint(notes.generate_full_index())
