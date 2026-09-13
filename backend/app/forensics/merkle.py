import math
import hashlib
from typing import List, Dict, Any, Optional

def _hash_pair(left: str, right: str) -> str:
    combined = (left + right).encode('utf-8')
    return hashlib.sha256(combined).hexdigest()

class BinaryMerkleTree:
    """Genuine Binary Merkle Tree implementation for cryptographic evidence verification.
    Provides root calculation and cryptographic audit inclusion proofs.
    """
    def __init__(self, leaf_data_items: Optional[List[str]] = None):
        self.leaves: List[str] = []
        self.levels: List[List[str]] = []
        if leaf_data_items:
            for item in leaf_data_items:
                self.add_leaf(item)
            self.build_tree()

    def add_leaf(self, raw_data_or_hash: str):
        # If already a 64-char hex string, treat as leaf hash; otherwise hash it
        if len(raw_data_or_hash) == 64 and all(c in "0123456789abcdefABCDEF" for c in raw_data_or_hash):
            self.leaves.append(raw_data_or_hash.lower())
        else:
            h = hashlib.sha256(raw_data_or_hash.encode('utf-8')).hexdigest()
            self.leaves.append(h)

    def build_tree(self) -> str:
        """Constructs tree levels and returns the Merkle Root hash."""
        if not self.leaves:
            empty_root = hashlib.sha256(b"CRIMENET_EMPTY_MERKLE_TREE").hexdigest()
            self.levels = [[empty_root]]
            return empty_root

        self.levels = [self.leaves[:]]
        current_level = self.leaves[:]

        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if (i + 1) < len(current_level) else left
                parent = _hash_pair(left, right)
                next_level.append(parent)
            self.levels.append(next_level)
            current_level = next_level

        return self.levels[-1][0]

    @property
    def root(self) -> str:
        if not self.levels:
            return self.build_tree()
        return self.levels[-1][0]

    @property
    def depth(self) -> int:
        return len(self.levels)

    def generate_proof(self, leaf_index: int) -> List[Dict[str, str]]:
        """Generates a Merkle audit inclusion proof path for a leaf at leaf_index."""
        if leaf_index < 0 or leaf_index >= len(self.leaves):
            raise IndexError("Leaf index out of bounds")

        proof = []
        idx = leaf_index

        for level in self.levels[:-1]:
            is_right_sibling = (idx % 2 == 0)
            sibling_idx = idx + 1 if is_right_sibling else idx - 1

            if sibling_idx < len(level):
                sibling_hash = level[sibling_idx]
            else:
                sibling_hash = level[idx]

            proof.append({
                "position": "right" if is_right_sibling else "left",
                "hash": sibling_hash
            })
            idx //= 2

        return proof

    @staticmethod
    def verify_proof(leaf_hash: str, proof: List[Dict[str, str]], expected_root: str) -> bool:
        """Verifies whether a leaf hash belongs to the Merkle tree with expected_root."""
        curr_hash = leaf_hash.lower()

        for step in proof:
            sibling = step["hash"].lower()
            if step["position"] == "right":
                curr_hash = _hash_pair(curr_hash, sibling)
            else:
                curr_hash = _hash_pair(sibling, curr_hash)

        return curr_hash.lower() == expected_root.lower()
