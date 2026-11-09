#!/usr/bin/env python3
"""Query published OCI image candidates without pulling, installing or pinning.

Intended for isolated GitHub CI discovery. Registry metadata is a candidate
for native arm64 qualification, not proof that a Kvin deployment is safe.
"""
from __future__ import annotations

import json
from urllib.request import Request, urlopen

TAGS = (
    ("Nginx stable Alpine", "library", "nginx", "stable-alpine"),
    ("Uptime Kuma 2.5.9", "louislam", "uptime-kuma", "2.5.9"),
)


def inspect(label, namespace, repository, tag):
    url = ("https://hub.docker.com/v2/repositories/"
           f"{namespace}/{repository}/tags/{tag}")
    request = Request(url, headers={
        "Accept": "application/json",
        "User-Agent": "sanctum-services-image-candidate-check/1",
    })
    with urlopen(request, timeout=18) as response:
        data = json.loads(response.read(200000))
    candidates = [
        item for item in data.get("images", [])
        if item.get("os") == "linux"
        and item.get("architecture") == "arm64"
        and item.get("digest", "").startswith("sha256:")
        and len(item["digest"]) == 71
    ]
    if len(candidates) != 1:
        raise ValueError(f"{label}: expected one linux/arm64 digest; got "
                         f"{len(candidates)}")
    return {
        "label": label,
        "repository": f"docker.io/{namespace}/{repository}",
        "tag": tag,
        "candidate_arm64_digest": candidates[0]["digest"],
        "tag_last_updated": data.get("last_updated"),
        "status": "registry_metadata_only_not_native_qualified",
    }


def main():
    results = [inspect(*row) for row in TAGS]
    print(json.dumps({"schema": "sanctum-image-candidates/v1",
                      "results": results,
                      "configuration_changed": False,
                      "image_downloaded": False}, indent=2))


if __name__ == "__main__":
    main()
