# generate_missing.py
import json, os, random, uuid
from datetime import date, timedelta
from faker import Faker

fake = Faker()
output_dir = "./synthea/output/fhir"
os.makedirs(output_dir, exist_ok=True)

MISSING_CONDITIONS = [
    {
        "snomed": "9566007",
        "icd10": "M45.9",
        "display": "Ankylosing Spondylitis",
        "gender": "M",   # more common in males
        "age_min": 20,
        "age_max": 40,
    },
    {
        "snomed": "9631008",
        "icd10": "M07.60",
        "display": "Psoriatic Arthritis",
        "gender": None,  # both genders
        "age_min": 30,
        "age_max": 55,
    },
    {
        "snomed": "34000006",
        "icd10": "K50.90",
        "display": "Crohn's Disease",
        "gender": None,
        "age_min": 20,
        "age_max": 50,
    },
    {
        "snomed": "64766004",
        "icd10": "K51.90",
        "display": "Ulcerative Colitis",
        "gender": None,
        "age_min": 20,
        "age_max": 50,
    },
    {
        "snomed": "57160005",
        "icd10": "M08.00",
        "display": "Juvenile Idiopathic Arthritis",
        "gender": "F",
        "age_min": 5,
        "age_max": 18,
    },
    {
        "snomed": "201791006",
        "icd10": "M06.09",
        "display": "Seronegative Rheumatoid Arthritis",
        "gender": "F",
        "age_min": 40,
        "age_max": 70,
    },
]

LAB_TESTS = [
    {"code": "11039-5", "display": "Erythrocyte sedimentation rate",
     "unit": "mm/h", "low": 20, "high": 80},
    {"code": "1988-5",  "display": "C-reactive protein",
     "unit": "mg/L",  "low": 5,  "high": 50},
    {"code": "4537-7",  "display": "Rheumatoid factor",
     "unit": "IU/mL", "low": 20, "high": 200},
    {"code": "14334-7", "display": "HLA-B27 Ag",
     "unit": None,    "low": 0,  "high": 1},
]

PAYERS = [
    "UnitedHealthcare", "Cigna", "Humana",
    "Aetna", "Blue Shield of California"
]

def make_patient(condition):
    gender  = condition["gender"] or random.choice(["M", "F"])
    min_age = condition["age_min"]
    max_age = condition["age_max"]
    dob     = date.today() - timedelta(
                days=random.randint(min_age*365, max_age*365))
    return {
        "resourceType": "Patient",
        "id": str(uuid.uuid4()),
        "name": [{
            "use": "official",
            "family": fake.last_name(),
            "given": [fake.first_name_male()
                      if gender == "M"
                      else fake.first_name_female()]
        }],
        "gender": "male" if gender == "M" else "female",
        "birthDate": dob.isoformat(),
        "address": [{
            "line": [fake.street_address()],
            "city": fake.city(),
            "state": fake.state_abbr(),
            "postalCode": fake.zipcode(),
            "country": "US"
        }]
    }

def make_condition(patient_id, condition):
    onset = date.today() - timedelta(days=random.randint(180, 1800))
    return {
        "resourceType": "Condition",
        "id": str(uuid.uuid4()),
        "clinicalStatus": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                "code": "active"
            }]
        },
        "verificationStatus": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                "code": "confirmed"
            }]
        },
        "code": {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": condition["snomed"],
                    "display": condition["display"]
                },
                {
                    "system": "http://hl7.org/fhir/sid/icd-10-cm",
                    "code": condition["icd10"],
                    "display": condition["display"]
                }
            ],
            "text": condition["display"]
        },
        "subject": {"reference": f"Patient/{patient_id}"},
        "onsetDateTime": onset.isoformat()
    }

def make_observation(patient_id):
    test     = random.choice(LAB_TESTS)
    obs_date = date.today() - timedelta(days=random.randint(0, 90))
    value    = round(random.uniform(test["low"], test["high"]), 1)
    obs = {
        "resourceType": "Observation",
        "id": str(uuid.uuid4()),
        "status": "final",
        "category": [{
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                "code": "laboratory"
            }]
        }],
        "code": {
            "coding": [{
                "system": "http://loinc.org",
                "code": test["code"],
                "display": test["display"]
            }]
        },
        "subject": {"reference": f"Patient/{patient_id}"},
        "effectiveDateTime": obs_date.isoformat(),
    }
    if test["unit"]:
        obs["valueQuantity"] = {
            "value": value,
            "unit":  test["unit"],
            "system": "http://unitsofmeasure.org"
        }
    else:
        obs["valueBoolean"] = random.choice([True, False])
    return obs

def make_coverage(patient_id):
    return {
        "resourceType": "Coverage",
        "id": str(uuid.uuid4()),
        "status": "active",
        "beneficiary": {"reference": f"Patient/{patient_id}"},
        "payor": [{"display": random.choice(PAYERS)}],
        "subscriberId": str(random.randint(100000000, 999999999))
    }

def make_bundle(patient, resources):
    all_resources = [patient] + resources
    return {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": [{"resource": r} for r in all_resources]
    }

# generate 50 patients per condition
PATIENTS_PER_CONDITION = 50

total = 0
for condition in MISSING_CONDITIONS:
    for i in range(PATIENTS_PER_CONDITION):
        patient    = make_patient(condition)
        patient_id = patient["id"]

        resources = [
            make_condition(patient_id, condition),
            make_coverage(patient_id),
        ]

        # 2-4 lab results
        for _ in range(random.randint(2, 4)):
            resources.append(make_observation(patient_id))

        bundle   = make_bundle(patient, resources)
        filename = f"python_{condition['display'].replace(' ','_')}_{i+1:03}.json"

        with open(os.path.join(output_dir, filename), "w",
                  encoding="utf-8") as f:
            json.dump(bundle, f, indent=2)

        total += 1

print(f"Generated {total} patients across {len(MISSING_CONDITIONS)} conditions")
print(f"Saved to {output_dir}")