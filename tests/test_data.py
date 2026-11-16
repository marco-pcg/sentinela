import csv
import json
from collections import Counter
from pathlib import Path

import pytest

from sentinela.data import main, read_inventory, split_folds, validate_label


def inventory(tmp_path, count=114):
    path = tmp_path / "inventory.csv"
    with path.open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["image", "label", "group"])
        for i in range(count):
            image = tmp_path / f"image{i}.jpeg"
            image.write_bytes(f"synthetic fixture {i}".encode())
            label = image.with_suffix(".txt")
            label.write_text(f"{i % 4} 0.5 0.5 0.4 0.4\n")
            writer.writerow([image.name, label.name, f"subject{i // 2}"])
    return path


def test_all_114_samples_validated_once_with_groups_disjoint(tmp_path):
    samples = read_inventory(inventory(tmp_path))
    folds = split_folds(samples)
    counts = Counter(s["image"] for fold in folds for s in fold["val"])
    assert len(counts) == 114 and set(counts.values()) == {1}
    for fold in folds:
        train = {s["group"] for s in fold["train"]}
        val = {s["group"] for s in fold["val"]}
        assert train.isdisjoint(val)
        assert len(fold["train"]) + len(fold["val"]) == 114
    assert folds == split_folds(list(reversed(samples)))
    assert folds != split_folds(samples, seed=42)


def test_inventory_row_order_does_not_change_membership(tmp_path):
    path = inventory(tmp_path, 12)
    expected = split_folds(read_inventory(path))
    lines = path.read_text().splitlines()
    path.write_text("\n".join([lines[0], *reversed(lines[1:])]) + "\n")
    assert split_folds(read_inventory(path)) == expected


def test_manifest_records_hashes_and_refuses_overwrite(tmp_path):
    path = inventory(tmp_path, 12)
    output = tmp_path / "folds.json"
    assert main([str(path), str(output)]) == 0
    content = json.loads(output.read_text())
    assert content["class_names"]["0"] == "joinha"
    assert len(content["inventory_sha256"]) == 64
    assert len(content["folds"][0]["val"][0]["image_sha256"]) == 64
    with pytest.raises(SystemExit):
        main([str(path), str(output)])
    assert json.loads(output.read_text()) == content


@pytest.mark.parametrize(
    "text",
    [
        "4 0.5 0.5 0.2 0.2",
        "0 nan 0.5 0.2 0.2",
        "0 0.5 0.5 0 0.2",
        "0 0.1 0.5 0.5 0.5",
        "0 0.5 0.5 0.2",
        "0 0.5 0.5 2 2",
    ],
)
def test_invalid_boxes_fail(tmp_path, text):
    path = tmp_path / "label.txt"
    path.write_text(text)
    with pytest.raises(ValueError):
        validate_label(path)


def test_empty_background_label_is_valid(tmp_path):
    path = tmp_path / "background.txt"
    path.write_text("")
    validate_label(path)


def test_missing_labels_duplicate_sources_and_too_few_groups_fail(tmp_path):
    path = inventory(tmp_path, 12)
    samples = read_inventory(path)
    with pytest.raises(ValueError):
        split_folds(samples, folds=7)
    with path.open("a") as stream:
        stream.write("image0.jpeg,image0.txt,subject0\n")
    with pytest.raises(ValueError, match="Duplicate"):
        read_inventory(path)
    Path(samples[0].label).unlink()
    with pytest.raises(FileNotFoundError):
        read_inventory(path)


def test_identical_images_in_different_groups_fail(tmp_path):
    path = inventory(tmp_path, 12)
    (tmp_path / "image2.jpeg").write_bytes((tmp_path / "image0.jpeg").read_bytes())
    with pytest.raises(ValueError, match="different groups"):
        read_inventory(path)
