#!/usr/bin/env bash
set -e

image_name="${IMAGE_NAME:-"alexiskandre/meinheld-gunicorn"}"
tag_name="${TAG_NAME:-"python3.7-alpine-latest"}"

if [ "$tag_name" == "latest" ] ; then
    tag_name="python3.7-alpine-latest"
fi

if [ "$IS_SIMPLIFIED" == 1 ] ; then
    tag_name="$tag_name-simplified"
fi
DOCKERFILE=$tag_name
use_tag="$image_name:$tag_name"

echo "$DOCKERFILE"

docker build -t "$use_tag" --file "./docker-images/${DOCKERFILE}.dockerfile" "./docker-images/"

