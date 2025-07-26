import asyncio
import os
from constants import CRITERIA_FOR_QUALIFICATION, DIR_NAME
from utils import call_llm

generation_prompt = """generate a single pre-personalized resume that {condition} this criteria:
{criteria_for_qualification}
Note: just generate the resume don't preface or add any conclusions, respond with resume directly and only
use an unusual name for candidate.
"""

data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), DIR_NAME)
os.makedirs(data_dir, exist_ok=True)

NUMBER_OF_RESUMES = 5

def is_even(number):
    if number % 2 == 0:
        return True
    return False


async def async_call_llm(step, prompt):
    formatted_prompt = prompt.format(condition="fails" if is_even(step) else "completely passes",
                                     criteria_for_qualification=CRITERIA_FOR_QUALIFICATION)
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(None, call_llm, formatted_prompt, 0.8)
    print(f"Task {step} complete")
    filepath = os.path.join(data_dir, f'resume_{step}.txt')
    with open(filepath, "w", encoding='utf-8') as f:
        f.write(response)


async def generate_resumes():
    tasks = [async_call_llm(i, generation_prompt) for i in range(NUMBER_OF_RESUMES)]
    results = await asyncio.gather(*tasks)
    print("All tasks complete")
    return results


asyncio.run(generate_resumes())
