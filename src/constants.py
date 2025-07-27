DATA_DIR_NAME = "data/"
SCREENING_TOP_K = 10
INTERVIEW_TOP_K = 3
THRESHOLD = 0.35
NUMBER_OF_TEST_RESUMES = 50

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
CRITERIA_EMBEDDING = 'criteria_embedding'
RESUME_EMBEDDINGS = 'resume_embeddings'
QUALIFIED_RESUMES = 'qualified_resumes_files'
RANKED_RESUMES = 'ranked_resumes'
RELEVANT_RESUMES = 'relevant_resumes'

# ===== Prompts =======
MANDATORY_CRITERIA = """Criteria for qualification.
- Strong technical skills in software development
- At least a bachelor's degree in a relevant field to software development
- At least 3 years of relevant work experience in software engineering"""

NON_MANDATORY_CRITERIA = """Additional preferred criteria (not mandatory):
- Experience with cloud platforms such as AWS, Azure, or Google Cloud
- Familiarity with Agile or Scrum development methodologies
- Good communication and teamwork skills
- Certifications in relevant technologies or project management (e.g., PMP, AWS Certified)
- Contributions to open source projects or relevant community involvement
- Knowledge of machine learning or AI concepts"""

FULL_CRITERIA = MANDATORY_CRITERIA.join(f'\n\n{NON_MANDATORY_CRITERIA}')

EVALUATION_RESULT_FORMAT = """Return your evaluation in YAML format:
```yaml
candidate_name: [Name of the candidate]
qualifies: [true/false]
reasons:
- [First reason for qualification/disqualification]
- [Second reason, if applicable]
```"""

RESUME_GENERATION = """generate a single pre-personalized resume that {condition} this criteria:
{criteria_for_qualification}
Note: just generate the resume don't preface or add any conclusions, respond with resume directly and only
Candidate name is 'Candidate {seed_number}'.
"""