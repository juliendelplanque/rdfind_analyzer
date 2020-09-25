from tkinter import *
from tkinter.ttk import *

def create_entry_from_line(line):
    """ Creates an entry from a line (string) extracted from the results file.
    """
    splitted = line.split(maxsplit=7)
    return Entry(
        entry_type=splitted[0],
        id=abs(int(splitted[1])),
        depth=int(splitted[2]),
        size=int(splitted[3]),
        device=int(splitted[4]),
        inode=int(splitted[5]),
        priority=int(splitted[6]),
        name=splitted[7],
    )

def create_report_from_file(path):
    """ Creates a DuplicationReport from the file stored at the path provided
        as argument.
    """
    report = DuplicationReport()
    with open(path, "r", encoding="utf-8") as report_file:
        for line in report_file:
            if not line.startswith("#"):
                entry = create_entry_from_line(line.rstrip('\n'))
                report.add_entry(entry)
    return report

class Error(Exception):
    pass

class Entry(object):
    """ Represents an entry in the result file. Each field is stored as an
        instance variable:
        - entry_type : a string representing the type of the entry (see rdfind
        doc).
        - id : 
        - depth : the depth of the file in the file tree relative to the root
        directory provided to rdfind.
        - size : the size of the file in byte(s).
        - device : the id of the device storing the file.
        - inode : the inode of the file.
        - priority : the value of the priority metric to determinate if the file
        is the original one or a duplicate (see rdfind doc).
        - name : the name of the file, in practice a path relative to the root
        directory provided to rdfind.
    """
    def __init__(self, entry_type, id, depth, size, device, inode, priority, name):
        self.entry_type = entry_type
        self.id = id
        self.depth = depth
        self.size = size
        self.device = device
        self.inode = inode
        self.priority = priority
        self.name = name
    
    def is_first_occurrence(self):
        return self.entry_type == "DUPTYPE_FIRST_OCCURRENCE"
    
    def is_duplicated_within_same_tree(self):
        return self.entry_type == "DUPTYPE_WITHIN_SAME_TREE"
    
    def is_duplicated_outside_tree(self):
        return self.entry_type == "DUPTYPE_OUTSIDE_TREE"
    
    def rdfind_str(self):
        return "%s %s%d %d %d %d %d %d %s" % (
            self.entry_type,
            "" if self.is_first_occurrence() else "-",
            self.id,
            self.depth,
            self.size,
            self.device,
            self.inode,
            self.priority,
            self.name
        )
    
    def children(self):
        return list()
    
    def tree_values(self):
        return [
            self.entry_type,
            self.id,
            self.depth,
            self.size,
            self.device,
            self.inode,
            self.priority,
            self.name
        ]
    
class DuplicationGroup(object):
    def __init__(self, entries=[]):
        self.entries = entries
    
    @property
    def first_occurence(self):
        assert self.entries[0].is_first_occurrence()
        return self.entries[0]
    
    @property
    def duplicated_entries(self):
        for e in self.entries[1:]:
            assert not e.is_first_occurrence()
        return self.entries[1:]
    
    @property
    def first_occurence_id(self):
        return self.first_occurence.id
    
    def should_entry_be_added(self, entry):
        return self.first_occurence_id == entry.id
    
    def add_entry(self, entry):
        self.entries.append(entry)
    
    @property
    def size(self):
        return sum(map(lambda e: e.size, self.entries))
    
    @property
    def space_to_save(self):
        return self.size - self.first_occurence.size
    
    def __len__(self):
        return len(self.entries)
    
    def __getitem__(self, key):
        return self.entries[key]
    
    def __iter__(self):
        for entry in self.entries:
            yield entry
    
    def children(self):
        return self.entries

class DuplicationReport(object):
    def __init__(self, groups=[]):
        self.groups = groups
    
    def add_group(self, group):
        self.groups.append(group)
    
    def should_entry_be_added_to_last_group(self, entry):
        if len(self.groups) == 0:
            return False
        else:
            return self.groups[-1].should_entry_be_added(entry)
    
    def add_entry(self, entry):
        if self.should_entry_be_added_to_last_group(entry):
            self.groups[-1].add_entry(entry)
        else:
            group = DuplicationGroup(entries=[entry])
            self.add_group(group)
    
    @property
    def space_to_save(self):
        return sum(map(lambda g: g.space_to_save, self.groups))
    
    @property
    def size(self):
        return sum(map(lambda g: g.size, self.groups))
    
    @property
    def size_after_duplicated_removal(self):
        return self.size - self.space_to_save
    
    def find_group_for_entry_named(self, entry_name):
        for group in self:
            for entry in group:
                if entry.name == entry_name:
                    return group
        raise Error("No entry named '%s'." % entry_name)

    def children(self):
        return self.groups

    def __iter__(self):
        for group in self.groups:
            yield group

def tkinter_tree(report):
    app = Tk()
    tree = Treeview(app, columns=["#1", "#2", "#3", "#4", "#5", "#6", "#7"])
    tree.heading("#1", text="type")
    tree.column("#1", minwidth=0, width=50)
    tree.heading("#2", text="id")
    tree.column("#2", minwidth=0, width=50)
    tree.heading("#3", text="depth")
    tree.column("#3", minwidth=0, width=50)
    tree.heading("#4", text="size")
    tree.column("#4", minwidth=0, width=50)
    tree.heading("#5", text="device")
    tree.column("#5", minwidth=0, width=50)
    tree.heading("#6", text="inode")
    tree.column("#6", minwidth=0, width=50)
    tree.heading("#7", text="priority")
    tree.column("#7", minwidth=0, width=50)
    for group in report.groups:
        tkgroup = tree.insert("", "end", text=group[0].name)
        for entry in group.entries:
            tree.insert(tkgroup, "end", text=entry.name, values=entry.tree_values())

    tree.pack(fill="both", expand=True)
    app.geometry("800x600")
    app.mainloop()

if __name__ == "__main__":
    import os
    import sys
    import time
    report = create_report_from_file("results.txt")
    print("Size to save %d bytes" % report.space_to_save)
    # for g in report:
        # print(g.first_occurence.name)
        # if not os.path.exists(g.first_occurence.name):
        #     print(g.first_occurence.name)
        # for e in g.duplicated_entries:
        #     if e.name.endswith("P4110384.JPG"):
        #         print(g.first_occurence.name)
        #         sys.exit(0)
        # for e in g.duplicated_entries:
        #     command = "trash \"%s\"" % e.name.replace("$", "\$")
        #     print(command)
        #     # res = os.system(command)
        #     # res = 0
        #     if res != 0:
        #         print("Res is not 0, quitting")
        #         sys.exit(1)
        #     time.sleep(0.1)
    # for g in report.groups:
    #     print(g.size)
    tkinter_tree(report)