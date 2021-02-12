from circuit import *



if __name__ == "__main__":

    c = Circuit.load_from_file("assets/reversible.qasm")

    print(c.render_ascii())
