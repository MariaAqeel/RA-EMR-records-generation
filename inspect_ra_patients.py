
import json
import os

input_dir = "synthea/output/fhir"

ra_ids = [
    "64e6f032-d54a-b188-d505-eac064f93e3b",
    "78031280-d656-cf0e-0577-8aebfc782ccd",
    "ac0f63ca-68c2-8b78-c6c9-54d23b6795fe",
    "8eb650dc-e939-1f13-5d74-a28527eb381d"
]

for filename in os.listdir(input_dir):

    if not filename.endswith(".json"):
        continue

    filepath = os.path.join(input_dir, filename)

    with open(filepath, "r", encoding="utf-8") as file:
        bundle = json.load(file)

    entries = bundle.get("entry", [])

    patient_id = None

    for entry in entries:
        resource = entry.get("resource", {})

        if resource.get("resourceType") == "Patient":
            patient_id = resource.get("id")
            break

    if patient_id not in ra_ids:
        continue

    print("\n" + "=" * 60)
    print("RA PATIENT:", patient_id)
    print("FILE:", filename)
    print("=" * 60)

    for entry in entries:

        resource = entry.get("resource", {})
        resource_type = resource.get("resourceType")

        if resource_type == "Patient":
            print("\nPATIENT")
            print(json.dumps(resource, indent=2))

        elif resource_type == "Condition":
            print("\nCONDITION")
            print(json.dumps(resource, indent=2))

        elif resource_type == "Observation":
            print("\nOBSERVATION")
            print(json.dumps(resource, indent=2))

        elif resource_type in [
            "MedicationRequest",
            "MedicationStatement",
            "Encounter"
        ]:
            print("\n", resource_type.upper())
            print(json.dumps(resource, indent=2))
