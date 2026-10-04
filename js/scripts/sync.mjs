// Copy the benchmark data and licences from the repo root into the package, so the npm
// package bundles exactly the data the Python package does.
import { cpSync, mkdirSync, rmSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const pkg = join(here, "..");
const root = join(pkg, "..");
rmSync(join(pkg, "data"), { recursive: true, force: true });
mkdirSync(join(pkg, "data"));
for (const p of ["pairs.jsonl", "conv-parts", "conv-long"]) {
  cpSync(join(root, "data", p), join(pkg, "data", p), { recursive: true });
}
for (const f of ["LICENSE", "LICENSE-DATA"]) cpSync(join(root, f), join(pkg, f));
