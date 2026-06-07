# Part 1 — Functions Deep Dive (25 min)
# Default Arguments + Multiple Return Values


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

def filter_jobs(jobs,min_salary=15,remote=False):
    return [j for j in jobs if j["salary"]>=min_salary and j.get("remote")==remote]

# Call karo
filter_jobs(jobs)              # defaults use honge
filter_jobs(jobs, min_salary=20)  # override
filter_jobs(jobs, 20, True)    # positional

# ━━━ MULTIPLE RETURN VALUES ━━━
# JS mein yeh nahi hota directly!

def analyze_jobs(job):
    is_good_salary=job["salary"]>=15
    skill_match= len(job.get("matched",[]))>=0
    return is_good_salary,skill_match

# Unpack karo
good_salary, skill_ok= analyze_jobs(jobs[0])
print(good_salary, skill_ok)  # True True
 
# ━━━ *args aur **kwargs ━━━
# JS:  (...args) => {}

def log(*args,**kwargs):
    print("Args:", args)
    print("Kwargs:", kwargs)

log("Naukri", "Applied", portal="Naukri", salary=25)
# Args: ('Naukri', 'Applied')
# Kwargs: {'portal': 'Naukri', 'salary': 25}


# Lambda + List Comprehension (yeh bahut use hoga!)
# ━━━ LAMBDA (= JS Arrow Function) ━━━
# JS:  jobs.sort((a,b) => b.salary - a.salary)
sorted_jobs=sorted(jobs, key=lambda j:j.get("salary"), reverse=True)
print(sorted_jobs[0]["company"])

# ━━━ LIST COMPREHENSION ━━━
# JS:  jobs.filter(j => j.salary >= 15).map(j => j.company)
good_companies=[j["company"] for j in jobs if j["salary"]>=15] # ['Flipkart', 'Swiggy', 'Paytm']
print(good_companies)  

# ━━━ DICT COMPREHENSION ━━━
# Company name → salary mapping
salary_map = {j["company"]:j["salary"] for j in jobs}
print(salary_map)