import getpass
import os

from langchain.prompts.chat import ChatPromptTemplate
from langchain.schema import AIMessage
from langchain_openai import ChatOpenAI

from src.utils.logger import get_logger

logger = get_logger(__name__)

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")


def load_prompt(prompt_name: str) -> str:
    """
    Load a prompt template from the PROJECT_ROOT/prompts folder.

    Args:
        prompt_name (str): The filename of the prompt (e.g., "transcription_cleanup.txt").

    Returns:
        str: The content of the prompt template.
    """
    prompt_path = os.path.join("prompts", prompt_name)
    assert os.path.exists(prompt_path), f"Prompt file {prompt_path} does not exist"
    with open(prompt_path, "r", encoding="utf-8") as file:
        return file.read()


class TranscriptionCleaner:
    """
    Uses a composed (chained) runnable to clean up raw transcription text.

    This class builds a chain by composing a runnable prompt with an LLM. The prompt instructs
    the LLM to remove filler words, fix grammatical errors, and produce a coherent cleaned transcription.
    This composition via the pipe operator leverages the new RunnableSequence interface.
    """

    def __init__(
        self,
        model_name: str = "gpt-3.5-turbo",
        prompt_file: str = "transcription_cleanup.txt",
        verbose: bool = False,
    ):
        # Load and convert the prompt text into a runnable ChatPromptTemplate.
        prompt_text = load_prompt(prompt_file)
        self.prompt_template = ChatPromptTemplate.from_template(prompt_text)
        self.llm = ChatOpenAI(model_name=model_name, temperature=0, verbose=verbose)
        self.runnable_chain = self.prompt_template | self.llm

    def clean(self, transcription: str) -> str:
        """
        Synchronously clean the provided transcription text by invoking the composed chain.

        Args:
            transcription (str): The raw transcription text.

        Returns:
            str: The cleaned transcription text.
        """
        result: AIMessage = self.runnable_chain.invoke({"transcription": transcription})
        return result.content.strip()

    async def aclean(self, transcription: str) -> str:
        """
        Asynchronously clean the provided transcription text by invoking the composed chain.

        Args:
            transcription (str): The raw transcription text.

        Returns:
            str: The cleaned transcription text.
        """
        result: AIMessage = await self.runnable_chain.ainvoke({"transcription": transcription})
        return result.content.strip()
