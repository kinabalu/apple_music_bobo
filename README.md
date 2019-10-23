# Apple Music Bobo, Damn you jottinger

## Goals

The initial goals of this project include supporting Pitchfork. The API requirements include:

1. Search for Song
1. Add Song to Playlist

Additional requirements - including those implied by the listed requirements - should be added specifically, because they imply what the supported object model needs to be.

## Objects

1. Song
1. Playlist

## Library Requirements

1. Need to be able to issue RESTful requests
1. Need to be able to map JSON into Python classes (`json` should be able to do it but requires lambda mapping)