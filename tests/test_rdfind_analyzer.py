from rdfind_analyzer.rdfind_analyzer import *

def test_create_entry_from_line():
    line = "DUPTYPE_FIRST_OCCURRENCE 9458 4 133 16777220 53402257 3 ./foo/bar test 999/test fo ba foobar/.hidden/file.jpg.xml"

    entry = create_entry_from_line(line)

    assert entry.entry_type == "DUPTYPE_FIRST_OCCURRENCE"
    assert entry.id == 9458
    assert entry.depth == 4
    assert entry.size == 133
    assert entry.device == 16777220
    assert entry.inode == 53402257
    assert entry.priority == 3
    assert entry.name == "./foo/bar test 999/test fo ba foobar/.hidden/file.jpg.xml"

def test_is_first_occurrence():
    line = "DUPTYPE_FIRST_OCCURRENCE 9458 4 133 16777220 53402257 3 ./foo/bar test 999/test fo ba foobar/.hidden/file.jpg.xml"

    entry = create_entry_from_line(line)

    assert entry.is_first_occurrence()

def test_is_not_first_occurrence():
    line = "DUPTYPE_OUTSIDE_TREE 9458 4 133 16777220 53402257 3 ./foo/bar test 999/test fo ba foobar/.hidden/file.jpg.xml"

    entry = create_entry_from_line(line)

    assert not entry.is_first_occurrence()