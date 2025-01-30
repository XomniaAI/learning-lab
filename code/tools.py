from trello import TrelloClient
import os
from dotenv import load_dotenv
import json
from smolagents import tool

load_dotenv()

client = TrelloClient(
    api_key=os.getenv('TRELLO_API_KEY'),
    token=os.getenv('TRELLO_TOKEN')
)
#board = client.get_board(os.getenv('TRELLO_BOARD_ID'))

@tool
def list_boards() -> str:
    """Get a list of all accessible Trello boards. This function should be called first to get the board ID
    before using select_board().
    
    Returns:
        str: A JSON string containing board details including id, name, and description.
    """
    boards = client.list_boards()
    board_list = [{
        'id': b.id,
        'name': b.name,
        'description': b.description,
        'url': b.url
    } for b in boards]
    return json.dumps(board_list)

@tool
def select_board(board_id: str) -> str:
    """Select a specific board to work with. The board_id should be obtained first by calling list_boards().
    
    Args:
        board_id: The ID of the board to select, which can be obtained from list_boards().
    
    Returns:
        str: A confirmation message with board details.
    """
    global board
    board = client.get_board(board_id)
    return f"Selected board: {board.name}"

@tool
def get_board_lists() -> str:
    """Get all lists from the current board, including both open and archived lists.
    Note that archived (closed) lists will be marked as such in the response.
    
    Returns:
        str: A JSON string containing lists and their details, including archive status.
    """
    lists = [{
        'id': lst.id,
        'name': lst.name,
        'cards_count': len(lst.list_cards()),
        'is_archived': lst.closed
    } for lst in board.list_lists(list_filter='all')]
    return json.dumps(lists)

@tool
def get_list_cards(list_name: str) -> str:
    """Get all cards from a specific list.
    Note that this can return cards from both active and archived lists - check the list status in the response.
    
    Args:
        list_name: The name of the list to get cards from.
    
    Returns:
        str: A JSON string containing card details and list status.
    """
    target_list = next((l for l in board.list_lists(list_filter='all') if l.name.lower() == list_name.lower()), None)
    if not target_list:
        return json.dumps({"error": f"List '{list_name}' not found"})
    
    cards = [{
        'id': card.id,
        'name': card.name,
        'description': card.description,
        'due_date': str(card.due_date) if card.due_date else None,
        'labels': [label.name for label in card.labels],
        'url': card.url,
        'list_is_archived': target_list.closed
    } for card in target_list.list_cards()]
    return json.dumps(cards)

@tool
def get_card_details(card_id: str) -> str:
    """Get detailed information about a specific card.
    
    Args:
        card_id: The ID of the card to inspect.
    
    Returns:
        str: A JSON string containing detailed card information.
    """
    card = client.get_card(card_id)
    details = {
        'id': card.id,
        'name': card.name,
        'description': card.description,
        'due_date': str(card.due_date) if card.due_date else None,
        'labels': [label.name for label in card.labels],
        'members': [member.full_name for member in card.member_id if member.full_name],
        'list_name': card.get_list().name,
        'url': card.url,
        'last_activity': str(card.date_last_activity) if card.date_last_activity else None,
        'comments': [comment['data']['text'] for comment in card.get_comments()]
    }
    return json.dumps(details)

@tool
def create_card(list_name: str, title: str, description: str, labels: str = None, due_date: str = None) -> str:
    """Create a new card in the specified list.
    
    Args:
        list_name: The name of the list where the card should be created.
        title: The title of the new card.
        description: The detailed description of the card.
        labels: Optional JSON string containing a list of label names to attach.
        due_date: Optional due date in ISO format (YYYY-MM-DD).
    
    Returns:
        str: A JSON string containing the new card's details.
    """
    target_list = next((l for l in board.list_lists() if l.name.lower() == list_name.lower()), None)
    if not target_list:
        return json.dumps({"error": f"List '{list_name}' not found"})
    
    card = target_list.add_card(name=title, desc=description)
    
    if due_date:
        card.set_due(due_date)
    
    if labels:
        label_list = json.loads(labels)
        board_labels = board.get_labels()
        for label_name in label_list:
            label = next((l for l in board_labels if l.name.lower() == label_name.lower()), None)
            if label:
                card.add_label(label)
    
    return get_card_details(card.id)

@tool
def get_available_labels() -> str:
    """Get all available labels on the current board.
    
    Returns:
        str: A JSON string containing label details.
    """
    labels = [{
        'id': label.id,
        'name': label.name,
        'color': label.color
    } for label in board.get_labels()]
    return json.dumps(labels) 