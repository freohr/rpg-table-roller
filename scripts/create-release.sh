#!/bin/bash

VERSION=$(dist/rolltable -v)

git switch main || exit 1
git merge --no-ff dev -m "Release v${VERSION}"
git tag -a -m "Release v${VERSION}" "v${VERSION}"
git push --all
git push --tags
