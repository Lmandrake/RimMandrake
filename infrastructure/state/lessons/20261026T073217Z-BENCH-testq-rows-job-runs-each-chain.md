A testq --rows job runs each chain only up to the requested row; every later row in that chain reads NOT_RUN. That is by design, not a failed run: read NOT_RUN on a --rows job as 'not asked for'.
