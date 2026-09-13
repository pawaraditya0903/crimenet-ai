import pytest
from backend.app.forensics.merkle import BinaryMerkleTree

def test_merkle_tree_construction_and_inclusion_proof():
    leaves = [
        "hash_ev_01_cdr_records",
        "hash_ev_02_bank_wires",
        "hash_ev_03_anpr_plates",
        "hash_ev_04_crypto_ledger"
    ]
    tree = BinaryMerkleTree(leaves)
    root = tree.root
    assert len(root) == 64

    # 1. Generate inclusion proof for leaf index 1 ("hash_ev_02_bank_wires")
    leaf_hash = tree.leaves[1]
    proof = tree.generate_proof(1)
    assert len(proof) > 0

    # 2. Valid proof verification must return True
    is_valid = BinaryMerkleTree.verify_proof(leaf_hash, proof, root)
    assert is_valid is True

    # 3. Forged / Tampered leaf must fail verification
    forged_leaf = "hash_ev_02_corrupted_tampered"
    is_forged_valid = BinaryMerkleTree.verify_proof(forged_leaf, proof, root)
    assert is_forged_valid is False
