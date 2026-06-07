import json

name="sahil"
print("Hi",name)


salary=20 # type: ignore
if salary>=15:
    print("Good Job!")
elif salary>=10:
    print("Decent")
else:
    print("keep looking")


# LISTS (=JS Arrays)
skills=["JAVA","Spring boot", "Python"]
skills.append("crewAI")
print(len(skills))
print(skills[0])

# DICT(=JS Objects)
job={
    "title":"Backend Dev",
    "company":"Flipkart",
    "salary":25,
    "remote":True
}
print(job["title"])
print(job.get("location","N/A"))

# FILE I/O + JSON

# ━━━ WRITE JSON ━━━
jobs = [
    {"company": "Flipkart", "role": "Backend Dev", "salary": 25},
    {"company": "Swiggy",   "role": "Java Dev",    "salary": 20},
    {"company": "TCS",      "role": "Java Dev",    "salary": 8}
]

with open("AI_learning/WEEK1/jobs.json","w") as f:
    json.dump(jobs,f,indent=2)
print("jobs.json saved")

# READ JSON
with open("jobs.json","r") as f:
    loaded=json.load(f)
print(f"Total jobs: {len(loaded)}")
print(f"First job:{loaded[0]['company']}")

