# automated-knowledge-base-index

A quick script to automatically write an Index.md file for a Zettelkasten-like knowledge base of markdown files, so I don't have to keep an index up to date manually.

It's a hacky one!

## Assumptions

- Notes are in markdown with `.md` file extension.
- All notes are on the same level, no subdirectories.
- Internal links (between notes in the knowledge base) are wikilinks `[[like this]]`.
- Index.md already exists in the directory and definitely isn't important (**IT WILL BE OVERWRITTEN**).
- I don't have spaces in my filenames, not sure how it will handle them.

## Requirements

I needed to install [wikitextparser](https://pypi.org/project/wikitextparser/#installation) and [NetworkX](https://networkx.org/documentation/stable/install.html), see their docs for details.

## Usage

`build_index.py path_to_dir`, where `path_to_dir` is the path to the directory which contains the notes. It will do some analysis and write an index file, overwriting it if it already exists (did I mention that it will overwrite Index.md? because it will).

You might also want to change some of the variables in the script too. `INDEX_NAME` is Index.md by default, and the max number of notes it can have for each section is 4 (`num_indexed_notes`). You can also change the title of the note and preamble if you want.

## How does it decide the index?

It treats them as a graph and uses NetworkX's implementation of the Label Propagation algorithm to determine communities of related notes.

Then for each of those communities, it uses NetworkX's implementation of VoteRank to find the most [influential spreaders](https://www.nature.com/articles/srep27823). The goal is to find a set of notes within that community that provide you the best access to the rest of the notes within it.

VoteRank will only return notes with a positive score though, so isolated notes won't be given a section.

The index then consists of sections, each containing 1-4 notes which will hopefully give you an idea of the kind of notes in that section, in lieu of a title. Sections are ordered by total community size.

## Example index

I wrote this by hand based on my own index, but it should be representative. Number of notes per section and number of sections may vary.

---

# Main Index

This index is automated, any edits will be overwritten on next regeneration.

---

## [[ExampleA]]
- [[ExampleA1]]
- [[ExampleB1]]

## [[ExampleB]]
- [[ExampleD1]]
- [[ExampleE]]
- [[ExampleF]]

## [[ExampleC]]

## [[ExampleD]]

---