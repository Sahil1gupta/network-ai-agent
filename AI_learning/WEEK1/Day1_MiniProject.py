import json

jobs = [
    {"company": "Flipkart",  "role": "Backend Dev",  "salary": 25,
     "skills": ["Spring Boot", "Java", "Kafka"]},
    {"company": "Swiggy",    "role": "Full Stack",   "salary": 20,
     "skills": ["React", "Node", "MongoDB"]},
    {"company": "Paytm",     "role": "Java Dev",     "salary": 18,
     "skills": ["Java", "Spring Boot", "MySQL"]},
    {"company": "TCS",       "role": "Java Dev",     "salary": 8,
     "skills": ["Java", "SQL"]},
]

MY_SKILLS = ["Spring Boot", "Java", "React"]
MIN_SALARY = 15

def filter_by_salary(jobs,min_salary):
    return [j for j in jobs if j["salary"]>=min_salary] #Give me j for each j in jobs, ONLY IF condition is true

# def match_by_skills(jobs, my_skills):
def match_by_skills(jobs, my_skills):
    result = []
    for job in jobs:
        matched = set(my_skills) & set(job["skills"])
        if matched:
            job["matched"] = list(matched)
            job["score"]   = len(matched)
            result.append(job)
    return sorted(result, key=lambda x: x["score"], reverse=True)

def match_by_skills_salary(jobs,myskils,expected_salary):
    result=[]
    for job in jobs:
        matched=set(job["skills"]) & set(myskils)

        if matched and job["salary"] >= expected_salary:
            job["matched"]=list(matched)
            job["score"]= list(len(matched))
            result.append(job)
    return sorted(result, key=lambda x: x["score"], reverse=True)

def match_by_company(jobs,MY_Company):
    result=[]
    for j in jobs:
        matched = set(MY_Company) & set([j["company"]])  # ✅ wrap in list for my practice 
        if matched:
            result.append(j)
    return result

MY_Company= ["TCS","Paytm"]
my_match_company=match_by_company(jobs,MY_Company)
print("my_match_company")
print(my_match_company)
filtered = filter_by_salary(jobs, MIN_SALARY)
matched  = match_by_skills(filtered, MY_SKILLS)

# Save karo
with open("matched_jobs.json", "w") as f:
    json.dump(matched, f, indent=2)

# Results print karo
print(f"\n✅ {len(matched)} jobs matched!\n")
for j in matched:
    print(f"  🏢 {j['company']} — {j['role']}")
    print(f"     💰 {j['salary']} LPA")
    print(f"     🎯 Matched: {j['matched']}\n")