from pydantic import BaseModel
from typing import List
from langchain_core.output_parsers import BaseOutputParser
from langchain.output_parsers import PydanticOutputParser
import re

class MissingDomain(BaseModel):
    missing_strengths: List[str]
    missing_weaknesses: List[str]

missing_domain_parser = PydanticOutputParser(pydantic_object=MissingDomain)

class ThinkTagParser(BaseOutputParser[str]):
    """Parser that extracts text after </think> tag"""
    
    def parse(self, text: str) -> str:
        pattern = r"</think>(.*)"
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1).strip() if match else text

