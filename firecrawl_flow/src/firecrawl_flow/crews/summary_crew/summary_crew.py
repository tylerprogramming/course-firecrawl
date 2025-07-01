from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from pydantic import BaseModel

class Summary(BaseModel):
    key_action_items: list[str]
    dramatic_news_points: list[str]
    key_takeaways: list[str]
    summary: str

@CrewBase
class SummaryCrew:
    """Summary Crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def summary_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["summary_agent"],  # type: ignore[index]
        )

    @task
    def summary_task(self) -> Task:
        return Task(
            config=self.tasks_config["summary_task"],  # type: ignore[index]
            output_pydantic=Summary,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Summary Crew"""

        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
