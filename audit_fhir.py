
import json
from pathlib import Path
from collections import Counter

FHIR_DIR = Path("synthea/output/fhir")

files = list(FHIR_DIR.glob("*.json"))

total_patients = 0
valid_bundles = 0
invalid_files = []
resource_counts = Counter()
ra_patients = []

RA_SNOMED = "69896004"

for file in files:
    try:
        with open(file, "r", encoding="utf-8") as f:
            bundle = json.load(f)

        if bundle.get("resourceType") != "Bundle":
            invalid_files.append(file.name)
            continue

        valid_bundles += 1
        entries = bundle.get("entry", [])

        patient_id = None

        for entry in entries:
            resource = entry.get("resource", {})
            resource_type = resource.get("resourceType")

            if resource_type:
                resource_counts[resource_type] += 1

            if resource_type == "Patient":
                patient_id = resource.get("id")

        if patient_id:
            total_patients += 1

        has_ra = False

        for entry in entries:
            resource = entry.get("resource", {})

            if resource.get("resourceType") != "Condition":
                continue

            code_data = resource.get("code", {})
            text = code_data.get("text", "").lower()

            if "rheumatoid arthritis" in text:
                has_ra = True

            for coding in code_data.get("coding", []):
                code = str(coding.get("code", ""))
                display = coding.get("display", "").lower()
                system = coding.get("system", "").lower()

                if code == RA_SNOMED:
                    has_ra = True

                if "rheumatoid arthritis" in display:
                    has_ra = True

                if "icd" in system and (
                    code.startswith("M05") or
                    code.startswith("M06")
                ):
                    has_ra = True

        if has_ra:
            ra_patients.append(patient_id)

    except Exception as e:
        invalid_files.append(file.name)
        print("Error:", file.name, e)

print("\n========== DATASET AUDIT ==========")
print("JSON files:", len(files))
print("Valid FHIR Bundles:", valid_bundles)
print("Patients:", total_patients)
print("Invalid files:", len(invalid_files))
print("RA patients:", len(ra_patients))

print("\n========== RESOURCE COUNTS ==========")

for name, count in resource_counts.most_common():
    print(name, ":", count)

print("\n========== RA PATIENT IDS ==========")

for patient in ra_patients:
    print(patient)
