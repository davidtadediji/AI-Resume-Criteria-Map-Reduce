import asyncio
import os

from src.constants import MANDATORY_CRITERIA, DATA_DIR_NAME
from src.constants import RESUME_GENERATION
from src.utils.logger import configured_logger
from src.utils.models import call_llm



data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), DATA_DIR_NAME)
os.makedirs(data_dir, exist_ok=True)

NUMBER_OF_RESUMES = 5


def is_even(number):
    return number % 2 == 0


async def async_call_llm(step, prompt):
    try:
        formatted_prompt = prompt.format(
            condition="fails" if is_even(step) else "completely passes",
            criteria_for_qualification=MANDATORY_CRITERIA
        )
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, call_llm, formatted_prompt, 0.8)

        filepath = os.path.join(data_dir, f'resume_{step}.txt')
        with open(filepath, "w", encoding='utf-8') as f:
            f.write(response)

        configured_logger.info(f"Task {step} complete")
        return response  # Optional: return result if needed

    except Exception as e:
        configured_logger.error(f"[Error] Task {step} failed: {e}")
        return None


async def generate_resumes():
    try:
        tasks = [async_call_llm(i, RESUME_GENERATION) for i in range(NUMBER_OF_RESUMES)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        configured_logger.info("All tasks complete")
        return results
    except Exception as e:
        configured_logger.error(f"[Critical Error] Failed to run tasks: {e}")
        return []


if __name__ == "__main__":
    asyncio.run(generate_resumes())
