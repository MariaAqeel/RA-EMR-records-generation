import json, os

input_dir  = "./output/fhir"
output_dir = "./filtered"
os.makedirs(output_dir, exist_ok=True)

# ICD-10 codes for your conditions
RA_CODES = ("M05", "M06", "M07", "M08", "L40")

count = 0
skipped = 0

for filename in os.listdir(input_dir):
    if not filename.endswith(".json"):
        continue

    with open(os.path.join(input_dir, filename)) as f:
        bundle = json.load(f)

    # skip hospital bundles synthea also generates
    if bundle.get("type") != "collection":
        skipped += 1
        continue

    # check if patient has any RA/psoriatic arthritis condition
    has_ra = False
    for entry in bundle.get("entry", []):
        resource = entry.get("resource", {})
        if resource.get("resourceType") != "Condition":
            continue
        for coding in resource.get("code", {}).get("coding", []):
            if coding.get("code", "").startswith(RA_CODES):
                has_ra = True
                break
        if has_ra:
            break

    if has_ra:
        out_path = os.path.join(output_dir, filename)
        with open(out_path, "w") as f:
            json.dump(bundle, f, indent=2)
        count += 1

print(f"Done. {count} rheumatology patients saved to {output_dir}")
print(f"Skipped {skipped} non-patient bundles")