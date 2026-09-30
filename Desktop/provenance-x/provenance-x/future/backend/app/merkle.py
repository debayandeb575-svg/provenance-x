import hashlib


def node_hash(
    left: str,
    right: str
) -> str:

    return hashlib.sha256(
        (left + right).encode()
    ).hexdigest()


def merkle_root(
    leaves: list[str]
) -> str:

    if not leaves:

        return hashlib.sha256(
            b"EMPTY"
        ).hexdigest()

    level = leaves[:]

    while len(level) > 1:

        if len(level) % 2:

            level.append(
                level[-1]
            )

        level = [
            node_hash(
                level[i],
                level[i + 1]
            )
            for i in range(
                0,
                len(level),
                2
            )
        ]

    return level[0]


def proof(
    leaves: list[str],
    index: int
) -> list[dict]:

    if (
        not leaves
        or index < 0
        or index >= len(leaves)
    ):
        return []

    level = leaves[:]

    idx = index

    result = []

    while len(level) > 1:

        if len(level) % 2:

            level.append(
                level[-1]
            )

        sibling = (
            idx - 1
            if idx % 2
            else idx + 1
        )

        result.append(
            {
                "position":
                    "left"
                    if idx % 2
                    else "right",

                "hash":
                    level[sibling],
            }
        )

        next_level = []

        for i in range(
            0,
            len(level),
            2
        ):

            next_level.append(
                node_hash(
                    level[i],
                    level[i + 1]
                )
            )

        idx //= 2

        level = next_level

    return result


def verify_proof(
    leaf: str,
    proof_items: list[dict],
    expected_root: str
) -> bool:

    current = leaf

    for item in proof_items:

        if item["position"] == "left":

            current = node_hash(
                item["hash"],
                current
            )

        else:

            current = node_hash(
                current,
                item["hash"]
            )

    return current == expected_root