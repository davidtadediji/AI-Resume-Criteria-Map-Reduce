DATA_DIR_NAME = "../data"
SCREENING_TOP_K = 10
INTERVIEW_TOP_K = 3

# ===== State ======
RESUMES = "resumes"
DEFAULT = "default"
EVALUATIONS = "evaluations"
QUALIFIES = "qualifies"
REASONS = "reasons"
CANDIDATE_NAME = "candidate_name"
FILTER_SUMMARY = "filter_summary"
QUALIFIED_COUNT = "qualified_count"
QUALIFIED_PERCENTAGE = "qualified_percentage"
TOTAL_CANDIDATES = "total_candidates"
USER = "user"
CRITERIA = 'criteria_embedding'
QUALIFIED_RESUMES = 'qualified_resumes_files'

# ===== Prompts =======
MANDATORY_CRITERIA = """Criteria for qualification.
- At least a bachelor's degree in a relevant field
- At least 3 years of relevant work experience
- Strong technical skills in software development"""

NON_MANDATORY_CRITERIA = """Additional preferred criteria (not mandatory):
- Experience with cloud platforms such as AWS, Azure, or Google Cloud
- Familiarity with Agile or Scrum development methodologies
- Good communication and teamwork skills
- Certifications in relevant technologies or project management (e.g., PMP, AWS Certified)
- Contributions to open source projects or relevant community involvement
- Knowledge of machine learning or AI concepts"""

FULL_CRITERIA = MANDATORY_CRITERIA.join(f'\n\n{NON_MANDATORY_CRITERIA}')
