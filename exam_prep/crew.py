# exam_prep/crew.py
import os
import requests
from crewai import Crew, Agent, Task, LLM

# Minimal Serper wrapper reused from your travel project
class SerperSearch:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.endpoint = "https://google.serper.dev/search"

    def search(self, query: str) -> dict:
        headers = {"X-API-KEY": self.api_key, "Content-Type": "application/json"}
        payload = {"q": query}
        resp = requests.post(self.endpoint, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()


class ExamPrepCrew:
    def __init__(self):
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        serper_api_key = os.getenv("SERPER_API_KEY")

        if not gemini_api_key:
            raise ValueError("Missing GEMINI_API_KEY in environment")
        if not serper_api_key:
            raise ValueError("Missing SERPER_API_KEY in environment")

        # Use CrewAI LLM (Gemini) — this matches your travel project approach
        self.llm = LLM(
            model="gemini/gemini-1.5-flash",
            api_key=gemini_api_key,
        )

        # Search/research tool
        self.search_tool = SerperSearch(serper_api_key)

    def crew(self) -> Crew:
        """Construct and return the crew for the exam-prep pipeline."""

        # === Agents ===
        pyq_analyzer = Agent(
            role="Previous Year Question Analyzer",
            goal="Analyze previous year questions to find repeated topics, formats and difficulty distribution.",
            backstory="Exam analysis specialist with deep knowledge of SSC/UPSC/IELTS question patterns.",
            allow_delegation=False,
            llm=self.llm,
        )

        topic_explainer = Agent(
            role="Topic Explainer",
            goal="Explain core concepts for requested topics in simple terms with examples and short practice tasks.",
            backstory="A patient teacher who explains topics with examples and quick practice questions.",
            allow_delegation=False,
            llm=self.llm,
        )

        mock_test_creator = Agent(
            role="Mock Test Creator",
            goal="Create mock test questions that mimic the target exam format, with answers and difficulty tags.",
            backstory="Exam coach who crafts balanced mock tests across topics and difficulty levels.",
            allow_delegation=False,
            llm=self.llm,
        )

        weakness_analyzer = Agent(
            role="Weakness Analyzer & Study Planner",
            goal="Analyze mock test results, identify weak topics, and generate a personalized study plan with daily tasks.",
            backstory="A mentor who creates actionable, time-boxed study plans targeted at weakest topics.",
            allow_delegation=False,
            llm=self.llm,
        )

        # === Tasks ===
        pyq_task = Task(
            description=(
                "Task: Analyze previous year questions for {exam_type} on subjects: {subjects}.\n\n"
                "Inputs available: pyq_folder (optional). If pyq_folder provided, parse documents there; otherwise use web research.\n\n"
                "Produce: 'output/01_pyq_analysis.md' summarizing most repeated topics, question formats, difficulty distribution, and recommended topic priorities."
            ),
            agent=pyq_analyzer,
            expected_output="Markdown report: output/01_pyq_analysis.md",
        )

        explanation_task = Task(
            description=(
                "Task: For subjects {subjects}, produce clear explanations for top N important topics identified earlier.\n\n"
                "Produce: 'output/02_topic_explanations.md' with explanations, short examples, and 2 quick practice questions per topic."
            ),
            agent=topic_explainer,
            expected_output="Markdown file: output/02_topic_explanations.md",
        )

        mock_test_task = Task(
            description=(
                "Task: Create a mock test of 20-30 questions for {exam_type} covering {subjects} and prioritized topics.\n\n"
                "Include question, answer, brief explanation, difficulty tag (easy/medium/hard).\n\n"
                "Produce: 'output/03_mock_test.md'."
            ),
            agent=mock_test_creator,
            expected_output="Markdown file: output/03_mock_test.md",
        )

        weakness_task = Task(
            description=(
                "Task: Given mock test responses (or simulated performance), analyze strengths & weaknesses, and produce:\n"
                " - 'output/04_weakness_report.md' (detailed weak topics + suggested micro-practice)\n"
                " - 'output/05_study_plan.md' (personalized day-by-day study plan for {days_until_exam} days using {study_hours}/day)"
            ),
            agent=weakness_analyzer,
            expected_output="Markdown files: output/04_weakness_report.md and output/05_study_plan.md",
        )

        # Return crew with agents & tasks in the required order
        return Crew(
            agents=[pyq_analyzer, topic_explainer, mock_test_creator, weakness_analyzer],
            tasks=[pyq_task, explanation_task, mock_test_task, weakness_task],
            verbose=True,
        )
