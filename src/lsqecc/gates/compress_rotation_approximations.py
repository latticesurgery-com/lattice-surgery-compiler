def partition_gate_sequence(gate_approximation: str):
    partitioned_sequence = list()
    partition = ""
    in_x_basis = False

    for index, gate in enumerate(gate_approximation):
        if index == len(gate_approximation) - 1:
            partition += gate
            if partition[0] == "H":
                partitioned_sequence.append(partition[0])
                partitioned_sequence.append(partition[1:])
        elif gate in {"S", "T"}:
            partition += gate
        elif gate == "X":
            if partition[0] == "H":
                partitioned_sequence.append(partition[0])
                partitioned_sequence.append(partition[1:])
            partitioned_sequence.append(gate)
            partition = ""

        elif gate == "H":
            if not in_x_basis:
                if not len(partition) == 0:
                    partitioned_sequence.append(partition)
                partition = gate
                in_x_basis = True
            else:
                partition += gate
                in_x_basis = False
                partitioned_sequence.append(partition)
                partition = ""

    return partitioned_sequence
