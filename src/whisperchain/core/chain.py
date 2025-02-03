import getpass
import os
from pathlib import Path

from langchain.prompts.chat import ChatPromptTemplate
from langchain.schema import AIMessage
from langchain_openai import ChatOpenAI

from whisperchain.utils.logger import get_logger

logger = get_logger(__name__)

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")


def load_prompt(prompt_path: str | Path) -> str:
    """
    Load a prompt template from the PROJECT_ROOT/prompts folder.

    Args:
        prompt_name (str): The filename of the prompt (e.g., "transcription_cleanup.txt").

    Returns:
        str: The content of the prompt template.
    """
    if isinstance(prompt_path, str):
        prompt_path = Path(prompt_path)

    # if the prompt path is relative, convert it to an absolute path
    if not prompt_path.is_absolute():
        prompt_path = Path(__file__).parent.parent / prompt_path

    assert prompt_path.exists(), f"prompt path: {prompt_path} does not exist"
    with open(str(prompt_path), "r", encoding="utf-8") as file:
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
        prompt_path: str = "prompts/transcription_cleanup.txt",  # relative to the whisperchain package
        verbose: bool = False,
    ):
        # Load and convert the prompt text into a runnable ChatPromptTemplate.
        prompt_text = load_prompt(prompt_path)
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
