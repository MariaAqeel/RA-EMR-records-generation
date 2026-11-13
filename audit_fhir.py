
# import json
# from pathlib import Path
# from collections import Counter

# FHIR_DIR = Path("synthea/output/fhir")

# files = list(FHIR_DIR.glob("*.json"))

# total_patients = 0
# valid_bundles = 0
# invalid_files = []
# resource_counts = Counter()
# ra_patients = []

# RA_SNOMED = "69896004"

# for file in files:
#     try:
#         with open(file, "r", encoding="utf-8") as f:
#             bundle = json.load(f)

#         if bundle.get("resourceType") != "Bundle":
#             invalid_files.append(file.name)
#             continue

#         valid_bundles += 1
#         entries = bundle.get("entry", [])

#         patient_id = None

#         for entry in entries:
#             resource = entry.get("resource", {})
#             resource_type = resource.get("resourceType")

#             if resource_type:
#                 resource_counts[resource_type] += 1

#             if resource_type == "Patient":
#                 patient_id = resource.get("id")

#         if patient_id:
#             total_patients += 1

#         has_ra = False

#         for entry in entries:
#             resource = entry.get("resource", {})

#             if resource.get("resourceType") != "Condition":
#                 continue

#             code_data = resource.get("code", {})
#             text = code_data.get("text", "").lower()

#             if "rheumatoid arthritis" in text:
#                 has_ra = True

#             for coding in code_data.get("coding", []):
#                 code = str(coding.get("code", ""))
#                 display = coding.get("display", "").lower()
#                 system = coding.get("system", "").lower()

#                 if code == RA_SNOMED:
#                     has_ra = True

#                 if "rheumatoid arthritis" in display:
#                     has_ra = True

#                 if "icd" in system and (
#                     code.startswith("M05") or
#                     code.startswith("M06")
#                 ):
#                     has_ra = True

#         if has_ra:
#             ra_patients.append(patient_id)

#     except Exception as e:
#         invalid_files.append(file.name)
#         print("Error:", file.name, e)

# print("\n========== DATASET AUDIT ==========")
# print("JSON files:", len(files))
# print("Valid FHIR Bundles:", valid_bundles)
# print("Patients:", total_patients)
# print("Invalid files:", len(invalid_files))
# print("RA patients:", len(ra_patients))

# print("\n========== RESOURCE COUNTS ==========")

# for name, count in resource_counts.most_common():
#     print(name, ":", count)

# print("\n========== RA PATIENT IDS ==========")

# for patient in ra_patients:
#     print(patient)

import json, os
from pathlib import Path
from collections import Counter

FHIR_DIR = Path("synthea/output/fhir")

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

RHEUM_ICD10   = ("M05","M06","M07","M08","M45","M46","K50","K51","L40")
RHEUM_KEYWORDS = (
    "rheumatoid arthritis","psoriatic arthritis","ankylosing spondylitis",
    "crohn","ulcerative colitis","psoriasis","juvenile idiopathic arthritis",
)

files          = list(FHIR_DIR.glob("*.json"))
valid_bundles  = 0
invalid_files  = []
resource_counts = Counter()
disease_counts  = Counter()
rheum_patients  = []

for file in files:
    try:
        with open(file, "r", encoding="utf-8") as f:
            bundle = json.load(f)

        if bundle.get("resourceType") != "Bundle":
            invalid_files.append(file.name)
            continue

        valid_bundles += 1
        entries    = bundle.get("entry", [])
        patient_id = None

        for entry in entries:
            resource = entry.get("resource", {})
            rt = resource.get("resourceType")
            if rt:
                resource_counts[rt] += 1
            if rt == "Patient":
                patient_id = resource.get("id")

        found_disease = None

        for entry in entries:
            resource = entry.get("resource", {})
            if resource.get("resourceType") != "Condition":
                continue

            code_data = resource.get("code", {})
            text      = code_data.get("text", "").lower()

            for keyword in RHEUM_KEYWORDS:
                if keyword in text:
                    found_disease = keyword.title()
                    break

            for coding in code_data.get("coding", []):
                code    = str(coding.get("code", ""))
                system  = coding.get("system", "").lower()
                display = coding.get("display", "").lower()

                if code in RHEUM_SNOMED:
                    found_disease = RHEUM_SNOMED[code]
                    break
                if "icd" in system and code.startswith(RHEUM_ICD10):
                    found_disease = code
                    break
                for keyword in RHEUM_KEYWORDS:
                    if keyword in display:
                        found_disease = keyword.title()
                        break

            if found_disease:
                break

        if found_disease and patient_id:
            rheum_patients.append((patient_id, found_disease))
            disease_counts[found_disease] += 1

    except Exception as e:
        invalid_files.append(file.name)
        print("Error:", file.name, e)

print("\n========== DATASET AUDIT ==========")
print(f"JSON files       : {len(files)}")
print(f"Valid Bundles    : {valid_bundles}")
print(f"Invalid files    : {len(invalid_files)}")
print(f"Rheum patients   : {len(rheum_patients)}")

print("\n========== BY DISEASE ==========")
for disease, n in disease_counts.most_common():
    print(f"  {n:4}  {disease}")

print("\n========== RESOURCE COUNTS ==========")
for name, count in resource_counts.most_common():
    print(f"  {name} : {count}")

print("\n========== PATIENT IDS ==========")
for pid, disease in rheum_patients:
    print(f"  {pid}  —  {disease}")