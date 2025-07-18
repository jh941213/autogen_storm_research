"""AutoGen STORM Research Assistant Data Models

이 모듈은 연구 과정에서 사용되는 데이터 모델들을 정의합니다.
"""

from dataclasses import dataclass
from typing import List, Optional
from pydantic import BaseModel, Field

class Analyst(BaseModel):
    """Analyst attributes and metadata definition class
    
    Each analyst has unique perspectives and expertise.
    """
    
    # Primary affiliation information
    affiliation: str = Field(description="Analyst's primary organization or institution")
    # Name
    name: str = Field(description="Analyst's name")
    # Role
    role: str = Field(description="Analyst's role related to the research topic")
    # Description of interests, concerns, and motivations
    description: str = Field(description="Description of analyst's interests, concerns, and motivations")

    @property
    def persona(self) -> str:
        """Return analyst's persona as string"""
        return f"Name: {self.name}\nRole: {self.role}\nAffiliation: {self.affiliation}\nDescription: {self.description}\n"


class Perspectives(BaseModel):
    """Class representing a collection of analysts"""
    
    analysts: List[Analyst] = Field(
        description="Comprehensive list of analysts including roles and affiliations"
    )


class SearchQuery(BaseModel):
    """Data class for search queries"""
    
    search_query: str = Field(description="Search query for information retrieval")


@dataclass
class ResearchTask:
    """연구 작업을 나타내는 데이터 클래스"""
    
    topic: str
    max_analysts: int = 3
    max_interview_turns: int = 3
    parallel_interviews: bool = True
    user_feedback: Optional[str] = None


@dataclass
class InterviewResult:
    """인터뷰 결과를 나타내는 데이터 클래스"""
    
    analyst: Analyst
    interview_content: str
    section_content: str


@dataclass
class ResearchResult:
    """최종 연구 결과를 나타내는 데이터 클래스"""
    
    topic: str
    analysts: List[Analyst]
    interviews: List[InterviewResult]
    introduction: str
    main_content: str
    conclusion: str
    final_report: str