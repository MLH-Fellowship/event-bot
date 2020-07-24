#!/bin/bash

echo -n "$GC_SA" | base64 -d > credentials.json
