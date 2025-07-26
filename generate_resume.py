import asyncio
import os
from constants import CRITERIA_FOR_QUALIFICATION, DIR_NAME
from utils import call_llm

generation_prompt = """generate a resume that {condition} this criteria in different ways, give me each in .txt files:
{criteria_for_qualification}
"""

data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), DIR_NAME)
os.makedirs(data_dir, exist_ok=True)

def is_even(number):
    if number % 2 == 0:
        return True
    return False


async def async_call_llm(step, prompt):
    formatted_prompt = prompt.format(condition="fail" if is_even(step) else "pass",
                                     criteria_for_qualification=CRITERIA_FOR_QUALIFICATION)
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(None, call_llm, formatted_prompt, 0.6)
    print(f"Task {step} complete")
    filepath = os.path.join(data_dir, f'resume_{step}.txt')
    with open(filepath, "w") as f:
        f.write(response)


async def generate_resumes():
    tasks = [async_call_llm(i, generation_prompt) for i in range(50)]
    results = await asyncio.gather(*tasks)
    print("All tasks complete")
    return results


asyncio.run(generate_resumes())
