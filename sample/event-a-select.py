#!/usr/bin/env python3
"""Event A held-out selection (G34).

Rule (pre-declared): walk the M2 population (bacardi analysis/api_diff.txt at the
pinned commit) in the same stable order as M2 (sorted case ID), skip the 12 M2
cases, and keep taking cases until N cases qualify as "not a straightforward API
replacement".
A case with no Java source compilation errors in the log (e.g. 83a25390, a Kotlin
binary incompatibility in the dependency jar) is excluded: Byam repairs Java client
code, so it has no error location to work from.
"cannot access X" (class missing from the classpath) counts as STRUCTURAL.
A case is also skipped if its project and updated dependency (groupId:artifactId)
match an M2 case or an already selected case. Same project + same dependency means
the same breaking change at a different version, so it is not unseen material.

A case qualifies if at least one of its unique compilation errors in the BUMP
breaking-build log is STRUCTURAL. Errors whose only problem is a missing name
(cannot find symbol, package does not exist, cannot be resolved, undefined method)
count as SYMBOL errors. These could be fixed by a rename or import swap, so they
do not qualify a case on their own.

Usage: python3 -I event-a-select.py <bump_dir> <bacardi_dir> <m2_sample.txt> [N]
Writes a TSV of every case examined to stdout. The selected IDs are the rows with
selected=yes.
"""
import json
import re
import sys
import tarfile

STRUCTURAL = [
    r"cannot be applied to",            # wrong arguments for method/constructor
    r"no suitable (method|constructor)",
    r"incompatible types",
    r"does not override",               # @Override target gone / abstract method not implemented
    r"is not abstract and does not override",
    r"must implement the inherited abstract method",
    r"unreported exception",
    r"not compatible with throws clause",
    r"has (private|protected) access",
    r"is not visible",
    r"is abstract; cannot be instantiated",
    r"Implicit super constructor",
    r"The constructor .* is undefined",
    r"cannot access ",                  # class file missing from classpath: dependency conflict
    r"Type mismatch",
    r"is not applicable for the arguments",
]
STRUCT_RE = re.compile("|".join(STRUCTURAL))
ERR_RE = re.compile(r"\[ERROR\] (/\S+\.java):\[(\d+)[,:](\d+)\] (?:error: )?(.*)")


def errors(bump, case):
    path = f"{bump}/reproductionLogs/successfulReproductionLogs/{case}.log"
    with tarfile.open(path) as t:
        text = t.extractfile(t.getmembers()[0]).read().decode("utf8", "replace")
    seen = {}
    for m in ERR_RE.finditer(text):
        seen.setdefault((m.group(1), m.group(2), m.group(3)), m.group(4).strip())
    return seen


def main():
    bump, bacardi, m2_file = sys.argv[1:4]
    n_target = int(sys.argv[4]) if len(sys.argv) > 4 else 12
    with open(f"{bacardi}/analysis/api_diff.txt") as f:
        pool = sorted(line.strip() for line in f if line.strip())
    with open(m2_file) as f:
        m2 = {line.strip() for line in f if line.strip()}

    print("order\tcase\tproject\tdependency\tversions\terrors\tfiles\tstructural\tqualifies\tstatus\tselected\texample_structural_error")
    def key(meta):
        dep = meta["updatedDependency"]
        return (meta["project"], dep["dependencyGroupID"], dep["dependencyArtifactID"])

    def load(case):
        with open(f"{bump}/data/benchmark/{case}.json") as f:
            return json.load(f)

    used = {key(load(c)) for c in m2}
    taken = 0
    for i, case in enumerate(pool, 1):
        errs = errors(bump, case)
        files = {k[0] for k in errs}
        struct = [msg for msg in errs.values() if STRUCT_RE.search(msg)]
        qualifies = bool(struct)
        meta = load(case)
        if case in m2:
            status = "used_in_M2"
        elif taken >= n_target:
            status = "not_examined_after_target"
        elif not errs:
            status = "excluded_no_java_source_errors"
        elif key(meta) in used:
            status = "same_project_and_dependency_as_used_case"
        else:
            status = "examined"
        selected = status == "examined" and qualifies
        if selected:
            taken += 1
            used.add(key(meta))
        if status == "not_examined_after_target":
            break
        dep = meta["updatedDependency"]
        print("\t".join(map(str, [
            i, case, meta["project"], f'{dep["dependencyGroupID"]}:{dep["dependencyArtifactID"]}',
            f'{dep["previousVersion"]}->{dep["newVersion"]}', len(errs), len(files),
            len(struct), "yes" if qualifies else "no", status,
            "yes" if selected else "no", (struct[0][:120] if struct else ""),
        ])))
    if taken < n_target:
        print(f"# only {taken} qualifying cases available (target {n_target})", file=sys.stderr)


if __name__ == "__main__":
    main()