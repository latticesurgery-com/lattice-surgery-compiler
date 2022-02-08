# Gate sequences to approximate rz gates with arguments ^n.
# Key is n so 0->rz(pi/1), 1->rz(pi/2), 2->rx(pi/4) ...
# Note that rz(theta) is a rotation by rx(theta/2) in our convention
get_pi_over_2_to_the_n_rz_gate = {
    0: "SS",
    1: "S",
    2: "SSXHSTHSTHTHSTHTHSTHSTHTHTHSTHSTHSTHTHTHSTHTHTHSTHSTHSTHSTHSTHTHSTHTHSTHSTHTHSTHTHSTHSTHSTHTHSTHSTHSTHSTHSTHTHTHTHTHTHSTHTHSTHTHTHSTHTHTHTHSTHTHTHSTHSTHTHSTHSTHTHSTHSTHSTHTHTHSTHTHTHTHTHTHTHTHSTHTHSTHTHSTHSTHSTHTHSTHTHTHSTHTHSTHTHTHSTHTHTHSTHTHSTHTHSTHSTHTHTHSTHSTHSTHTHTHTHTHTHSTHSTHTHSTHTHSTHSTHSTHTHTHSTHTHSTHSTHSTHTHTHTHS",  # noqa: E501
    3: "HTHSTHTHTHSTHTHSTHSTHSTHSTHTHSTHSTHTHSTHSTHTHTHTHSTHSTHTHSTHTHTHSTHSTHSTHSTHTHTHSTHTHSTHTHTHTHTHSTHSTHTHSTHSTHSTHTHTHTHSTHSTHTHSTHSTHTHTHTHSTHSTHSTHSTHSTHSTHSTHSTHTHTHSTHSTHTHTHTHTHTHSTHSTHSTHTHTHSTHSTHSTHTHSTHSTHSTHSTHTHSTHSTHSTHTHTHTHTHSTHSTHTHSTHTH",  # noqa: E501
    4: "XHSTHSTHSTHSTHSTHSTHSTHTHTHTHTHSTHSTHSTHTHSTHSTHTHSTHTHTHTHSTHTHTHSTHSTHTHTHSTHTHTHTHSTHSTHTHTHTHTHSTHSTHTHTHTHSTHTHTHTHTHSTHSTHTHSTHTHTHTHTHSTHTHTHSTHTHSTHSTHTHSTHTHTHSTHTHSTHSTHTHSTHSTHSTHSTHSTHSTHTHTHTHSTHSTHTHTHTHSTHSTHSTHTHTHTHSTHSTHTHTHSTHTHTH",  # noqa: E501
    5: "HTHSTHTHTHSTHSTHTHTHSTHTHTHTHSTHSTHTHTHSTHSTHSTHSTHSTHSTHSTHTHTHSTHTHSTHTHSTHSTHSTHSTHTHTHSTHTHTHTHSTHSTHSTHSTHTHSTHSTHSTHTHSTHSTHTHSTHSTHTHSTHTHSTHTHTHSTHTHSTHSTHSTHTHSTHTHTHTHSTHSTHTHSTHTHTHTHTHTHTHSTHTHTHSTHTHSTHSTHTHTHSTHSTHTHTHSTHSTHTHSTHTHTHSTHSTH",  # noqa: E501
    6: "SSSHSTHTHTHSTHTHTHTHSTHTHSTHSTHSTHSTHTHTHSTHSTHTHSTHSTHSTHSTHTHSTHTHSTHTHTHSTHSTHTHTHTHTHSTHSTHSTHSTHTHSTHSTHTHSTHSTHSTHTHSTHTHTHSTHSTHSTHSTHTHTHTHTHSTHTHSTHTHSTHTHSTHSTHTHSTHSTHTHTHSTHSTHSTHTHTHSTHSTHSTHSTHSTHTHTHSTHSTHTHTHTHTHTHSTHTHTHTHSTHSTHSTHSTHSTHS",  # noqa: E501
    7: "SSSHSTHSTHSTHTHTHTHSTHTHSTHSTHSTHTHTHSTHSTHTHTHSTHTHSTHTHTHTHTHTHTHSTHSTHSTHTHSTHTHSTHTHTHTHSTHTHTHSTHTHSTHTHTHTHSTHSTHSTHTHTHSTHSTHSTHSTHTHSTHSTHSTHSTHTHSTHTHSTHSTHTHTHTHTHSTHTHTHTHSTHSTHSTHTHSTHSTHTHTHSTHTHTHTHTHSTHSTHTHTHTHTHSTHTHTHTHSTHTHTHTHTHTHTHS",  # noqa: E501
    8: "SSSHTHSTHSTHSTHSTHSTHTHSTHTHTHSTHTHSTHTHTHSTHSTHSTHSTHTHSTHTHTHSTHTHSTHTHSTHTHSTHSTHTHTHTHTHTHTHSTHTHSTHTHSTHSTHSTHSTHTHSTHSTHTHSTHSTHTHSTHTHSTHTHSTHTHTHSTHSTHTHSTHSTHSTHTHTHTHTHTHTHTHTHTHSTHTHSTHSTHTHSTHSTHTHSTHTHSTHSTHTHTHTHTHTHTHTHSTHSTHTHTHTHSTHSTHTHTHS",  # noqa: E501
    9: "HTHSTHSTHTHSTHTHTHSTHTHSTHTHTHSTHTHSTHTHTHTHTHSTHTHSTHTHTHSTHSTHSTHSTHSTHTHSTHTHSTHSTHSTHTHTHTHTHTHTHSTHSTHSTHTHTHTHTHTHSTHTHSTHSTHTHTHTHTHSTHSTHTHSTHTHSTHSTHTHSTHSTHTHSTHSTHSTHSTHSTHSTHTHTHTHTHSTHTHTHSTHTHSTHSTHSTHTHTHTHSTHSTHTHTHTHSTHTHSTHST",  # noqa: E501
    10: "XHSTHSTHSTHSTHSTHSTHTHSTHSTHSTHSTHSTHTHSTHTHSTHTHSTHSTHSTHSTHSTHTHTHTHTHSTHSTHTHSTHSTHTHTHTHTHTHTHSTHTHSTHSTHTHTHTHTHSTHTHSTHTHTHSTHTHSTHSTHSTHTHSTHTHTHTHSTHTHTHSTHSTHSTHTHTHTHTHTHTHTHSTHTHTHTHSTHSTHSTHTHTHSTHSTHSTHSTHTHTHTHSTHSTHTHSTHSTHTHTHTHSTHTHSTH",  # noqa: E501
    11: "STHTHTHTHTHTHSTHTHSTHTHSTHTHTHSTHSTHTHTHSTHTHTHTHSTHTHSTHSTHSTHTHSTHTHTHSTHSTHTHSTHTHSTHTHSTHTHTHSTHSTHSTHSTHSTHSTHTHSTHSTHTHTHSTHSTHSTHSTHTHTHTHTHTHTHSTHSTHTHTHTHTHSTHSTHSTHSTHSTHTHSTHTHTHTHSTHSTHSTHTHSTHTHTHSTHTHSTHSTHSTHTHTHTHSTHTHSTHTHTHTHTHSTH",  # noqa: E501
    12: "STHSTHSTHTHTHTHTHSTHTHTHTHSTHTHTHSTHSTHTHTHTHSTHTHTHTHTHTHSTHTHTHTHTHSTHSTHTHSTHSTHTHSTHSTHSTHSTHTHSTHTHSTHSTHTHTHSTHTHTHTHTHSTHTHTHSTHSTHSTHTHSTHSTHTHTHSTHSTHSTHTHSTHSTHTHSTHSTHSTHSTHTHSTHTHSTHSTHTHTHTHTHTHTHTHTHSTHSTHSTHSTHSTHTHTHSTHSTHTHSTHSTHSTH",  # noqa: E501
    13: "SXHTHSTHSTHTHTHSTHSTHTHTHSTHTHSTHTHTHTHTHSTHTHSTHSTHTHTHSTHTHTHSTHSTHTHSTHTHTHSTHTHTHSTHTHSTHSTHTHTHSTHSTHSTHSTHTHSTHTHSTHTHTHSTHTHSTHTHSTHSTHSTHSTHTHTHSTHTHSTHSTHSTHSTHSTHSTHTHSTHTHSTHTHTHSTHTHSTHSTHSTHSTHTHSTHTHTHSTHTHTHSTHSTHSTHTHTHTHSTHTHTHSTHSTHSTHSTH",  # noqa: E501
    14: "SSHSTHSTHSTHTHTHTHSTHSTHSTHTHSTHSTHTHSTHSTHTHSTHTHTHTHSTHTHTHTHTHSTHTHTHSTHTHTHTHTHSTHSTHTHTHTHSTHSTHTHTHSTHTHSTHTHTHTHSTHTHTHSTHSTHTHTHTHTHSTHSTHTHTHSTHSTHTHTHSTHTHSTHSTHSTHSTHTHTHSTHSTHSTHTHTHSTHSTHTHTHTHTHSTHSTHSTHTHSTHSTHTHTHTHTHTHSTHTHSTHS",  # noqa: E501
    15: "HSTHSTHSTHSTHTHSTHSTHSTHSTHTHTHTHSTHTHTHTHTHTHTHSTHTHSTHTHSTHSTHTHTHSTHTHTHSTHTHSTHTHTHSTHSTHTHSTHTHSTHTHTHTHSTHTHTHTHSTHTHTHSTHSTHSTHSTHTHTHSTHTHSTHTHSTHSTHTHTHTHTHTHSTHTHSTHSTHTHTHTHTHSTHSTHSTHSTHTHSTHTHTHTHSTHSTHTHTHTHSTHTHTHTHTHTHTHTHTHSTH",  # noqa: E501
    16: "SSSXHTHSTHSTHTHSTHTHSTHTHSTHSTHTHSTHSTHTHTHSTHSTHSTHSTHTHTHTHSTHTHSTHTHTHTHTHTHTHTHTHSTHSTHTHTHSTHTHSTHTHTHSTHSTHSTHTHTHTHTHSTHSTHTHSTHSTHSTHTHTHTHSTHSTHSTHTHTHTHSTHTHTHSTHSTHTHTHTHSTHTHTHTHTHTHSTHSTHTHSTHTHSTHSTHSTHTHSTHSTHTHTHSTHSTHTHTHTHSTHTHSTHTHTHTH",  # noqa: E501
    17: "SHTHSTHTHSTHTHSTHTHTHSTHSTHTHSTHTHTHTHSTHTHSTHTHSTHTHTHSTHSTHSTHSTHTHTHSTHTHTHSTHTHTHSTHSTHSTHTHTHTHTHTHSTHSTHTHSTHTHSTHSTHSTHTHSTHSTHSTHTHTHTHTHSTHTHTHTHTHSTHSTHTHTHSTHSTHTHSTHTHTHSTHTHTHSTHSTHTHTHTHSTHTHTHTHTHSTHSTHTHSTHSTHTHSTHSTHSTHSTHTHTHS",  # noqa: E501
    18: "SSSTHSTHTHSTHTHSTHSTHSTHTHTHSTHSTHSTHSTHTHTHSTHSTHTHTHTHTHTHSTHTHSTHSTHTHSTHTHSTHTHSTHTHTHSTHSTHTHTHSTHTHSTHSTHTHSTHSTHSTHSTHSTHSTHTHSTHSTHTHSTHTHSTHSTHSTHSTHTHSTHTHTHSTHTHTHSTHSTHSTHTHSTHTHSTHSTHSTHSTHSTHTHSTHTHTHSTHSTHSTHSTHTHTHSTHTHTHSTHSTHTHTHSTHSTHSTHSTHSTH",  # noqa: E501
    19: "SSSHSTHSTHTHSTHSTHSTHTHSTHTHTHTHSTHSTHSTHTHSTHTHTHTHSTHSTHTHSTHSTHSTHTHTHTHTHTHSTHSTHSTHSTHSTHTHSTHSTHSTHSTHSTHSTHSTHTHTHSTHTHTHTHTHTHTHTHSTHTHSTHTHSTHSTHSTHSTHSTHTHTHTHSTHTHSTHSTHTHTHTHSTHSTHTHTHSTHSTHSTHSTHTHSTHSTHSTHTHTHTHSTHTHSTHSTHSTHTHTHTHSTHTHTHSTHSTHS",  # noqa: E501
    20: "SSSXHTHTHTHTHTHTHSTHTHTHSTHTHSTHTHTHTHSTHSTHSTHTHTHTHSTHTHSTHTHTHTHSTHSTHTHTHTHSTHSTHTHTHSTHSTHSTHTHTHTHTHSTHSTHSTHSTHSTHTHSTHTHSTHTHTHSTHTHSTHSTHSTHSTHTHTHTHTHTHTHSTHSTHTHSTHTHSTHTHSTHTHTHSTHTHTHSTHSTHSTHSTHSTHTHTHTHSTHTHTHSTHTHTHSTHS",  # noqa: E501
    21: "SSSHTHSTHSTHSTHSTHTHSTHTHSTHSTHSTHTHTHTHSTHTHTHSTHTHTHSTHSTHSTHTHTHTHSTHSTHSTHSTHSTHTHTHSTHSTHTHTHTHSTHTHTHSTHSTHSTHSTHTHTHTHTHSTHSTHTHSTHTHTHSTHSTHTHSTHSTHTHSTHSTHSTHSTHSTHSTHTHSTHSTHSTHSTHTHSTHTHSTHTHSTHTHSTHTHSTHTHTHSTHSTHSTHSTHSTHTHTHSTHTHTHSTHSTHSTHSTH",  # noqa: E501
    22: "SHSTHSTHSTHSTHSTHTHTHSTHSTHSTHTHTHSTHSTHTHTHTHTHTHSTHSTHSTHTHSTHTHSTHTHSTHSTHSTHSTHTHSTHSTHTHSTHSTHSTHSTHTHSTHSTHTHTHSTHTHTHSTHTHTHTHTHTHTHTHTHSTHSTHTHTHTHSTHTHSTHTHTHSTHTHTHSTHTHSTHTHTHSTHSTHSTHSTHSTHSTHSTHSTHSTHTHSTHTHSTHTHSTHTHSTHTHTHTHSTHSTHTHSTHTHTHSTHSTHTHTH",  # noqa: E501
    23: "XTHTHTHTHSTHSTHTHTHTHTHTHTHSTHTHSTHTHTHTHSTHSTHTHSTHSTHSTHTHSTHTHTHSTHSTHSTHTHSTHSTHSTHSTHTHSTHTHTHTHTHTHTHSTHTHTHSTHSTHTHTHSTHSTHSTHSTHSTHTHSTHTHSTHTHTHSTHTHSTHTHSTHSTHTHSTHTHTHTHSTHSTHTHTHSTHSTHSTHSTHSTHSTHTHSTHSTHSTHTHTHSTHSTHTHTHSTHSTHSTHSTHSTHSTHTHTHSTHTHTHTHSTHSTHSTH",  # noqa: E501
    24: "SXTHSTHSTHSTHTHSTHTHSTHTHSTHSTHTHSTHTHSTHTHSTHTHSTHSTHTHSTHSTHSTHTHTHTHSTHSTHSTHSTHSTHTHSTHTHSTHSTHTHSTHSTHSTHSTHSTHSTHSTHTHTHTHSTHTHTHTHTHSTHTHTHTHTHTHSTHTHSTHTHTHSTHSTHTHTHTHSTHTHTHSTHSTHSTHSTHSTHTHTHTHSTHSTHTHTHSTHSTHTHSTHSTHTHSTHSTHSTHTHSTHSTHTHSTHSTHSTHSTHSTHTHTHSTHSTH",  # noqa: E501
    25: "SHSTHSTHSTHTHSTHSTHTHTHSTHSTHSTHSTHTHTHTHTHSTHSTHSTHSTHTHTHSTHSTHSTHTHSTHSTHTHSTHTHTHTHTHSTHSTHSTHTHTHSTHTHSTHSTHSTHTHSTHTHSTHTHTHSTHSTHSTHTHTHTHSTHTHSTHSTHTHTHSTHSTHSTHTHTHSTHTHSTHTHSTHTHTHSTHSTHTHTHSTHTHTHSTHSTHSTHSTHSTHSTHTHSTHTHSTHSTHTHTHTHTHTHTHSTHSTHSTHSTHTHSTHTHTHSTHSTHSTHTHSTHTH",  # noqa: E501
    26: "XHTHSTHSTHTHSTHTHSTHTHTHTHSTHTHTHSTHTHTHSTHSTHSTHTHSTHSTHSTHSTHTHSTHSTHTHTHTHSTHTHTHSTHTHTHSTHTHTHTHTHTHTHSTHTHTHSTHSTHSTHSTHSTHSTHSTHSTHTHTHSTHTHTHSTHSTHTHTHSTHTHTHSTHTHSTHTHSTHSTHSTHTHSTHSTHTHTHTHSTHTHSTHTHSTHTHSTHSTHTHSTHSTHSTHTHTHTHTHSTHTHSTHSTHSTHTHSTHSTHSTHSTHTHTHSTHTHSTHSTHTHSTHST",  # noqa: E501
    27: "SSXHTHSTHTHSTHTHTHSTHSTHSTHSTHTHSTHSTHSTHSTHTHTHSTHSTHSTHTHSTHSTHTHTHTHSTHTHTHTHSTHSTHSTHTHSTHTHTHTHTHTHSTHTHTHSTHSTHSTHSTHSTHTHSTHTHTHSTHTHTHSTHSTHTHSTHTHSTHSTHTHTHSTHSTHTHSTHTHTHTHSTHTHSTHSTHTHSTHSTHSTHSTHSTHTHTHTHTHTHTHTHSTHTHSTHTHTHSTHTHSTHSTHTHTHSTHSTHTHTHTHTHSTHTHSTHSTHTHTHSTHSTHSTHS",  # noqa: E501
    28: "SXTHSTHTHSTHSTHSTHSTHTHSTHSTHTHSTHSTHTHTHSTHTHTHSTHTHTHTHTHSTHTHSTHSTHTHSTHTHTHSTHTHSTHSTHSTHTHTHTHTHSTHTHTHTHSTHSTHTHSTHTHSTHSTHSTHSTHTHSTHSTHSTHTHTHTHTHTHTHSTHSTHSTHTHSTHSTHSTHSTHSTHTHTHSTHSTHTHTHSTHSTHSTHTHSTHTHTHSTHSTHSTHTHSTHTHSTHSTHTHTHSTHSTHTHSTHSTHTHTHSTHSTHSTHSTHTHTHTHSTHTHTHSTHTHSTHSTHS",  # noqa: E501
    29: "SSXTHSTHSTHSTHSTHSTHSTHSTHTHSTHSTHTHTHTHSTHTHTHTHTHTHTHTHSTHTHSTHSTHTHTHSTHTHTHTHTHTHSTHSTHSTHSTHTHSTHTHSTHSTHSTHTHSTHTHSTHTHSTHTHSTHTHTHTHTHTHTHSTHTHTHSTHTHSTHSTHTHSTHTHSTHTHTHSTHSTHTHSTHSTHTHTHSTHSTHTHSTHTHTHSTHTHSTHSTHTHTHTHSTHTHSTHSTHSTHTHSTHTHSTHSTHSTHTHTHTHSTHSTHSTHSTHTH",  # noqa: E501
}
