from smolagents import (
    ToolCallingAgent,
    HfApiModel,
)

from tools import (
    list_boards,
    select_board,
    get_board_lists,
    get_list_cards,
    get_card_details,
    create_card,
    get_available_labels
)

model = HfApiModel()

trello_agent = ToolCallingAgent(
    tools=[
        list_boards,
        select_board,
        get_board_lists,
        get_list_cards,
        get_card_details,
        create_card,
        get_available_labels
    ],
    model=model,
)

if __name__ == "__main__":
    example_tasks = [
        "List the names of the Trello boards",
        "Create 2 tickets for preparing an LLM training in the GenAI board",
        "What tickets can I pick up? I prefer tasks related to coding",
        "Show me top 3 high priority tasks in the internal board",
    ]

    trello_agent.run(example_tasks[0]) 