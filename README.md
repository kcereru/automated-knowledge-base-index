# automated-knowledge-base-index

I use Obsidian to work with my Zettelkasten-like knowledge base of markdown files (notes). This is a script to generate an index file so I don't have to keep an index up to date manually.

Some context because it's pretty closely tied to my particular organisational quirks: in my current note naming system, I have "nameless" files which contain all kinds of thoughts I wrote down and might want to resurface later (with IDs like 9a4b1) and "named" files (for concepts like "Zettelkasten", which I'll just `[[wikilink]]` as I write my other thoughts).

This script turns my notes into a graph using wikilinks between notes, and then prints out an index of "named" files in sections based on communities in the graph and the most important notes in that section. Importance of a note is determined using PageRank within the section to try and determine which concepts are most relevant. This gives me a way to quickly find particular areas without having to keep a map of content (MOC) file up to date.

Since I fairly often just link to a concept without creating a note for it, this means a whole bunch of notes in the index may not exist, but in Obsidian I can just click on the note to create it and then traverse the backlinks from there (which I currently use the Map Of Content plugin for, it's really good! https://github.com/Robin-Haupt-1/Obsidian-Map-of-Content).


## Example index

I wrote this by hand based on my own index, but it should be representative. Number of notes per section and number of sections may vary.

---

# Index

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
