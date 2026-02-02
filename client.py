import requests
import json

BASE_URL = "http://127.0.0.1:8001"

def pretty_print_response(action: str, response: requests.Response):
    """Print response as pretty JSON"""
    print(f"[{action}] Status: {response.status_code}")

    try:
        data = response.json()
    except ValueError:
        # If response has no JSON (e.g. empty body)
        print("Antwort: <kein JSON>\n")
        return None

    print("Antwort:")
    print(json.dumps(data, indent=2, ensure_ascii=False))  # nice formatting
    print()  # empty line for spacing
    return data

################################################################################

def create_ticket(ticket_data):
    """Ein neues Ticket erstellen"""
    response = requests.post(f"{BASE_URL}/tickets", json=ticket_data)
    return pretty_print_response("ERSTELLEN", response)


def get_status_list():
    """Liste der IDs und Status aller Tickets abrufen"""
    response = requests.get(f"{BASE_URL}/tickets")
    if response.status_code != 200:
        print(f"[FEHLER] Ticket not found. Status: {response.status_code}")
        return []

    try:
        tickets = response.json()
        result = [{"id": ticket["id"], "priority": ticket["priority"] ,"status": ticket["status"]} for ticket in tickets]
        print(json.dumps(result, indent=2, ensure_ascii=False))   #nice formatting
        # return []

    except (ValueError, KeyError) as e:
        print(f"[FEHLER] JSON processing error: {e}")
        return []



def get_ticket(ticket_id):
    """Ein einzelnes Ticket nach ID abrufen"""
    response = requests.get(f"{BASE_URL}/tickets/{ticket_id}")
    return pretty_print_response("ABRUFEN", response)


def get_all_tickets():
    """Liste aller Tickets abrufen"""
    response = requests.get(f"{BASE_URL}/tickets")
    return pretty_print_response("ALLE ABRUFEN", response)


def update_ticket(ticket_id, ticket_data):
    """Ticket aktualisieren"""
    response = requests.put(f"{BASE_URL}/tickets/{ticket_id}", json=ticket_data)
    return pretty_print_response("AKTUALISIEREN", response)


def delete_ticket(ticket_id):
    """Ticket löschen"""
    response = requests.delete(f"{BASE_URL}/tickets/{ticket_id}")
    return pretty_print_response("LÖSCHEN", response)



# def create_ticket(ticket_data):
#     """Ein neues Ticket erstellen"""
#     response = requests.post(f"{BASE_URL}/tickets", json=ticket_data)
#     print(f"[ERSTELLEN] Status: {response.status_code}")
#     print(f"Antwort: {response.json()}\n")
#     return response.json()
#
#
# def get_ticket(ticket_id):
#     """Ein einzelnes Ticket nach ID abrufen"""
#     response = requests.get(f"{BASE_URL}/tickets/{ticket_id}")
#     print(f"[ABRUFEN] Status: {response.status_code}")
#     if response.status_code == 200:
#         print(f"Antwort: {response.json()}\n")
#         return response.json()
#     else:
#         print(f"Fehler: {response.json()}\n")
#         return None
#
#
# def get_all_tickets():
#     """Liste aller Tickets abrufen"""
#     response = requests.get(f"{BASE_URL}/tickets")
#     print(f"[ALLE ABRUFEN] Status: {response.status_code}")
#     print(f"Antwort: {response.json()}\n")
#     return response.json()
#
#
# def update_ticket(ticket_id, ticket_data):
#     """Ticket aktualisieren"""
#     response = requests.put(f"{BASE_URL}/tickets/{ticket_id}", json=ticket_data)
#     print(f"[AKTUALISIEREN] Status: {response.status_code}")
#     print(f"Antwort: {response.json()}\n")
#     return response.json()
#
#
# def delete_ticket(ticket_id):
#     """Ticket löschen"""
#     response = requests.delete(f"{BASE_URL}/tickets/{ticket_id}")
#     print(f"[LÖSCHEN] Status: {response.status_code}")
#     print(f"Antwort: {response.json()}\n")
#     return response.json()


def main():
    """Demonstration der API-Funktionalität"""
    print("=== Ticket Tracker Client Demo ===\n")

    # 1. Tickets erstellen
    print("--- Tickets erstellen ---")
    ticket1 = {
        "id": 1,
        "title": "Login-Bug beheben",
        "description": "Benutzer kann sich nicht mit korrektem Passwort anmelden",
        "status": "open",
        "priority": "high",
        "assignee": "Dima"
    }
    create_ticket(ticket1)

    ticket2 = {
        "id": 2,
        "title": "Auth-Modul refaktorieren",
        "description": "Legacy-Code aufräumen",
        "status": "in_progress",
        "priority": "normal",
        "assignee": "Alex"
    }
    create_ticket(ticket2)

    ticket3 = {
        "id": 3,
        "title": "Test Ticket",
        "description": "API-Test",
        "status": "open",
        "priority": "low",
        "assignee": "Maria"
    }
    create_ticket(ticket3)

    # 1.1. Liste der IDs und Status aller Tickets abrufen
    print("--- Liste der IDs und Status aller Tickets ---")
    statuses = get_status_list()
    # print(statuses)


    # 2. Ein Ticket abrufen
    print("--- Ticket #1 abrufen ---")
    get_ticket(1)

    # 3. Ticket aktualisieren (Status ändern)
    print("--- Ticket #1 aktualisieren (Status auf 'in_progress' ändern) ---")
    ticket1["status"] = "in_progress"
    ticket1["description"] = "I need two days to fix this bug."
    update_ticket(1, ticket1)

    # 4. Alle Tickets abrufen
    print("--- Alle Tickets abrufen ---")
    all_tickets = get_all_tickets()
    if all_tickets is not None:
        print(f"Anzahl der Tickets: {len(all_tickets)}\n")

    # 5. Ticket löschen
    print("--- Ticket #2 löschen ---")
    delete_ticket(2)

    # 6. Versuch, gelöschtes Ticket abzurufen (404 erwartet)
    print("--- Versuch, gelöschtes Ticket #2 abzurufen ---")
    get_ticket(2)

    # 7. Finale Liste
    print("--- Finale Ticket-Liste ---")
    final_tickets = get_all_tickets()
    if final_tickets is not None:
        print(f"Verbleibende Tickets: {len(final_tickets)}")


if __name__ == "__main__":
    main()