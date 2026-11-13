# import json, os, random, uuid
# from datetime import date, timedelta
# from faker import Faker

# fake = Faker()

# input_dir  = "./filtered"
# output_dir = "./final"
# os.makedirs(output_dir, exist_ok=True)

# # your five real payers from the SRS
# PAYERS = [
#     "UnitedHealthcare",
#     "Cigna",
#     "Humana",
#     "Aetna",
#     "Blue Shield of California"
# ]

# # prior drugs payers require proof of failure (step therapy)
# PRIOR_DRUGS = [
#     {"code": "105585", "display": "methotrexate"},
#     {"code": "114194", "display": "hydroxychloroquine"},
#     {"code": "327361", "display": "leflunomide"},
#     {"code": "373747", "display": "etanercept"},
#     {"code": "327362", "display": "adalimumab"},
# ]

# # your three target drugs from the SRS
# TARGET_DRUGS = [
#     {"code": "356248", "display": "Cimzia (certolizumab pegol)"},
#     {"code": "358258", "display": "Orencia (abatacept)"},
#     {"code": "614391", "display": "Simponi Aria (golimumab)"},
# ]

# def make_prior_medication(patient_id):
#     drug  = random.choice(PRIOR_DRUGS)
#     start = date.today() - timedelta(days=random.randint(365, 900))
#     end   = start + timedelta(days=random.randint(90, 365))
#     return {
#         "resourceType": "MedicationStatement",
#         "id": str(uuid.uuid4()),
#         "status": "stopped",
#         "medicationCodeableConcept": {
#             "coding": [{
#                 "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
#                 "code": drug["code"],
#                 "display": drug["display"]
#             }],
#             "text": drug["display"]
#         },
#         "subject": {"reference": f"Patient/{patient_id}"},
#         "effectivePeriod": {
#             "start": start.isoformat(),
#             "end":   end.isoformat()
#         },
#         "reasonCode": [{"text": "Inadequate response or intolerance"}]
#     }

# def make_target_medication_request(patient_id):
#     drug = random.choice(TARGET_DRUGS)
#     return {
#         "resourceType": "MedicationRequest",
#         "id": str(uuid.uuid4()),
#         "status": "draft",
#         "intent": "proposal",
#         "medicationCodeableConcept": {
#             "coding": [{
#                 "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
#                 "code": drug["code"],
#                 "display": drug["display"]
#             }],
#             "text": drug["display"]
#         },
#         "subject": {"reference": f"Patient/{patient_id}"}
#     }

# def get_patient_id(bundle):
#     for entry in bundle.get("entry", []):
#         if entry.get("resource", {}).get("resourceType") == "Patient":
#             return entry["resource"]["id"]
#     return None

# def replace_payer(bundle):
#     payer = random.choice(PAYERS)
#     for entry in bundle.get("entry", []):
#         resource = entry.get("resource", {})
#         if resource.get("resourceType") == "Coverage":
#             resource["payor"] = [{"display": payer}]
#             resource["subscriberId"] = str(random.randint(100000000, 999999999))
#     return bundle

# count = 0
# for filename in os.listdir(input_dir):
#     if not filename.endswith(".json"):
#         continue

#     with open(os.path.join(input_dir, filename)) as f:
#         bundle = json.load(f)

#     patient_id = get_patient_id(bundle)
#     if not patient_id:
#         continue

#     # replace fictional payer with one of your five real payers
#     bundle = replace_payer(bundle)

#     # add 1-3 prior failed medications (step therapy evidence)
#     num_prior = random.randint(1, 3)
#     for _ in range(num_prior):
#         bundle["entry"].append({
#             "resource": make_prior_medication(patient_id)
#         })

#     # add the target drug request (Cimzia / Orencia / Simponi Aria)
#     bundle["entry"].append({
#         "resource": make_target_medication_request(patient_id)
#     })

#     out_path = os.path.join(output_dir, filename)
#     with open(out_path, "w") as f:
#         json.dump(bundle, f, indent=2)

#     count += 1

# print(f"Done. {count} enriched patient bundles saved to ./final")

import json, os, random, uuid
from datetime import date, timedelta

input_dir  = "./filtered"
output_dir = "./final"
os.makedirs(output_dir, exist_ok=True)

PAYERS = [
    "UnitedHealthcare",
    "Cigna",
    "Humana",
    "Aetna",
    "Blue Shield of California"
]

PRIOR_DRUGS = [
    {"code": "105585", "display": "methotrexate"},
    {"code": "114194", "display": "hydroxychloroquine"},
    {"code": "327361", "display": "leflunomide"},
    {"code": "373747", "display": "etanercept"},
    {"code": "327362", "display": "adalimumab"},
]

TARGET_DRUGS = [
    {"code": "356248", "display": "Cimzia (certolizumab pegol)"},
    {"code": "358258", "display": "Orencia (abatacept)"},
    {"code": "614391", "display": "Simponi Aria (golimumab)"},
]

def get_patient_id(bundle):
    for entry in bundle.get("entry", []):
        if entry.get("resource", {}).get("resourceType") == "Patient":
            return entry["resource"]["id"]
    return None

def make_prior_medication(patient_id):
    drug  = random.choice(PRIOR_DRUGS)
    start = date.today() - timedelta(days=random.randint(365, 900))
    end   = start + timedelta(days=random.randint(90, 365))
    return {
        "resourceType": "MedicationStatement",
        "id": str(uuid.uuid4()),
        "status": "stopped",
        "medicationCodeableConcept": {
            "coding": [{
                "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                "code": drug["code"],
                "display": drug["display"]
            }],
            "text": drug["display"]
        },
        "subject": {"reference": f"Patient/{patient_id}"},
        "effectivePeriod": {
            "start": start.isoformat(),
            "end":   end.isoformat()
        },
        "reasonCode": [{"text": "Inadequate response or intolerance"}]
    }

def make_target_medication_request(patient_id):
    drug = random.choice(TARGET_DRUGS)
    return {
        "resourceType": "MedicationRequest",
        "id": str(uuid.uuid4()),
        "status": "draft",
        "intent": "proposal",
        "medicationCodeableConcept": {
            "coding": [{
                "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                "code": drug["code"],
                "display": drug["display"]
            }],
            "text": drug["display"]
        },
        "subject": {"reference": f"Patient/{patient_id}"}
    }

def replace_payer(bundle, patient_id):
    payer = random.choice(PAYERS)
    replaced = False
    for entry in bundle.get("entry", []):
        resource = entry.get("resource", {})
        if resource.get("resourceType") == "Coverage":
            resource["payor"] = [{"display": payer}]
            resource["subscriberId"] = str(random.randint(100000000, 999999999))
            replaced = True
    # add Coverage if Synthea did not generate one
    if not replaced:
        bundle["entry"].append({
            "resource": {
                "resourceType": "Coverage",
                "id": str(uuid.uuid4()),
                "status": "active",
                "beneficiary": {"reference": f"Patient/{patient_id}"},
                "payor": [{"display": payer}],
                "subscriberId": str(random.randint(100000000, 999999999))
            }
        })
    return bundle

count = 0
for filename in os.listdir(input_dir):
    if not filename.endswith(".json"):
        continue

    with open(os.path.join(input_dir, filename), encoding="utf-8") as f:
        bundle = json.load(f)

    patient_id = get_patient_id(bundle)
    if not patient_id:
        continue

    bundle = replace_payer(bundle, patient_id)

    for _ in range(random.randint(1, 3)):
        bundle["entry"].append({
            "resource": make_prior_medication(patient_id)
        })

    bundle["entry"].append({
        "resource": make_target_medication_request(patient_id)
    })

    with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
        json.dump(bundle, f, indent=2)

    count += 1

print(f"Done. {count} enriched patient bundles saved to ./final")