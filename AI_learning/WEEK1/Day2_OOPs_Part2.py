# ━━━ JAVA vs PYTHON CLASS ━━━

# Java:
# public class Job {
#     private String company;
#     public Job(String company) { this.company = company; }
#     public String getCompany() { return company; }
# }

# Python:
class Job:
    def __init__(self, company, role, salary, skills):
        # __init__ = constructor
        # self = this
        self.company = company
        self.role    = role
        self.salary  = salary
        self.skills  = skills
        self.applied = False  # default value

    def is_good_match(self, my_skills, min_salary=15):
        skill_overlap = set(self.skills) & set(my_skills)
        return len(skill_overlap) > 0 and self.salary >= min_salary

    def apply(self):
        self.applied = True
        print(f"✅ Applied to {self.company} — {self.role}")

    def __str__(self):
        # Java ka toString()
        return f"{self.company} | {self.role} | {self.salary} LPA"


# Object banao
j1 = Job("Flipkart", "Backend Dev", 25, ["Spring Boot", "Java", "Kafka"])
j2 = Job("TCS",      "Java Dev",    8,  ["Java", "SQL"])

MY_SKILLS = ["Spring Boot", "Java"]

print(j1)                               # Flipkart | Backend Dev | 25 LPA
print(j1.is_good_match(MY_SKILLS))      # True
print(j2.is_good_match(MY_SKILLS))      # False (salary < 15)

j1.apply()                              # ✅ Applied to Flipkart — Backend Dev
print(j1.applied)                       # True



# Inheritance — Agent classes ke liye (yeh Week 7 mein kaam aayega!)
# ━━━ BASE AGENT CLASS ━━━
class BaseAgent:
    def __init__(self, name, portal):
        self.name   = name
        self.portal = portal
        self.applied_count = 0

    def log(self, message):
        print(f"[{self.name}] {message}")

    def run(self):
        raise NotImplementedError("Subclass mein implement karo!")


# ━━━ NAUKRI AGENT (inherits BaseAgent) ━━━
class NaukriAgent(BaseAgent):
    def __init__(self):
        super().__init__("NaukriAgent", "naukri.com")

    def run(self, keyword, min_salary):
        self.log(f"Searching '{keyword}' on {self.portal}...")
        # Week 7 mein real Playwright code aayega yahan
        self.log(f"Found 20 jobs, filtering salary >= {min_salary} LPA")
        self.applied_count += 5
        self.log(f"Applied to 5 jobs! ✅")


# ━━━ INSTAHYRE AGENT ━━━
class InstaHyreAgent(BaseAgent):
    def __init__(self):
        super().__init__("InstaHyreAgent", "instahyre.com")

    def run(self, keyword, min_salary):
        self.log(f"Searching '{keyword}' on {self.portal}...")
        self.applied_count += 3
        self.log(f"Applied to 3 jobs! ✅")


# Run karo
naukri   = NaukriAgent()
instahyre = InstaHyreAgent()

naukri.run("Backend Developer", 15)
instahyre.run("Backend Developer", 15)

print(f"\nTotal applied: {naukri.applied_count + instahyre.applied_count}")