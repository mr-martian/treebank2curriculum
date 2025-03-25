from udapi.core.block import Block

RELATIONS = [
    [], # level 0, no simplification
    ['vocative', 'dislocated'],
    ['acl', 'acl:relcl'],
    ['nmod', 'nummod', 'appos', 'amod'],
    ['obl'],
    ['conj'],
]

class Simplify(Block):
    def __init__(self, *args, level=1, **kwargs):
        super().__init__(*args, **kwargs)
        self.level = level
        self.drop = set()
        for i, row in enumerate(RELATIONS):
            if i > level:
                break
            self.drop.update(row)
    def process_tree(self, tree):
        for node in tree.descendants:
            if node.deprel in self.drop:
                node.remove()
        print('<div class="sentence">')
        print('<span class="sent_id">'+tree.sent_id+'</span>')
        print('<span class="text">'+tree.compute_text()+'</span>')
        print('</div>')
