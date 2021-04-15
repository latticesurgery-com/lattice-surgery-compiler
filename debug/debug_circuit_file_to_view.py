import segmented_qasm_parser



if __name__ == "__main__":

    c = segmented_qasm_parser.parse_file("assets/reversible.qasm")

    print(c.render_ascii())
