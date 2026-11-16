"""Validate a source inventory and produce reproducible group-disjoint folds."""

import argparse
import csv
import hashlib
import json
import random
from dataclasses import asdict, dataclass
from math import isfinite
from pathlib import Path

CLASS_NAMES = {0: "joinha", 1: "paz", 2: "saudacao_vulcana", 3: "rock"}


@dataclass(frozen=True)
class Sample:
    image: str
    label: str
    group: str
    image_sha256: str
    label_sha256: str


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def validate_label(path: Path) -> None:
    """Validate YOLO normalized boxes. Empty labels are explicit background images."""
    for line_number, line in enumerate(path.read_text().splitlines(), 1):
        parts = line.split()
        if len(parts) != 5 or parts[0] not in {str(key) for key in CLASS_NAMES}:
            raise ValueError(f"{path}:{line_number}: expected class_id x y width height")
        x, y, width, height = map(float, parts[1:])
        if not all(isfinite(v) for v in (x, y, width, height)):
            raise ValueError(f"{path}:{line_number}: nonfinite box")
        if not (0 <= x <= 1 and 0 <= y <= 1 and 0 < width <= 1 and 0 < height <= 1):
            raise ValueError(f"{path}:{line_number}: invalid normalized box")
        if (
            min(x - width / 2, y - height / 2) < -1e-6
            or max(x + width / 2, y + height / 2) > 1 + 1e-6
        ):
            raise ValueError(f"{path}:{line_number}: box outside image")


def read_inventory(path: Path) -> list[Sample]:
    samples = []
    images = set()
    hashes: dict[str, str] = {}
    with path.open(newline="", encoding="utf-8") as stream:
        rows = csv.DictReader(stream)
        if rows.fieldnames != ["image", "label", "group"]:
            raise ValueError("CSV header must be image,label,group")
        for row in rows:
            if set(row) != {"image", "label", "group"} or any(
                not value or not value.strip() for value in row.values()
            ):
                raise ValueError("Every row needs image, label and group")
            image = (path.parent / row["image"]).resolve()
            label = (path.parent / row["label"]).resolve()
            if image.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
                raise ValueError(f"Unsupported image extension: {image}")
            if image in images:
                raise ValueError(f"Duplicate image path: {image}")
            images.add(image)
            validate_label(label)
            image_hash = digest(image)
            group = row["group"].strip()
            if image_hash in hashes and hashes[image_hash] != group:
                raise ValueError("Identical image content assigned to different groups")
            hashes[image_hash] = group
            samples.append(Sample(str(image), str(label), group, image_hash, digest(label)))
    if not samples:
        raise ValueError("Inventory is empty")
    return sorted(samples, key=lambda item: (item.group, item.image))


def split_folds(samples: list[Sample], folds: int = 5, seed: int = 0) -> list[dict]:
    samples = sorted(samples, key=lambda item: (item.group, item.image))
    groups = sorted({sample.group for sample in samples})
    if folds < 2 or len(groups) < folds:
        raise ValueError("Need at least two folds and at least one independent group per fold")
    random.Random(seed).shuffle(groups)
    membership = {group: index % folds for index, group in enumerate(groups)}
    return [
        {
            "train": [asdict(s) for s in samples if membership[s.group] != fold],
            "val": [asdict(s) for s in samples if membership[s.group] == fold],
        }
        for fold in range(folds)
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inventory", type=Path)
    parser.add_argument("output", type=Path, help="New JSON manifest; never overwrites a file")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args(argv)
    try:
        samples = read_inventory(args.inventory)
        manifest = {
            "schema_version": 1,
            "seed": args.seed,
            "inventory_sha256": digest(args.inventory),
            "class_names": CLASS_NAMES,
            "folds": split_folds(samples, args.folds, args.seed),
        }
        with args.output.open("x", encoding="utf-8") as stream:
            json.dump(manifest, stream, indent=2)
            stream.write("\n")
    except (OSError, ValueError) as error:
        parser.exit(2, f"sentinela-split: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
