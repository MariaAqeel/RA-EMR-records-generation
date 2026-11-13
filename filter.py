# import json, os

# input_dir  = "./output/fhir"
# output_dir = "./filtered"
# os.makedirs(output_dir, exist_ok=True)

# # ICD-10 codes for your conditions
# RA_CODES = ("M05", "M06", "M07", "M08", "L40")

# count = 0
# skipped = 0

# for filename in os.listdir(input_dir):
#     if not filename.endswith(".json"):
#         continue

#     with open(os.path.join(input_dir, filename)) as f:
#         bundle = json.load(f)

#     # skip hospital bundles synthea also generates
#     if bundle.get("type") != "collection":
#         skipped += 1
#         continue

#     # check if patient has any RA/psoriatic arthritis condition
#     has_ra = False
#     for entry in bundle.get("entry", []):
#         resource = entry.get("resource", {})
#         if resource.get("resourceType") != "Condition":
#             continue
#         for coding in resource.get("code", {}).get("coding", []):
#             if coding.get("code", "").startswith(RA_CODES):
#                 has_ra = True
#                 break
#         if has_ra:
#             break

#     if has_ra:
#         out_path = os.path.join(output_dir, filename)
#         with open(out_path, "w") as f:
#             json.dump(bundle, f, indent=2)
#         count += 1

# print(f"Done. {count} rheumatology patients saved to {output_dir}")
# print(f"Skipped {skipped} non-patient bundles")

import json, os

input_dir  = "./synthea/output/fhir"
output_dir = "./filtered"
os.makedirs(output_dir, exist_ok=True)

# ICD-10 codes
RHEUM_ICD10 = ("M05", "M06", "M07", "M08", "M45", "M46", "K50", "K51", "L40")

# SNOMED codes Synthea actually uses
RHEUM_SNOMED = {
    "69896004":  "Rheumatoid Arthritis",
    "9631008":   "Psoriatic Arthritis",
    "9566007":   "Ankylosing Spondylitis",
    "34000006":  "Crohn's Disease",
    "64766004":  "Ulcerative Colitis",
    "44054006":  "Psoriasis",
    "201791006": "Seronegative RA",
    "57160005":  "Juvenile Idiopathic Arthritis",
}

# text keywords as fallback
RHEUM_KEYWORDS = (
    "rheumatoid arthritis",
    "psoriatic arthritis",
    "ankylosing spondylitis",
    "crohn",
    "ulcerative colitis",
    "psoriasis",
    "juvenile idiopathic arthritis",
    "spondylitis",
)

count = 0
skipped = 0
disease_counts = {}

for filename in os.listdir(input_dir):
    if not filename.endswith(".json"):
        continue

    with open(os.path.join(input_dir, filename),encoding="utf-8") as f:
        bundle = json.load(f)

    # skip non-Bundle files
    if bundle.get("resourceType") != "Bundle":
        skipped += 1
        continue

    # skip if no Patient resource inside
    has_patient = any(
        entry.get("resource", {}).get("resourceType") == "Patient"
        for entry in bundle.get("entry", [])
    )
    if not has_patient:
        skipped += 1
        continue

    found_disease = None

    for entry in bundle.get("entry", []):
        resource = entry.get("resource", {})
        if resource.get("resourceType") != "Condition":
            continue

        code_data = resource.get("code", {})

        # check text field
        text = code_data.get("text", "").lower()
        for keyword in RHEUM_KEYWORDS:
            if keyword in text:
                found_disease = text[:50]
                break

        # check codings
        for coding in code_data.get("coding", []):
            code   = str(coding.get("code", ""))
            system = coding.get("system", "").lower()
            display = coding.get("display", "").lower()

            # check SNOMED
            if code in RHEUM_SNOMED:
                found_disease = RHEUM_SNOMED[code]
                break

            # check ICD-10
            if "icd" in system and code.startswith(RHEUM_ICD10):
                found_disease = code
                break

            # check display text
            for keyword in RHEUM_KEYWORDS:
                if keyword in display:
                    found_disease = display[:50]
                    break

        if found_disease:
            break

    if found_disease:
        with open(os.path.join(output_dir, filename),"w", encoding="utf-8") as f:
            json.dump(bundle, f, indent=2)
        disease_counts[found_disease] = disease_counts.get(found_disease, 0) + 1
        count += 1
    else:
        skipped += 1

print(f"\nDone. {count} rheumatology patients saved to ./filtered")
print(f"Skipped {skipped} files")
print("\nBreakdown by disease:")
for disease, n in sorted(disease_counts.items(), key=lambda x: -x[1]):
    print(f"  {n:3}  {disease}")