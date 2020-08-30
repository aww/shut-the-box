

import pprint
pp = pprint.PrettyPrinter(indent=4)



class STBTransition():
    def __init__(self):
        self.state = None
        self.pshut = None
        self.meanscore = None

class STBState():
    def __init__(self, label):
        self.label = label
        self.next = []
        self.previous = []

    def score(self):
        shifted = self.label
        score = 0
        num = 1
        while(shifted):
            if shifted & 1:
                score += num
            shifted = (shifted >> 1)

def compute_partitions(N=9, partition_encoder=None):
    if partition_encoder is None:
        partition_encoder = lambda x: x
    rolls = {}
    for roll in range(1, 13):
        part = []
        for i in range(min(N, roll), 0, -1):
            if i == roll:
                part.append(partition_encoder([i]))
                continue
            for j in range(i - 1, 0, -1):
                if i + j == roll:
                    part.append(partition_encoder([i, j]))
                    continue
                for k in range(j - 1, 0, -1):
                    if i + j + k == roll:
                        part.append(partition_encoder([i,j,k]))
                        continue
                    for l in range(k - 1, 0, -1):
                        if i + j + k + l == roll:
                            part.append(partition_encoder([i,j,k,l]))
                        # For rolls up to 12 the maxiumum number of elements in our partition is 4.
                        # The only 4-partitions of numbers less than or equal to 12 are
                        # 1 + 2 + 3 + 4 = 10
                        # 1 + 2 + 3 + 5 = 11
                        # 1 + 2 + 3 + 6 = 12
                        # 1 + 2 + 4 + 5 = 12
        rolls[roll] = part
    return rolls

def binary_partition_encoder(x):
    # Presumes these are unique partitions
    r = 0
    for i in x:
        r += 2**(i-1)
    return r

class STBStateGraph():
    def __init__(self, N):
        self.N = N
        self.state_imap = {}
        self.state_map = {}
        self.start = None
        self.end = None

    def fill_imap(self, partition_table):
        for state in range(2**self.N):
            next_states = set()
            for roll, partitions in partition_table.items():
                if roll == 1 and (state & (2**8 + 2**7 + 2**6)):
                    # Rolling 1 is only possible with a single die.
                    # Standard rules allow you to choose to roll a single die
                    # but only when 7, 8, and 9 have been shut.
                    continue
                for part in partitions:
                    if (state | part) == state:
                        next_states.add(state ^ part)
            self.state_imap[state] = next_states

    def fill_state_graph(self):
        # First create the state objects
        for k in self.state_imap.keys():
            self.state_map[k] = STBState(k)
        # Now fill the forward links
        for k, v in self.state_imap.items():
            for nextstate_index in v:
                self.state_map[k].next.append(self.state_map[nextstate_index])
                self.state_map[nextstate_index].previous.append(self.state_map[k])
        self.start = self.state_map[2**self.N - 1]
        self.end = self.state_map[0]

    def to_dot(self):
        lines = []
        lines.append("digraph stategraph {")
        for state in self.state_imap.keys():
            lines.append(f'    v{state} [label="{state:b}"];')
        for state, next_states in self.state_imap.items():
            for next_state in next_states:
                lines.append(f'    v{state} -> v{next_state};')
        lines.append('}')
        return lines


r = compute_partitions(9, binary_partition_encoder)
# The arguement here is just r but with the partition labels transformed to binary representations
pp.pprint({k:[f'{x:b}' for x in v] for k,v in r.items()})


graph = STBStateGraph(9)
graph.fill_imap(r)
graph.fill_state_graph()
#pp.pprint(graph.state_imap)


dot_lines = graph.to_dot()
with open('shutthebox_states.dot', 'w') as f:
    for line in dot_lines:
        f.write(line + '\n')


