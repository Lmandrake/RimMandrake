# vendor_viz — pinned browser libraries for `codebase_health.py`

Minified UMD bundles, inlined verbatim into the self-contained HTML that
`src/RimMandrake/Utils/codebase_health.py` writes. They are here so the page
renders with no network, and so the version that produced a given page is
recoverable from git rather than from whatever a CDN serves today.

| file | version | source |
|---|---|---|
| `d3.min.js` | 7.9.0 | `https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js` |
| `d3-weighted-voronoi.min.js` | 1.1.3 | `https://cdn.jsdelivr.net/npm/d3-weighted-voronoi@1.1.3/build/d3-weighted-voronoi.min.js` |
| `d3-voronoi-map.min.js` | 2.1.1 | `https://cdn.jsdelivr.net/npm/d3-voronoi-map@2.1.1/build/d3-voronoi-map.min.js` |
| `d3-voronoi-treemap.min.js` | 1.1.2 | `https://cdn.jsdelivr.net/npm/d3-voronoi-treemap@1.1.2/build/d3-voronoi-treemap.min.js` |

`d3-voronoi-treemap` requires the other two Kcnarf plugins at runtime and must
load after `d3` and both of them. Load order is fixed in the generator.

⚠️ These are third-party files. Do not edit them; replace a whole file and
update its version in the table above.
