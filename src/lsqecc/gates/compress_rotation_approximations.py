def partition_gate_sequence(gate_approximation: str):
    partitioned_sequence = list()
    partition = ""
    in_x_basis = False

    # note: The sequence 'HXH' is not covered by this function.
    # But this also not encountered in the cached rotations
    for index, gate in enumerate(gate_approximation):
        if gate in {"S", "T"}:
            partition += gate
            if index == len(gate_approximation) - 1:
                if not in_x_basis:
                    partitioned_sequence.append(partition)
                else:
                    partitioned_sequence.append(partition[0])
                    partitioned_sequence.append(partition[1:])

        elif gate == "X":
            if not len(partition):  # empty partition
                pass
            elif partition[0] == "H":
                partitioned_sequence.append(partition[0])
                partitioned_sequence.append(partition[1:])
            else:
                partitioned_sequence.append(partition)
            partitioned_sequence.append(gate)
            partition = ""

        elif gate == "H":
            if not in_x_basis:
                if not len(partition) == 0:
                    partitioned_sequence.append(partition)
                partition = gate
                if index == len(gate_approximation) - 1:
                    partitioned_sequence.append(partition)
                in_x_basis = True
            else:
                partition += gate
                in_x_basis = False
                partitioned_sequence.append(partition)
                partition = ""

    return partitioned_sequence
